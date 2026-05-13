---
name: seo-schema
description: "Schema.org markup detection, validation, and generation. Checks JSON-LD, Microdata, RDFa. Validates against Google rich result types. Generates missing schema markup."
user-invokable: true
argument-hint: "<url>"
license: MIT
version: "1.9.6-unified"
---

# SEO Schema - Structured Data Analysis

## Detection

Scans for:
- **JSON-LD** (preferred by Google)
- **Microdata**
- **RDFa**

## Supported Schema Types

### Core Business
- Organization
- LocalBusiness
- Person
- Website

### Content
- Article
- BlogPosting
- NewsArticle
- FAQ (note: limited Google support since Aug 2023)

### E-commerce
- Product
- Offer
- AggregateRating
- Review

### Local
- LocalBusiness
- PostalAddress
- GeoCoordinates
- OpeningHoursSpecification

### Technical
- BreadcrumbList
- SiteNavigationElement
- WebPage

### Deprecated (avoid)
- HowTo (deprecated Sept 2023)
- FAQ for non-gov/health (limited Aug 2023)

## Validation

1. Syntax validation (JSON-LD parsing)
2. Google Rich Results Test compatibility
3. Required property completeness
4. Type-specific validation rules

## Scoring (0-10 points)

| Schema Type | Points |
|-------------|--------|
| Organization/LocalBusiness | 3 |
| WebPage/Breadcrumbs | 2 |
| Article/Content | 2 |
| Product (if e-commerce) | 2 |
| Additional relevant types | 1 |

## Output

```json
{
  "url": "https://example.com",
  "score": 7,
  "max_score": 10,
  "detected": [
    {
      "type": "Organization",
      "format": "JSON-LD",
      "valid": true,
      "properties": ["name", "url", "logo"]
    },
    {
      "type": "WebSite",
      "format": "JSON-LD",
      "valid": true,
      "properties": ["name", "url", "potentialAction"]
    }
  ],
  "missing": ["LocalBusiness", "BreadcrumbList"],
  "errors": [],
  "recommendations": [
    "Add LocalBusiness schema for local SEO",
    "Add BreadcrumbList for navigation"
  ]
}
```

## Generation

Can generate schema markup for:
- Missing required types
- Enhanced rich result eligibility
- E-commerce product pages
- Local business pages
