#!/bin/bash
# Google APIs Extension Installer (PageSpeed, CrUX, GSC, GA4)
# Part of claude-seo-unified-v1.9.6

set -e

EXTENSION_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$EXTENSION_DIR/../.." && pwd)"
VENV_DIR="$ROOT_DIR/.venv"

echo "🚀 Installing Google APIs Extension..."

# Activate virtual environment
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
else
    echo "❌ Virtual environment not found. Run install.sh first."
    exit 1
fi

# Install dependencies
echo "📦 Installing Google API client libraries..."
pip install --upgrade \
    google-api-python-client>=2.100.0 \
    google-auth>=2.23.0 \
    google-auth-oauthlib>=1.1.0 \
    google-auth-httplib2>=0.1.1

# Copy config templates
echo "⚙️ Setting up configuration..."
cp "$EXTENSION_DIR/config.example.yaml" "$ROOT_DIR/config/google-apis.yaml" || true
cp "$EXTENSION_DIR/.env.example" "$ROOT_DIR/.env.google" || true

# Create credentials directory
mkdir -p "$ROOT_DIR/config/credentials"

echo "✅ Google APIs extension installed!"
echo ""
echo "📋 Next steps:"
echo "1. Get API keys from https://console.cloud.google.com/apis/credentials"
echo "   - PageSpeed Insights API"
echo "   - Chrome UX Report API"
echo "2. Enable OAuth 2.0 for Google Search Console & Analytics"
echo "   - Download credentials.json to config/credentials/"
echo "3. Set environment variables in .env.google:"
echo "   GOOGLE_PAGESPEED_API_KEY=your_key"
echo "   GOOGLE_CRUX_API_KEY=your_key"
echo "4. Run first-time OAuth: python scripts/google_auth_setup.py"
echo ""
