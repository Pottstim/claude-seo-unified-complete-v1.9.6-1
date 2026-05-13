---
name: seo-backlinks
description: "Backlink profile analysis and link building recommendations"
user-invokable: true
---

# Backlink Analysis Skill

## Overview

Analyzes backlink profiles, identifies link building opportunities, and detects potentially harmful links.

## Commands

| Command | Description |
|---------|-------------|
| `/seo backlinks <url>` | Full backlink profile analysis |
| `/seo backlinks audit <url>` | Audit backlink health |
| `/seo backlinks competitors <url>` | Compare competitor backlinks |
| `/seo backlinks opportunities <url>` | Find link building opportunities |

## Workflow

1. Fetch backlink data (requires DataForSEO or Ahrefs/Moz API)
2. Analyze link quality metrics
3. Identify toxic/spam links
4. Compare with competitors
5. Generate link building recommendations

## Quality Metrics

- **Domain Authority** - Overall domain strength
- **Page Authority** - Specific page strength
- **Anchor Text Diversity** - Natural vs over-optimized
- **Link Velocity** - Growth rate of backlinks
- **Referring Domains** - Unique domains linking
- **Link Type Distribution** - Follow/nofollow ratio

## Output

```json
{
  "url": "https://example.com",
  "backlinks": {
    "total": 1250,
    "referring_domains": 312,
    "follow_links": 890,
    "nofollow_links": 360
  },
  "quality_score": 72,
  "toxic_links": 12,
  "opportunities": [...]
}
```

## Data Sources

- DataForSEO (configured)
- Ahrefs API (optional)
- Moz API (optional)
- Manual link audit

## Requirements

Configure backlink data source in `config/config.yaml`:

```yaml
providers:
  backlinks:
    active_provider: dataforseo
```
