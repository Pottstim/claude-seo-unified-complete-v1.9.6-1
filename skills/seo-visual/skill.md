---
name: seo-visual
description: "Visual SEO analysis including screenshots and rendering tests"
user-invokable: true
---

# Visual SEO Skill

## Overview

Visual analysis of web pages including screenshots, mobile rendering, and visual regression testing.

## Commands

| Command | Description |
|---------|-------------|
| `/seo visual <url>` | Capture and analyze page visuals |
| `/seo visual mobile <url>` | Mobile rendering test |
| `/seo visual compare <url1> <url2>` | Visual comparison |
| `/seo visual fold <url>` | Above-the-fold analysis |

## Visual Checks

### Above the Fold
- Hero section visible
- Value proposition clear
- CTA accessible
- No blocking elements
- Logo visible

### Mobile Rendering
- Responsive design working
- Touch targets adequate (min 48px)
- Font sizes readable
- No horizontal scroll
- Form inputs accessible

### Visual Hierarchy
- Clear focal point
- Content flows logically
- Adequate whitespace
- Contrast ratios meet WCAG

## Screenshots

Captures multiple viewports:
- Desktop (1920x1080)
- Tablet (768x1024)
- Mobile (375x667)

## Output

```json
{
  "url": "https://example.com",
  "screenshots": {
    "desktop": "screenshots/example-desktop.png",
    "tablet": "screenshots/example-tablet.png",
    "mobile": "screenshots/example-mobile.png"
  },
  "above_fold": {
    "hero_visible": true,
    "cta_visible": true,
    "value_prop_clear": true,
    "issues": []
  },
  "mobile_analysis": {
    "touch_targets": "pass",
    "font_sizes": "pass",
    "horizontal_scroll": false,
    "issues": []
  },
  "visual_score": 88
}
```

## Requirements

Requires browser automation:
- Playwright (recommended)
- Selenium (alternative)

Install with:
```bash
pip install playwright
playwright install chromium
```
