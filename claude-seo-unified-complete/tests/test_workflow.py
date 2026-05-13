#!/usr/bin/env python3
"""
Tests for claude-seo-unified workflow executor
Run with: pytest tests/test_workflow.py -v
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from run_skill_workflow import (
    detect_business_type,
    analyze_technical,
    analyze_content,
    analyze_schema,
    calculate_health_score,
    get_cache_path,
)


class TestBusinessTypeDetection:
    """Tests for business type detection"""
    
    def test_detect_saas(self):
        """Should detect SaaS business type"""
        html = """
        <html>
            <body>
                <a href="/pricing">Pricing</a>
                <a href="/features">Features</a>
                <p>Start your free trial today</p>
            </body>
        </html>
        """
        result = detect_business_type(html, "https://example.com")
        assert result == "saas"
    
    def test_detect_ecommerce(self):
        """Should detect e-commerce business type"""
        html = """
        <html>
            <body>
                <a href="/products">Products</a>
                <a href="/cart">Cart</a>
                <button>Add to Cart</button>
            </body>
        </html>
        """
        result = detect_business_type(html, "https://shop.example.com")
        assert result == "ecommerce"
    
    def test_detect_local(self):
        """Should detect local business type"""
        html = """
        <html>
            <body>
                <p>Phone: 555-1234</p>
                <p>Address: 123 Main St</p>
                <p>Hours: 9-5</p>
            </body>
        </html>
        """
        result = detect_business_type(html, "https://local.example.com")
        assert result == "local"
    
    def test_detect_unknown(self):
        """Should return unknown for unclear sites"""
        html = "<html><body><p>Some content</p></body></html>"
        result = detect_business_type(html, "https://example.com")
        assert result == "unknown"


class TestTechnicalAnalysis:
    """Tests for technical SEO analysis"""
    
    @pytest.fixture
    def sample_html(self):
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Page - Example Site</title>
            <meta name="description" content="This is a test page description for SEO testing purposes">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="canonical" href="https://example.com/test">
            <script type="application/ld+json">
            {"@type": "Organization", "name": "Test"}
            </script>
        </head>
        <body>
            <h1>Test Page Heading</h1>
            <p>Content here</p>
        </body>
        </html>
        """
    
    def test_analyze_technical_basic(self, sample_html):
        """Should analyze basic technical SEO factors"""
        result = analyze_technical(sample_html, "https://example.com", {})
        
        assert "score" in result
        assert "max_score" in result
        assert "checks" in result
        assert result["max_score"] == 22
    
    def test_detects_https(self, sample_html):
        """Should detect HTTPS correctly"""
        result = analyze_technical(sample_html, "https://example.com", {})
        assert result["checks"]["https"]["status"] == "pass"
    
    def test_detects_http_warning(self, sample_html):
        """Should warn about HTTP"""
        result = analyze_technical(sample_html, "http://example.com", {})
        assert result["checks"]["https"]["status"] == "fail"
    
    def test_detects_canonical(self, sample_html):
        """Should detect canonical tag"""
        result = analyze_technical(sample_html, "https://example.com", {})
        assert result["checks"]["canonicals"]["status"] == "pass"
    
    def test_detects_viewport(self, sample_html):
        """Should detect viewport meta tag"""
        result = analyze_technical(sample_html, "https://example.com", {})
        assert result["checks"]["mobile"]["status"] == "pass"


class TestContentAnalysis:
    """Tests for content quality analysis"""
    
    @pytest.fixture
    def sample_html(self):
        return """
        <!DOCTYPE html>
        <html>
        <head><title>Test</title></head>
        <body>
            <h1>Main Heading</h1>
            <h2>Subheading One</h2>
            <h2>Subheading Two</h2>
            <article>
                <p>This is a comprehensive article about SEO best practices and how to implement them effectively. 
                We will cover technical SEO, content quality, and link building strategies that work in 2026.
                Our team has years of experience helping businesses improve their search visibility.</p>
                <p>We recommend starting with a technical audit, then moving to content optimization.
                Link building should come last, once your foundation is solid.</p>
            </article>
            <a href="/about">About Us</a>
            <a href="/contact">Contact</a>
        </body>
        </html>
        """
    
    def test_analyze_content_basic(self, sample_html):
        """Should analyze content quality"""
        result = analyze_content(sample_html, "https://example.com")
        
        assert "score" in result
        assert "max_score" in result
        assert "word_count" in result
        assert result["max_score"] == 23
    
    def test_counts_words(self, sample_html):
        """Should count words correctly"""
        result = analyze_content(sample_html, "https://example.com")
        assert result["word_count"] > 50
    
    def test_detects_heading_structure(self, sample_html):
        """Should detect heading structure"""
        result = analyze_content(sample_html, "https://example.com")
        assert result["heading_structure"]["h1"] == 1
        assert result["heading_structure"]["h2"] == 2
    
    def test_calculates_eeat(self, sample_html):
        """Should calculate E-E-A-T scores"""
        result = analyze_content(sample_html, "https://example.com")
        assert "eeat" in result
        assert all(k in result["eeat"] for k in ["experience", "expertise", "authoritativeness", "trustworthiness"])


class TestSchemaAnalysis:
    """Tests for structured data analysis"""
    
    def test_detects_json_ld(self):
        """Should detect JSON-LD schema"""
        html = """
        <html>
        <head>
            <script type="application/ld+json">
            {"@context": "https://schema.org", "@type": "Organization", "name": "Test Corp"}
            </script>
        </head>
        <body></body>
        </html>
        """
        result = analyze_schema(html, "https://example.com")
        
        assert len(result["detected"]) == 1
        assert result["detected"][0]["type"] == "Organization"
        assert result["detected"][0]["valid"] is True
    
    def test_detects_multiple_schemas(self):
        """Should detect multiple schema types"""
        html = """
        <html>
        <head>
            <script type="application/ld+json">
            {"@type": "Organization", "name": "Test"}
            </script>
            <script type="application/ld+json">
            {"@type": "WebSite", "name": "Test Site"}
            </script>
        </head>
        <body></body>
        </html>
        """
        result = analyze_schema(html, "https://example.com")
        assert len(result["detected"]) == 2
    
    def test_handles_invalid_json(self):
        """Should handle invalid JSON-LD gracefully"""
        html = """
        <html>
        <head>
            <script type="application/ld+json">
            {invalid json here
            </script>
        </head>
        <body></body>
        </html>
        """
        result = analyze_schema(html, "https://example.com")
        assert result["detected"][0]["valid"] is False
    
    def test_scores_organization_schema(self):
        """Should score Organization schema highly"""
        html = """
        <html>
        <head>
            <script type="application/ld+json">
            {"@type": "Organization", "name": "Test"}
            </script>
        </head>
        <body></body>
        </html>
        """
        result = analyze_schema(html, "https://example.com")
        assert result["score"] >= 3  # Organization = 3 points


class TestHealthScore:
    """Tests for health score calculation"""
    
    def test_calculates_weighted_score(self):
        """Should calculate weighted health score"""
        results = {
            "technical": {"score": 18, "max_score": 22},
            "content": {"score": 20, "max_score": 23},
            "schema": {"score": 8, "max_score": 10},
            "performance": {"score": 7, "max_score": 10},
        }
        
        health_score, scores = calculate_health_score(results)
        
        assert 0 <= health_score <= 100
        assert isinstance(scores, dict)
    
    def test_handles_empty_results(self):
        """Should handle empty results"""
        health_score, scores = calculate_health_score({})
        assert health_score == 0
    
    def test_handles_missing_scores(self):
        """Should handle partial results"""
        results = {
            "technical": {"score": 10, "max_score": 22},
        }
        
        health_score, scores = calculate_health_score(results)
        assert health_score > 0


class TestCachePath:
    """Tests for cache path generation"""
    
    def test_generates_consistent_path(self):
        """Should generate consistent cache path for same URL"""
        path1 = get_cache_path("https://example.com/page")
        path2 = get_cache_path("https://example.com/page")
        
        assert path1 == path2
    
    def test_different_paths_for_different_urls(self):
        """Should generate different paths for different URLs"""
        path1 = get_cache_path("https://example.com/page1")
        path2 = get_cache_path("https://example.com/page2")
        
        assert path1 != path2


class TestIntegration:
    """Integration tests (require network)"""
    
    @pytest.mark.integration
    def test_audit_example_com(self):
        """Test full audit on example.com"""
        pytest.skip("Integration test - run manually with: pytest -m integration")
        
        from run_skill_workflow import run_audit
        result = run_audit("https://example.com", use_cache=False)
        
        assert "error" not in result
        assert "health_score" in result
        assert 0 <= result["health_score"] <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
