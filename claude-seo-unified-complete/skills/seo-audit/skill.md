---
name: seo-audit
description: "Full site SEO audit orchestrator. Coordinates parallel subagent analysis across technical, content, schema, performance, and AI readiness dimensions. Generates comprehensive health score and prioritized action plan."
user-invokable: true
argument-hint: "<url>"
license: MIT
version: "1.9.6-unified"
---

# SEO Audit - Full Site Orchestrator

## Purpose

Execute comprehensive SEO audit with parallel subagent delegation. Generates SEO Health Score (0-100) and prioritized recommendations.

## Workflow

1. **Initialize**: Parse URL, validate accessibility
2. **Detect Business Type**: SaaS, Local, E-commerce, Publisher, Agency
3. **Spawn Core Agents** (parallel):
   - seo-technical
   - seo-content
   - seo-schema
   - seo-sitemap
   - seo-performance
   - seo-visual
   - seo-geo
   - seo-sxo
4. **Spawn Conditional Agents**:
   - seo-local (if local business signals)
   - seo-maps (if local + DataForSEO)
   - seo-google (if API credentials)
   - seo-backlinks (if APIs configured)
   - seo-ecommerce (if e-commerce detected)
   - seo-drift (if baseline exists)
5. **Aggregate Results**: Combine scores, dedupe issues
6. **Generate Report**: Markdown, JSON, or PDF

## Scoring

| Category | Weight |
|----------|--------|
| Technical SEO | 22% |
| Content Quality | 23% |
| On-Page SEO | 20% |
| Schema/Structured Data | 10% |
| Performance (CWV) | 10% |
| AI Search Readiness | 10% |
| Images | 5% |

## Output

```json
{
  "url": "https://example.com",
  "timestamp": "2026-05-13T19:30:00Z",
  "health_score": 73,
  "scores": {
    "technical": 16,
    "content": 17,
    "onpage": 15,
    "schema": 8,
    "performance": 9,
    "ai_readiness": 5,
    "images": 3
  },
  "business_type": "SaaS",
  "issues": {
    "critical": [],
    "high": ["Missing robots.txt", "No Organization schema"],
    "medium": ["LCP 2.8s (target <2.5s)"],
    "low": ["Consider WebP images"]
  },
  "recommendations": [
    {"priority": "high", "action": "Add robots.txt file", "impact": "+3 health score"},
    {"priority": "high", "action": "Implement Organization schema", "impact": "+2 health score"}
  ]
}
```

## Cache Integration

Check `.seo-cache/` before analysis:
- `site-meta.json` - Business type, industry
- `audit-scores.json` - Previous scores

Use `--refresh` to bypass cache.
