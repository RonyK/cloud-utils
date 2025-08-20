# PyPI Deployment Guide

This document explains how to deploy the `cloud-utils` package to PyPI.

## Prerequisites

### 1. Create PyPI Account
- Create an account at [PyPI](https://pypi.org/account/register/).
- Also create an account at [Test PyPI](https://test.pypi.org/account/register/).

### 2. Generate API Token
- Go to "API tokens" section in PyPI account settings
- Click "Add API token"
- Enter token name and select "Entire account (all projects)"
- Save the generated token in a safe place

### 3. Configure GitHub Secrets
Set the following secrets in your GitHub repository at Settings > Secrets and variables > Actions:

- `PYPI_API_TOKEN`: PyPI API token
- `TEST_PYPI_API_TOKEN`: Test PyPI API token

## Local Testing

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Build Package
```bash
./scripts/build.sh
```

### 3. Test Upload to Test PyPI
```bash
twine upload --repository testpypi dist/*
```

### 4. Test Installation from Test PyPI
```bash
pip install --index-url https://test.pypi.org/simple/ cloud-utils
```

## Automatic Deployment

### 1. Create GitHub Release
- Create a new release on GitHub
- Create a tag (e.g., `v0.1.0`)
- Set the release to "Publish" status

### 2. Verify Automatic Deployment
- The `Publish to PyPI` workflow will automatically run in GitHub Actions
- The package will be uploaded to PyPI

## Manual Deployment

### 1. Build Package
```bash
python -m build
```

### 2. Upload to PyPI
```bash
twine upload dist/*
```

## Version Management

### 1. Update Version
- Modify `__version__` in `src/cloud_utils/__init__.py`
- Manage versions by creating Git tags

### 2. Create Tag
```bash
git tag v0.1.0
git push origin v0.1.0
```

## Troubleshooting

### 1. Build Errors
- Check syntax in `pyproject.toml`
- Verify all dependencies are properly installed

### 2. Upload Errors
- Verify PyPI API token is correct
- Check if package name is already in use
- Ensure version number is higher than previous version

### 3. Installation Errors
- Verify required files are included in `MANIFEST.in`
- Check package configuration in `pyproject.toml`

## Useful Commands

```bash
# Check package information
python -m build --help

# Validate package
twine check dist/*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ cloud-utils

# Install in development mode locally
pip install -e .
```

## References

- [Python Packaging User Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [setuptools Documentation](https://setuptools.pypa.io/)

