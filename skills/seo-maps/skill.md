---
name: seo-maps
description: "Maps and local search intelligence"
user-invokable: true
---

# Maps Intelligence Skill

## Overview

Local search and Google Maps intelligence for local SEO optimization.

## Commands

| Command | Description |
|---------|-------------|
| `/seo maps geo-grid <location>` | Generate geo-grid ranking report |
| `/seo maps gbp <business>` | Google Business Profile audit |
| `/seo maps citations <business>` | Citation consistency check |
| `/seo maps competitors <location>` | Local competitor analysis |

## Geo-Grid Analysis

Tracks rankings across different geographic points:

```
        North
          ↑
West ←   ●   → East
          ↓
        South

Grid shows ranking positions at each point
```

## Output

```json
{
  "geo_grid": {
    "center": {"lat": 40.7128, "lng": -74.0060},
    "keyword": "pizza near me",
    "rankings": [
      {"point": "NW", "rank": 3, "distance": "2mi"},
      {"point": "N", "rank": 2, "distance": "1mi"},
      {"point": "NE", "rank": 4, "distance": "2mi"}
    ],
    "average_rank": 3.2
  }
}
```

## GBP Audit

- Profile completeness
- Category optimization
- Photo upload frequency
- Review count and rating
- Post frequency
- Q&A activity

## Citation Sources

- Google Business Profile
- Yelp
- Facebook
- Bing Places
- Apple Maps
- Industry-specific directories
- Local chamber of commerce

## Requirements

- Google Places API key (optional but recommended)
- Business name and address for GBP audit
