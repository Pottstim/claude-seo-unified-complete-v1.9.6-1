# Makefile for claude-seo-unified

.PHONY: help install test lint clean api dashboard docker-build docker-run

help:
	@echo "Claude SEO Unified - Available commands:"
	@echo ""
	@echo "  make install       Install dependencies"
	@echo "  make test          Run tests"
	@echo "  make lint          Run linter"
	@echo "  make api           Start REST API server"
	@echo "  make dashboard     Serve the business dashboard"
	@echo "  make analyze URL=  Analyze a URL (CLI)"
	@echo "  make report URL=   Generate PDF report for URL"
	@echo "  make docker-build  Build Docker image"
	@echo "  make docker-run    Run Docker container"
	@echo "  make clean         Clean cache and output files"
	@echo ""

install:
	pip install -r requirements.txt
	playwright install

test:
	pytest tests/ -v

lint:
	pylint scripts/ --ignore-patterns="providers"

api:
	python scripts/api_server.py

dashboard:
	@echo "Serving dashboard at http://localhost:8000"
	@echo "Press Ctrl+C to stop"
	cd dashboard && python -m http.server 8000

docker-build:
	docker build -f deploy/Dockerfile -t claude-seo-unified:latest .

docker-run:
	docker run -p 5000:5000 \
		-e SEO_API_KEY=your-api-key \
		claude-seo-unified:latest

# Run audit from CLI
audit:
ifndef URL
	$(error URL is required. Use: make audit URL=https://example.com)
endif
	python scripts/run_skill_workflow.py audit --url $(URL)

technical:
ifndef URL
	$(error URL is required. Use: make technical URL=https://example.com)
endif
	python scripts/run_skill_workflow.py technical --url $(URL)

content:
ifndef URL
	$(error URL is required. Use: make content URL=https://example.com)
endif
	python scripts/run_skill_workflow.py content --url $(URL)

schema:
ifndef URL
	$(error URL is required. Use: make schema URL=https://example.com)
endif
	python scripts/run_skill_workflow.py schema --url $(URL)

drift-baseline:
ifndef URL
	$(error URL is required. Use: make drift-baseline URL=https://example.com)
endif
	python scripts/run_skill_workflow.py drift-baseline --url $(URL)

drift-compare:
ifndef URL
	$(error URL is required. Use: make drift-compare URL=https://example.com)
endif
	python scripts/run_skill_workflow.py drift-compare --url $(URL)
