#!/usr/bin/env python3
"""
Headless workflow executor for claude-seo-unified
Enables deterministic execution in CI/CD, cron, or API mode
"""

import sys
import os
import json
import argparse
import asyncio
import aiohttp
import hashlib
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


@dataclass
class AuditResult:
    """Structured audit result"""
    url: str
    timestamp: str
    health_score: int
    scores: Dict[str, int]
    issues: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    business_type: Optional[str] = None


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """Load YAML config"""
    if not YAML_AVAILABLE:
        logger.warning("PyYAML not available, using defaults")
        return {}
    
    path = Path(config_path)
    if not path.exists():
        logger.warning(f"Config file not found: {config_path}")
        return {}
    
    with open(path) as f:
        return yaml.safe_load(f)


def get_cache_path(url: str) -> Path:
    """Get cache directory for a URL"""
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    slug = re.sub(r'[^a-zA-Z0-9-]', '-', urlparse(url).netloc)
    return Path(f".seo-cache/pages/{slug}-{url_hash}")


def load_cache(url: str) -> Optional[Dict[str, Any]]:
    """Load cached analysis if available"""
    cache_path = get_cache_path(url) / "page-analysis.json"
    if cache_path.exists():
        with open(cache_path) as f:
            data = json.load(f)
            # Check if cache is recent (less than 24 hours)
            cached_time = datetime.fromisoformat(data.get("timestamp", "2000-01-01"))
            if (datetime.now(timezone.utc) - cached_time).total_seconds() < 86400:
                return data
    return None


def save_cache(url: str, data: Dict[str, Any]) -> None:
    """Save analysis to cache"""
    cache_path = get_cache_path(url)
    cache_path.mkdir(parents=True, exist_ok=True)
    with open(cache_path / "page-analysis.json", "w") as f:
        json.dump(data, f, indent=2)


def detect_business_type(html: str, url: str) -> str:
    """Detect business type from page content"""
    url_lower = url.lower()
    html_lower = html.lower()
    
    signals = {
        "saas": ["/pricing", "/features", "/docs", "free trial", "demo", "software"],
        "local": ["phone", "address", "location", "hours", "maps", "visit us"],
        "ecommerce": ["/products", "/cart", "/shop", "add to cart", "checkout", "price"],
        "publisher": ["/blog", "/article", "author", "published", "category"],
        "agency": ["/case-studies", "/portfolio", "client", "services", "agency"]
    }
    
    scores = {}
    for biz_type, keywords in signals.items():
        score = sum(1 for kw in keywords if kw in url_lower or kw in html_lower)
        scores[biz_type] = score
    
    if max(scores.values()) > 0:
        return max(scores, key=scores.get)
    return "unknown"


def analyze_technical(html: str, url: str, headers: Dict[str, str]) -> Dict[str, Any]:
    """Analyze technical SEO factors"""
    if not BS4_AVAILABLE:
        return {"score": 0, "max_score": 22, "error": "BeautifulSoup not available"}
    
    soup = BeautifulSoup(html, 'lxml')
    score = 0
    max_score = 22
    checks = {}
    issues = []
    
    # Check robots.txt (simulated - would need actual fetch)
    checks["robots_txt"] = {"status": "unknown", "details": "Requires robots.txt fetch"}
    
    # Check for sitemap link
    sitemap_link = soup.find("link", {"rel": "sitemap"})
    if sitemap_link:
        score += 2
        checks["sitemap"] = {"status": "pass", "url": sitemap_link.get("href")}
    else:
        checks["sitemap"] = {"status": "warning", "details": "No sitemap link in head"}
        issues.append({"severity": "low", "issue": "No sitemap link in <head>"})
    
    # Check HTTPS
    if url.startswith("https://"):
        score += 4
        checks["https"] = {"status": "pass", "ssl": True}
    else:
        checks["https"] = {"status": "fail", "details": "Not using HTTPS"}
        issues.append({"severity": "critical", "issue": "Site not using HTTPS"})
    
    # Check canonical
    canonical = soup.find("link", {"rel": "canonical"})
    if canonical:
        score += 2
        checks["canonicals"] = {"status": "pass", "url": canonical.get("href")}
    else:
        checks["canonicals"] = {"status": "warning", "details": "No canonical tag"}
        issues.append({"severity": "medium", "issue": "Missing canonical tag"})
    
    # Check viewport (mobile)
    viewport = soup.find("meta", {"name": "viewport"})
    if viewport and "width=device-width" in str(viewport):
        score += 2
        checks["mobile"] = {"status": "pass", "viewport": "configured"}
    else:
        checks["mobile"] = {"status": "warning", "details": "Viewport not configured"}
        issues.append({"severity": "medium", "issue": "Missing viewport meta tag"})
    
    # Check title
    title = soup.find("title")
    if title and len(title.get_text()) > 10:
        score += 2
        checks["title"] = {"status": "pass", "text": title.get_text()[:50]}
    else:
        checks["title"] = {"status": "warning", "details": "Title missing or too short"}
    
    # Check meta description
    meta_desc = soup.find("meta", {"name": "description"})
    if meta_desc and len(meta_desc.get("content", "")) > 50:
        score += 2
        checks["meta_description"] = {"status": "pass"}
    else:
        checks["meta_description"] = {"status": "warning", "details": "Meta description missing or too short"}
        issues.append({"severity": "medium", "issue": "Missing or short meta description"})
    
    # Check H1
    h1 = soup.find("h1")
    if h1:
        score += 2
        checks["h1"] = {"status": "pass", "text": h1.get_text()[:50]}
    else:
        checks["h1"] = {"status": "warning", "details": "No H1 found"}
        issues.append({"severity": "high", "issue": "Missing H1 tag"})
    
    # Security headers (would need actual HTTP check)
    checks["security_headers"] = {"status": "unknown", "details": "Requires HTTP header analysis"}
    
    # TTFB (would need actual timing)
    checks["ttfb"] = {"status": "unknown", "details": "Requires HTTP timing"}
    
    return {
        "score": score,
        "max_score": max_score,
        "checks": checks,
        "issues": issues
    }


def analyze_content(html: str, url: str) -> Dict[str, Any]:
    """Analyze content quality and E-E-A-T"""
    if not BS4_AVAILABLE:
        return {"score": 0, "max_score": 23, "error": "BeautifulSoup not available"}
    
    soup = BeautifulSoup(html, 'lxml')
    score = 0
    max_score = 23
    
    # Remove script and style for text analysis
    for element in soup(["script", "style", "nav", "footer"]):
        element.decompose()
    
    text = soup.get_text()
    words = text.split()
    word_count = len(words)
    
    # Content depth
    if word_count > 1000:
        score += 2
    elif word_count > 500:
        score += 1
    
    # E-E-A-T signals (simplified)
    eeat = {
        "experience": 3 if any(kw in text.lower() for kw in ["we", "our", "i", "my"]) else 1,
        "expertise": 4 if soup.find("article") or soup.find("time") else 2,
        "authoritativeness": 3 if soup.find_all("a", href=True) else 1,
        "trustworthiness": 3 if soup.find("a", href="/about") or soup.find("a", href="/contact") else 1
    }
    score += sum(eeat.values())
    
    # Heading structure
    h1_count = len(soup.find_all("h1"))
    h2_count = len(soup.find_all("h2"))
    if h1_count == 1 and h2_count > 0:
        score += 2
    
    # Readability (simplified)
    avg_word_length = sum(len(w) for w in words) / max(len(words), 1)
    if 4 <= avg_word_length <= 6:
        score += 2
    
    return {
        "score": min(score, max_score),
        "max_score": max_score,
        "eeat": eeat,
        "word_count": word_count,
        "heading_structure": {"h1": h1_count, "h2": h2_count}
    }


def analyze_schema(html: str, url: str) -> Dict[str, Any]:
    """Analyze structured data"""
    if not BS4_AVAILABLE:
        return {"score": 0, "max_score": 10, "error": "BeautifulSoup not available"}
    
    soup = BeautifulSoup(html, 'lxml')
    score = 0
    max_score = 10
    detected = []
    
    # Find JSON-LD
    for script in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            data = json.loads(script.string)
            schema_type = data.get("@type", "Unknown")
            detected.append({
                "type": schema_type,
                "format": "JSON-LD",
                "valid": True
            })
            
            # Score based on type
            if schema_type in ["Organization", "LocalBusiness"]:
                score += 3
            elif schema_type in ["WebSite", "WebPage"]:
                score += 2
            elif schema_type in ["Article", "BlogPosting"]:
                score += 2
            elif schema_type == "Product":
                score += 2
            else:
                score += 1
        except (json.JSONDecodeError, TypeError):
            detected.append({
                "type": "Invalid",
                "format": "JSON-LD",
                "valid": False
            })
    
    return {
        "score": min(score, max_score),
        "max_score": max_score,
        "detected": detected,
        "missing": []
    }


def analyze_performance(html: str, url: str) -> Dict[str, Any]:
    """Analyze performance signals (simplified)"""
    if not BS4_AVAILABLE:
        return {"score": 0, "max_score": 10, "error": "BeautifulSoup not available"}
    
    soup = BeautifulSoup(html, 'lxml')
    score = 5  # Default assumption
    max_score = 10
    
    # Check for common performance issues
    images = soup.find_all("img")
    large_images = [img for img in images if not img.get("loading") == "lazy"]
    
    scripts = soup.find_all("script", src=True)
    
    issues = []
    if len(large_images) > 3:
        issues.append({"severity": "medium", "issue": f"{len(large_images)} images without lazy loading"})
    
    return {
        "score": score,
        "max_score": max_score,
        "images": len(images),
        "scripts": len(scripts),
        "issues": issues,
        "note": "Full CWV analysis requires PageSpeed Insights API"
    }


def calculate_health_score(results: Dict[str, Dict]) -> Tuple[int, Dict[str, int]]:
    """Calculate overall SEO health score"""
    weights = {
        "technical": 22,
        "content": 23,
        "onpage": 20,
        "schema": 10,
        "performance": 10,
        "ai_readiness": 10,
        "images": 5
    }
    
    scores = {}
    total_weight = 0
    total_score = 0
    
    for category, weight in weights.items():
        if category in results:
            result = results[category]
            cat_score = result.get("score", 0)
            cat_max = result.get("max_score", weight)
            normalized = (cat_score / max(cat_max, 1)) * weight
            scores[category] = round(normalized)
            total_score += normalized
            total_weight += weight
    
    health_score = round((total_score / total_weight) * 100) if total_weight > 0 else 0
    return health_score, scores


def run_audit(url: str, use_cache: bool = True, refresh: bool = False) -> Dict[str, Any]:
    """Execute full SEO audit"""
    logger.info(f"Starting SEO audit for: {url}")
    
    # Check cache
    if use_cache and not refresh:
        cached = load_cache(url)
        if cached:
            logger.info("Using cached results (use --refresh to bypass)")
            return cached
    
    if not REQUESTS_AVAILABLE:
        return {
            "error": "requests library not installed",
            "url": url,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    # Fetch page
    try:
        response = requests.get(url, timeout=30, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        response.raise_for_status()
        html = response.text
        headers = dict(response.headers)
    except Exception as e:
        return {
            "error": str(e),
            "url": url,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    # Detect business type
    business_type = detect_business_type(html, url)
    
    # Run analyses
    results = {}
    
    results["technical"] = analyze_technical(html, url, headers)
    results["content"] = analyze_content(html, url)
    results["schema"] = analyze_schema(html, url)
    results["performance"] = analyze_performance(html, url)
    
    # Calculate health score
    health_score, scores = calculate_health_score(results)
    
    # Aggregate issues
    all_issues = []
    for category, result in results.items():
        for issue in result.get("issues", []):
            issue["category"] = category
            all_issues.append(issue)
    
    # Generate recommendations
    recommendations = []
    for issue in sorted(all_issues, key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x.get("severity", "low"), 3)):
        recommendations.append({
            "priority": issue.get("severity", "medium"),
            "action": issue.get("issue", "Unknown issue"),
            "category": issue.get("category", "general")
        })
    
    result = {
        "url": url,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "health_score": health_score,
        "scores": scores,
        "business_type": business_type,
        "details": results,
        "issues": all_issues,
        "recommendations": recommendations[:10]  # Top 10
    }
    
    # Save to cache
    if use_cache:
        save_cache(url, result)
    
    return result


def run_technical(url: str) -> Dict[str, Any]:
    """Run technical SEO analysis only"""
    if not REQUESTS_AVAILABLE:
        return {"error": "requests library not installed"}
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return analyze_technical(response.text, url, dict(response.headers))
    except Exception as e:
        return {"error": str(e), "url": url}


def run_content(url: str) -> Dict[str, Any]:
    """Run content analysis only"""
    if not REQUESTS_AVAILABLE:
        return {"error": "requests library not installed"}
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return analyze_content(response.text, url)
    except Exception as e:
        return {"error": str(e), "url": url}


def run_schema(url: str) -> Dict[str, Any]:
    """Run schema analysis only"""
    if not REQUESTS_AVAILABLE:
        return {"error": "requests library not installed"}
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return analyze_schema(response.text, url)
    except Exception as e:
        return {"error": str(e), "url": url}


def run_drift_baseline(url: str) -> Dict[str, Any]:
    """Capture baseline for drift monitoring"""
    result = run_audit(url, use_cache=False)
    
    if "error" not in result:
        # Save as baseline
        baseline_path = Path(f".seo-cache/baselines/{urlparse(url).netloc}")
        baseline_path.mkdir(parents=True, exist_ok=True)
        
        baseline_file = baseline_path / "baseline.json"
        with open(baseline_file, "w") as f:
            json.dump(result, f, indent=2)
        
        result["baseline_file"] = str(baseline_file)
        result["message"] = "Baseline captured successfully"
    
    return result


def run_drift_compare(url: str) -> Dict[str, Any]:
    """Compare current state vs baseline"""
    baseline_path = Path(f".seo-cache/baselines/{urlparse(url).netloc}/baseline.json")
    
    if not baseline_path.exists():
        return {
            "error": "No baseline found",
            "message": "Run 'drift baseline' first to capture a baseline"
        }
    
    with open(baseline_path) as f:
        baseline = json.load(f)
    
    current = run_audit(url, use_cache=False)
    
    if "error" in current:
        return current
    
    # Compare scores
    baseline_score = baseline.get("health_score", 0)
    current_score = current.get("health_score", 0)
    delta = current_score - baseline_score
    
    # Detect changes
    changes = []
    
    # Title change
    baseline_title = baseline.get("details", {}).get("technical", {}).get("checks", {}).get("title", {}).get("text")
    current_title = current.get("details", {}).get("technical", {}).get("checks", {}).get("title", {}).get("text")
    if baseline_title != current_title:
        changes.append({
            "element": "title",
            "baseline": baseline_title,
            "current": current_title,
            "severity": "high"
        })
    
    # Schema changes
    baseline_schemas = set(s["type"] for s in baseline.get("details", {}).get("schema", {}).get("detected", []))
    current_schemas = set(s["type"] for s in current.get("details", {}).get("schema", {}).get("detected", []))
    
    removed = baseline_schemas - current_schemas
    if removed:
        changes.append({
            "element": "schema",
            "baseline": list(baseline_schemas),
            "current": list(current_schemas),
            "removed": list(removed),
            "severity": "critical"
        })
    
    return {
        "url": url,
        "baseline_date": baseline.get("timestamp"),
        "current_date": current.get("timestamp"),
        "baseline_score": baseline_score,
        "current_score": current_score,
        "delta": delta,
        "changes": changes,
        "regressions": len([c for c in changes if c.get("severity") in ["critical", "high"]]),
        "improvements": max(0, delta)
    }


def main():
    parser = argparse.ArgumentParser(
        description="Run SEO workflow headless",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_skill_workflow.py audit --url https://example.com
  python run_skill_workflow.py technical --url https://example.com --json
  python run_skill_workflow.py drift-baseline --url https://example.com
  python run_skill_workflow.py drift-compare --url https://example.com
        """
    )
    
    parser.add_argument(
        "workflow",
        choices=["audit", "technical", "content", "schema", "drift-baseline", "drift-compare"],
        help="Workflow to execute"
    )
    parser.add_argument("--url", required=True, help="Target URL")
    parser.add_argument("--format", choices=["json", "yaml", "markdown"], default="json",
                       help="Output format")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--config", default="config/config.yaml", help="Config file")
    parser.add_argument("--refresh", action="store_true", help="Ignore cache, fetch fresh data")
    parser.add_argument("--no-cache", action="store_true", help="Disable caching")
    
    args = parser.parse_args()
    
    # Load config (for future extensions)
    config = load_config(args.config)
    
    # Execute workflow
    if args.workflow == "audit":
        result = run_audit(args.url, use_cache=not args.no_cache, refresh=args.refresh)
    elif args.workflow == "technical":
        result = run_technical(args.url)
    elif args.workflow == "content":
        result = run_content(args.url)
    elif args.workflow == "schema":
        result = run_schema(args.url)
    elif args.workflow == "drift-baseline":
        result = run_drift_baseline(args.url)
    elif args.workflow == "drift-compare":
        result = run_drift_compare(args.url)
    else:
        print(f"Workflow '{args.workflow}' not implemented", file=sys.stderr)
        return 1
    
    # Output result
    output_content = None
    
    if args.format == "json":
        output_content = json.dumps(result, indent=2)
    elif args.format == "yaml":
        if not YAML_AVAILABLE:
            print("YAML format requires PyYAML. Install with: pip install pyyaml", file=sys.stderr)
            return 1
        output_content = yaml.dump(result, default_flow_style=False)
    elif args.format == "markdown":
        # Generate markdown report
        lines = [
            f"# SEO Audit Report",
            f"",
            f"**URL:** {result.get('url', 'N/A')}",
            f"**Date:** {result.get('timestamp', 'N/A')}",
            f"**Health Score:** {result.get('health_score', 'N/A')}/100",
            f"",
            f"## Scores",
            f"",
        ]
        for cat, score in result.get("scores", {}).items():
            lines.append(f"- **{cat.title()}:** {score}")
        
        if result.get("recommendations"):
            lines.extend(["", "## Recommendations", ""])
            for rec in result.get("recommendations", [])[:10]:
                lines.append(f"- [{rec.get('priority', 'medium').upper()}] {rec.get('action', 'N/A')}")
        
        output_content = "\n".join(lines)
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(output_content)
        print(f"✅ Result saved to {output_path}")
    else:
        print(output_content)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
