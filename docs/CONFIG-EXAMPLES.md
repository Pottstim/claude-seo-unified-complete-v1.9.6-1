# Example Configurations for claude-seo-unified

These examples show how to mix and match providers based on your needs and budget.

## Example 1: Fully Free (Open Source Only)

```yaml
# config.yaml - No API keys required
# Works entirely offline after initial setup

llm:
  active_provider: "ollama"
  providers:
    ollama:
      base_url: "http://localhost:11434"
      model: "llama3.2"

performance:
  active_provider: "lighthouse"
  providers:
    lighthouse:
      enabled: true
      chrome_flags: "--headless --no-sandbox"

serp:
  active_provider: "custom_scrape"
  providers:
    custom_scrape:
      enabled: true
      rotate_user_agents: true
      delay_range: [2, 5]

crawling:
  active_provider: "playwright"
  providers:
    playwright:
      enabled: true
      headless: true

image_generation:
  active_provider: "stable_diffusion"
  providers:
    stable_diffusion:
      api_base: "http://localhost:7860"
      model: "sd_xl_base_1.0"

analytics:
  active_provider: null  # Disabled or use Matomo

backlinks:
  active_provider: null  # Requires paid API
```

**Setup:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.2

# Install Lighthouse
npm install -g lighthouse

# Install Stable Diffusion (optional)
# Download from https://github.com/AUTOMATIC1111/stable-diffusion-webui

# Install Python dependencies
pip install playwright
playwright install chromium
```

---

## Example 2: Ollama + Google APIs (Hybrid Free/Paid)

```yaml
# config.yaml - Mix local LLM with Google APIs

llm:
  active_provider: "ollama"  # Free, local
  providers:
    ollama:
      base_url: "http://localhost:11434"
      model: "llama3.2"

performance:
  active_provider: "pagespeed_api"  # Google API
  providers:
    pagespeed_api:
      enabled: true
      api_key: ${GOOGLE_PAGESPEED_API_KEY}
    lighthouse:
      enabled: true  # Fallback

serp:
  active_provider: null  # Disabled

crawling:
  active_provider: "playwright"  # Free

image_generation:
  active_provider: null  # Disabled

analytics:
  active_provider: "google_search_console"  # Google API
  providers:
    google_search_console:
      enabled: true
      credentials_path: "config/credentials/gsc_credentials.json"

backlinks:
  active_provider: null
```

**Required .env:**
```bash
GOOGLE_PAGESPEED_API_KEY=your_key_here
```

---

## Example 3: Groq (Free Tier) + Google APIs

```yaml
# config.yaml - Fast free LLM with Google data

llm:
  active_provider: "groq"  # Free tier available
  providers:
    groq:
      api_key: ${GROQ_API_KEY}
      model: "llama-3.3-70b-versatile"

performance:
  active_provider: "crux_api"  # Real user data from Google
  providers:
    crux_api:
      enabled: true
      api_key: ${GOOGLE_CRUX_API_KEY}

serp:
  active_provider: null

crawling:
  active_provider: "playwright"

analytics:
  active_provider: "google_search_console"

image_generation:
  active_provider: null
```

**Required .env:**
```bash
GROQ_API_KEY=your_groq_key
GOOGLE_CRUX_API_KEY=your_google_key
```

---

## Example 4: Anthropic + DataForSEO + Firecrawl (Full Paid)

```yaml
# config.yaml - Premium setup with all features

llm:
  active_provider: "anthropic"
  providers:
    anthropic:
      api_key: ${ANTHROPIC_API_KEY}
      model: "claude-sonnet-4-20250514"

performance:
  active_provider: "pagespeed_api"
  providers:
    pagespeed_api:
      api_key: ${GOOGLE_PAGESPEED_API_KEY}

serp:
  active_provider: "dataforseo"
  providers:
    dataforseo:
      username: ${DATAFORSEO_USERNAME}
      password: ${DATAFORSEO_PASSWORD}

crawling:
  active_provider: "firecrawl"  # Handles JS, bypasses blocks
  providers:
    firecrawl:
      api_key: ${FIRECRAWL_API_KEY}

image_generation:
  active_provider: "dalle"
  providers:
    dalle:
      api_key: ${OPENAI_API_KEY}

analytics:
  active_provider: "google_search_console"

backlinks:
  active_provider: "dataforseo"
```

---

## Example 5: OpenRouter + SerpAPI + Local Everything Else

```yaml
# config.yaml - Access to many models, cheap SERP data

llm:
  active_provider: "openrouter"  # Access to 100+ models
  providers:
    openrouter:
      api_key: ${OPENROUTER_API_KEY}
      model: "anthropic/claude-sonnet-4"  # Or meta-llama/llama-3-70b

performance:
  active_provider: "lighthouse"  # Free local

serp:
  active_provider: "serpapi"  # 100 free searches/month
  providers:
    serpapi:
      api_key: ${SERPAPI_KEY}

crawling:
  active_provider: "playwright"  # Free local

image_generation:
  active_provider: null

analytics:
  active_provider: null
```

---

## Example 6: Self-Hosted Everything (Privacy-Focused)

```yaml
# config.yaml - All self-hosted, no external APIs

llm:
  active_provider: "ollama"
  providers:
    ollama:
      base_url: "http://localhost:11434"
      model: "llama3.2"

performance:
  active_provider: "lighthouse"

serp:
  active_provider: "custom_scrape"
  providers:
    custom_scrape:
      enabled: true
      proxy_list: "/path/to/proxies.txt"

crawling:
  active_provider: "playwright"

image_generation:
  active_provider: "stable_diffusion"
  providers:
    stable_diffusion:
      api_base: "http://localhost:7860"

analytics:
  active_provider: "matomo"  # Self-hosted analytics
  providers:
    matomo:
      api_base: "https://matomo.yourdomain.com"
      site_id: "1"
      auth_token: ${MATOMO_AUTH_TOKEN}

backlinks:
  active_provider: null  # Would need external API
```

---

## Cost Comparison

| Setup | LLM | Performance | SERP | Crawling | Total/Month |
|-------|-----|-------------|------|----------|-------------|
| Fully Free | Ollama (free) | Lighthouse (free) | Custom scrape (free) | Playwright (free) | **$0** |
| Hybrid | Ollama (free) | PageSpeed API (free tier) | None | Playwright (free) | **$0** |
| Groq + Google | Groq (free tier) | CrUX API (free) | None | Playwright (free) | **$0** |
| OpenRouter | ~$0.15/1M tokens | Lighthouse (free) | SerpAPI ($50) | Playwright (free) | **~$50** |
| Full Paid | Anthropic (~$20) | PageSpeed (free tier) | DataForSEO (~$50) | Firecrawl ($19) | **~$89** |

---

## Setting Up .env File

Create `.env` in your project root:

```bash
# LLM Keys (choose one or more)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
OPENROUTER_API_KEY=sk-or-...

# Google APIs
GOOGLE_PAGESPEED_API_KEY=AIza...
GOOGLE_CRUX_API_KEY=AIza...
GOOGLE_AI_API_KEY=AIza...

# SERP Providers (choose one)
SERPAPI_KEY=...
DATAFORSEO_USERNAME=...
DATAFORSEO_PASSWORD=...
VALUESERP_KEY=...

# Crawling
FIRECRAWL_API_KEY=...
BROWSERLESS_KEY=...

# Image Generation
REPLICATE_API_KEY=...
HUGGINGFACE_API_KEY=...

# Analytics
PLAUSIBLE_API_KEY=...
MATOMO_AUTH_TOKEN=...
```

The config uses `${VAR_NAME}` syntax to pull from environment variables.
