---
name: seo-technical
description: "Technical SEO analysis covering crawlability, indexability, robots.txt, sitemap, canonical tags, redirects, HTTPS, security headers, and JavaScript rendering risks."
user-invokable: true
argument-hint: "<url>"
license: MIT
version: "1.9.6-unified"
---

# SEO Technical - Technical SEO Analysis

## Scope

Analyzes 9 technical SEO categories:

1. **Crawlability**
   - Robots.txt presence and syntax
   - Meta robots directives
   - X-Robots-Tag headers

2. **Indexability**
   - Canonical tags
   - Noindex detection
   - Pagination handling

3. **URL Structure**
   - URL length and readability
   - Parameter handling
   - URL canonicalization

4. **Redirects**
   - Redirect chains
   - Redirect loops
   - 301/302 usage

5. **HTTPS & Security**
   - SSL certificate validity
   - Mixed content warnings
   - Security headers (HSTS, X-Frame-Options, etc.)

6. **JavaScript Rendering**
   - Critical content in JS
   - SSR/CSR detection
   - Googlebot crawlability

7. **Mobile**
   - Mobile-friendly detection
   - Viewport configuration
   - Touch target sizing

8. **International (if applicable)**
   - hreflang tags
   - Language annotations
   - Geographic targeting

9. **Page Speed Signals**
   - TTFB measurement
   - Render-blocking resources
   - Critical CSS

## Scoring (0-22 points)

| Check | Points |
|-------|--------|
| Valid robots.txt | 2 |
| XML sitemap present | 2 |
| HTTPS enforced | 2 |
| Valid SSL | 2 |
| No redirect chains | 2 |
| Canonicals correct | 2 |
| Mobile-friendly | 2 |
| Security headers | 2 |
| No JS rendering issues | 2 |
| Fast TTFB (<600ms) | 2 |

## Output

```json
{
  "url": "https://example.com",
  "score": 18,
  "max_score": 22,
  "checks": {
    "robots_txt": {"status": "pass", "details": "Valid robots.txt found"},
    "sitemap": {"status": "pass", "url": "/sitemap.xml"},
    "https": {"status": "pass", "ssl_grade": "A"},
    "canonicals": {"status": "warning", "details": "Multiple canonicals on /blog"},
    "mobile": {"status": "pass", "viewport": "configured"},
    "security_headers": {"status": "fail", "missing": ["HSTS", "X-Frame-Options"]}
  },
  "issues": [
    {"severity": "high", "issue": "Missing HSTS header", "fix": "Add Strict-Transport-Security header"},
    {"severity": "medium", "issue": "Multiple canonical tags on /blog", "fix": "Remove duplicate canonical"}
  ]
}
```
