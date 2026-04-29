#!/bin/bash
# DataForSEO Extension Installer
# Provides: Live SERP data, keyword volumes, backlink analysis

set -e

echo "🔍 Installing DataForSEO Extension..."

# Check if main SEO skill is installed
if [ ! -f "../../SKILL.md" ]; then
    echo "❌ Error: Main SEO skill not found. Install base package first."
    exit 1
fi

# Create extension directory
EXTENSION_DIR="$HOME/.antigravity/skills/seo/extensions/dataforseo"
mkdir -p "$EXTENSION_DIR"

# Copy extension files
cp -r . "$EXTENSION_DIR/"

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install -q dataforseo-client>=1.0.0

# Configure API credentials
echo ""
echo "🔑 DataForSEO API Configuration"
echo "Get your credentials at: https://app.dataforseo.com"
echo ""
read -p "Enter DataForSEO Username: " DATAFORSEO_USER
read -sp "Enter DataForSEO Password: " DATAFORSEO_PASS
echo ""

# Add to .env
ENV_FILE="$HOME/.antigravity/.env"
if [ ! -f "$ENV_FILE" ]; then
    touch "$ENV_FILE"
fi

# Remove old entries if exist
sed -i '/DATAFORSEO_USERNAME=/d' "$ENV_FILE"
sed -i '/DATAFORSEO_PASSWORD=/d' "$ENV_FILE"

# Add new entries
echo "DATAFORSEO_USERNAME=$DATAFORSEO_USER" >> "$ENV_FILE"
echo "DATAFORSEO_PASSWORD=$DATAFORSEO_PASS" >> "$ENV_FILE"

# Test connection
echo ""
echo "🧪 Testing API connection..."
python3 << EOF
import requests
import sys

username = "$DATAFORSEO_USER"
password = "$DATAFORSEO_PASS"

response = requests.get(
    "https://api.dataforseo.com/v3/appendix/user_data",
    auth=(username, password)
)

if response.status_code == 200:
    data = response.json()
    if data.get("status_code") == 20000:
        print("✅ DataForSEO connection successful!")
        print(f"📊 Account balance: \${data['tasks'][0]['result'][0].get('money', {}).get('balance', 'N/A')}")
        sys.exit(0)
    else:
        print("❌ API error:", data.get("status_message"))
        sys.exit(1)
else:
    print("❌ Connection failed. Check credentials.")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ DataForSEO extension installed successfully!"
    echo ""
    echo "Available commands:"
    echo "  /seo dataforseo serp <keyword>"
    echo "  /seo dataforseo backlinks <url>"
    echo "  /seo dataforseo keywords <domain>"
    echo ""
else
    echo ""
    echo "⚠️  Installation completed but API test failed."
    echo "Check credentials in: $ENV_FILE"
fi
