# Troubleshooting Guide

## Common Issues

### Installation Issues

#### Python Version Error

**Error:** `Python 3.10+ required`

**Solution:**
```bash
# Check Python version
python3 --version

# Install Python 3.10+ if needed (Ubuntu/Debian)
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip

# On macOS with Homebrew
brew install python@3.10
```

#### Playwright Installation Fails

**Error:** `playwright install chromium` fails

**Solution:**
```bash
# Install system dependencies first
playwright install-deps chromium

# Then install browser
playwright install chromium
```

#### Permission Denied

**Error:** `Permission denied` when running install.sh

**Solution:**
```bash
chmod +x install.sh
chmod +x extensions/*/install.sh
```

### Runtime Issues

#### BeautifulSoup Not Available

**Error:** `BeautifulSoup not available`

**Solution:**
```bash
pip install beautifulsoup4 lxml
```

#### Requests Module Not Found

**Error:** `ModuleNotFoundError: No module named 'requests'`

**Solution:**
```bash
pip install requests
```

#### Cache Corruption

**Error:** Cache returns stale/invalid data

**Solution:**
```bash
# Clear cache
rm -rf .seo-cache/*

# Or use --refresh flag
python scripts/run_skill_workflow.py audit --url https://example.com --refresh
```

### Claude Desktop Issues

#### Skill Not Recognized

**Error:** `/seo` commands not recognized in Claude Desktop

**Solution:**
1. Verify installation location:
   - macOS/Linux: `~/.claude/skills/seo/`
   - Windows: `%USERPROFILE%\.claude\skills\seo\`

2. Restart Claude Desktop completely

3. Check the skill is loaded:
   ```bash
   ls ~/.claude/skills/seo/SKILL.md
   ```

#### MCP Server Not Starting

**Error:** MCP connection failed

**Solution:**
1. Check Python environment is activated
2. Verify dependencies installed:
   ```bash
   cd ~/.claude/skills/seo
   source .venv/bin/activate
   pip list | grep -E "requests|beautifulsoup"
   ```

### API Key Issues

#### DataForSEO Authentication Failed

**Error:** `401 Unauthorized`

**Solution:**
1. Verify credentials in `~/.antigravity/.env`
2. Check API key format (should be long string)
3. Test credentials:
   ```bash
   curl -X POST "https://api.dataforseo.com/v3/serp/google/organic/live/advanced" \
     --user "login:password" \
     -H "Content-Type: application/json" \
     -d '[{"keyword":"test","location_code":2840,"language_code":"en"}]'
   ```

#### Google OAuth Error

**Error:** `OAuth credentials not found`

**Solution:**
```bash
# Re-run Google auth setup
python scripts/google_auth.py --setup

# Check credentials exist
ls config/credentials/token.json
```

### Network Issues

#### Connection Timeout

**Error:** `Connection timeout` or `ReadTimeout`

**Solution:**
```python
# Increase timeout in config.yaml
crawling:
  timeout: 60  # seconds
```

#### SSL Certificate Error

**Error:** `SSLError` or `CERTIFICATE_VERIFY_FAILED`

**Solution:**
```bash
# Update certificates (macOS)
/Applications/Python*/Install\ Certificates.command

# Or disable verification (not recommended for production)
export PYTHONHTTPSVERIFY=0
```

### Performance Issues

#### Slow Audits

**Issue:** Audits taking too long

**Solution:**
1. Enable caching (default)
2. Use parallel processing for multiple pages
3. Install optional dependencies for speed:
   ```bash
   pip install httpx aiohttp
   ```

#### Memory Issues

**Error:** `MemoryError` or system becomes unresponsive

**Solution:**
1. Reduce concurrency
2. Process fewer pages at once
3. Clear old cache:
   ```bash
   rm -rf .seo-cache/*
   ```

## Debug Mode

Enable verbose logging:

```bash
# Set log level
export LOG_LEVEL=DEBUG

# Run with debug
python scripts/run_skill_workflow.py audit --url https://example.com
```

## Getting Help

1. Check [Documentation](docs/)
2. Check existing issues on GitHub
3. Join [AI Marketing Hub](https://www.skool.com/ai-marketing-hub) community
4. Contact support with:
   - Full error message
   - Steps to reproduce
   - Environment info:
     ```bash
     python --version
     pip list | grep -E "requests|beautifulsoup|playwright"
     uname -a  # System info
     ```
