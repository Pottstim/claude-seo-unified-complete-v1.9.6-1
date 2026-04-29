# SEO Skills Directory

This directory contains the modular sub-skills for the unified SEO audit system. Each skill is a standalone MCP tool that can be called independently or orchestrated together.

## Structure

```
skills/
├── seo-audit/              # Main orchestrator skill
├── seo-technical/          # Technical SEO analysis
├── seo-content/            # Content quality & E-E-A-T
├── seo-schema/             # Schema.org markup
├── seo-performance/        # Core Web Vitals & performance
├── seo-images/             # Image optimization
├── seo-local/              # Local SEO (GMB, citations)
├── seo-competitor/         # Competitive analysis
├── seo-keyword/            # Keyword research
├── seo-backlink/           # Backlink analysis
├── seo-drift/              # Change detection & monitoring
└── seo-ai/                 # AI readiness (GEO, SGE, Perplexity)
```

## Skill Files

Each skill directory should contain:
- `skill.md` - MCP skill definition
- `agent.md` - Agent persona & instructions (if applicable)
- `config.yaml` - Skill-specific configuration
- `README.md` - Documentation

## Usage

Skills are automatically registered by the main orchestrator (`../SKILL.md`). Individual skills can also be called directly:

```bash
# Via orchestrator
/seo audit https://example.com

# Direct skill invocation
/seo-technical https://example.com
/seo-content https://example.com --check-eat
/seo-schema https://example.com --validate
```

## Development

To create a new skill:

1. Create directory: `mkdir skills/seo-newskill`
2. Add `skill.md` with MCP definition
3. Optional: add `agent.md` for specialized agent
4. Register in main `SKILL.md` orchestrator
5. Test: `antigravity skill register skills/seo-newskill/skill.md`

## Note

In this package version, skill directories are placeholders for the full unified system. The main orchestrator in `../SKILL.md` contains embedded logic for all 26 SEO workflows. Future versions will fully modularize each sub-skill.
