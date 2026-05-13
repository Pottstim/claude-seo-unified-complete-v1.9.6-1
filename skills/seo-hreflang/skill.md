---
name: seo-hreflang
description: "International SEO and hreflang implementation analysis"
user-invokable: true
---

# Hreflang & International SEO Skill

## Overview

Analyzes hreflang implementation, international targeting, and multi-regional SEO best practices.

## Commands

| Command | Description |
|---------|-------------|
| `/seo hreflang audit <url>` | Full hreflang audit |
| `/seo hreflang validate <url>` | Validate hreflang syntax |
| `/seo hreflang conflicts <url>` | Detect hreflang conflicts |
| `/seo international <url>` | International SEO review |

## Hreflang Checks

- Self-referencing tags present
- Reciprocal links between alternates
- x-default implementation
- Language code validity (ISO 639-1)
- Region code validity (ISO 3166-1 Alpha-2)
- URL consistency (HTTP/HTTPS, trailing slashes)
- Sitemap inclusion

## Common Issues

| Issue | Severity | Description |
|-------|----------|-------------|
| Missing return links | Critical | Page A links to B, B doesn't link back |
| Invalid language code | High | Using unsupported language codes |
| Missing self-reference | Medium | Page should reference itself |
| x-default missing | Medium | Default page not specified |
| HTTP/HTTPS mismatch | High | Mixed protocol in alternates |

## Output

```json
{
  "hreflang_tags": [
    {"lang": "en", "url": "https://example.com/en/"},
    {"lang": "es", "url": "https://example.com/es/"},
    {"lang": "x-default", "url": "https://example.com/"}
  ],
  "issues": [
    {
      "type": "missing_return_link",
      "severity": "critical",
      "details": "es version missing link to en"
    }
  ],
  "recommendations": [...]
}
```

## Best Practices

- Include hreflang in sitemap OR HTML head (not both)
- Use full URLs (not relative)
- Include x-default for unmatched languages
- Verify with Google's International Targeting report
