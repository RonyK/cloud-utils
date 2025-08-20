# PyPI Deployment Quick Start

## 🚀 Quick Deployment

### 1. Activate Virtual Environment
```bash
./activate.sh
```

### 2. Build Package
```bash
python -m build
```

### 3. Validate Package
```bash
twine check dist/*
```

### 4. Upload to Test PyPI (for testing)
```bash
twine upload --repository testpypi dist/*
```

### 5. Upload to PyPI (production deployment)
```bash
twine upload dist/*
```

## 📋 Prerequisites

1. **Create PyPI Account**: https://pypi.org/account/register/
2. **Generate API Token**: PyPI Account Settings → API tokens
3. **Configure GitHub Secrets**: Add `PYPI_API_TOKEN`

## 🔧 Troubleshooting

- **Dependency Error**: `pip install -r requirements.txt`
- **Build Error**: `python -m build --help`
- **Upload Error**: Verify API token

## 📚 Detailed Guide

Refer to `DEPLOYMENT.md` file.
