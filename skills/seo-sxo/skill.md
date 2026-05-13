---
name: seo-sxo
description: "Search Experience Optimization combining SEO + UX"
user-invokable: true
---

# SXO (Search Experience Optimization) Skill

## Overview

Combines SEO and UX principles to optimize for both search engines and user satisfaction. Focuses on the intersection of discoverability and usability.

## Commands

| Command | Description |
|---------|-------------|
| `/seo sxo <url>` | Full SXO analysis |
| `/seo sxo intent <url>` | Search intent alignment |
| `/seo sxo journey <url>` | User journey analysis |
| `/seo sxo conversion <url>` | Conversion path optimization |

## SXO Framework

### Discoverability (SEO)
- Keyword targeting
- Search visibility
- SERP features
- Click-through rate

### Usability (UX)
- Page speed
- Mobile experience
- Navigation clarity
- Content readability

### Conversion
- Call-to-action placement
- Form optimization
- Trust signals
- Exit intent handling

## Analysis Areas

| Element | SEO Impact | UX Impact |
|---------|------------|-----------|
| Title tag | High | Medium (SERP display) |
| Meta description | Medium | High (SERP CTR) |
| H1 heading | High | High (page structure) |
| Internal links | High | High (navigation) |
| Images | Medium | High (visual appeal) |
| Forms | Low | High (conversion) |

## Output

```json
{
  "sxo_score": 78,
  "discoverability": {
    "score": 82,
    "issues": ["Missing meta description on 3 pages"]
  },
  "usability": {
    "score": 75,
    "issues": ["Mobile menu difficult to use", "Forms lack clear labels"]
  },
  "conversion": {
    "score": 68,
    "issues": ["CTA below fold", "No trust signals visible"]
  },
  "recommendations": [
    {
      "type": "sxo",
      "task": "Move CTA above fold",
      "seo_impact": "Low",
      "ux_impact": "High",
      "conversion_impact": "High"
    }
  ]
}
```

## Integration

Works with:
- `/seo audit` for SEO baseline
- `/seo performance` for speed metrics
- `/seo content` for content quality
