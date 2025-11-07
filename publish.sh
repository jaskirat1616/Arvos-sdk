#!/bin/bash
# Automated PyPI publish script

set -e  # Exit on error

echo "🚀 Arvos SDK - PyPI Publisher"
echo "=============================="
echo ""

# Check if build and twine are installed
if ! python3 -m pip show build >/dev/null 2>&1 || ! python3 -m pip show twine >/dev/null 2>&1; then
    echo "📦 Installing build tools..."
    python3 -m pip install --upgrade pip build twine
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info python/arvos.egg-info

# Build the package
echo "🔨 Building package..."
python3 -m build

# Check the build
echo "✅ Build complete! Files created:"
ls -lh dist/

echo ""
echo "Choose upload destination:"
echo "1) TestPyPI (recommended for first upload)"
echo "2) PyPI (production)"
echo "3) Cancel"
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo "📤 Uploading to TestPyPI..."
        python3 -m twine upload --repository testpypi dist/*
        echo ""
        echo "✅ Uploaded to TestPyPI!"
        echo "Test installation with:"
        echo "  pip install --index-url https://test.pypi.org/simple/ arvos-sdk"
        ;;
    2)
        echo "📤 Uploading to PyPI..."
        python3 -m twine upload dist/*
        echo ""
        echo "✅ Uploaded to PyPI!"
        echo "Package available at: https://pypi.org/project/arvos-sdk/"
        echo "Install with: pip install arvos-sdk"
        ;;
    3)
        echo "❌ Cancelled"
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
