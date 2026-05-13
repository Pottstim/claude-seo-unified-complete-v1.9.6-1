---
name: seo-local
description: "Local SEO analysis for Google Business Profile (GBP), NAP consistency, citation audit, review sentiment, and multi-location support. Optimizes for local pack visibility."
user-invokable: true
argument-hint: "<url>"
license: MIT
version: "1.9.6-unified"
---

# SEO Local - Local SEO Analysis

## Analysis Scope

### Google Business Profile (GBP)
- Profile completeness
- Category optimization
- Photo count and quality
- Posts frequency
- Q&A section
- Review response rate

### NAP Consistency
- Name, Address, Phone consistency across:
  - Website
  - GBP
  - Top citations (Yelp, Yellow Pages, etc.)

### Citations
- Tier 1: Google, Facebook, Yelp
- Tier 2: Industry-specific directories
- Tier 3: General local directories
- Duplicate detection
- NAP accuracy

### Reviews
- Average rating
- Review count
- Response rate
- Sentiment analysis
- Recent review velocity

### Local Ranking Factors
- Proximity signals
- Category relevance
- Keyword in GBP title
- Photo quantity
- Review recency

## Scoring (0-20 points for local businesses)

| Factor | Points |
|--------|--------|
| GBP completeness | 5 |
| NAP consistency | 4 |
| Review rating (4.5+) | 3 |
| Review count (50+) | 2 |
| Review response rate (80%+) | 2 |
| Citation accuracy | 2 |
| Local landing pages | 2 |

## Output

```json
{
  "url": "https://example.com",
  "business_name": "Example Business",
  "score": 15,
  "max_score": 20,
  "gbp": {
    "claimed": true,
    "completeness": 85,
    "categories": ["Primary Category", "Secondary"],
    "photos": 24,
    "posts_last_30_days": 2,
    "review_response_rate": 92
  },
  "nap": {
    "consistent": true,
    "locations_checked": 15,
    "inconsistencies": []
  },
  "reviews": {
    "average_rating": 4.7,
    "total_count": 127,
    "response_rate": 92,
    "recent_30_days": 8
  },
  "citations": {
    "tier1_accurate": true,
    "tier2_found": 12,
    "duplicates": 0
  },
  "recommendations": [
    "Add more GBP posts (aim for weekly)",
    "Upload more photos to GBP",
    "Claim additional industry directories"
  ]
}
```

## Multi-Location Support

For businesses with 10+ locations:
- Check unique content requirement (60%+ unique)
- Validate location page schema
- Audit store locator functionality
- Review location-specific GBP profiles
