---
name: seo-ecommerce
description: "E-commerce specific SEO analysis for product pages and catalogs"
user-invokable: true
---

# E-commerce SEO Skill

## Overview

Specialized SEO analysis for e-commerce websites including product page optimization, category structure, and schema markup for products.

## Commands

| Command | Description |
|---------|-------------|
| `/seo ecommerce <url>` | Full e-commerce audit |
| `/seo ecommerce product <url>` | Product page analysis |
| `/seo ecommerce category <url>` | Category page analysis |
| `/seo ecommerce faceted <url>` | Faceted navigation audit |

## Key Checks

### Product Pages
- Product schema (Product, Offer, AggregateRating)
- Image optimization (multiple angles)
- Unique descriptions (no manufacturer defaults)
- Reviews and ratings markup
- Price and availability
- Breadcrumb navigation

### Category Pages
- Category hierarchy depth
- Faceted navigation handling
- Pagination strategy
- Internal linking to products
- Filter parameter handling

### Technical
- Shopping cart indexing
- Checkout flow blocking
- Product variant handling
- Stock status management

## Schema Requirements

```json
{
  "@type": "Product",
  "name": "...",
  "image": [...],
  "offers": {
    "@type": "Offer",
    "price": "29.99",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.5",
    "reviewCount": "127"
  }
}
```

## Output

```json
{
  "product_pages": 50,
  "issues": {
    "missing_schema": 12,
    "thin_content": 8,
    "duplicate_descriptions": 15
  },
  "recommendations": [...]
}
```
