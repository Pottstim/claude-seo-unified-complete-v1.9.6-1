---
name: seo-sitemap
description: "XML sitemap analysis and generation. Validates sitemap structure, checks URL coverage, identifies orphan pages, and generates compliant sitemaps."
user-invokable: true
argument-hint: "<url>"
license: MIT
version: "1.9.6-unified"
---

# SEO Sitemap - XML Sitemap Analysis

## Analysis Scope

### Sitemap Detection
- `/sitemap.xml`
- `/sitemap_index.xml`
- Robots.txt sitemap directive
- Common alternate locations

### Validation
- XML syntax validity
- URL count and limits (50,000 max)
- File size limits (50MB max)
- Last modification dates
- Priority values
- Change frequency values

### Coverage Analysis
- Indexed URLs vs sitemap URLs
- Orphan pages (in site, not in sitemap)
- Redirect URLs in sitemap
- Non-canonical URLs in sitemap
- Broken URLs in sitemap

### Multi-Sitemap
- Sitemap index validation
- Cross-reference checking
- Deduplication

## Scoring (part of Technical SEO)

| Check | Status |
|-------|--------|
| Sitemap exists | Required |
| Valid XML | Required |
| All URLs canonical | Required |
| No broken URLs | Required |
| Coverage > 90% | Recommended |

## Output

```json
{
  "url": "https://example.com",
  "sitemap_found": true,
  "sitemap_url": "/sitemap.xml",
  "validation": {
    "valid_xml": true,
    "url_count": 127,
    "file_size_kb": 45
  },
  "coverage": {
    "sitemap_urls": 127,
    "crawlable_urls": 145,
    "coverage_percent": 87.5,
    "orphan_pages": 18
  },
  "issues": [
    {
      "severity": "medium",
      "issue": "18 pages not in sitemap",
      "pages": ["/blog/post-1", "/about/team", "..."]
    },
    {
      "severity": "low",
      "issue": "changefreq deprecated by Google",
      "recommendation": "Remove changefreq tags"
    }
  ],
  "recommendations": [
    "Add 18 orphan pages to sitemap",
    "Remove changefreq tags (ignored by Google)",
    "Consider splitting sitemap (approaching 50,000 URL limit)"
  ]
}
```

## Sitemap Generation

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/</loc>
    <lastmod>2026-05-13</lastmod>
    <priority>1.0</priority>
  </url>
</urlset>
```

## Commands

- `/seo sitemap <url>` - Analyze existing sitemap
- `/seo sitemap generate <url>` - Generate new sitemap
- `/seo sitemap submit <url>` - Submit to search engines (IndexNow)
