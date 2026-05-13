#!/bin/bash
# Firecrawl Extension Installer
# Provides: JS-rendered site crawling, bypasses anti-bot protection

set -e

echo "🔍 Installing Firecrawl Extension..."

# Check if main SEO skill is installed
if [ ! -f "../../SKILL.md" ]; then
    echo "❌ Error: Main SEO skill not found. Install base package first."
    exit 1
fi

# Create extension directory
EXTENSION_DIR="$HOME/.antigravity/skills/seo/extensions/firecrawl"
mkdir -p "$EXTENSION_DIR"

# Copy extension files
cp -r . "$EXTENSION_DIR/"

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install -q firecrawl-py>=0.0.8

# Configure API key
echo ""
echo "🔑 Firecrawl API Configuration"
echo "Get your API key at: https://firecrawl.dev"
echo "Free tier: 500 pages/month"
echo ""
read -p "Enter Firecrawl API Key: " FIRECRAWL_KEY

# Add to .env
ENV_FILE="$HOME/.antigravity/.env"
if [ ! -f "$ENV_FILE" ]; then
    touch "$ENV_FILE"
fi

sed -i '/FIRECRAWL_API_KEY=/d' "$ENV_FILE"
echo "FIRECRAWL_API_KEY=$FIRECRAWL_KEY" >> "$ENV_FILE"

# Test connection
echo ""
echo "🧪 Testing API connection..."
python3 << EOF
from firecrawl import FirecrawlApp
import sys

api_key = "$FIRECRAWL_KEY"
app = FirecrawlApp(api_key=api_key)

try:
    result = app.scrape_url("https://example.com")
    if result and "content" in result:
        print("✅ Firecrawl connection successful!")
        print("📊 Test crawl completed")
        sys.exit(0)
    else:
        print("❌ Unexpected response format")
        sys.exit(1)
except Exception as e:
    print(f"❌ Connection failed: {e}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Firecrawl extension installed successfully!"
    echo ""
    echo "Available commands:"
    echo "  /seo firecrawl <url>"
    echo "  /seo firecrawl batch <url1> <url2> ..."
    echo ""
else
    echo ""
    echo "⚠️  Installation completed but API test failed."
    echo "Check API key in: $ENV_FILE"
fi
