# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- PostgreSQL database support for persistent storage
- Redis caching layer for rate limiting and sessions
- Load testing suite with Locust
- Prometheus metrics endpoint (`/metrics`)
- OpenTelemetry tracing support
- API versioning (`/api/v1/`)
- Request ID tracking for debugging
- Circuit breaker pattern for external API calls
- Automatic retry with exponential backoff

### Changed
- Migrated from file-based cache to Redis
- Improved error handling with custom exceptions
- Enhanced logging with request context

### Security
- Added HSTS and CSP headers
- Implemented request signing for internal APIs
- Added API key rotation support

## [1.9.8] - 2025-05-13

### Added
- Business Tool Mode with web dashboard (`dashboard/index.html`)
- PDF report generation (`scripts/pdf_report.py`)
- REST API server with authentication and rate limiting
- 26 modular SEO skill workflows
- Provider abstraction layer for LLMs, analytics, SERP APIs
- Mix-and-match configuration examples
- Docker deployment support
- VPS one-click deployment script

### Changed
- Reorganized repository structure (moved files to root)
- Split requirements into core/optional
- Added flexible provider system with open-source alternatives

### Fixed
- Fixed `total_weight` bug in health score calculation
- Fixed internal link detection regex
- Fixed `analyze_images()` None handling
- Fixed missing workflow error handling (exit code 1)
- Removed dead code and unused imports

### Security
- Added SSRF protection (blocks localhost, private IPs, AWS metadata)
- Added rate limiting on API endpoints
- Added Bearer token authentication
- Added security headers (X-Frame-Options, X-Content-Type-Options)

## [1.9.7] - 2025-05-13

### Fixed
- Fixed all analyzer functions now properly return scores
- Fixed phantom category scores in health calculation
- Fixed E-E-A-T keyword matching (narrowed scope)
- Fixed heading extraction to use `<article>` and `<main>` only
- Added missing onpage, AI readiness, and images analyzers

## [1.9.6] - 2025-05-12

### Added
- Initial unified release combining claude-seo and codex-seo
- 26 SEO analysis workflows
- Technical SEO analyzer
- Content quality analyzer (E-E-A-T)
- Schema markup analyzer
- Core Web Vitals analyzer
- GEO/AI search optimization
- Local SEO analyzer
- Competitor analysis
- SERP analysis
- Drift monitoring

### Changed
- Unified skill definition format (SKILL.md)
- Added agent definitions in agents/ directory
- Created reference documentation

## [1.0.0] - 2025-01-15

### Added
- Initial release
- Basic SEO audit workflow
- Claude Desktop integration via MCP

[Unreleased]: https://github.com/Pottstim/claude-seo-unified-complete-v1.9.6-1/compare/v1.9.8...HEAD
[1.9.8]: https://github.com/Pottstim/claude-seo-unified-complete-v1.9.6-1/compare/v1.9.7...v1.9.8
[1.9.7]: https://github.com/Pottstim/claude-seo-unified-complete-v1.9.6-1/compare/v1.9.6...v1.9.7
[1.9.6]: https://github.com/Pottstim/claude-seo-unified-complete-v1.9.6-1/compare/v1.0.0...v1.9.6
[1.0.0]: https://github.com/Pottstim/claude-seo-unified-complete-v1.9.6-1/releases/tag/v1.0.0
