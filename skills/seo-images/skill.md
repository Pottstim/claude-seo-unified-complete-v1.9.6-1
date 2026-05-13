---
name: seo-images
description: "Image SEO analysis and optimization. Checks alt text, file sizes, format recommendations (WebP/AVIF), lazy loading, and image sitemap inclusion."
user-invokable: true
argument-hint: "<url>"
license: MIT
version: "1.9.6-unified"
---

# SEO Images - Image Optimization

## Analysis Scope

### Alt Text
- Presence of alt attributes
- Keyword relevance
- Length optimization (125 chars max)
- Decorative image handling

### File Optimization
- File size (target < 100KB)
- Format recommendations
- Compression opportunities
- Responsive images (srcset)

### Technical
- Lazy loading implementation
- Image sitemap inclusion
- CDN usage
- Next-gen formats (WebP, AVIF)

### Performance
- LCP image optimization
- Preload recommendations
- Aspect ratio stability

## Scoring (0-5 points)

| Check | Points |
|-------|--------|
| All images have alt text | 1 |
| Images under 100KB | 1 |
| WebP/AVIF format used | 1 |
| Lazy loading enabled | 1 |
| Images in sitemap | 1 |

## Output

```json
{
  "url": "https://example.com",
  "score": 3,
  "max_score": 5,
  "images_analyzed": 24,
  "issues": {
    "missing_alt": 3,
    "oversized": 5,
    "no_next_gen": 18,
    "not_lazy_loaded": 0
  },
  "details": [
    {
      "image": "/images/hero.jpg",
      "issues": [
        {"type": "size", "current": "1.2MB", "recommendation": "Compress to < 100KB"},
        {"type": "format", "current": "JPEG", "recommendation": "Convert to WebP"}
      ]
    },
    {
      "image": "/images/logo.png",
      "issues": [
        {"type": "alt", "current": null, "recommendation": "Add descriptive alt text"}
      ]
    }
  ],
  "recommendations": [
    "Add alt text to 3 images",
    "Compress 5 images over 100KB",
    "Convert 18 images to WebP format"
  ]
}
```

## Optimization Commands

```bash
# Convert to WebP
convert input.jpg -quality 80 output.webp

# Resize large images
convert input.jpg -resize 1920x output.jpg

# Batch optimize
find . -name "*.jpg" -exec convert {} -quality 80 {} \;
```
