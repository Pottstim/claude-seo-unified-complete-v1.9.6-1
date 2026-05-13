---
name: seo-competitor
description: "Competitive SEO analysis and benchmarking"
user-invokable: true
---

# Competitor Analysis Skill

## Overview

Comprehensive competitor SEO analysis including keyword gaps, content comparison, and backlink benchmarking.

## Commands

| Command | Description |
|---------|-------------|
| `/seo competitor analyze <url>` | Full competitor analysis |
| `/seo competitor keywords <url>` | Keyword gap analysis |
| `/seo competitor content <url>` | Content comparison |
| `/seo competitor backlinks <url>` | Backlink gap analysis |

## Analysis Dimensions

- **Keyword Overlap** - Shared vs unique keywords
- **Content Gaps** - Topics competitors rank for that you don't
- **Backlink Gaps** - Links competitors have that you don't
- **Technical Comparison** - Performance, schema, etc.
- **SERP Features** - Who's winning featured snippets

## Output Format

```json
{
  "competitors": ["competitor1.com", "competitor2.com"],
  "keyword_gaps": {
    "total_opportunities": 150,
    "high_value": 25,
    "quick_wins": 40
  },
  "content_gaps": [...],
  "backlink_gaps": [...]
}
```

## Requirements

Set competitors in config or specify inline:

```yaml
project:
  competitors:
    - competitor1.com
    - competitor2.com
```
