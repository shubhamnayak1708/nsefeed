# How to Publish nsefeed to PyPI

## ✅ Pre-Publication Checklist

- [x] Author information updated (Shubham Nayak)
- [x] GitHub URLs updated (shubhamnayak1708/nsefeed)
- [x] CHANGELOG.md updated to v1.0.0
- [x] Package rebuilt successfully
- [ ] GitHub repository created and code pushed
- [ ] PyPI account created
- [ ] TestPyPI account created (optional but recommended)

---

## 📋 Step-by-Step Publishing Guide

### Step 1: Install Required Tools

```bash
pip install --upgrade twine build
```

### Step 2: Create PyPI Accounts

**a) Create PyPI Account (Production)**
- Go to: https://pypi.org/account/register/
- Create account with your email
- Verify email
- **Enable 2FA (required for uploading)**

**b) Create TestPyPI Account (Optional - for testing)**
- Go to: https://test.pypi.org/account/register/
- Create account (can use same email)
- Verify email

### Step 3: Create API Tokens

**For PyPI (Production):**
1. Login to https://pypi.org
2. Go to Account Settings → API tokens
3. Click "Add API token"
4. Name: `nsefeed-upload`
5. Scope: "Entire account" (or specific to nsefeed after first upload)
6. **COPY THE TOKEN** (starts with `pypi-...`)
7. Save it securely - you'll only see it once!

**For TestPyPI (Optional):**
1. Login to https://test.pypi.org
2. Repeat same steps as above
3. Token will start with `pypi-...`

### Step 4: Configure Credentials

**Option A: Create ~/.pypirc file (Recommended)**

Create file `C:\Users\shubh\.pypirc` with:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_PYPI_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TESTPYPI_TOKEN_HERE
```

**Replace `pypi-YOUR_PYPI_TOKEN_HERE` with your actual token!**

**Option B: Use token directly in command (see Step 6)**

---

## 🧪 Step 5: Test on TestPyPI First (Recommended)

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*
```

**If using token directly (no .pypirc):**
```bash
twine upload --repository testpypi dist/* -u __token__ -p pypi-YOUR_TESTPYPI_TOKEN_HERE
```

**Verify installation from TestPyPI:**
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ nsefeed
```

**Test it works:**
```bash
python -c "import nsefeed as nf; ticker = nf.Ticker('TCS'); print('Success!')"
```

**Uninstall test version:**
```bash
pip uninstall nsefeed -y
```

---

## 🚀 Step 6: Publish to PyPI (Production)

### Final Verification
```bash
# Check package contents
tar -tzf dist/nsefeed-1.0.0.tar.gz | head -20

# Check package metadata
twine check dist/*
```

### Upload to PyPI
```bash
# Using .pypirc file
twine upload dist/*
```

**OR using token directly:**
```bash
twine upload dist/* -u __token__ -p pypi-YOUR_PYPI_TOKEN_HERE
```

### Expected Output
```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading nsefeed-1.0.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 58.0/58.0 kB • 00:00
Uploading nsefeed-1.0.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 52.0/52.0 kB • 00:00

View at:
https://pypi.org/project/nsefeed/1.0.0/
```

---

## ✅ Step 7: Verify Publication

### Check PyPI Page
Open: https://pypi.org/project/nsefeed/

### Install from PyPI
```bash
pip install nsefeed
```

### Test Installation
```bash
python -c "import nsefeed as nf; print(f'nsefeed v{nf.__version__} by {nf.__author__}'); ticker = nf.Ticker('RELIANCE'); print('SUCCESS!')"
```

---

## 🎉 Step 8: Announce Release

### Update GitHub
```bash
# Create and push Git tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Create GitHub Release
# Go to: https://github.com/shubhamnayak1708/nsefeed/releases/new
# Tag: v1.0.0
# Title: nsefeed v1.0.0 - Production Release
# Description: Copy from CHANGELOG.md
```

### Share on Social Media
- Twitter/X
- LinkedIn
- Reddit (r/Python, r/algotrading, r/IndianStockMarket)
- Dev.to / Medium

---

## 🔧 Troubleshooting

### Error: "Invalid or non-existent authentication information"
- Check your API token is correct
- Ensure 2FA is enabled on PyPI account
- Token format: `pypi-AgEIcHlwaS5vcmcC...`

### Error: "File already exists"
- Package version 1.0.0 already uploaded
- Increment version in `pyproject.toml` and rebuild:
  ```bash
  # Edit version in pyproject.toml to 1.0.1
  python -m build --sdist --wheel .
  twine upload dist/*
  ```

### Error: "403 Forbidden"
- Enable 2FA on PyPI account
- Recreate API token after enabling 2FA

### Error: Package not found after upload
- Wait 1-2 minutes for PyPI to process
- Check: https://pypi.org/project/nsefeed/

---

## 📝 Quick Command Reference

```bash
# 1. Install tools
pip install --upgrade twine build

# 2. Build package (after making changes)
rm -rf build dist nsefeed.egg-info
python -m build --sdist --wheel .

# 3. Check package
twine check dist/*

# 4. Upload to TestPyPI (optional)
twine upload --repository testpypi dist/*

# 5. Upload to PyPI (production)
twine upload dist/*

# 6. Create Git tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

---

## 🎯 Next Steps After Publishing

1. **Monitor PyPI Stats**
   - https://pypistats.org/packages/nsefeed

2. **Respond to Issues**
   - Watch GitHub issues: https://github.com/shubhamnayak1708/nsefeed/issues

3. **Plan Next Release**
   - Work on index data alternative sources
   - Add features from CHANGELOG "Planned" section

4. **Build Community**
   - Write blog posts / tutorials
   - Create example notebooks
   - Respond to user questions

---

## 📞 Support

- PyPI Help: https://pypi.org/help/
- Twine Docs: https://twine.readthedocs.io/
- Python Packaging Guide: https://packaging.python.org/

**Your package is ready to go! 🚀**
