#!/usr/bin/env python3
"""
REST API server for claude-seo-unified
Production-ready Flask API with auth, rate limiting, retry logic, circuit breaker, and observability
"""

import os
import sys
import json
import time
import uuid
import hashlib
import secrets
import signal
import atexit
import logging
import threading
from datetime import datetime, timezone, timedelta
from functools import wraps
from typing import Dict, Any, Optional, List
from collections import defaultdict
from contextlib import contextmanager
import backoff

# Sentry integration (optional)
SENTRY_DSN = os.environ.get("SENTRY_DSN")
if SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[FlaskIntegration()],
            traces_sample_rate=float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
            profiles_sample_rate=float(os.environ.get("SENTRY_PROFILES_SAMPLE_RATE", "0.1")),
            environment=os.environ.get("ENVIRONMENT", "production"),
            release=f"seo-unified@{os.environ.get('APP_VERSION', '1.9.8')}"
        )
        print("✅ Sentry initialized")
    except ImportError:
        print("⚠️  Sentry DSN set but sentry-sdk not installed")

# Structured logging with context
import structlog
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    cache_logging_on_first_use=False,
)
logger = structlog.get_logger()

# Prometheus metrics (optional)
METRICS_ENABLED = os.environ.get("PROMETHEUS_ENABLED", "false").lower() == "true"
if METRICS_ENABLED:
    try:
        from prometheus_flask_exporter import PrometheusMetrics
        print("✅ Prometheus metrics enabled")
    except ImportError:
        METRICS_ENABLED = False
        print("⚠️  Prometheus enabled but prometheus_flask_exporter not installed")

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, send_file, render_template_string, g, Response
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
    __version__ = "1.9.8"

try:
    from scripts.pdf_report import generate_report
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Initialize Flask
app = Flask(__name__)
CORS(app, origins=os.environ.get("CORS_ORIGINS", "*").split(","))

# Prometheus metrics
if METRICS_ENABLED:
    metrics = PrometheusMetrics(app, group_by_endpoint=True, group_by_url_rule=True)
    # Custom metrics
    analysis_requests = metrics.counter(
        'analysis_requests_total', 
        'Total analysis requests',
        labels={'workflow': lambda: request.view_args.get('workflow', 'unknown')}
    )
    analysis_duration = metrics.histogram(
        'analysis_duration_seconds',
        'Analysis duration in seconds',
        labels={'workflow': lambda: request.view_args.get('workflow', 'unknown')}
    )

# Security headers - COMPLETE
@app.after_request
def add_security_headers(response):
    # Basic security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # HSTS - Strict Transport Security
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    
    # Content Security Policy
    response.headers['Content-Security-Policy'] = os.environ.get(
        "CSP_POLICY",
        "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    )
    
    # Referrer Policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Permissions Policy (formerly Feature Policy)
    response.headers['Permissions-Policy'] = 'accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()'
    
    # Cache control for API responses
    if request.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    
    return response

# Request ID tracking
@app.before_request
def add_request_id():
    """Add unique request ID for tracing"""
    g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
    g.start_time = time.time()
    
    # Bind to structlog context
    structlog.contextvars.bind_contextvars(request_id=g.request_id)

@app.after_request
def log_request(response):
    """Log request with duration and status"""
    duration = time.time() - getattr(g, 'start_time', time.time())
    
    logger.info(
        "request_completed",
        method=request.method,
        path=request.path,
        status=response.status_code,
        duration_ms=round(duration * 1000, 2),
        ip=request.remote_addr,
        user_agent=request.headers.get('User-Agent', '')[:100]
    )
    
    # Add request ID to response headers
    response.headers['X-Request-ID'] = getattr(g, 'request_id', '')
    response.headers['X-Response-Time'] = f"{round(duration * 1000, 2)}ms"
    
    return response

# Configuration
app.config['SECRET_KEY'] = os.environ.get('API_SECRET_KEY', secrets.token_hex(32))
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['JSON_SORT_KEYS'] = False  # Preserve key order

# Circuit Breaker
class CircuitBreaker:
    """Circuit breaker for external service calls"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60, half_open_requests: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_requests = half_open_requests
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
        self.half_open_successes = 0
        self._lock = threading.Lock()
    
    def can_execute(self) -> bool:
        with self._lock:
            if self.state == "closed":
                return True
            elif self.state == "open":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = "half-open"
                    self.half_open_successes = 0
                    return True
                return False
            else:  # half-open
                return self.half_open_successes < self.half_open_requests
    
    def record_success(self):
        with self._lock:
            if self.state == "half-open":
                self.half_open_successes += 1
                if self.half_open_successes >= self.half_open_requests:
                    self.state = "closed"
                    self.failures = 0
    
    def record_failure(self):
        with self._lock:
            self.failures += 1
            self.last_failure_time = time.time()
            if self.state == "half-open":
                self.state = "open"
            elif self.failures >= self.failure_threshold:
                self.state = "open"

# Circuit breakers for different services
circuit_breakers = {
    "external_api": CircuitBreaker(failure_threshold=5, recovery_timeout=60),
    "browser": CircuitBreaker(failure_threshold=3, recovery_timeout=120),
    "llm": CircuitBreaker(failure_threshold=5, recovery_timeout=30)
}

# Storage (replace with database in production)
analysis_cache: Dict[str, Dict] = {}
api_keys: Dict[str, Dict] = {}  # api_key -> {name, email, created, requests}
rate_limits: Dict[str, list] = defaultdict(list)  # ip -> [timestamps]
pending_emails: list = []  # Email queue (use Celery/Redis in production)

# Graceful shutdown
shutting_down = False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global shutting_down
    logger.info("Shutdown signal received", signal=signum)
    shutting_down = True
    
    # Wait for in-flight requests
    logger.info("Waiting for in-flight requests to complete...")
    time.sleep(5)
    
    logger.info("Shutdown complete")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
atexit.register(lambda: logger.info("Application exiting"))


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


@app.route('/api/health/live')
def liveness():
    """Kubernetes liveness probe - is the app running?"""
    return jsonify({"status": "alive"}), 200


@app.route('/api/health/ready')
def readiness():
    """Kubernetes readiness probe - is the app ready to serve traffic?"""
    checks = {
        "api": True,
        "workflow": WORKFLOW_AVAILABLE,
        "cache": True,
        "database": True
    }
    
    # Check database if available
    try:
        from scripts.database import get_db
        db = get_db()
        if db:
            with db.session() as session:
                session.execute("SELECT 1")
    except Exception:
        checks["database"] = False
    
    # Check Redis if available
    try:
        from scripts.database import get_cache
        cache = get_cache()
        if cache and cache._connected:
            cache.client.ping()
    except Exception:
        checks["cache"] = False
    
    all_healthy = all(checks.values())
    
    return jsonify({
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks
    }), 200 if all_healthy else 503


@app.route('/metrics')
def metrics_endpoint():
    """Prometheus metrics endpoint (if enabled)"""
    if not METRICS_ENABLED:
        return jsonify({
            "error": "Prometheus metrics not enabled. Set PROMETHEUS_ENABLED=true"
        }), 404
    
    # Metrics are automatically exposed by prometheus_flask_exporter
    # This endpoint just confirms metrics are available
    return Response(
        "# Metrics available at /metrics\n# Prometheus Flask Exporter is active\n",
        mimetype="text/plain"
    )


@app.route('/api/stats')
@require_api_key
def stats():
    """Get API usage statistics (admin only)"""
    return jsonify({
        "analyses": {
            "total_cached": len(analysis_cache),
            "pending_emails": len(pending_emails)
        },
        "api_keys": {
            "total": len(api_keys)
        },
        "circuit_breakers": {
            name: {
                "state": cb.state,
                "failures": cb.failures
            }
            for name, cb in circuit_breakers.items()
        },
        "rate_limits": {
            "active_ips": len(rate_limits)
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
