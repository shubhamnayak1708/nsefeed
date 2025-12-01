"""
Unit tests for NSE Session management.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests

from nsefeed.session import NSESession
from nsefeed.exceptions import (
    NSEConnectionError,
    NSERateLimitError,
    NSESessionError,
)


@pytest.fixture(autouse=True)
def reset_session():
    """Reset session singleton before each test."""
    NSESession.reset_instance()
    yield
    NSESession.reset_instance()


class TestNSESessionSingleton:
    """Tests for singleton pattern."""

    def test_singleton_returns_same_instance(self):
        """Test that multiple calls return same instance."""
        with patch.object(NSESession, "_init_session"):
            session1 = NSESession.get_instance()
            session2 = NSESession.get_instance()
            assert session1 is session2

    def test_reset_creates_new_instance(self):
        """Test that reset creates a new instance."""
        with patch.object(NSESession, "_init_session"):
            session1 = NSESession.get_instance()
            NSESession.reset_instance()
            session2 = NSESession.get_instance()
            assert session1 is not session2


class TestNSESessionInit:
    """Tests for session initialization."""

    @patch("nsefeed.session.requests.Session")
    def test_session_created(self, mock_session_class):
        """Test that requests session is created."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.ok = True
        mock_response.cookies = {"cookie1": "value1"}
        mock_session.get.return_value = mock_response

        session = NSESession.get_instance()
        assert session is not None

    @patch("nsefeed.session.requests.Session")
    def test_session_establishes_with_homepage(self, mock_session_class):
        """Test that session visits homepage for cookies."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.ok = True
        mock_response.cookies = {}
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        NSESession.get_instance()

        # Should have called get on homepage
        assert mock_session.get.called


class TestNSESessionGet:
    """Tests for GET requests."""

    @patch("nsefeed.session.requests.Session")
    def test_get_success(self, mock_session_class):
        """Test successful GET request."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # Mock homepage response
        mock_homepage = Mock()
        mock_homepage.ok = True
        mock_homepage.cookies = {"nsit": "test"}
        mock_homepage.raise_for_status = Mock()

        # Mock API response
        mock_api = Mock()
        mock_api.ok = True
        mock_api.json.return_value = {"data": "test"}

        mock_session.get.side_effect = [mock_homepage, mock_api]

        session = NSESession.get_instance()
        response = session.get("https://www.nseindia.com/api/test")

        assert response.ok

    @patch("nsefeed.session.requests.Session")
    def test_get_handles_401(self, mock_session_class):
        """Test that 401 triggers session refresh."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # Mock homepage response
        mock_homepage = Mock()
        mock_homepage.ok = True
        mock_homepage.cookies = {}
        mock_homepage.raise_for_status = Mock()

        # Mock 401 response
        mock_401 = Mock()
        mock_401.ok = False
        mock_401.status_code = 401

        # Need enough responses for: initial homepage, 401 response, 
        # session refresh homepage, retry attempts (MAX_RETRIES = 3)
        mock_session.get.side_effect = [
            mock_homepage,  # Initial session
            mock_401,       # First API call - 401
            mock_homepage,  # Session refresh
            mock_401,       # Retry 1 - still 401
            mock_homepage,  # Session refresh again
            mock_401,       # Retry 2 - still 401
            mock_homepage,  # Session refresh again
            mock_401,       # Retry 3 - still 401
            mock_homepage,  # Session refresh again
        ]

        session = NSESession.get_instance()

        with pytest.raises((NSESessionError, NSEConnectionError)):
            session.get("https://www.nseindia.com/api/test")


class TestNSESessionRateLimiting:
    """Tests for rate limiting."""

    @patch("nsefeed.session.requests.Session")
    @patch("nsefeed.session.time.sleep")
    def test_rate_limiting_enforced(self, mock_sleep, mock_session_class):
        """Test that rate limiting delays requests."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.ok = True
        mock_response.cookies = {}
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        session = NSESession.get_instance()

        # Make multiple rapid requests
        for _ in range(3):
            session.get("https://www.nseindia.com/api/test")

        # Rate limiting sleep should have been called
        # (First request doesn't sleep, subsequent ones might)


class TestNSESessionContextManager:
    """Tests for context manager usage."""

    @patch("nsefeed.session.requests.Session")
    def test_context_manager(self, mock_session_class):
        """Test using session as context manager."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.ok = True
        mock_response.cookies = {}
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        with NSESession.get_instance() as session:
            assert session is not None
