# Commands Reference - Claude SEO Unified

Complete reference for all 26 SEO workflows.

## Core Auditing

### `/seo audit <url>`
**Full website audit with parallel subagent delegation**

Runs 8+ specialists in parallel, auto-detects business type, generates unified report with SEO Health Score (0-100) and prioritized action plan.

**Example:**
```
/seo audit https://example.com
```

**Output:**
- SEO Health Score (0-100)
- Critical issues
- High priority optimizations
- Medium priority improvements
- Low priority suggestions
- Optional: Premium HTML/PDF report

---

### `/seo page <url>`
**Deep single-page analysis**

Comprehensive on-page SEO audit for a specific URL.

**Analyzes:**
- Title tag optimization
- Meta description
- Heading structure (H1-H6)
- Content quality & length
- Internal/external links
- Image optimization
- Schema markup
- Page speed signals

---

## Technical SEO

### `/seo technical <url>`
**Technical SEO audit (9 categories)**

**Categories:**
1. Crawlability (robots.txt, XML sitemap)
2. Indexability (meta robots, canonical)
3. Security (HTTPS, security headers)
4. URL structure (clean URLs, parameters)
5. Mobile optimization (viewport, mobile-friendly)
6. Core Web Vitals (INP, LCP, CLS)
7. Structured data (JSON-LD detection)
8. JavaScript rendering (hydration risks)
9. IndexNow integration

---

## Content & Quality

### `/seo content <url>`
**E-E-A-T and content quality analysis**

Evaluates content against Google's Quality Rater Guidelines (September 2025 update).

**E-E-A-T Factors:**
- **Experience**: First-hand knowledge signals
- **Expertise**: Author credentials, depth of coverage
- **Authoritativeness**: Industry recognition, citations
- **Trustworthiness**: Contact info, transparency, security

**Additional Analysis:**
- Readability (Flesch score)
- Content length vs competitors
- Thin content detection
- Keyword density (natural usage)
- Internal linking opportunities

---

## Schema & Structured Data

### `/seo schema <url>`
**Schema detection, validation, and generation**

**Detects:**
- JSON-LD (preferred)
- Microdata
- RDFa

**Validates:**
- Google's supported types
- Required properties
- Nested structures
- Deprecation warnings

**Generates:**
- Organization
- LocalBusiness (+ 100+ subtypes)
- Product
- Article
- BreadcrumbList
- FAQ (with restrictions notice)
- Event
- VideoObject
- And 20+ more types

---

## Performance

### `/seo performance <url>`
**Core Web Vitals and performance analysis**

**Metrics (Current as of 2024):**
- **INP** (Interaction to Next Paint): Target < 200ms
- **LCP** (Largest Contentful Paint): Target < 2.5s
- **CLS** (Cumulative Layout Shift): Target < 0.1
- **FCP** (First Contentful Paint)
- **TTFB** (Time to First Byte)

**Note:** FID was deprecated and removed September 2024.

---

## Images

### `/seo images <url>`
**Image optimization analysis**

**Analyzes:**
- Alt text quality & presence
- File size optimization
- Format recommendations (WebP/AVIF)
- Responsive images (srcset)
- Lazy loading implementation
- CLS prevention
- Image SERP opportunities

**Provides:**
- Optimization priorities
- Compression recommendations
- Alt text suggestions
- Image sitemap guidance

---

## Sitemaps

### `/seo sitemap <url>`
**XML sitemap analysis**

Discovers and validates XML sitemaps.

**Checks:**
- Sitemap location (robots.txt, /sitemap.xml)
- URL count and structure
- Change frequency settings
- Priority values
- HTTP status codes
- Sitemap index support

### `/seo sitemap generate`
**Generate new sitemap**

Creates XML sitemap with industry-specific templates.

**Templates:**
- SaaS (features, docs, pricing)
- E-commerce (products, categories)
- Local business (services, locations)
- Publisher (articles, categories, authors)
- Agency (case studies, services)

---

## AI Search (GEO)

### `/seo geo <url>`
**Generative Engine Optimization**

Optimize for AI-powered search engines.

**Targets:**
- Google AI Overviews
- ChatGPT web search
- Perplexity
- Bing Copilot

**Analyzes:**
- AI crawler access (GPTBot, Google-Extended)
- llms.txt support
- Citation-friendly formatting
- Answer-first content structure
- Entity clarity
- Fact-checking signals

---

## Local SEO

### `/seo local <url>`
**Local SEO analysis**

**Analyzes:**
- Google Business Profile signals
- NAP (Name, Address, Phone) consistency
- Citation quality & distribution
- Review sentiment & response rate
- Local schema markup
- Map pack ranking factors
- Multi-location support

**Citation Tiers:**
- Tier 1: Google, Apple, Bing, Yelp
- Tier 2: Industry-specific directories
- Tier 3: Local chambers, BBB

---

### `/seo maps <command>`
**Maps intelligence workflows**

#### `/seo maps geo-grid <business-name> <location>`
7x7 geo-grid rank tracking around a location.

#### `/seo maps gbp-audit <place-id>`
25-field GBP profile audit.

#### `/seo maps reviews <place-id>`
Review sentiment analysis and response recommendations.

#### `/seo maps competitors <business-name> <radius-miles>`
Competitor mapping within radius.

**Requires:** DataForSEO extension for live data.

---

## Google APIs

### `/seo google <command>`

#### `/seo google pagespeed <url>`
PageSpeed Insights + CrUX field data.

#### `/seo google gsc <url>`
Search Console: top queries, impressions, CTR, URL inspection.

#### `/seo google indexing <url>`
Notify Google of new/updated/removed URLs.

#### `/seo google ga4 <property-id>`
Organic traffic, top landing pages, device/country breakdown.

#### `/seo google report <type>`
Generate PDF report:
- `cwv-audit` - Core Web Vitals audit
- `gsc-performance` - Search Console performance
- `full` - Complete SEO + Google APIs report

**Setup:**
```bash
python scripts/google_auth.py --setup
```

---

## Backlinks

### `/seo backlinks <url>`
**Backlink profile analysis**

**Free sources:**
- Moz Link Explorer (domain-level)
- Bing Webmaster Tools
- Common Crawl (domain discovery)

**Premium (DataForSEO):**
- Referring domains count
- Domain Authority / Page Authority
- Anchor text distribution
- Toxic link detection
- New/lost backlinks
- Competitor backlink gaps

---

## Content Strategy

### `/seo cluster <seed-keyword>`
**SERP-based semantic clustering**

Builds topic clusters from SERP analysis.

**Generates:**
- Hub page recommendations
- Spoke content ideas
- Internal linking map
- Content gap analysis
- Search intent grouping

**Example:**
```
/seo cluster "AI marketing automation"
```

**Output:**
- Pillar content (hub)
- Supporting articles (spokes)
- Keyword groupings
- Content briefs

---

### `/seo sxo <url>`
**Search Experience Optimization**

Analyzes page-type fit and user experience.

**Evaluates:**
- Page type detection (homepage, product, article, etc.)
- User story alignment
- Persona fit scoring
- Intent mismatch detection
- UX friction points
- Conversion path clarity

---

## Change Monitoring

### `/seo drift baseline <url>`
**Capture SEO baseline**

Takes snapshot of critical SEO signals before changes.

**Captures:**
- Title tags
- Meta descriptions
- H1-H6 headings
- Canonical URLs
- Schema markup
- Robots directives
- Internal links
- Content hashes

### `/seo drift compare <url>`
**Compare against baseline**

Detects SEO changes since baseline.

**Reports:**
- Changed elements
- Missing elements
- New elements
- Regression severity

### `/seo drift history <url>`
**Show drift history**

Timeline of all baselines and comparisons.

---

## E-commerce

### `/seo ecommerce <url>`
**E-commerce SEO intelligence**

**Analyzes:**
- Product schema (Product, Offer, AggregateRating)
- Marketplace visibility signals
- Category page optimization
- Product description quality
- Image optimization for products
- Review schema implementation
- Shopping feed readiness

---

## Planning

### `/seo plan <business-type>`
**Strategic SEO planning**

**Business types:**
- `saas` - SaaS platform strategy
- `local` - Local service business
- `ecommerce` - E-commerce store
- `publisher` - Content publisher/blog
- `agency` - Marketing/digital agency

**Generates:**
- Competitive analysis framework
- Content pillar strategy
- Site architecture plan
- 4-phase implementation roadmap
- KPI tracking recommendations

---

### `/seo programmatic <url>`
**Programmatic SEO analysis**

For sites generating pages at scale from data.

**Analyzes:**
- Existing programmatic pages
- Thin content risk
- Cannibalization detection
- URL pattern quality
- Template structure

**Plans:**
- URL patterns
- Internal linking automation
- Canonical strategy
- Quality gates
- Index bloat prevention

**Quality gates:**
- ⚠️ WARNING: 100+ pages
- 🛑 HARD STOP: 500+ pages without audit

---

### `/seo competitor-pages <url>`
**Competitor comparison page generator**

Creates "X vs Y" and "Alternatives to X" pages.

**Features:**
- Structured comparison tables
- Feature matrices
- Product schema with AggregateRating
- CTA optimization
- Fairness guidelines
- Keyword targeting for comparison queries

---

## International SEO

### `/seo hreflang <url>`
**Hreflang validation and generation**

**Validates:**
- Self-referencing tags
- Return tags (bidirectional)
- ISO code validation (639-1 + 3166-1)
- x-default implementation
- HTTP/HTTPS consistency
- Cross-domain support

**Generates:**
- HTML `<link>` tags
- HTTP header format
- XML sitemap format

---

## FLOW Framework

### `/seo flow <stage> [url|topic]`
**Evidence-led SEO prompts**

**Stages:**
- `find` - Opportunity discovery
- `leverage` - Content gaps & quick wins
- `optimize` - Technical & on-page optimization
- `win` - Conversion & user experience
- `local` - Local SEO tactics

41 AI prompts total (CC BY 4.0 license).

---

## Extensions

### `/seo firecrawl <command>`
**Full-site crawling via Firecrawl**

#### `/seo firecrawl crawl <url>`
JS-rendered full-site crawl.

#### `/seo firecrawl map <url>`
Site URL discovery and mapping.

**Setup:**
```bash
./extensions/firecrawl/install.sh
```

---

### `/seo dataforseo <command>`
**Live SEO data via DataForSEO**

22 commands across 9 API modules:

#### SERP
```
/seo dataforseo serp <keyword>
```

#### Keywords
```
/seo dataforseo keywords <seed>
/seo dataforseo volume <keyword>
```

#### Backlinks
```
/seo dataforseo backlinks <domain>
```

#### On-Page
```
/seo dataforseo onpage <url>
```

#### Content
```
/seo dataforseo content <topic>
```

#### AI Visibility
```
/seo dataforseo ai-mentions <brand>
/seo dataforseo ai-scrape <brand>
```

**Setup:**
```bash
./extensions/dataforseo/install.sh
```

---

### `/seo image-gen <use-case> <description>`
**AI image generation for SEO**

**Use cases:**
- `og` - Open Graph preview images
- `hero` - Hero section images
- `product` - Product photography
- `infographic` - Data visualizations
- `thumbnail` - Video/article thumbnails
- `batch` - Multiple variations

**Example:**
```
/seo image-gen og "Professional SaaS dashboard with clean UI"
/seo image-gen hero "AI-powered content creation workspace"
/seo image-gen batch "Modern office workspace" 3
```

**Setup:**
```bash
./extensions/banana/install.sh
```

---

## Headless/API Usage

Run any workflow programmatically:

```bash
# Single workflow
python scripts/run_skill_workflow.py --skill seo-technical https://example.com --json

# Full smoke suite (all 26 workflows)
python scripts/run_api_smoke_suite.py https://example.com --json

# Verify environment readiness
python scripts/verify_environment.py --target https://example.com --json
```

**Output locations:**
- `output/` - Reports (Markdown, JSON, HTML, PDF)
- `.seo-cache/` - Shared evidence cache

---

## Natural Language

You can also use natural language instead of commands:

```
"Do a full SEO audit on my website https://example.com"
"Check the schema markup on this page"
"Analyze Core Web Vitals for our homepage"
"Create an SEO strategy for a local dentist office"
"Compare SEO signals against our baseline"
```

The orchestrator will route to the appropriate specialist workflow.

---

## Getting Help

```
/seo help
```

Or ask naturally:
```
"What SEO commands are available?"
"How do I check my site's technical SEO?"
"Explain E-E-A-T analysis"
```
