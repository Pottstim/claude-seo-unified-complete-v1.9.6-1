---
name: seo-performance
description: "Core Web Vitals analysis (INP, LCP, CLS). Measures real user metrics via CrUX API and lab data via PageSpeed Insights. Provides optimization recommendations."
user-invokable: true
argument-hint: "<url>"
license: MIT
version: "1.9.6-unified"
---

# SEO Performance - Core Web Vitals

## Core Web Vitals (2024 Standard)

### INP (Interaction to Next Paint)
- **Good**: < 200ms
- **Needs Improvement**: 200-500ms
- **Poor**: > 500ms
- Replaces FID (deprecated Sept 2024)

### LCP (Largest Contentful Paint)
- **Good**: < 2.5s
- **Needs Improvement**: 2.5s - 4.0s
- **Poor**: > 4.0s

### CLS (Cumulative Layout Shift)
- **Good**: < 0.1
- **Needs Improvement**: 0.1 - 0.25
- **Poor**: > 0.25

## Data Sources

1. **CrUX API** - Real user data (28-day rolling)
2. **PageSpeed Insights** - Lab + field data
3. **Lighthouse** - Synthetic analysis

## Additional Metrics

- TTFB (Time to First Byte)
- FCP (First Contentful Paint)
- TBT (Total Blocking Time)
- Speed Index

## Scoring (0-10 points)

| Metric | Good | Needs Work | Poor |
|--------|------|------------|------|
| INP | 3 | 2 | 0 |
| LCP | 3 | 2 | 0 |
| CLS | 2 | 1 | 0 |
| TTFB < 600ms | 2 | 1 | 0 |

## Output

```json
{
  "url": "https://example.com",
  "score": 7,
  "max_score": 10,
  "cwv": {
    "inp": {"value": 145, "rating": "good", "threshold": "< 200ms"},
    "lcp": {"value": 2.8, "rating": "needs-improvement", "threshold": "< 2.5s"},
    "cls": {"value": 0.05, "rating": "good", "threshold": "< 0.1"}
  },
  "additional": {
    "ttfb": {"value": 450, "rating": "good"},
    "fcp": {"value": 1.2, "rating": "good"},
    "speed_index": {"value": 2.1, "rating": "good"}
  },
  "issues": [
    {
      "severity": "medium",
      "metric": "LCP",
      "value": "2.8s",
      "target": "< 2.5s",
      "recommendations": [
        "Optimize largest image (hero.jpg - 1.2MB)",
        "Preload LCP image",
        "Consider WebP format"
      ]
    }
  ]
}
```

## Quality Gates

- Use INP (not FID) for Core Web Vitals
- Check mobile + desktop separately
- Prioritize real user data over lab data
