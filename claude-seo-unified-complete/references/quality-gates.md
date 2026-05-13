# Quality Gates for SEO Recommendations

## Hard Stops

These conditions require explicit justification before proceeding:

### Location Page Scale
- ⚠️ **WARNING** at 30+ location pages: Require 60%+ unique content per page
- 🛑 **HARD STOP** at 50+ location pages: Require business justification and content plan

### Schema Deprecations
- ❌ **NEVER** recommend HowTo schema (deprecated September 2023)
- ⚠️ **CAUTION** with FAQ schema: Only for gov/health sites for Google rich results (August 2023)

## Deprecated Elements

| Element | Status | Alternative |
|---------|--------|-------------|
| HowTo Schema | Deprecated Sept 2023 | Use Article/VideoObject |
| FAQ Schema | Limited Aug 2023 | Use for gov/health only |
| FID Metric | Replaced Sept 2024 | Use INP |
| `changefreq` | Ignored by Google | Remove from sitemaps |
| `priority` in sitemaps | Ignored by Google | Remove from sitemaps |

## Content Minimums

| Page Type | Minimum Words |
|-----------|---------------|
| Homepage | 300 |
| Service page | 500 |
| Blog post | 800 |
| Product page | 300 |
| Location page | 400 |

## Core Web Vitals (2024)

| Metric | Good | Warning | Fail |
|--------|------|---------|------|
| INP | < 200ms | 200-500ms | > 500ms |
| LCP | < 2.5s | 2.5-4.0s | > 4.0s |
| CLS | < 0.1 | 0.1-0.25 | > 0.25 |

Note: INP replaced FID in March 2024.

## Priority Levels

### Critical (Fix Now)
- Blocks indexing
- Causes penalties
- Security issues
- Broken critical pages

### High (Fix Within 1 Week)
- Significantly impacts rankings
- Major UX issues
- Missing essential elements

### Medium (Fix Within 1 Month)
- Optimization opportunities
- Minor UX issues
- Enhancement potential

### Low (Backlog)
- Nice to have
- Minimal impact
- Future consideration

## Recommendation Guidelines

1. **Always prioritize by impact** - Critical > High > Medium > Low
2. **Provide actionable fixes** - Not just "improve X" but "do Y to improve X"
3. **Include expected impact** - "+2 health score" or "+5% traffic"
4. **Reference documentation** - Link to relevant guidelines

## Safety Rules

1. Never recommend cloaking or hidden content
2. Never suggest buying links
3. Never recommend keyword stuffing
4. Always prefer user experience over SEO tricks
5. When in doubt, follow Google's guidelines
