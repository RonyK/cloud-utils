#!/bin/bash

# Package Build Script

echo "🧹 Cleaning previous build files..."
rm -rf dist/ build/ *.egg-info/

echo "📦 Building package..."
python -m build

echo "✅ Build completed!"
echo "📁 Check the dist/ directory."

