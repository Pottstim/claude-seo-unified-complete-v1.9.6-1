---
name: seo-content
description: "E-E-A-T content quality analysis. Evaluates Experience, Expertise, Authoritativeness, Trustworthiness, content depth, readability, thin content detection, and helpful content signals."
user-invokable: true
argument-hint: "<url>"
license: MIT
version: "1.9.6-unified"
---

# SEO Content - E-E-A-T & Content Quality

## E-E-A-T Framework

### Experience (0-5 points)
- First-hand experience demonstrated
- Case studies, examples, data
- Personal anecdotes where relevant
- Original research/surveys

### Expertise (0-6 points)
- Author credentials visible
- Subject matter depth
- Technical accuracy
- Industry recognition

### Authoritativeness (0-6 points)
- External citations/references
- Industry awards/mentions
- Expert quotes
- Publication history

### Trustworthiness (0-6 points)
- Contact information
- About page quality
- Privacy policy
- Source citations
- Date stamps

## Content Quality Metrics

| Metric | Threshold | Points |
|--------|-----------|--------|
| Word count | >1000 words | 2 |
| Readability (Flesch) | 60-70 | 2 |
| Heading structure | H1-H3 hierarchy | 2 |
| Internal links | 3+ per 1000 words | 2 |
| External links | 1+ authoritative | 1 |
| Images | 1+ per 500 words | 2 |
| Thin content | No pages <300 words | 2 |

## Helpful Content Signals

- Satisfies search intent
- Provides complete answer
- Updated recently ( freshness)
- No excessive ads above fold
- Clear value proposition

## Scoring (0-23 points)

Maximum 23 points weighted at 23% of total health score.

## Output

```json
{
  "url": "https://example.com/blog/post",
  "score": 17,
  "max_score": 23,
  "eeat": {
    "experience": 4,
    "expertise": 5,
    "authoritativeness": 4,
    "trustworthiness": 4
  },
  "content_metrics": {
    "word_count": 1850,
    "readability_score": 65,
    "heading_hierarchy": true,
    "internal_links": 5,
    "external_links": 3,
    "images": 4
  },
  "issues": [
    {"severity": "medium", "issue": "No author bio visible", "fix": "Add author byline with credentials"},
    {"severity": "low", "issue": "Last updated date missing", "fix": "Add last-modified timestamp"}
  ]
}
```
