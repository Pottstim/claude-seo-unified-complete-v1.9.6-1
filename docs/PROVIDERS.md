# Provider Alternatives Guide

This guide covers all available providers for each category, including open-source, self-hosted, and commercial options.

## Table of Contents

- [LLM Providers](#llm-providers)
- [Performance Providers](#performance-providers)
- [SERP / Keyword Research Providers](#serp--keyword-research-providers)
- [Web Crawling Providers](#web-crawling-providers)
- [Image Generation Providers](#image-generation-providers)
- [Analytics Providers](#analytics-providers)

---

## LLM Providers

Configure in `config.yaml`:

```yaml
llm:
  active_provider: "anthropic"  # Change this to switch providers
```

### Comparison

| Provider | Type | API Key Required | Cost | Best For |
|----------|------|------------------|------|----------|
| **Anthropic** | Cloud | Yes | Pay-per-use | Highest quality, long context |
| **OpenAI** | Cloud | Yes | Pay-per-use | Reliable, good multimodal |
| **Groq** | Cloud | Yes | Pay-per-use | Fastest inference |
| **Cerebras** | Cloud | Yes | Pay-per-use | Ultra-fast inference |
| **OpenRouter** | Aggregator | Yes | Varies | Access to 100+ models |
| **Together** | Cloud | Yes | Pay-per-use | Open-source models |
| **Ollama** | Local/Self-hosted | No | Free | Privacy, no limits, offline |

### Open Source / Self-Hosted Options

#### Ollama (Recommended for free usage)

**Install:**
```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3.2
ollama pull mistral
ollama pull codellama
```

**Configure:**
```yaml
llm:
  active_provider: "ollama"
  providers:
    ollama:
      base_url: "http://localhost:11434"
      model: "llama3.2"
```

**No API key required!**

#### LM Studio

1. Download from: https://lmstudio.ai
2. Load a model (e.g., Llama 3.2, Mistral)
3. Start local server (default: `http://localhost:1234`)

**Configure:**
```yaml
llm:
  active_provider: "custom"
  providers:
    custom:
      base_url: "http://localhost:1234/v1"
      model: "local-model"
```

#### vLLM / TGI / FastChat

For production self-hosted deployments, use vLLM or Text Generation Inference:

```yaml
llm:
  active_provider: "custom"
  providers:
    custom:
      base_url: "http://your-server:8000/v1"
      api_key: null  # Optional
```

---

## Performance Providers

Configure in `config.yaml`:

```yaml
performance:
  active_provider: "lighthouse"  # Change this to switch providers
```

### Comparison

| Provider | Type | API Key | Data Type | Best For |
|----------|------|---------|-----------|----------|
| **Lighthouse CLI** | Local | No | Lab data | Free, detailed audits |
| **PageSpeed API** | Cloud | Yes | Lab data | Easy integration |
| **CrUX API** | Cloud | Yes | Real user data | Field metrics |

### Open Source / Self-Hosted Options

#### Lighthouse CLI (Recommended for free usage)

**Install:**
```bash
npm install -g lighthouse
# Or use npx
npx lighthouse https://example.com
```

**No API key required!** Runs entirely locally.

**Configure:**
```yaml
performance:
  active_provider: "lighthouse"
  providers:
    lighthouse:
      enabled: true
      chrome_flags: "--headless --no-sandbox"
```

---

## SERP / Keyword Research Providers

Configure in `config.yaml`:

```yaml
serp:
  active_provider: null  # null = use custom scraper (free)
```

### Comparison

| Provider | Type | Free Tier | Cost | Best For |
|----------|------|-----------|------|----------|
| **Custom Scraper** | Local | Unlimited | Free | Basic SERP data |
| **SerpAPI** | Cloud | 100/mo | $50/mo+ | Production use |
| **DataForSEO** | Cloud | $100 credit | ~$0.25/request | Enterprise data |
| **ValueSERP** | Cloud | 100/mo | $30/mo+ | Cost-effective |

### Open Source / Self-Hosted Options

#### Custom Scraper (Recommended for free usage)

Uses Playwright with rotating user agents. **No API key required!**

**Configure:**
```yaml
serp:
  active_provider: "custom_scrape"
  providers:
    custom_scrape:
      enabled: true
      proxy_list: null  # Add proxies for scale
      rotate_user_agents: true
```

**Limitations:**
- May hit rate limits at scale
- No keyword volume data
- Use proxies for production

#### Proxies for Custom Scraper

For production use, add rotating proxies:

```yaml
serp:
  providers:
    custom_scrape:
      proxy_list: "proxies.txt"  # One proxy per line
      delay_range: [3, 7]  # Random delay between requests
```

---

## Web Crawling Providers

Configure in `config.yaml`:

```yaml
crawling:
  active_provider: "playwright"  # Change this to switch providers
```

### Comparison

| Provider | Type | API Key | JS Rendering | Best For |
|----------|------|---------|--------------|----------|
| **Playwright** | Local | No | Yes | Most use cases |
| **Selenium** | Local | No | Yes | Legacy support |
| **Requests** | Local | No | No | Fast, simple pages |
| **Firecrawl** | Cloud | Yes | Yes | Bypass anti-bot |
| **Browserless** | Cloud | Yes | Yes | Managed browser |

### Open Source / Self-Hosted Options

#### Playwright (Recommended)

**Install:**
```bash
pip install playwright
playwright install chromium
```

**No API key required!**

**Configure:**
```yaml
crawling:
  active_provider: "playwright"
  providers:
    playwright:
      enabled: true
      browser: "chromium"
      headless: true
```

#### Scrapy (Python framework)

For large-scale crawling:

```bash
pip install scrapy
```

---

## Image Generation Providers

Configure in `config.yaml`:

```yaml
image_generation:
  active_provider: null  # null = disabled (optional feature)
```

### Comparison

| Provider | Type | API Key | Cost | Best For |
|----------|------|---------|------|----------|
| **Stable Diffusion** | Local | No | Free | Privacy, unlimited |
| **ComfyUI** | Local | No | Free | Advanced workflows |
| **DALL-E** | Cloud | Yes | $0.04-0.12/image | Quality |
| **Replicate** | Cloud | Yes | Varies | Open-source models |

### Open Source / Self-Hosted Options

#### Stable Diffusion WebUI (AUTOMATIC1111)

**Install:**
```bash
# Clone and run
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui
cd stable-diffusion-webui
./webui.sh --api
```

**Configure:**
```yaml
image_generation:
  active_provider: "stable_diffusion"
  providers:
    stable_diffusion:
      api_base: "http://localhost:7860"
      model: "sd_xl_base_1.0"
```

**No API key required!**

#### ComfyUI

For node-based workflows:

```bash
git clone https://github.com/comfyanonymous/ComfyUI
cd ComfyUI
python main.py --listen
```

---

## Analytics Providers

Configure in `config.yaml`:

```yaml
analytics:
  active_provider: null  # null = disabled (optional feature)
```

### Comparison

| Provider | Type | Self-Hostable | Best For |
|----------|------|---------------|----------|
| **Google Search Console** | Cloud | No | Organic search data |
| **Google Analytics** | Cloud | No | Traffic analytics |
| **Plausible** | Cloud | Yes | Privacy-focused |
| **Matomo** | Cloud/Self-hosted | Yes | Open source |

### Open Source / Self-Hosted Options

#### Plausible

Privacy-focused, GDPR compliant. Self-host with Docker:

```bash
git clone https://github.com/plausible/hosting
cd hosting
docker-compose up -d
```

**Configure:**
```yaml
analytics:
  active_provider: "plausible"
  providers:
    plausible:
      api_key: ${PLAUSIBLE_API_KEY}
      site_id: ${PLAUSIBLE_SITE_ID}
      api_base: "https://your-plausible-instance.com"
```

#### Matomo

100% open source, self-hosted:

```bash
docker run -d --name matomo -p 8080:80 matomo
```

**Configure:**
```yaml
analytics:
  active_provider: "matomo"
  providers:
    matomo:
      api_base: "http://localhost:8080"
      site_id: "1"
      auth_token: ${MATOMO_AUTH_TOKEN}
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
# LLM (choose one or more)
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx
GROQ_API_KEY=gsk_xxx
OLLAMA_BASE_URL=http://localhost:11434

# Performance (optional - lighthouse works without)
GOOGLE_PAGESPEED_API_KEY=xxx
GOOGLE_CRUX_API_KEY=xxx

# SERP (optional - custom scraper works without)
SERPAPI_KEY=xxx
DATAFORSEO_USERNAME=xxx
DATAFORSEO_PASSWORD=xxx

# Crawling (optional - playwright works without)
FIRECRAWL_API_KEY=xxx

# Image generation (optional)
BANANA_API_KEY=xxx
GOOGLE_AI_API_KEY=xxx

# Analytics (optional)
PLAUSIBLE_API_KEY=xxx
MATOMO_AUTH_TOKEN=xxx
```

---

## Quick Start (Free Tier)

Run entirely for free with these settings:

```yaml
llm:
  active_provider: "ollama"
  
performance:
  active_provider: "lighthouse"
  
serp:
  active_provider: "custom_scrape"
  
crawling:
  active_provider: "playwright"
  
image_generation:
  active_provider: null  # Disable or use local SD
  
analytics:
  active_provider: null  # Disable or self-host
```

**Total cost: $0/month** (requires local compute)

---

## Need Help?

- **Ollama**: https://ollama.com/docs
- **Lighthouse**: https://developer.chrome.com/docs/lighthouse
- **Playwright**: https://playwright.dev/python/docs/intro
- **Stable Diffusion**: https://github.com/AUTOMATIC1111/stable-diffusion-webui
- **Plausible**: https://plausible.io/docs
- **Matomo**: https://matomo.org/docs
