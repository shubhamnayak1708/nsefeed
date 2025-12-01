"""
NSE Session management with proper cookie and header handling.

This module provides a singleton NSESession class that manages:
- Session initialization with NSE website
- Cookie acquisition and management
- Rate limiting (max 3 requests/second)
- Automatic retry with exponential backoff
- Session refresh on authentication errors
- User-Agent rotation for resilience
"""

from __future__ import annotations

import random
import threading
import time
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from . import logger
from .constants import (
    DEFAULT_HEADERS,
    ARCHIVE_HEADERS,
    USER_AGENTS,
    NSE_BASE_URL,
    NSE_ENDPOINTS,
    MAX_RETRIES,
    RETRY_BACKOFF_FACTOR,
    INITIAL_RETRY_DELAY,
    REQUEST_TIMEOUT,
    MIN_REQUEST_DELAY,
    SESSION_REFRESH_INTERVAL,
)
from .exceptions import (
    NSEConnectionError,
    NSERateLimitError,
    NSESessionError,
)


class NSESession:
    """
    Singleton class for managing NSE HTTP sessions.

    This class handles all communication with NSE servers, including:
    - Initial session establishment (cookie acquisition)
    - Rate limiting to avoid being blocked
    - Automatic retry with exponential backoff
    - Session refresh on authentication failures

    Usage:
        session = NSESession.get_instance()
        data = session.get("/api/quote-equity", params={"symbol": "RELIANCE"})

    Thread-Safety:
        This class is thread-safe and can be used from multiple threads.
    """

    _instance: Optional["NSESession"] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> "NSESession":
        """Ensure singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize the session (only runs once due to singleton)."""
        if self._initialized:
            return

        self._session: Optional[requests.Session] = None
        self._cookies: dict[str, str] = {}
        self._last_request_time: float = 0.0
        self._session_created_time: float = 0.0
        self._request_lock: threading.Lock = threading.Lock()
        self._ua_index: int = 0

        self._initialized = True
        self._init_session()

    @classmethod
    def get_instance(cls) -> "NSESession":
        """Get the singleton instance of NSESession."""
        return cls()

    def _init_session(self) -> None:
        """Initialize a new requests session with proper configuration."""
        logger.debug("Initializing new NSE session")

        # Create new session
        self._session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=RETRY_BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

        # Set default headers
        self._session.headers.update(self._get_headers())

        # Establish session with NSE
        self._establish_session()

    def _get_headers(self, for_archive: bool = False) -> dict[str, str]:
        """
        Get headers for requests, rotating User-Agent.

        Args:
            for_archive: If True, return archive-specific headers

        Returns:
            Dictionary of HTTP headers
        """
        headers = ARCHIVE_HEADERS.copy() if for_archive else DEFAULT_HEADERS.copy()

        # Rotate User-Agent
        self._ua_index = (self._ua_index + 1) % len(USER_AGENTS)
        headers["User-Agent"] = USER_AGENTS[self._ua_index]

        return headers

    def _establish_session(self) -> None:
        """
        Establish session by visiting NSE homepage to get cookies.

        NSE requires cookies from visiting the homepage before accessing
        any API endpoints. This method handles that initial handshake.
        """
        try:
            logger.debug("Establishing session with NSE homepage")

            # Visit homepage to get cookies
            response = self._session.get(
                NSE_ENDPOINTS["home"],
                headers=self._get_headers(),
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()

            # Store cookies
            self._cookies = dict(response.cookies)
            self._session_created_time = time.time()

            logger.info("NSE session established successfully")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to establish NSE session: {e}")
            raise NSESessionError(
                "Failed to establish session with NSE",
                details=str(e),
            )

    def _should_refresh_session(self) -> bool:
        """Check if session needs to be refreshed."""
        if self._session_created_time == 0:
            return True
        elapsed = time.time() - self._session_created_time
        return elapsed > SESSION_REFRESH_INTERVAL

    def _rate_limit(self) -> None:
        """
        Implement rate limiting to avoid being blocked.

        Ensures minimum delay between requests (approximately 3 req/sec).
        """
        with self._request_lock:
            now = time.time()
            elapsed = now - self._last_request_time
            if elapsed < MIN_REQUEST_DELAY:
                sleep_time = MIN_REQUEST_DELAY - elapsed
                logger.debug(f"Rate limiting: sleeping for {sleep_time:.3f}s")
                time.sleep(sleep_time)
            self._last_request_time = time.time()

    def _handle_response_error(
        self, response: requests.Response, url: str
    ) -> None:
        """
        Handle HTTP error responses.

        Args:
            response: The HTTP response object
            url: The requested URL

        Raises:
            NSERateLimitError: If rate limited (429)
            NSEConnectionError: For other HTTP errors
        """
        status_code = response.status_code

        if status_code == 401 or status_code == 403:
            logger.warning(f"Authentication error ({status_code}), refreshing session")
            self._establish_session()
            raise NSESessionError(
                f"Authentication failed (HTTP {status_code})",
                details="Session has been refreshed, please retry",
            )

        if status_code == 429:
            retry_after = float(response.headers.get("Retry-After", 60))
            logger.warning(f"Rate limited, retry after {retry_after}s")
            raise NSERateLimitError(retry_after=retry_after)

        if status_code == 404:
            raise NSEConnectionError(
                "Resource not found",
                details=f"URL: {url}",
                status_code=status_code,
            )

        raise NSEConnectionError(
            f"HTTP error {status_code}",
            details=response.text[:200] if response.text else None,
            status_code=status_code,
        )

    def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        for_archive: bool = False,
        timeout: int = REQUEST_TIMEOUT,
    ) -> requests.Response:
        """
        Make a GET request to NSE with proper session handling.

        Args:
            url: URL or endpoint path (if starts with /, prepends NSE_BASE_URL)
            params: Query parameters
            for_archive: If True, use archive-specific headers
            timeout: Request timeout in seconds

        Returns:
            requests.Response object

        Raises:
            NSEConnectionError: On connection failures
            NSERateLimitError: If rate limited
            NSESessionError: On session issues
        """
        # Build full URL if needed
        if url.startswith("/"):
            url = f"{NSE_BASE_URL}{url}"

        # Refresh session if needed
        if self._should_refresh_session():
            logger.debug("Session expired, refreshing")
            self._establish_session()

        # Apply rate limiting
        self._rate_limit()

        # Make request with retry logic
        retry_count = 0
        last_exception: Exception | None = None

        while retry_count <= MAX_RETRIES:
            try:
                logger.debug(f"GET {url} (attempt {retry_count + 1})")

                response = self._session.get(
                    url,
                    params=params,
                    headers=self._get_headers(for_archive=for_archive),
                    cookies=self._cookies,
                    timeout=timeout,
                )

                # Handle non-success status codes
                if not response.ok:
                    self._handle_response_error(response, url)

                return response

            except NSESessionError:
                # Session was refreshed, retry immediately
                retry_count += 1
                continue

            except NSERateLimitError as e:
                # Rate limited, wait and retry
                if e.retry_after:
                    time.sleep(e.retry_after)
                retry_count += 1
                last_exception = e
                continue

            except requests.exceptions.Timeout as e:
                logger.warning(f"Request timeout: {url}")
                retry_count += 1
                last_exception = e
                time.sleep(INITIAL_RETRY_DELAY * (RETRY_BACKOFF_FACTOR ** retry_count))
                continue

            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                retry_count += 1
                last_exception = e
                time.sleep(INITIAL_RETRY_DELAY * (RETRY_BACKOFF_FACTOR ** retry_count))
                continue

        # All retries exhausted
        raise NSEConnectionError(
            "Failed to connect to NSE after multiple retries",
            details=str(last_exception) if last_exception else None,
        )

    def get_json(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        timeout: int = REQUEST_TIMEOUT,
    ) -> dict[str, Any]:
        """
        Make a GET request and parse JSON response.

        Args:
            url: URL or endpoint path
            params: Query parameters
            timeout: Request timeout in seconds

        Returns:
            Parsed JSON as dictionary

        Raises:
            NSEConnectionError: On connection or parsing failures
        """
        response = self.get(url, params=params, timeout=timeout)

        try:
            return response.json()
        except ValueError as e:
            raise NSEConnectionError(
                "Failed to parse JSON response",
                details=str(e),
            )

    def download_file(
        self,
        url: str,
        timeout: int = REQUEST_TIMEOUT * 2,
    ) -> bytes:
        """
        Download a file (e.g., bhav copy ZIP) from NSE archives.

        Args:
            url: URL of the file to download
            timeout: Request timeout in seconds

        Returns:
            File content as bytes

        Raises:
            NSEConnectionError: On download failures
        """
        response = self.get(url, for_archive=True, timeout=timeout)
        return response.content

    def close(self) -> None:
        """Close the session and clean up resources."""
        if self._session:
            self._session.close()
            self._session = None
            self._cookies = {}
            self._session_created_time = 0
            logger.debug("NSE session closed")

    def __enter__(self) -> "NSESession":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - close session."""
        self.close()

    @classmethod
    def reset_instance(cls) -> None:
        """
        Reset the singleton instance.

        Useful for testing or when a fresh session is needed.
        """
        with cls._lock:
            if cls._instance is not None:
                cls._instance.close()
                cls._instance = None
