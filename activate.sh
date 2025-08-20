#!/bin/bash

# Virtual Environment Activation Script

echo "🐍 Activating Python virtual environment..."
source .venv/bin/activate

echo "✅ Virtual environment activated!"
echo "📦 Currently installed packages:"
pip list | grep -E "(cloud-utils|setuptools|wheel|build|twine)"

echo ""
echo "🚀 Available commands:"
echo "  - python -m build          # Build package"
echo "  - twine check dist/*       # Validate package"
echo "  - twine upload dist/*      # Upload to PyPI"
echo "  - twine upload --repository testpypi dist/*  # Upload to Test PyPI"
