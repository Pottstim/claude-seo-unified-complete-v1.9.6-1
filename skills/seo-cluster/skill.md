---
name: seo-cluster
description: "Topic cluster and content hub analysis for semantic SEO"
user-invokable: true
---

# Topic Cluster Analysis Skill

## Overview

Analyzes and builds topic clusters for semantic SEO. Identifies pillar pages, cluster content opportunities, and internal linking structures.

## Commands

| Command | Description |
|---------|-------------|
| `/seo cluster analyze <url>` | Analyze existing topic clusters |
| `/seo cluster build <topic>` | Build topic cluster structure |
| `/seo cluster gaps <url>` | Find content gaps in clusters |
| `/seo cluster links <url>` | Optimize internal linking |

## Cluster Structure

```
Pillar Page (Topic Hub)
├── Cluster Page 1 (Subtopic)
│   ├── Supporting Article 1
│   └── Supporting Article 2
├── Cluster Page 2 (Subtopic)
│   ├── Supporting Article 1
│   └── Supporting Article 2
└── Cluster Page 3 (Subtopic)
```

## Analysis Output

```json
{
  "topic": "SEO",
  "pillar_page": "https://example.com/seo-guide",
  "clusters": [
    {
      "topic": "Technical SEO",
      "url": "/technical-seo",
      "supporting_content": 5,
      "internal_links": 12,
      "completeness": 80
    }
  ],
  "gaps": ["Mobile SEO", "International SEO"]
}
```

## Best Practices

- Each cluster should have 5-15 supporting articles
- All cluster pages link to pillar
- Cross-link related cluster content
- Target medium-tail keywords in clusters
