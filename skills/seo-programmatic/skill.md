---
name: seo-programmatic
description: "Programmatic SEO for scalable page generation"
user-invokable: true
---

# Programmatic SEO Skill

## Overview

Guides programmatic SEO implementation for generating large-scale, SEO-optimized pages from structured data.

## Commands

| Command | Description |
|---------|-------------|
| `/seo programmatic plan <url>` | Plan programmatic strategy |
| `/seo programmatic template <url>` | Generate page templates |
| `/seo programmatic data <url>` | Analyze data structure |
| `/seo programmatic risks <url>` | Identify scalability risks |

## Use Cases

- Location pages for multi-location businesses
- Product variations (color, size, etc.)
- Directory/listing pages
- Glossary/definition pages
- Comparison pages
- Event calendars

## Quality Gates

🛑 **Hard Stops** (require explicit justification):
- More than 50 location pages
- Duplicate content > 30%
- Thin content (< 200 words)
- Missing unique value per page

⚠️ **Warnings**:
- Similar page templates
- Limited unique content
- Parameter-based URLs

## Template Structure

```html
<!-- Template: Location Page -->
<h1>{service} in {city}, {state}</h1>
<p>Professional {service} serving {city} and surrounding areas...</p>

<!-- Unique content blocks -->
<section class="local-info">
  {city_specific_content}
</section>

<!-- Dynamic data -->
<section class="services">
  {services_list}
</section>
```

## Data Requirements

- Primary key field (URL slug)
- Unique content fields
- Variable injection points
- Canonical URL logic

## Output

```json
{
  "strategy": "location_pages",
  "estimated_pages": 150,
  "template_structure": {...},
  "unique_content_requirements": {
    "per_page_minimum": 300,
    "unique_blocks": 3
  },
  "risks": [
    "Potential thin content on small cities"
  ],
  "recommendations": [
    "Combine cities under 50k population"
  ]
}
```
