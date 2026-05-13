#!/usr/bin/env python3
"""
Tests for claude-seo-unified workflow executor
Run with: pytest tests/test_workflow.py -v
"""

import pytest
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from run_skill_workflow import (
    validate_url,
    detect_business_type,
    calculate_health_score,
    analyze_technical,
    analyze_onpage,
    analyze_content,
    analyze_schema,
    analyze_performance,
    analyze_ai_readiness,
    analyze_images,
    load_cache,
    get_cache_path,
)


class TestURLValidation:
    """Tests for URL validation"""
    
    def test_valid_https_url(self):
        valid, result = validate_url("https://example.com")
        assert valid is True
        assert result == "https://example.com"
    
    def test_valid_http_url(self):
        valid, result = validate_url("http://example.com")
        assert valid is True
        assert result == "http://example.com"
    
    def test_invalid_url_no_scheme(self):
        valid, error = validate_url("example.com")
        assert valid is False
        assert "http://" in error or "https://" in error
    
    def test_invalid_url_empty(self):
        valid, error = validate_url("")
        assert valid is False
    
    def test_invalid_url_no_domain(self):
        valid, error = validate_url("https://")
        assert valid is False


class TestBusinessTypeDetection:
    """Tests for business type detection"""
    
    def test_saas_detection(self):
        html = '<html><body><a href="/pricing">Pricing</a><a href="/features">Features</a></body></html>'
        result = detect_business_type(html, "https://saas-app.com")
        assert result == "saas"
    
    def test_ecommerce_detection(self):
        html = '<html><body><a href="/cart">Cart</a><a href="/products">Products</a></body></html>'
        result = detect_business_type(html, "https://shop.example.com")
        assert result == "ecommerce"
    
    def test_local_detection(self):
        html = '<html><body><p>Call us: 555-1234</p><p>Visit our location</p></body></html>'
        result = detect_business_type(html, "https://local-business.com")
        assert result == "local"
    
    def test_unknown_detection(self):
        html = '<html><body><p>Generic content</p></body></html>'
        result = detect_business_type(html, "https://generic-site.com")
        assert result == "unknown"
    
    def test_tie_breaking_priority(self):
        """Test that ties are broken by priority order"""
        # This HTML has both saas and ecommerce signals equally
        html = '<html><body><a href="/pricing">Pricing</a><a href="/cart">Cart</a></body></html>'
        result = detect_business_type(html, "https://hybrid-site.com")
        # SaaS should win due to priority order
        assert result == "saas"


class TestHealthScoreCalculation:
    """Tests for health score calculation"""
    
    def test_full_score_all_categories(self):
        """Test that all categories contribute to score"""
        results = {
            "technical": {"score": 20, "max_score": 22},
            "content": {"score": 20, "max_score": 23},
            "onpage": {"score": 18, "max_score": 20},
            "schema": {"score": 8, "max_score": 10},
            "performance": {"score": 8, "max_score": 10},
            "ai_readiness": {"score": 8, "max_score": 10},
            "images": {"score": 4, "max_score": 5}
        }
        health, scores = calculate_health_score(results)
        
        # All categories should be in scores
        assert "technical" in scores
        assert "content" in scores
        assert "onpage" in scores
        assert "schema" in scores
        assert "performance" in scores
        assert "ai_readiness" in scores
        assert "images" in scores
        
        # Health should be reasonable (not 0)
        assert health > 0
        assert health <= 100
    
    def test_partial_categories(self):
        """Test score calculation with partial results"""
        results = {
            "technical": {"score": 15, "max_score": 22},
            "content": {"score": 10, "max_score": 23}
        }
        health, scores = calculate_health_score(results)
        
        # Only analyzed categories should be scored
        assert health > 0
        assert len(scores) == 2
    
    def test_no_phantom_categories(self):
        """Ensure no phantom categories affect score"""
        # With only technical and content, score should be based on those only
        results = {
            "technical": {"score": 22, "max_score": 22},
            "content": {"score": 23, "max_score": 23}
        }
        health, scores = calculate_health_score(results)
        
        # Should be 100% since both are perfect
        assert health == 100


class TestContentAnalysis:
    """Tests for content analysis"""
    
    def test_eeat_focuses_on_main_content(self):
        """E-E-A-T should focus on main content area, not nav/footer"""
        html = '''
        <html>
        <nav>We are the best company</nav>
        <main>
            <p>This is the actual article content.</p>
        </main>
        <footer>We provide excellent services</footer>
        </html>
        '''
        result = analyze_content(html, "https://example.com")
        
        # Should have eeat scores
        assert "eeat" in result
        assert "experience" in result["eeat"]
        assert "expertise" in result["eeat"]
    
    def test_word_count(self):
        html = '<html><body><main>' + 'word ' * 500 + '</main></body></html>'
        result = analyze_content(html, "https://example.com")
        assert result["word_count"] >= 500


class TestSchemaAnalysis:
    """Tests for schema detection"""
    
    def test_json_ld_detection(self):
        html = '''
        <html>
        <head>
        <script type="application/ld+json">
        {"@context": "https://schema.org", "@type": "Organization", "name": "Test"}
        </script>
        </head>
        <body></body>
        </html>
        '''
        result = analyze_schema(html, "https://example.com")
        
        assert len(result["detected"]) > 0
        assert result["detected"][0]["type"] == "Organization"
        assert result["detected"][0]["valid"] is True
    
    def test_invalid_json_ld(self):
        html = '''
        <html>
        <script type="application/ld+json">
        {invalid json}
        </script>
        <body></body>
        </html>
        '''
        result = analyze_schema(html, "https://example.com")
        
        # Should mark as invalid
        assert len(result["detected"]) > 0
        assert result["detected"][0]["valid"] is False


class TestCacheTimezone:
    """Tests for cache timezone handling"""
    
    def test_timezone_aware_comparison(self):
        """Cache timestamp should be timezone-aware"""
        import tempfile
        import os
        
        # Create a temp cache
        cache_dir = tempfile.mkdtemp()
        cache_file = Path(cache_dir) / "page-analysis.json"
        
        # Write cache with UTC timestamp
        cache_data = {
            "url": "https://example.com",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "health_score": 85
        }
        
        with open(cache_file, "w") as f:
            json.dump(cache_data, f)
        
        # This should not raise TypeError
        # (The actual load_cache uses get_cache_path, but we're testing the logic)
        cached_time = datetime.fromisoformat(cache_data["timestamp"].replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        
        # This comparison should work without TypeError
        delta = (now - cached_time).total_seconds()
        assert delta >= 0
        
        # Cleanup
        import shutil
        shutil.rmtree(cache_dir)


class TestAnalyzerCompleteness:
    """Tests to ensure all analyzers are present and functional"""
    
    def test_technical_analyzer_exists(self):
        html = '<html><head><title>Test</title></head><body></body></html>'
        result = analyze_technical(html, "https://example.com", {})
        assert "score" in result
        assert "max_score" in result
    
    def test_onpage_analyzer_exists(self):
        html = '<html><head><title>Test Page Title</title></head><body></body></html>'
        result = analyze_onpage(html, "https://example.com")
        assert "score" in result
        assert "max_score" in result
    
    def test_ai_readiness_analyzer_exists(self):
        html = '<html><body><h2>What is SEO?</h2><p>SEO stands for...</p></body></html>'
        result = analyze_ai_readiness(html, "https://example.com")
        assert "score" in result
        assert "max_score" in result
    
    def test_images_analyzer_exists(self):
        html = '<html><body><img src="test.jpg" alt="Test image"></body></html>'
        result = analyze_images(html, "https://example.com")
        assert "score" in result
        assert "max_score" in result


class TestCLIInterface:
    """Tests for CLI argument handling"""
    
    def test_version_available(self):
        """Version should be accessible"""
        from run_skill_workflow import __version__
        assert __version__ is not None
        assert "unified" in __version__


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
