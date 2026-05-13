# Makefile for claude-seo-unified

.PHONY: help install test lint clean api docker-build docker-run

help:
	@echo "Claude SEO Unified - Available commands:"
	@echo ""
	@echo "  make install        Install dependencies"
	@echo "  make test           Run tests"
	@echo "  make test-integration Run integration tests"
	@echo "  make lint           Run linters"
	@echo "  make clean          Clean build artifacts"
	@echo "  make api            Start API server locally"
	@echo "  make docker-build   Build Docker image"
	@echo "  make docker-run     Run Docker container"
	@echo "  make audit URL=...  Run SEO audit"
	@echo ""

install:
	pip install -r requirements.txt
	playwright install chromium

install-core:
	pip install -r requirements-core.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-optional.txt
	pre-commit install

test:
	pytest tests/test_workflow.py -v

test-integration:
	pytest tests/test_integration.py -v -m integration

test-all:
	pytest tests/ -v

lint:
	black --check scripts/ tests/
	ruff scripts/ tests/
	mypy scripts/

format:
	black scripts/ tests/

clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache
	rm -rf *.egg-info build dist
	rm -rf .seo-cache/*
	rm -rf screenshots/*

api:
	python scripts/api_server.py

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
