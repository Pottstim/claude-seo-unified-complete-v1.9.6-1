---
name: seo
description: "Comprehensive SEO analysis for any website. Full audits, technical SEO, content quality (E-E-A-T), schema markup, Core Web Vitals, AI search optimization (GEO), local SEO, drift monitoring, and strategic planning. Unified package combining claude-seo + codex-seo capabilities."
user-invokable: true
argument-hint: "[command] [url]"
license: MIT
version: "1.9.6-unified"
---

# SEO: Universal SEO Analysis Skill (Unified)

**Combined best-of-both from Claude SEO + Codex SEO**

Invoke naturally ("audit this site", "check schema") or with commands (`/seo audit <url>`).

## Quick Reference

| Command | Purpose |
|---------|---------|
| `/seo audit <url>` | Full site audit with parallel subagents |
| `/seo page <url>` | Deep single-page analysis |
| `/seo technical <url>` | Technical SEO (9 categories) |
| `/seo content <url>` | E-E-A-T content quality |
| `/seo schema <url>` | Schema detection & generation |
| `/seo images <url>` | Image optimization |
| `/seo sitemap <url>` | Sitemap analysis/generation |
| `/seo geo <url>` | AI search optimization |
| `/seo performance <url>` | Core Web Vitals |
| `/seo visual <url>` | Screenshots & mobile |
| `/seo local <url>` | Local SEO (GBP, NAP) |
| `/seo maps <cmd>` | Maps intelligence |
| `/seo google <cmd>` | Google APIs (GSC, PSI) |
| `/seo backlinks <url>` | Backlink analysis |
| `/seo cluster <keyword>` | Topic clustering |
| `/seo sxo <url>` | Search experience |
| `/seo drift baseline <url>` | Capture baseline |
| `/seo drift compare <url>` | Compare vs baseline |
| `/seo ecommerce <url>` | E-commerce SEO |
| `/seo plan <type>` | Strategic planning |
| `/seo flow <stage>` | FLOW framework |

## Orchestration Logic

**Full Audit (`/seo audit <url>`):**

1. **Detect business type** (SaaS, local, e-commerce, publisher, agency)
2. **Spawn core subagents** (parallel execution):
   - seo-technical (crawlability, indexability, CWV)
   - seo-content (E-E-A-T, readability)
   - seo-schema (structured data)
   - seo-sitemap (XML analysis)
   - seo-performance (Core Web Vitals)
   - seo-visual (screenshots, mobile)
   - seo-geo (AI search readiness)
   - seo-sxo (search experience)

3. **Conditional subagents** (based on detection):
   - seo-local (if local business detected)
   - seo-maps (if local + DataForSEO available)
   - seo-google (if Google API credentials exist)
   - seo-backlinks (if backlink APIs configured)
   - seo-cluster (if content strategy detected)
   - seo-ecommerce (if e-commerce detected)
   - seo-drift (if baseline exists)

4. **Unified report generation**:
   - SEO Health Score (0-100)
   - Prioritized action plan (Critical → High → Medium → Low)
   - Optional: Premium HTML/PDF report

## Shared Cache System

**Before any analysis**, check `.seo-cache/` for existing data:

```
.seo-cache/
  site-meta.json           # Domain, business type, industry
  audit-scores.json        # Prior audit summary
  pages/{url-slug}/
    page-analysis.json     # Page-level data
```

- **If found**: Use cached data (note timestamp)
- **If missing**: Gather fresh data
- **If user says "refresh"**: Ignore cache

## Industry Detection

Auto-detect from homepage signals:

| Type | Signals |
|------|---------|
| **SaaS** | /pricing, /features, /docs, "free trial" |
| **Local** | Phone, address, maps embed → suggest `/seo local` |
| **E-commerce** | /products, /cart, product schema |
| **Publisher** | /blog, /articles, article schema |
| **Agency** | /case-studies, /portfolio, client logos |

## Scoring Methodology

**SEO Health Score (0-100)** - Weighted aggregate:

| Category | Weight |
|----------|--------|
| Technical SEO | 22% |
| Content Quality | 23% |
| On-Page SEO | 20% |
| Schema/Structured Data | 10% |
| Performance (CWV) | 10% |
| AI Search Readiness | 10% |
| Images | 5% |

**Priority Levels:**
- **Critical**: Blocks indexing/causes penalties (fix NOW)
- **High**: Significantly impacts rankings (fix within 1 week)
- **Medium**: Optimization opportunity (fix within 1 month)
- **Low**: Nice to have (backlog)

## Quality Gates

Hard rules (see `references/quality-gates.md`):
- ⚠️ WARNING at 30+ location pages (require 60%+ unique content)
- 🛑 HARD STOP at 50+ location pages (require justification)
- ❌ Never recommend HowTo schema (deprecated Sept 2023)
- ⚠️ FAQ schema: Only gov/health for Google rich results (Aug 2023)
- ✅ Use INP for Core Web Vitals (FID deprecated Sept 2024)

## Core Features

### Technical SEO
- Robots.txt, sitemap, canonical checks
- Security headers, HTTPS, IndexNow
- Core Web Vitals (INP, LCP, CLS)
- JavaScript rendering risk
- Mobile optimization

### Content & E-E-A-T
- Experience, Expertise, Authoritativeness, Trustworthiness
- Helpful content signals
- Readability analysis
- Thin content detection

### Schema Markup
- JSON-LD detection (preferred)
- Validation against Google types
- Generation templates (30+ types)
- Deprecation awareness

### AI Search (GEO)
- Google AI Overviews optimization
- ChatGPT/Perplexity citation readiness
- llms.txt support
- Answer-first formatting

### Local SEO
- Google Business Profile (GBP) audit
- NAP consistency
- Citation analysis (tier-based)
- Review sentiment
- Multi-location support

### Drift Monitoring
- Capture baseline snapshots
- Compare deployments
- Track title/meta/schema changes
- Alert on regressions

## Sub-Skills (26 Total)

**Core workflows:**
1. seo-audit - Full site audit orchestrator
2. seo-page - Single-page deep dive
3. seo-technical - Technical SEO (9 categories)
4. seo-content - E-E-A-T & content quality
5. seo-schema - Schema detection/validation/generation
6. seo-images - Image optimization & SERP analysis
7. seo-sitemap - XML sitemap analysis/generation
8. seo-geo - AI search optimization (GEO)
9. seo-performance - Core Web Vitals measurement
10. seo-visual - Screenshots, mobile, above-fold
11. seo-plan - Strategic planning (templates)
12. seo-programmatic - Programmatic SEO at scale
13. seo-competitor-pages - Comparison page generation
14. seo-hreflang - International SEO (i18n)
15. seo-local - Local SEO (GBP, NAP, citations)
16. seo-maps - Maps intelligence (geo-grid, reviews)
17. seo-google - Google APIs (GSC, PSI, CrUX, GA4)
18. seo-backlinks - Backlink profile analysis
19. seo-cluster - Semantic topic clustering
20. seo-sxo - Search experience optimization
21. seo-drift - Change monitoring (baseline/compare)
22. seo-ecommerce - E-commerce SEO intelligence
23. seo-flow - FLOW framework (41 prompts)

**Extensions (optional):**
24. seo-firecrawl - Full-site crawling (Firecrawl MCP)
25. seo-dataforseo - Live SERP data (DataForSEO MCP)
26. seo-image-gen - AI image generation (Gemini/Banana)

## Headless Execution

Run programmatically via scripts:

```bash
# Single workflow
python scripts/run_skill_workflow.py --skill seo-technical <url> --json

# Full smoke suite
python scripts/run_api_smoke_suite.py <url> --json

# Verify environment
python scripts/verify_environment.py --target <url> --json
```

Output goes to:
- `output/` - Reports (MD, JSON, HTML, PDF)
- `.seo-cache/` - Shared evidence cache

## Extensions Setup

**DataForSEO** (live SERP, keywords, backlinks):
```bash
./extensions/dataforseo/install.sh
```

**Google APIs** (GSC, PageSpeed, CrUX, GA4):
```bash
python scripts/google_auth.py --setup
```

**Firecrawl** (JS-rendered crawling):
```bash
./extensions/firecrawl/install.sh
```

**Banana** (AI image generation):
```bash
./extensions/banana/install.sh
```

## Error Handling

| Scenario | Action |
|----------|--------|
| Unrecognized command | List available commands, suggest closest match |
| URL unreachable | Report error, don't guess content |
| Sub-skill fails | Report partial results, note which failed |
| Ambiguous business type | Present top 2 types with signals, ask user |

## Reference Files

Load on-demand (don't load all at startup):
- `references/cwv-thresholds.md` - Core Web Vitals
- `references/schema-types.md` - Supported schema types
- `references/eeat-framework.md` - E-E-A-T criteria (Sept 2025)
- `references/quality-gates.md` - Content length minimums
- `references/local-seo-signals.md` - Local ranking factors
- `references/maps-*.md` - Maps intelligence references

## Credits

Combined from:
- [claude-seo](https://github.com/AgriciDaniel/claude-seo)
- [codex-seo](https://github.com/AgriciDaniel/codex-seo)

Built by [@AgriciDaniel](https://github.com/AgriciDaniel)

## License

MIT License - see LICENSE file
