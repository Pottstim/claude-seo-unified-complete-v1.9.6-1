#!/bin/bash
# Banana/Gemini Image Generation Extension
# Provides: AI-generated OG images, visual assets for SEO

set -e

echo "🔍 Installing Banana Image Generation Extension..."

# Check if main SEO skill is installed
if [ ! -f "../../SKILL.md" ]; then
    echo "❌ Error: Main SEO skill not found. Install base package first."
    exit 1
fi

# Create extension directory
EXTENSION_DIR="$HOME/.antigravity/skills/seo/extensions/banana"
mkdir -p "$EXTENSION_DIR"

# Copy extension files
cp -r . "$EXTENSION_DIR/"

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install -q pillow>=10.0.0 requests>=2.31.0

# Configure API
echo ""
echo "🔑 AI Image Generation Configuration"
echo ""
echo "Choose backend:"
echo "1. Banana (https://banana.dev) - Stable Diffusion"
echo "2. Gemini Imagen (Google AI)"
echo "3. Both"
echo ""
read -p "Enter choice [1-3]: " BACKEND_CHOICE

ENV_FILE="$HOME/.antigravity/.env"
if [ ! -f "$ENV_FILE" ]; then
    touch "$ENV_FILE"
fi

if [[ "$BACKEND_CHOICE" == "1" ]] || [[ "$BACKEND_CHOICE" == "3" ]]; then
    echo ""
    echo "Get Banana API key at: https://app.banana.dev"
    read -p "Enter Banana API Key: " BANANA_KEY
    sed -i '/BANANA_API_KEY=/d' "$ENV_FILE"
    echo "BANANA_API_KEY=$BANANA_KEY" >> "$ENV_FILE"
fi

if [[ "$BACKEND_CHOICE" == "2" ]] || [[ "$BACKEND_CHOICE" == "3" ]]; then
    echo ""
    echo "Get Google AI API key at: https://makersuite.google.com/app/apikey"
    read -p "Enter Google AI API Key: " GOOGLE_AI_KEY
    sed -i '/GOOGLE_AI_API_KEY=/d' "$ENV_FILE"
    echo "GOOGLE_AI_API_KEY=$GOOGLE_AI_KEY" >> "$ENV_FILE"
fi

echo ""
echo "✅ Banana/Gemini extension installed successfully!"
echo ""
echo "Available commands:"
echo "  /seo image-gen og <title> <description>"
echo "  /seo image-gen hero <topic>"
echo "  /seo image-gen thumbnail <article-url>"
echo ""
