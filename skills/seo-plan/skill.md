---
name: seo-plan
description: "Strategic SEO planning and roadmap creation"
user-invokable: true
---

# SEO Planning Skill

## Overview

Creates strategic SEO roadmaps with prioritized recommendations based on impact and effort.

## Commands

| Command | Description |
|---------|-------------|
| `/seo plan create <url>` | Create SEO roadmap |
| `/seo plan prioritize <url>` | Prioritize existing issues |
| `/seo plan quick-wins <url>` | Identify quick wins |
| `/seo plan roadmap <url>` | Generate detailed roadmap |

## Planning Framework

### Priority Matrix

| | Low Effort | High Effort |
|---|---|---|
| **High Impact** | Quick Wins | Major Projects |
| **Low Impact** | Fill-ins | Avoid |

### Issue Prioritization

Factors considered:
- Traffic potential impact
- Ranking improvement potential
- Conversion impact
- Implementation effort
- Resource requirements
- Dependencies

## Roadmap Structure

```json
{
  "roadmap": {
    "phase_1": {
      "name": "Quick Wins",
      "duration": "2 weeks",
      "items": [
        {"task": "Fix title tags", "impact": "high", "effort": "low"},
        {"task": "Add meta descriptions", "impact": "medium", "effort": "low"}
      ]
    },
    "phase_2": {
      "name": "Technical Foundation",
      "duration": "4 weeks",
      "items": [...]
    },
    "phase_3": {
      "name": "Content Expansion",
      "duration": "8 weeks",
      "items": [...]
    }
  },
  "estimated_traffic_impact": "+45% in 6 months"
}
```

## Business Type Templates

Different roadmaps for:
- SaaS companies
- E-commerce stores
- Local businesses
- Publishers
- Agencies

## Integration

Works with `/seo audit` results to generate actionable plans.
