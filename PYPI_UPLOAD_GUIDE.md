# How to Upload Arvos SDK to PyPI

## Prerequisites
1. PyPI account: https://pypi.org/account/register/
2. TestPyPI account (optional, for testing): https://test.pypi.org/account/register/

## Step 1: Install Build Tools

```bash
cd /Users/jaskiratsingh/Desktop/arvos-sdk

# Install build tools
pip install --upgrade pip
pip install build twine
```

## Step 2: Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build distribution packages
python -m build
```

This creates:
- `dist/arvos_sdk-1.0.0.tar.gz` (source distribution)
- `dist/arvos_sdk-1.0.0-py3-none-any.whl` (wheel)

## Step 3: Test on TestPyPI (Optional but Recommended)

```bash
# Upload to TestPyPI first
python -m twine upload --repository testpypi dist/*

# You'll be prompted for:
# Username: your_testpypi_username
# Password: your_testpypi_password
```

Test installation:
```bash
pip install --index-url https://test.pypi.org/simple/ arvos-sdk
```

## Step 4: Upload to Real PyPI

```bash
# Upload to PyPI
python -m twine upload dist/*

# You'll be prompted for:
# Username: your_pypi_username
# Password: your_pypi_password
```

## Step 5: Verify Installation

```bash
# Install from PyPI
pip install arvos-sdk

# Test it
python -c "from arvos import ArvosServer; print('Success!')"
```

## Using API Tokens (Recommended)

Instead of username/password, use API tokens:

1. Go to https://pypi.org/manage/account/token/
2. Create a new API token with scope: "Entire account"
3. Save the token (starts with `pypi-...`)

Upload with token:
```bash
python -m twine upload dist/* -u __token__ -p pypi-YOUR_TOKEN_HERE
```

Or save in `~/.pypirc`:
```ini
[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE

[testpypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE
```

Then just run:
```bash
python -m twine upload dist/*
```

## Updating the Package

When you make changes:

1. Update version in `setup.py` (e.g., `1.0.0` → `1.0.1`)
2. Clean and rebuild:
   ```bash
   rm -rf dist/ build/ *.egg-info
   python -m build
   ```
3. Upload:
   ```bash
   python -m twine upload dist/*
   ```

## Quick Command Summary

```bash
# One-time setup
pip install build twine

# For each release
rm -rf dist/ build/ *.egg-info
python -m build
python -m twine upload dist/*
```

## After Upload

Your package will be available at:
- PyPI page: https://pypi.org/project/arvos-sdk/
- Install with: `pip install arvos-sdk`

Update the README to include:
```markdown
## Installation

```bash
pip install arvos-sdk
```
```

## Troubleshooting

**Error: "The user '...' isn't allowed to upload to project 'arvos-sdk'"**
- The package name is already taken. Change `name` in `setup.py` to something else (e.g., `arvos-sensor-sdk`)

**Error: "Package ... already exists"**
- You can't re-upload the same version. Increment version number in `setup.py`

**Error: "Invalid or non-existent authentication"**
- Check your PyPI credentials
- Make sure you're using the correct username/password or API token

## Links

- PyPI: https://pypi.org/
- TestPyPI: https://test.pypi.org/
- Packaging Tutorial: https://packaging.python.org/tutorials/packaging-projects/
