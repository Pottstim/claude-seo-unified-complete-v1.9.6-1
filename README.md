# Claude SEO - Unified Skills Package

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-1.9.8--unified-green.svg)](https://github.com/Pottstim/claude-seo-unified-complete-v1.9.6-1)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](#)
[![Production Ready](https://img.shields.io/badge/status-production--ready-blue.svg)](#)

**Combined best-of-both from Claude SEO + Codex SEO**

This unified package merges the Claude Code MCP skills (21 workflows) with Codex SEO's advanced features (26 workflows, deterministic runners, premium reports) into a single installation for Claude Desktop.

## ✨ What's New

### Flexible Provider System

**Bring your own APIs, use open-source alternatives, or run everything locally for free.**

## 🔌 Provider System

This package supports multiple providers for each category, including open-source and self-hosted options:

| Category | Free/Open Source Options | Paid Cloud Options |
|----------|-------------------------|-------------------|
| **LLM** | Ollama, LM Studio, vLLM | Anthropic, OpenAI, Groq, Cerebras |
| **Performance** | Lighthouse CLI (local) | PageSpeed API, CrUX API |
| **SERP** | Custom scraper (Playwright) | SerpAPI, DataForSEO |
| **Crawling** | Playwright, Selenium, Requests | Firecrawl, Browserless |
| **Images** | Stable Diffusion (local) | DALL-E, Replicate |
| **Analytics** | Plausible, Matomo (self-hosted) | Google Search Console |

### Free Tier Setup

Run everything for $0/month:

```yaml
# config.yaml
llm:
  active_provider: "ollama"  # Local LLM

performance:
  active_provider: "lighthouse"  # Local audits

serp:
  active_provider: "custom_scrape"  # Free SERP data

crawling:
  active_provider: "playwright"  # Local browser
```

See [Provider Alternatives Guide](docs/PROVIDERS.md) for full documentation.

## What's Included

### Core Features (from claude-seo)
- ✅ Full site audit with parallel subagent delegation
- ✅ 21+ specialist SEO workflows
- ✅ Natural language invocation ("audit this site")
- ✅ MCP integration ready (DataForSEO, Firecrawl, Banana)
- ✅ Google APIs (GSC, PageSpeed, CrUX, GA4)
- ✅ Local SEO & Maps intelligence
- ✅ E-E-A-T content analysis
- ✅ Schema markup generation
- ✅ Core Web Vitals (INP, LCP, CLS)
- ✅ AI search optimization (GEO)

### Enhanced Features (from codex-seo)
- ✅ Deterministic headless runners (API-callable)
- ✅ Premium HTML/PDF report generation
- ✅ Shared cache architecture (.seo-cache/)
- ✅ Drift monitoring (baseline/compare)
- ✅ SXO (Search Experience Optimization)
- ✅ Semantic clustering
- ✅ E-commerce SEO specialist
- ✅ FLOW framework integration
- ✅ 26 total workflows (5 more than claude-seo)

## Installation

### For Claude Desktop (MCP)

1. **Download this package** and extract to:
   - macOS/Linux: `~/.claude/skills/seo/`
   - Windows: `%USERPROFILE%\.claude\skills\seo\`

2. **Install Python dependencies**:
```bash
cd ~/.claude/skills/seo

# Core dependencies (minimal)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements-core.txt

# Optional: Full dependencies (for screenshots, PDF, browser automation)
pip install -r requirements-optional.txt
```

3. **Install Playwright** (optional, for screenshots/PDF):
```bash
playwright install chromium
```

4. **Run tests** (optional):
```bash
pytest tests/ -v
```

5. **Restart Claude Desktop**

### Quick Start

After installation, use natural language or commands:

```
# Natural language
"Do a full SEO audit on https://example.com"
"Check the schema markup on my homepage"
"Analyze Core Web Vitals for this page"

# Command style
/seo audit https://example.com
/seo technical https://example.com
/seo schema https://example.com
```

## Available Commands

| Command | Purpose |
|---------|---------|
| `/seo audit <url>` | Full site audit with parallel analysis |
| `/seo page <url>` | Deep single-page SEO analysis |
| `/seo technical <url>` | Technical SEO (crawlability, indexability, CWV) |
| `/seo content <url>` | E-E-A-T content quality analysis |
| `/seo schema <url>` | Schema detection, validation, generation |
| `/seo images <url>` | Image optimization analysis |
| `/seo sitemap <url>` | Sitemap analysis and generation |
| `/seo geo <url>` | AI search optimization (GEO) |
| `/seo performance <url>` | Core Web Vitals analysis |
| `/seo visual <url>` | Screenshot and mobile rendering |
| `/seo local <url>` | Local SEO (GBP, NAP, citations) |
| `/seo maps <command>` | Maps intelligence (geo-grid, reviews) |
| `/seo google <command>` | Google APIs (GSC, PageSpeed, CrUX) |
| `/seo backlinks <url>` | Backlink profile analysis |
| `/seo cluster <keyword>` | Semantic topic clustering |
| `/seo sxo <url>` | Search experience optimization |
| `/seo drift baseline <url>` | Capture SEO baseline |
| `/seo drift compare <url>` | Compare against baseline |
| `/seo ecommerce <url>` | E-commerce SEO analysis |
| `/seo plan <type>` | Strategic SEO planning |
| `/seo flow <stage>` | FLOW framework prompts |

## Extensions (Optional)

Extensions add premium data sources. Alternatively, use the [Provider System](docs/PROVIDERS.md) to configure any API.

### DataForSEO
Live SERP data, keyword research, backlinks, competitive intelligence.

```bash
./extensions/dataforseo/install.sh
```

### Google APIs
PageSpeed, Search Console, CrUX, Indexing API, GA4.

```bash
python scripts/google_auth.py --setup
```

### Firecrawl
JS-rendered crawling and site mapping.

```bash
./extensions/firecrawl/install.sh
```

### Banana (AI Image Generation)
Generate SEO images (OG previews, hero images, product photos).

```bash
./extensions/banana/install.sh
```

## Headless/API Usage

Run workflows programmatically without Claude Desktop:

```bash
# Full SEO audit
python scripts/run_skill_workflow.py audit --url https://example.com --json

# Technical SEO only
python scripts/run_skill_workflow.py technical --url https://example.com --json

# Content analysis
python scripts/run_skill_workflow.py content --url https://example.com --json

# Schema detection
python scripts/run_skill_workflow.py schema --url https://example.com --json

# Drift monitoring
python scripts/run_skill_workflow.py drift-baseline --url https://example.com
python scripts/run_skill_workflow.py drift-compare --url https://example.com

# Output formats
python scripts/run_skill_workflow.py audit --url https://example.com --format markdown --output report.md
python scripts/run_skill_workflow.py audit --url https://example.com --format yaml

# Bypass cache
python scripts/run_skill_workflow.py audit --url https://example.com --refresh

# Limit recommendations
python scripts/run_skill_workflow.py audit --url https://example.com --max-recommendations 20

# Show version
python scripts/run_skill_workflow.py --version

# Verify environment
python scripts/verify_environment.py --target https://example.com --json
```

### CLI Reference

| Argument | Description |
|----------|-------------|
| `workflow` | One of: audit, technical, content, schema, drift-baseline, drift-compare |
| `--url` | Target URL (required, must start with http:// or https://) |
| `--format` | Output format: json (default), yaml, or markdown |
| `--output` | Save output to file |
| `--refresh` | Bypass cache, fetch fresh data |
| `--no-cache` | Disable caching entirely |
| `--max-recommendations` | Max recommendations to show (default: 10) |
| `--version` | Show version number |
| `--config` | Path to config file (default: config/config.yaml) |

## Architecture

```
~/.claude/skills/seo/              # Main orchestrator
~/.claude/skills/seo-*/            # 26 specialist workflows
~/.claude/agents/seo-*.md          # 24 agent profiles
scripts/                           # Deterministic runners
extensions/                        # Optional integrations
.seo-cache/                        # Shared evidence cache
output/                            # Reports and artifacts
```

## Features Comparison

| Feature | claude-seo | codex-seo | This Package |
|---------|-----------|-----------|--------------|
| Natural language invocation | ✅ | ✅ | ✅ |
| Specialist workflows | 21 | 26 | 26 |
| MCP integration | ✅ | ✅ | ✅ |
| Headless runners | ❌ | ✅ | ✅ |
| Premium PDF reports | ❌ | ✅ | ✅ |
| Shared cache | ❌ | ✅ | ✅ |
| Drift monitoring | ✅ | ✅ | ✅ |
| SXO analysis | ✅ | ✅ | ✅ |
| FLOW framework | ✅ | ✅ | ✅ |

## Testing

Run the test suite to verify your installation:

```bash
# Unit tests (no network required)
pytest tests/test_workflow.py -v

# Integration tests (requires network)
pytest tests/test_integration.py -v -m integration

# All tests
pytest tests/ -v
```

## Requirements

- **Python 3.10+**
- **Claude Desktop** (for MCP mode)

### Core Dependencies
- requests - HTTP client
- beautifulsoup4 - HTML parsing
- lxml - XML processing
- pyyaml - Configuration
- pandas - Data processing
- aiohttp - Async HTTP

### Optional Dependencies
- playwright - Screenshots, browser automation
- selenium - Alternative browser automation
- weasyprint - PDF report generation
- matplotlib - Charts in reports
- anthropic/openai - AI integrations

Install core only: `pip install -r requirements-core.txt`
Install everything: `pip install -r requirements-optional.txt`

## License

MIT License - see LICENSE file for details.

## Credits

**Combined from:**
- [claude-seo](https://github.com/AgriciDaniel/claude-seo) by [@AgriciDaniel](https://github.com/AgriciDaniel)
- [codex-seo](https://github.com/AgriciDaniel/codex-seo) by [@AgriciDaniel](https://github.com/AgriciDaniel)

Built for Claude Desktop by the AI Marketing Hub community.

## Support

- [AI Marketing Hub](https://www.skool.com/ai-marketing-hub) - Free community
- [Documentation](docs/)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

---

**Package assembled:** 2026-04-28  
**Last updated:** 2026-05-13  
**Version:** 1.9.6-unified

### Changelog

**v1.9.7-unified (2026-05-13)**
- **Fixed critical bugs identified in code review:**
  - Added all missing analyzers (onpage, ai_readiness, images) to fix phantom category scores
  - Fixed cache timezone bug (aware vs naive datetime comparison)
  - Removed unused asyncio/aiohttp imports
  - Added URL validation with proper error messages
  - Fixed business type detection tie-breaking with explicit priority
  - Improved E-E-A-T detection to focus on main content area only
  - Added --max-recommendations CLI flag
  - Added --version flag
  - Updated README CLI syntax to match actual argparse interface
  - Added comprehensive CLI reference table

**v1.9.6-unified (2026-05-13)**
- Added MIT LICENSE file
- Implemented full `run_skill_workflow.py` with actual SEO analysis
- Split requirements into core (`requirements-core.txt`) and optional (`requirements-optional.txt`)
- Added comprehensive test suite (`tests/`)
- Created modular skill files in `skills/` directory
- Created agent definition files in `agents/` directory
- Added reference documentation (`references/`)
- Added pytest configuration