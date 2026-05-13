---
name: seo-drift
description: "SEO drift monitoring. Capture baselines and compare deployments for title, meta, schema, and content changes. Detect regressions and track SEO health over time."
user-invokable: true
argument-hint: "baseline <url> | compare <url>"
license: MIT
version: "1.9.6-unified"
---

# SEO Drift - Change Monitoring

## Commands

### Baseline Capture
```
/seo drift baseline <url>
```
Captures current state for comparison.

### Drift Comparison
```
/seo drift compare <url>
```
Compares current state vs baseline.

## Baseline Storage

```
.seo-cache/baselines/
  {url-slug}/
    baseline.json        # Full baseline snapshot
    timestamp.txt        # When captured
```

## Tracked Elements

### Meta Elements
- Title tags
- Meta descriptions
- Canonical URLs
- Robots directives

### Schema
- Schema types present
- Property values
- Validation status

### Content
- H1 text
- Word count
- Internal link count
- Image count

### Technical
- Robots.txt content
- Sitemap URLs
- Redirect chains
- Security headers

## Drift Detection

| Change Type | Severity |
|-------------|----------|
| Title changed | High |
| Meta description changed | Medium |
| Schema removed | Critical |
| H1 changed | High |
| Robots.txt changed | Critical |
| Word count -50% | Medium |

## Output

### Baseline Capture
```json
{
  "url": "https://example.com",
  "timestamp": "2026-05-13T19:30:00Z",
  "captured": {
    "title": "Example - Best Service Provider",
    "meta_description": "We provide...",
    "h1": "Welcome to Example",
    "schema_types": ["Organization", "WebSite"],
    "word_count": 1250,
    "robots_txt": "User-agent: *\\nAllow: /"
  },
  "file": ".seo-cache/baselines/example-com/baseline.json"
}
```

### Drift Comparison
```json
{
  "url": "https://example.com",
  "baseline_date": "2026-04-15T10:00:00Z",
  "compare_date": "2026-05-13T19:30:00Z",
  "changes": [
    {
      "element": "title",
      "baseline": "Example - Best Service Provider",
      "current": "Example - #1 Service Provider",
      "severity": "medium",
      "impact": "Minor keyword change"
    },
    {
      "element": "schema",
      "baseline": ["Organization", "WebSite"],
      "current": ["Organization"],
      "severity": "critical",
      "impact": "WebSite schema removed"
    }
  ],
  "score_delta": -3,
  "regressions": 1,
  "improvements": 0
}
```

## CI/CD Integration

```bash
# In deployment pipeline
python scripts/run_skill_workflow.py drift --url https://example.com --baseline .seo-cache/baselines/example-com/baseline.json

# Exit code 1 if critical regressions found
```
