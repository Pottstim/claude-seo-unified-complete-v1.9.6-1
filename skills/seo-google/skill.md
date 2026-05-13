---
name: seo-google
description: "Google Search Console and Analytics integration"
user-invokable: true
---

# Google Integration Skill

## Overview

Integration with Google Search Console and Google Analytics for data-driven SEO insights.

## Commands

| Command | Description |
|---------|-------------|
| `/seo google status` | Check API connection status |
| `/seo google search-console <url>` | GSC data analysis |
| `/seo google analytics <url>` | GA data integration |
| `/seo google pagespeed <url>` | PageSpeed Insights |
| `/seo google index <url>` | Index status check |

## Setup

1. Enable Google APIs in Google Cloud Console
2. Create OAuth credentials
3. Run authentication:

```bash
python scripts/google_auth.py --setup
```

## Configuration

```yaml
# config/config.yaml
providers:
  google:
    search_console:
      enabled: true
      cache_ttl: 43200  # 12 hours
    analytics:
      enabled: true
      property_id: "GA_PROPERTY_ID"
    pagespeed:
      api_key: "${GOOGLE_PAGESPEED_API_KEY}"
```

## Data Available

### Search Console
- Impressions, clicks, CTR
- Average position
- Top queries
- Page performance
- Index coverage
- Core Web Vitals

### Analytics
- Organic traffic
- Bounce rate
- Session duration
- Goal completions
- Landing page performance

## Output

```json
{
  "search_console": {
    "impressions": 125000,
    "clicks": 8500,
    "ctr": 6.8,
    "top_queries": [...],
    " declining_queries": [...]
  },
  "analytics": {
    "organic_sessions": 45000,
    "bounce_rate": 42.5,
    "top_landing_pages": [...]
  }
}
```

## Requirements

- Google Cloud project
- APIs enabled (Search Console, Analytics)
- OAuth credentials configured
