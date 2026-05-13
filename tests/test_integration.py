#!/usr/bin/env python3
"""
Integration tests for claude-seo-unified
Run with: pytest tests/test_integration.py -v -m integration
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


@pytest.mark.integration
class TestLiveAudit:
    """Tests against live websites"""
    
    def test_audit_example_com(self):
        """Test audit against example.com"""
        from run_skill_workflow import run_audit
        
        result = run_audit("https://example.com", use_cache=False)
        
        assert "error" not in result
        assert "health_score" in result
        assert result["health_score"] > 0
    
    def test_technical_analysis_example_com(self):
        """Test technical analysis against example.com"""
        from run_skill_workflow import run_technical
        
        result = run_technical("https://example.com")
        
        assert "error" not in result
        assert "score" in result
    
    def test_schema_analysis_example_com(self):
        """Test schema analysis against example.com"""
        from run_skill_workflow import run_schema
        
        result = run_schema("https://example.com")
        
        assert "error" not in result
        assert "detected" in result


@pytest.mark.integration
class TestDriftWorkflow:
    """Tests for drift monitoring workflow"""
    
    def test_baseline_and_compare(self):
        """Test baseline capture and comparison"""
        from run_skill_workflow import run_drift_baseline, run_drift_compare
        import tempfile
        import os
        
        # Change to temp directory for isolation
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            # Capture baseline
            baseline = run_drift_baseline("https://example.com")
            assert "error" not in baseline
            assert "baseline_file" in baseline
            
            # Compare (should be identical)
            compare = run_drift_compare("https://example.com")
            assert "error" not in compare
            assert "delta" in compare
            assert compare["delta"] == 0  # Same page, no change


@pytest.mark.integration
class TestOutputFormats:
    """Tests for different output formats"""
    
    def test_json_output(self):
        """Test JSON output format"""
        from run_skill_workflow import run_audit
        import json
        
        result = run_audit("https://example.com", use_cache=False)
        json_str = json.dumps(result)
        
        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed["url"] == "https://example.com"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
