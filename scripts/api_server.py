#!/usr/bin/env python3
"""
REST API server for claude-seo-unified
Production-ready Flask API with auth, rate limiting, and PDF generation
"""

import os
import sys
import json
import time
import uuid
import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from functools import wraps
from typing import Dict, Any, Optional
from collections import defaultdict

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

# Import our modules
try:
    from scripts.run_skill_workflow import (
        analyze_url,
        validate_url,
        __version__
    )
    WORKFLOW_AVAILABLE = True
except ImportError:
    WORKFLOW_AVAILABLE = False

try:
    from scripts.pdf_report import generate_report
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('API_SECRET_KEY', secrets.token_hex(32))
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Storage (replace with database in production)
analysis_cache: Dict[str, Dict] = {}
api_keys: Dict[str, Dict] = {}  # api_key -> {name, email, created, requests}
rate_limits: Dict[str, list] = defaultdict(list)  # ip -> [timestamps]
pending_emails: list = []  # Email queue (use Celery/Redis in production)


# ============
# DECORATORS
# ============

def require_api_key(f):
    """Require valid API key for endpoint"""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        if not api_key:
            return jsonify({"error": "API key required"}), 401
        
        if api_key not in api_keys:
            return jsonify({"error": "Invalid API key"}), 401
        
        # Update last used
        api_keys[api_key]['last_used'] = datetime.now(timezone.utc).isoformat()
        api_keys[api_key]['requests'] += 1
        
        return f(*args, **kwargs)
    return decorated


def rate_limit(max_requests: int = 10, window_seconds: int = 60):
    """Rate limit decorator"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            ip = request.remote_addr
            now = time.time()
            
            # Clean old requests
            rate_limits[ip] = [t for t in rate_limits[ip] if now - t < window_seconds]
            
            if len(rate_limits[ip]) >= max_requests:
                return jsonify({
                    "error": "Rate limit exceeded",
                    "retry_after": int(window_seconds - (now - rate_limits[ip][0]))
                }), 429
            
            rate_limits[ip].append(now)
            return f(*args, **kwargs)
        return decorated
    return decorator


# ============
# ROUTES
# ============

@app.route('/')
def index():
    """API info"""
    return jsonify({
        "name": "Claude SEO Unified API",
        "version": __version__ if WORKFLOW_AVAILABLE else "unknown",
        "endpoints": {
            "POST /api/analyze": "Analyze a website",
            "GET /api/report/<id>": "Get analysis by ID",
            "GET /api/report/pdf": "Download PDF report",
            "POST /api/email": "Email report to client",
            "POST /api/keys": "Create new API key",
            "GET /api/health": "Health check"
        },
        "documentation": "https://github.com/Pottstim/claude-seo-unified-complete-v1.9.6-1"
    })


@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": __version__ if WORKFLOW_AVAILABLE else "unknown",
        "components": {
            "workflow": WORKFLOW_AVAILABLE,
            "pdf_generation": PDF_AVAILABLE
        }
    })


@app.route('/api/analyze', methods=['POST'])
@rate_limit(max_requests=5, window_seconds=60)
def analyze():
    """Analyze a website"""
    if not WORKFLOW_AVAILABLE:
        return jsonify({"error": "Workflow engine not available"}), 500
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400
    
    url = data.get('url')
    if not url:
        return jsonify({"error": "URL required"}), 400
    
    # Validate URL
    valid, url_or_error = validate_url(url)
    if not valid:
        return jsonify({"error": url_or_error}), 400
    
    # Check cache (1 hour TTL)
    cache_key = hashlib.md5(url.encode()).hexdigest()
    if cache_key in analysis_cache:
        cached = analysis_cache[cache_key]
        if datetime.now(timezone.utc) - datetime.fromisoformat(cached['timestamp']) < timedelta(hours=1):
            return jsonify({
                **cached,
                "cached": True
            })
    
    try:
        # Run analysis
        result = analyze_url(url)
        
        # Add metadata
        report_id = str(uuid.uuid4())
        result['report_id'] = report_id
        result['timestamp'] = datetime.now(timezone.utc).isoformat()
        result['url'] = url
        
        # Generate recommendations from findings
        result['recommendations'] = generate_recommendations(result)
        
        # Cache result
        analysis_cache[cache_key] = result
        analysis_cache[report_id] = result
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/report/<report_id>')
def get_report(report_id: str):
    """Get analysis by report ID"""
    if report_id not in analysis_cache:
        return jsonify({"error": "Report not found"}), 404
    
    return jsonify(analysis_cache[report_id])


@app.route('/api/report/pdf')
def download_pdf():
    """Download PDF report"""
    if not PDF_AVAILABLE:
        return jsonify({"error": "PDF generation not available. Install reportlab."}), 500
    
    url = request.args.get('url') or request.args.get('report_id')
    
    if not url:
        return jsonify({"error": "url or report_id parameter required"}), 400
    
    # Get cached analysis or return error
    if url.startswith('http'):
        cache_key = hashlib.md5(url.encode()).hexdigest()
        report_id = cache_key
    else:
        report_id = url
        cache_key = url
    
    if cache_key not in analysis_cache and report_id not in analysis_cache:
        return jsonify({"error": "Analysis not found. Run analysis first."}), 404
    
    analysis_data = analysis_cache.get(cache_key) or analysis_cache.get(report_id)
    
    # Business settings from query params or defaults
    business_name = request.args.get('business_name', 'Legrand Consulting')
    client_name = request.args.get('client_name')
    
    try:
        # Generate PDF
        output_path = generate_report(
            analysis_data,
            business_name=business_name,
            client_name=client_name
        )
        
        return send_file(
            output_path,
            as_attachment=True,
            download_name=f"seo-report-{url.replace('https://', '').replace('http://', '').split('/')[0]}.pdf"
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/email', methods=['POST'])
@rate_limit(max_requests=5, window_seconds=300)
def email_report():
    """Queue email report for sending"""
    data = request.get_json()
    
    report_id = data.get('report_id') or data.get('url')
    email = data.get('email')
    message = data.get('message', '')
    
    if not report_id or not email:
        return jsonify({"error": "report_id/url and email required"}), 400
    
    # Get analysis
    cache_key = report_id if report_id in analysis_cache else hashlib.md5(report_id.encode()).hexdigest()
    if cache_key not in analysis_cache:
        return jsonify({"error": "Analysis not found. Run analysis first."}), 404
    
    analysis_data = analysis_cache[cache_key]
    
    # Queue email (in production, use Celery/Redis)
    email_task = {
        "to": email,
        "report_id": analysis_data.get('report_id'),
        "url": analysis_data.get('url'),
        "message": message,
        "queued_at": datetime.now(timezone.utc).isoformat()
    }
    pending_emails.append(email_task)
    
    # In production, send actual email via SendGrid/Mailgun/etc.
    # For now, just acknowledge
    return jsonify({
        "success": True,
        "message": f"Report queued for delivery to {email}",
        "queue_position": len(pending_emails)
    })


# ============
# API KEY MANAGEMENT
# ============

@app.route('/api/keys', methods=['POST'])
def create_api_key():
    """Create a new API key"""
    data = request.get_json()
    
    name = data.get('name', 'Unnamed')
    email = data.get('email')
    
    # Generate key
    api_key = f"seo_{secrets.token_hex(16)}"
    
    api_keys[api_key] = {
        "name": name,
        "email": email,
        "created": datetime.now(timezone.utc).isoformat(),
        "last_used": None,
        "requests": 0
    }
    
    return jsonify({
        "api_key": api_key,
        "name": name,
        "created": api_keys[api_key]['created']
    })


@app.route('/api/keys', methods=['GET'])
@require_api_key
def list_api_keys():
    """List all API keys (admin)"""
    return jsonify({
        "keys": [
            {
                "key": k[:10] + "...",  # Partial key only
                **v
            }
            for k, v in api_keys.items()
        ]
    })


# ============
# BATCH PROCESSING
# ============

@app.route('/api/batch', methods=['POST'])
@require_api_key
def batch_analyze():
    """Analyze multiple URLs"""
    data = request.get_json()
    urls = data.get('urls', [])
    
    if not urls:
        return jsonify({"error": "urls array required"}), 400
    
    if len(urls) > 10:
        return jsonify({"error": "Maximum 10 URLs per batch"}), 400
    
    results = []
    for url in urls:
        valid, url_or_error = validate_url(url)
        if not valid:
            results.append({"url": url, "error": url_or_error})
            continue
        
        try:
            result = analyze_url(url)
            result['url'] = url
            results.append(result)
        except Exception as e:
            results.append({"url": url, "error": str(e)})
    
    return jsonify({
        "total": len(urls),
        "results": results
    })


# ============
# HELPERS
# ============

def generate_recommendations(analysis: Dict) -> list:
    """Generate prioritized recommendations from analysis"""
    recommendations = []
    
    # From critical issues
    for issue in analysis.get('findings', {}).get('critical', []):
        recommendations.append({
            "title": issue.get('issue', str(issue))[:100],
            "priority": "High",
            "effort": "Low" if "meta" in str(issue).lower() else "Medium",
            "impact": "High"
        })
    
    # From warnings
    for issue in analysis.get('findings', {}).get('warnings', []):
        recommendations.append({
            "title": issue.get('issue', str(issue))[:100],
            "priority": "Medium",
            "effort": "Medium",
            "impact": "Medium"
        })
    
    # From opportunities
    for issue in analysis.get('findings', {}).get('opportunities', []):
        recommendations.append({
            "title": issue.get('issue', str(issue))[:100],
            "priority": "Low",
            "effort": "Medium",
            "impact": "Medium"
        })
    
    # Add category-specific recommendations based on scores
    scores = analysis.get('scores', {})
    
    if scores.get('performance', 100) < 50:
        recommendations.append({
            "title": "Improve page load speed (Core Web Vitals)",
            "priority": "High",
            "effort": "High",
            "impact": "High"
        })
    
    if scores.get('ai_readiness', 100) < 60:
        recommendations.append({
            "title": "Optimize content for AI search engines (GEO)",
            "priority": "Medium",
            "effort": "Medium",
            "impact": "High"
        })
    
    if scores.get('schema', 100) < 50:
        recommendations.append({
            "title": "Implement structured data markup",
            "priority": "Medium",
            "effort": "Low",
            "impact": "Medium"
        })
    
    # Sort by priority
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    recommendations.sort(key=lambda x: priority_order.get(x['priority'], 99))
    
    return recommendations[:20]  # Top 20


# ============
# MAIN
# ============

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    print(f"Starting Claude SEO Unified API on port {port}")
    print(f"Version: {__version__ if WORKFLOW_AVAILABLE else 'unknown'}")
    print(f"PDF Generation: {'Available' if PDF_AVAILABLE else 'Not available'}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
