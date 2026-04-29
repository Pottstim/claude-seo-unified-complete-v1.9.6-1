# SEO Agents Directory

This directory contains the specialist AI agent definitions for parallel SEO analysis. Each agent focuses on a specific domain and runs concurrently for maximum speed.

## Agent Architecture

The unified SEO system uses **9 parallel specialist agents** that analyze different aspects simultaneously:

1. **Technical SEO Agent** (`technical-agent.md`)
   - Crawlability, robots.txt, sitemap
   - Status codes, redirects, canonical
   - HTTPS, HSTS, security headers

2. **Content Quality Agent** (`content-agent.md`)
   - E-E-A-T assessment
   - Content depth, readability
   - Keyword optimization, topical relevance

3. **Schema Markup Agent** (`schema-agent.md`)
   - Schema.org validation
   - Rich results eligibility
   - Structured data errors

4. **Performance Agent** (`performance-agent.md`)
   - Core Web Vitals (LCP, INP, CLS)
   - PageSpeed scores
   - Resource optimization

5. **On-Page SEO Agent** (`onpage-agent.md`)
   - Meta tags, headings
   - Internal linking
   - URL structure

6. **Image Optimization Agent** (`images-agent.md`)
   - Alt text, file sizes
   - Format optimization (WebP, AVIF)
   - Lazy loading

7. **Local SEO Agent** (`local-agent.md`)
   - NAP consistency
   - Google Business Profile
   - Local citations

8. **Backlink Agent** (`backlink-agent.md`)
   - Link profile quality
   - Toxic link detection
   - Anchor text distribution

9. **AI Readiness Agent** (`ai-agent.md`)
   - GEO optimization
   - SGE compatibility
   - AI crawler support (GPTBot, ClaudeBot)

## Agent Definition Format

Each `*-agent.md` file contains:

```markdown
# [Agent Name]

## Persona
[Agent expertise and focus]

## Instructions
[Detailed analysis steps]

## Scoring Criteria
[How to calculate score 0-100]

## Output Format
[JSON schema for results]
```

## Usage in Orchestrator

The main audit workflow (`SKILL.md`) spawns agents in parallel:

```python
async def run_audit(url):
    agents = [
        TechnicalAgent(url),
        ContentAgent(url),
        SchemaAgent(url),
        PerformanceAgent(url),
        # ... 5 more
    ]
    results = await asyncio.gather(*[a.analyze() for a in agents])
    return aggregate_scores(results)
```

## Agent Communication

Agents share a common context object:
```json
{
  "url": "https://example.com",
  "html": "...",
  "headers": {...},
  "resources": [...],
  "cache": {...}
}
```

This avoids redundant page fetches—HTML is loaded once, then shared across all agents.

## Note

In this package version, agent definitions are embedded in the main orchestrator. Future modular releases will separate each agent into individual files for easier customization and third-party agent development.
