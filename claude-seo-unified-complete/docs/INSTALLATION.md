# Installation Guide - Claude SEO Unified

## Prerequisites

- Python 3.10 or higher
- Claude Desktop installed
- 500MB free disk space
- Internet connection

## Quick Install

### macOS / Linux

```bash
git clone https://github.com/AgriciDaniel/claude-seo-unified.git
cd claude-seo-unified
bash install.sh
```

### Windows (PowerShell)

```powershell
git clone https://github.com/AgriciDaniel/claude-seo-unified.git
cd claude-seo-unified
powershell -ExecutionPolicy Bypass -File install.ps1
```

## Manual Installation

### 1. Download Package

Extract the `.zip` file to:
- **macOS/Linux**: `~/.claude/skills/seo/`
- **Windows**: `%USERPROFILE%\.claude\skills\seo\`

### 2. Install Python Dependencies

```bash
cd ~/.claude/skills/seo
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Optional: Install Playwright

For screenshots and PDF generation:

```bash
playwright install chromium
```

### 4. Restart Claude Desktop

Close and reopen Claude Desktop to load the new skills.

## Verification

Test the installation:

```bash
# In Claude Desktop
/seo audit https://example.com
```

Or run verification script:

```bash
python scripts/verify_environment.py --target https://example.com
```

## Extensions Setup

### DataForSEO (Live SERP Data)

1. Get API key from [DataForSEO](https://dataforseo.com/)
2. Run installer:
```bash
./extensions/dataforseo/install.sh
```
3. Enter credentials when prompted

### Google APIs (GSC, PageSpeed, CrUX)

```bash
python scripts/google_auth.py --setup
```

Follow OAuth flow to authorize.

### Firecrawl (JS Crawling)

1. Get API key from [Firecrawl](https://firecrawl.dev/)
2. Run installer:
```bash
./extensions/firecrawl/install.sh
```

### Banana (AI Image Generation)

Requires existing `nanobanana-mcp` setup:

```bash
./extensions/banana/install.sh
```

## Troubleshooting

### "Module not found" errors

```bash
cd ~/.claude/skills/seo
source .venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

### Playwright installation fails

```bash
# Install system dependencies first
sudo apt-get update && sudo apt-get install -y \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2
```

### Skills not appearing in Claude

1. Check installation path: `ls ~/.claude/skills/seo/SKILL.md`
2. Restart Claude Desktop completely
3. Check logs: `~/.claude/logs/`

### Permission errors (macOS)

```bash
chmod +x ~/.claude/skills/seo/install.sh
chmod +x ~/.claude/skills/seo/extensions/*/install.sh
```

## Uninstall

```bash
rm -rf ~/.claude/skills/seo
rm -rf ~/.claude/skills/seo-*
rm -rf ~/.claude/agents/seo-*
```

## Support

- GitHub Issues: [Report a bug](https://github.com/AgriciDaniel/claude-seo-unified/issues)
- Community: [AI Marketing Hub](https://www.skool.com/ai-marketing-hub)
- Documentation: `/docs/`
