#!/usr/bin/env python3
"""
Headless workflow executor for claude-seo-unified
Enables deterministic execution in CI/CD, cron, or API mode
"""

__version__ = "1.9.7-unified"

import sys
import os
import json
import argparse
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


def validate_url(url: str) -> Tuple[bool, str]:
    """Validate URL format, scheme, and SSRF protection"""
    if not url:
        return False, "URL is required"
    
    if not url.startswith(("http://", "https://")):
        return False, "URL must start with http:// or https://"
    
    parsed = urlparse(url)
    if not parsed.netloc:
        return False, "Invalid URL: missing domain"
    
    # SSRF protection - block localhost and private IPs
    hostname = parsed.netloc.split(':')[0].lower()
    
    # Block localhost
    if hostname in ('localhost', '127.0.0.1', '::1', '0.0.0.0'):
        return False, "Access to localhost is not allowed"
    
    # Block private IP ranges (10.x, 172.16-31.x, 192.168.x)
    import ipaddress
    import socket
    try:
        # Resolve the hostname to an IP to prevent DNS rebinding
        ip = socket.gethostbyname(hostname)
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved:
            return False, "Access to private/internal IPs is not allowed"
    except socket.gaierror:
        # DNS resolution failed, let it fail in the request naturally or block it
        pass
    except ValueError:
        # Not an IP address, likely a domain - check for internal patterns
        if hostname.endswith('.local') or hostname.endswith('.internal') or hostname.endswith('.localhost'):
            return False, "Access to internal domains is not allowed"
    
    # Block AWS metadata endpoint
    if hostname == '169.254.169.254':
        return False, "Access to metadata endpoints is not allowed"
    
    # Max URL length
    if len(url) > 2048:
        return False, "URL exceeds maximum length (2048 characters)"
    
    return True, url


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
            timestamp_str = data.get("timestamp", "2000-01-01T00:00:00+00:00")
            # Ensure timezone-aware parsing
            if not timestamp_str.endswith(("Z", "+00:00")):
                timestamp_str += "+00:00"
            cached_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            if (datetime.now(timezone.utc) - cached_time).total_seconds() < 86400:
                return data
    return None


def save_cache(url: str, data: Dict[str, Any]) -> None:
    """Save analysis to cache"""
    cache_path = get_cache_path(url)
    cache_path.mkdir(parents=True, exist_ok=True)
    with open(cache_path / "page-analysis.json", "w") as f:
        json.dump(data, f, indent=2)


# Business type detection with explicit priority for ties
BUSINESS_TYPE_PRIORITY = ["saas", "ecommerce", "agency", "local", "publisher"]


def detect_business_type(html: str, url: str) -> str:
    """Detect business type from page content with tie-breaking"""
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
    
    max_score = max(scores.values()) if scores else 0
    if max_score == 0:
        return "unknown"
    
    # Get all types with max score
    top_types = [t for t, s in scores.items() if s == max_score]
    
    # Use priority order for tie-breaking
    for biz_type in BUSINESS_TYPE_PRIORITY:
        if biz_type in top_types:
            return biz_type
    
    return top_types[0]  # Fallback


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


def analyze_onpage(html: str, url: str) -> Dict[str, Any]:
    """Analyze on-page SEO factors"""
    if not BS4_AVAILABLE:
        return {"score": 0, "max_score": 20, "error": "BeautifulSoup not available"}
    
    soup = BeautifulSoup(html, 'lxml')
    score = 0
    max_score = 20
    checks = {}
    issues = []
    
    # Title length (optimal: 50-60 chars)
    title = soup.find("title")
    title_text = title.get_text() if title else ""
    title_len = len(title_text)
    if 50 <= title_len <= 60:
        score += 5
        checks["title_length"] = {"status": "pass", "length": title_len}
    elif title_len > 0:
        score += 2
        checks["title_length"] = {"status": "warning", "length": title_len, "optimal": "50-60"}
    else:
        checks["title_length"] = {"status": "fail", "issue": "Missing title"}
        issues.append({"severity": "high", "issue": "Missing page title"})
    
    # Meta description length (optimal: 150-160 chars)
    meta_desc = soup.find("meta", {"name": "description"})
    desc_content = meta_desc.get("content", "") if meta_desc else ""
    desc_len = len(desc_content)
    if 150 <= desc_len <= 160:
        score += 5
        checks["meta_desc_length"] = {"status": "pass", "length": desc_len}
    elif desc_len > 0:
        score += 2
        checks["meta_desc_length"] = {"status": "warning", "length": desc_len, "optimal": "150-160"}
    else:
        checks["meta_desc_length"] = {"status": "fail", "issue": "Missing meta description"}
        issues.append({"severity": "medium", "issue": "Missing meta description"})
    
    # Heading hierarchy
    h1_count = len(soup.find_all("h1"))
    h2_count = len(soup.find_all("h2"))
    h3_count = len(soup.find_all("h3"))
    
    if h1_count == 1:
        score += 5
        checks["heading_hierarchy"] = {"status": "pass", "h1": h1_count, "h2": h2_count}
    elif h1_count == 0:
        checks["heading_hierarchy"] = {"status": "fail", "h1": 0}
        issues.append({"severity": "high", "issue": "No H1 tag found"})
    else:
        checks["heading_hierarchy"] = {"status": "warning", "h1": h1_count, "note": "Multiple H1s"}
        issues.append({"severity": "medium", "issue": f"Multiple H1 tags ({h1_count})"})
    
    # Internal links - improved detection for relative, protocol-relative, and absolute URLs
    links = soup.find_all("a", href=True)
    base_parsed = urlparse(url)
    internal_links = []
    
    for link in links:
        href = link["href"]
        parsed_href = urlparse(href)
        
        # Empty href or javascript: skip
        if not href or href.startswith(("javascript:", "mailto:", "tel:", "#")):
            continue
        
        # Relative URL (empty netloc) - always internal
        # Protocol-relative URL (//example.com) - check netloc
        # Absolute URL - check netloc match
        is_internal = (
            not parsed_href.netloc or  # Relative URL
            parsed_href.netloc == base_parsed.netloc or  # Same domain
            (href.startswith("//") and parsed_href.netloc == base_parsed.netloc)  # Protocol-relative
        )
        
        if is_internal:
            internal_links.append(link)
    
    if len(internal_links) >= 3:
        score += 5
        checks["internal_links"] = {"status": "pass", "count": len(internal_links)}
    else:
        checks["internal_links"] = {"status": "warning", "count": len(internal_links)}
    
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
    
    # Focus on main content areas only (not nav, footer, etc.)
    main_content = soup.find("main") or soup.find("article") or soup.find("div", class_=re.compile(r"(content|post|article|entry)", re.I)) or soup
    
    # Remove script and style for text analysis - use list() to materialize iterator before mutation
    for element in list(main_content.find_all(["script", "style", "nav", "footer", "header", "aside"])):
        element.decompose()
    
    text = main_content.get_text()
    words = text.split()
    word_count = len(words)
    
    # Content depth
    if word_count > 1000:
        score += 2
    elif word_count > 500:
        score += 1
    
    # E-E-A-T signals - only look in main content area
    eeat = {
        "experience": 0,
        "expertise": 0,
        "authoritativeness": 0,
        "trustworthiness": 0
    }
    
    # Experience signals - look for first-person in content area only
    text_lower = text.lower()
    if any(kw in text_lower for kw in ["i have", "i've", "we have", "our experience", "in my experience"]):
        eeat["experience"] = 3
    else:
        eeat["experience"] = 1
    
    # Expertise signals - structured content, citations, data
    if soup.find("article") or soup.find("time"):
        eeat["expertise"] = 4
    elif soup.find("cite") or soup.find_all("a", href=re.compile(r"(source|citation|reference)", re.I)):
        eeat["expertise"] = 3
    else:
        eeat["expertise"] = 2
    
    # Authoritativeness - external links, author info
    if soup.find_all("a", href=True) and len(soup.find_all("a", href=True)) > 3:
        eeat["authoritativeness"] = 3
    else:
        eeat["authoritativeness"] = 1
    
    # Trustworthiness - contact, about, privacy
    if soup.find("a", href=re.compile(r"(about|contact|privacy|terms)", re.I)):
        eeat["trustworthiness"] = 3
    else:
        eeat["trustworthiness"] = 1
    
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


def analyze_ai_readiness(html: str, url: str) -> Dict[str, Any]:
    """Analyze AI search readiness (GEO)"""
    if not BS4_AVAILABLE:
        return {"score": 0, "max_score": 10, "error": "BeautifulSoup not available"}
    
    soup = BeautifulSoup(html, 'lxml')
    score = 0
    max_score = 10
    checks = {}
    
    # Check for FAQ structured content
    faq_items = soup.find_all(["dt", "dd"]) or soup.find_all(class_=re.compile(r"faq", re.I))
    if faq_items:
        score += 2
        checks["faq_content"] = {"status": "pass", "count": len(faq_items)}
    else:
        checks["faq_content"] = {"status": "warning", "details": "No FAQ content detected"}
    
    # Check for clear Q&A format
    headings = soup.find_all(["h2", "h3"])
    question_headings = [h for h in headings if h.get_text().strip().endswith("?")]
    if question_headings:
        score += 2
        checks["question_headings"] = {"status": "pass", "count": len(question_headings)}
    
    # Check for structured lists (AI-friendly)
    lists = soup.find_all(["ul", "ol"])
    if len(lists) >= 2:
        score += 2
        checks["structured_lists"] = {"status": "pass", "count": len(lists)}
    
    # Check for definition lists
    dl = soup.find_all("dl")
    if dl:
        score += 2
        checks["definition_lists"] = {"status": "pass"}
    
    # Check for clear, concise intro
    paragraphs = soup.find_all("p")
    if paragraphs and 50 <= len(paragraphs[0].get_text()) <= 200:
        score += 2
        checks["intro_paragraph"] = {"status": "pass"}
    
    return {
        "score": score,
        "max_score": max_score,
        "checks": checks,
        "issues": []
    }


def analyze_images(html: str, url: str) -> Dict[str, Any]:
    """Analyze image SEO"""
    if not BS4_AVAILABLE:
        return {"score": None, "max_score": 5, "error": "BeautifulSoup not available", "issues": []}
    
    soup = BeautifulSoup(html, 'lxml')
    score = 0
    max_score = 5
    issues = []
    
    images = soup.find_all("img")
    
    # No images found - return None score so it's excluded from health calculation
    # A page with no images hasn't "passed" image SEO, it has nothing to evaluate
    if not images:
        return {
            "score": None,  # None = skip in health score calculation
            "max_score": 5,
            "images": 0,
            "issues": [],
            "note": "No images found - category excluded from health score"
        }
    
    # Check alt text
    with_alt = [img for img in images if img.get("alt")]
    alt_ratio = len(with_alt) / len(images) if images else 0
    
    if alt_ratio >= 0.9:
        score += 2
    elif alt_ratio >= 0.5:
        score += 1
    else:
        issues.append({"severity": "medium", "issue": f"Only {int(alt_ratio*100)}% of images have alt text"})
    
    # Check lazy loading
    lazy_images = [img for img in images if img.get("loading") == "lazy"]
    if len(lazy_images) >= len(images) * 0.5:
        score += 2
    elif lazy_images:
        score += 1
    
    # Check for large image warnings (width/height attributes)
    sized_images = [img for img in images if img.get("width") and img.get("height")]
    if len(sized_images) >= len(images) * 0.8:
        score += 1
    
    return {
        "score": score,
        "max_score": max_score,
        "images": len(images),
        "with_alt": len(with_alt),
        "alt_ratio": round(alt_ratio, 2),
        "issues": issues
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
        if category in results and "error" not in results[category]:
            result = results[category]
            cat_score = result.get("score")
            
            # Skip categories with None score (e.g., no images on page)
            if cat_score is None:
                continue
            
            cat_max = result.get("max_score", weight)
            normalized = (cat_score / max(cat_max, 1)) * weight
            scores[category] = round(normalized)
            total_score += normalized
            total_weight += weight  # IMPORTANT: Must increment total_weight for each valid category
        elif category in weights:
            # Category not analyzed or has error, skip from weight calculation
            pass
    
    # Only count weight for categories that were actually analyzed
    health_score = round((total_score / total_weight) * 100) if total_weight > 0 else 0
    return health_score, scores


def run_audit(url: str, use_cache: bool = True, refresh: bool = False, max_recommendations: int = 10) -> Dict[str, Any]:
    """Execute full SEO audit"""
    logger.info(f"Starting SEO audit for: {url}")
    
    # Validate URL
    valid, url_or_error = validate_url(url)
    if not valid:
        return {
            "error": url_or_error,
            "url": url,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    url = url_or_error
    
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
            "User-Agent": "Mozilla/5.0 (compatible; ClaudeSEO-Bot/1.9.6; +https://github.com/Pottstim/claude-seo-unified)"
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
    
    # Run all analyses
    results = {}
    
    results["technical"] = analyze_technical(html, url, headers)
    results["onpage"] = analyze_onpage(html, url)
    results["content"] = analyze_content(html, url)
    results["schema"] = analyze_schema(html, url)
    results["performance"] = analyze_performance(html, url)
    results["ai_readiness"] = analyze_ai_readiness(html, url)
    results["images"] = analyze_images(html, url)
    
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
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    for issue in sorted(all_issues, key=lambda x: severity_order.get(x.get("severity", "low"), 3)):
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
        "recommendations": recommendations[:max_recommendations]
    }
    
    # Save to cache
    if use_cache:
        save_cache(url, result)
    
    return result


def run_technical(url: str) -> Dict[str, Any]:
    """Run technical SEO analysis only"""
    # Validate URL
    valid, url_or_error = validate_url(url)
    if not valid:
        return {"error": url_or_error, "url": url}
    url = url_or_error
    
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
    # Validate URL
    valid, url_or_error = validate_url(url)
    if not valid:
        return {"error": url_or_error, "url": url}
    url = url_or_error
    
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
    # Validate URL
    valid, url_or_error = validate_url(url)
    if not valid:
        return {"error": url_or_error, "url": url}
    url = url_or_error
    
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
            "message": "Run 'drift-baseline' first to capture a baseline"
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
  python run_skill_workflow.py --version
        """
    )
    
    parser.add_argument(
        "workflow",
        nargs="?",
        choices=["audit", "technical", "content", "schema", "drift-baseline", "drift-compare"],
        help="Workflow to execute"
    )
    parser.add_argument("--url", help="Target URL (must include http:// or https://)")
    parser.add_argument("--format", choices=["json", "yaml", "markdown"], default="json",
                       help="Output format")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--config", default="config/config.yaml", help="Config file")
    parser.add_argument("--refresh", action="store_true", help="Ignore cache, fetch fresh data")
    parser.add_argument("--no-cache", action="store_true", help="Disable caching")
    parser.add_argument("--max-recommendations", type=int, default=10, 
                       help="Maximum number of recommendations to show (default: 10)")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    
    args = parser.parse_args()
    
    # Handle missing workflow - return error instead of just showing help
    if not args.workflow:
        print("Error: No workflow specified", file=sys.stderr)
        print("Usage: python run_skill_workflow.py <workflow> --url <url>", file=sys.stderr)
        print("\nAvailable workflows: audit, technical, content, schema, drift-baseline, drift-compare", file=sys.stderr)
        print("Use --help for more information", file=sys.stderr)
        return 1
    
    # Validate URL is provided for workflows that need it
    if args.workflow not in ["help"] and not args.url:
        print("Error: --url is required for this workflow", file=sys.stderr)
        print("Example: python run_skill_workflow.py audit --url https://example.com", file=sys.stderr)
        return 1
    
    # Load config (for future extensions)
    config = load_config(args.config)
    
    # Execute workflow
    if args.workflow == "audit":
        result = run_audit(args.url, use_cache=not args.no_cache, refresh=args.refresh, 
                          max_recommendations=args.max_recommendations)
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
            for rec in result.get("recommendations", []):
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
