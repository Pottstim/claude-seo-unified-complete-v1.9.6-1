---
name: seo-page
description: "Individual page SEO analysis"
user-invokable: true
---

# Page-Level SEO Skill

## Overview

Detailed SEO analysis for individual pages, focusing on on-page optimization and content quality.

## Commands

| Command | Description |
|---------|-------------|
| `/seo page <url>` | Full page analysis |
| `/seo page title <url>` | Title tag analysis |
| `/seo page meta <url>` | Meta description analysis |
| `/seo page headings <url>` | Heading structure |
| `/seo page links <url>` | Link analysis |
| `/seo page content <url>` | Content quality check |

## Analysis Categories

### Title Tag
- Length (optimal: 50-60 chars)
- Keyword presence
- Uniqueness
- Brand inclusion

### Meta Description
- Length (optimal: 150-160 chars)
- Call-to-action
- Keyword inclusion
- Uniqueness

### Headings
- H1 presence and uniqueness
- Heading hierarchy (H1 → H2 → H3)
- Keyword distribution
- Content structure

### Links
- Internal link count
- External link count
- Broken links
- Anchor text diversity

### Content
- Word count
- Keyword density
- Readability
- Duplicate content

## Output

```json
{
  "url": "https://example.com/page",
  "title": {
    "text": "Example Page Title",
    "length": 52,
    "status": "optimal"
  },
  "meta_description": {
    "text": "...",
    "length": 155,
    "status": "optimal"
  },
  "headings": {
    "h1": {"count": 1, "text": "..."},
    "h2": {"count": 5},
    "h3": {"count": 3}
  },
  "content": {
    "word_count": 1250,
    "readability": "Flesch-Kincaid Grade 8"
  },
  "score": 85,
  "issues": [...],
  "recommendations": [...]
}
```
