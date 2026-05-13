# Core Web Vitals Thresholds (2024 Standard)

## Primary Metrics

### INP (Interaction to Next Paint)
**Replaces FID (deprecated September 2024)**

| Rating | Threshold |
|--------|-----------|
| Good | < 200ms |
| Needs Improvement | 200ms - 500ms |
| Poor | > 500ms |

INP measures the latency of all interactions throughout the page lifecycle.

### LCP (Largest Contentful Paint)

| Rating | Threshold |
|--------|-----------|
| Good | < 2.5s |
| Needs Improvement | 2.5s - 4.0s |
| Poor | > 4.0s |

LCP marks when the largest content element becomes visible.

### CLS (Cumulative Layout Shift)

| Rating | Threshold |
|--------|-----------|
| Good | < 0.1 |
| Needs Improvement | 0.1 - 0.25 |
| Poor | > 0.25 |

CLS measures visual stability throughout the page lifecycle.

## Additional Metrics

### TTFB (Time to First Byte)
- Good: < 800ms
- Needs Improvement: 800ms - 1800ms
- Poor: > 1800ms

### FCP (First Contentful Paint)
- Good: < 1.8s
- Needs Improvement: 1.8s - 3.0s
- Poor: > 3.0s

## Key Changes

| Metric | Status |
|--------|--------|
| FID | **Deprecated** (Sept 2024) |
| INP | **New Core Web Vital** (March 2024) |

## Optimization Tips

### INP
- Break up long tasks (>50ms)
- Use `requestIdleCallback` for non-critical work
- Optimize event handlers

### LCP
- Preload LCP image with `<link rel="preload">`
- Optimize server response time
- Use CDN for static assets
- Optimize images (WebP, AVIF)

### CLS
- Set explicit dimensions on images
- Reserve space for ads
- Avoid inserting content above existing content
- Use `font-display: optional` for web fonts
