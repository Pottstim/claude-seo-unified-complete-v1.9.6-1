#!/bin/bash
set -e

echo "🚀 Claude SEO Unified - Installation"
echo "===================================="
echo ""

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    CLAUDE_HOME="${HOME}/.claude"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    CLAUDE_HOME="${HOME}/.claude"
else
    CLAUDE_HOME="${USERPROFILE}/.claude"
fi

# Allow override
CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"

echo "📁 Claude home: ${CLAUDE_HOME}"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python ${PYTHON_VERSION} detected"

# Create directories
mkdir -p "${CLAUDE_HOME}/skills/seo"
mkdir -p "${CLAUDE_HOME}/agents"

# Copy files
echo "📦 Copying skill files..."
cp -r . "${CLAUDE_HOME}/skills/seo/"

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
cd "${CLAUDE_HOME}/skills/seo"
python3 -m venv .venv

# Activate and install dependencies
echo "📥 Installing dependencies..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    .venv/Scripts/activate
else
    source .venv/bin/activate
fi

pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1

echo ""
echo "✅ Installation complete!"
echo ""
echo "📝 Next steps:"
echo "1. Restart Claude Desktop"
echo "2. Try: /seo audit https://example.com"
echo ""
echo "📚 Optional extensions:"
echo "   ./extensions/dataforseo/install.sh  # Live SERP data"
echo "   python scripts/google_auth.py --setup  # Google APIs"
echo "   ./extensions/firecrawl/install.sh  # JS crawling"
echo "   ./extensions/banana/install.sh  # AI images"
echo ""
echo "💡 Documentation: ${CLAUDE_HOME}/skills/seo/README.md"
echo ""
