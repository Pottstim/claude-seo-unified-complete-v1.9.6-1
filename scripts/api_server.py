#!/usr/bin/env python3
"""
REST API server for claude-seo-unified
Production-ready Flask API with authentication and rate limiting
"""

__version__ = "1.9.7-unified"

import os
import json
import logging
from datetime import datetime, timezone
from functools import wraps
from typing import Dict, Any, Optional

from flask import Flask, request, jsonify, g
from flask_cors import CORS
import hashlib
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['JSON_SORT_KEYS'] = False

# Rate limiting (simple in-memory - use Redis for production)
rate_limit_store: Dict[str, list] = {}
RATE_LIMIT_REQUESTS = 60  # requests per window
RATE_LIMIT_WINDOW = 60    # seconds

# API keys (load from environment or config)
API_KEYS = {}
def load_api_keys():
    """Load API keys from environment"""
    global API_KEYS
    keys_str = os.environ.get('SEO_API_KEYS', '')
    if keys_str:
        for key in keys_str.split(','):
            key = key.strip()
            if key:
                API_KEYS[hashlib.sha256(key.encode()).hexdigest()[:16]] = key
    # Also check for single key
    single_key = os.environ.get('SEO_API_KEY')
    if single_key:
        API_KEYS[hashlib.sha256(single_key.encode()).hexdigest()[:16]] = single_key

load_api_keys()


def check_rate_limit(client_id: str) -> bool:
    """Check if client is within rate limit"""
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW
    
    if client_id not in rate_limit_store:
        rate_limit_store[client_id] = []
    
    # Clean old entries
    rate_limit_store[client_id] = [
        t for t in rate_limit_store[client_id] if t > window_start
    ]
    
    if len(rate_limit_store[client_id]) >= RATE_LIMIT_REQUESTS:
        return False
    
    rate_limit_store[client_id].append(now)
    return True


def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip auth if no keys configured (dev mode)
        if not API_KEYS:
            g.client_id = 'dev'
            return f(*args, **kwargs)
        
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({
                'error': 'Missing or invalid Authorization header',
                'hint': 'Use: Authorization: Bearer <your-api-key>'
            }), 401
        
        api_key = auth_header[7:]
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
        
        if key_hash not in API_KEYS:
            return jsonify({'error': 'Invalid API key'}), 401
        
        g.client_id = key_hash
        return f(*args, **kwargs)
    return decorated_function


@app.before_request
def before_request():
    """Check rate limit before each request"""
    client_id = getattr(g, 'client_id', request.remote_addr)
    
    if not check_rate_limit(client_id):
        return jsonify({
            'error': 'Rate limit exceeded',
            'retry_after': RATE_LIMIT_WINDOW
        }), 429


# Import workflow functions
try:
    from run_skill_workflow import (
        run_audit,
        run_technical,
        run_content,
        run_schema,
        run_drift_baseline,
        run_drift_compare,
        __version__
    )
    WORKFLOW_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Workflow module not available: {e}")
    WORKFLOW_AVAILABLE = False


# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for load balancers"""
    return jsonify({
        'status': 'healthy',
        'version': __version__,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'workflows': WORKFLOW_AVAILABLE
    })


# API info endpoint
@app.route('/api/v1', methods=['GET'])
def api_info():
    """API information and available endpoints"""
    return jsonify({
        'name': 'claude-seo-unified-api',
        'version': __version__,
        'endpoints': {
            'POST /api/v1/audit': 'Full SEO audit',
            'POST /api/v1/technical': 'Technical SEO analysis',
            'POST /api/v1/content': 'Content quality analysis',
            'POST /api/v1/schema': 'Schema markup analysis',
            'POST /api/v1/drift/baseline': 'Capture drift baseline',
            'POST /api/v1/drift/compare': 'Compare against baseline',
            'GET /health': 'Health check'
        },
        'authentication': 'Bearer token required' if API_KEYS else 'None (dev mode)'
    })


# Audit endpoint
@app.route('/api/v1/audit', methods=['POST'])
@require_api_key
def api_audit():
    """Run full SEO audit"""
    if not WORKFLOW_AVAILABLE:
        return jsonify({'error': 'Workflow engine not available'}), 503
    
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({
            'error': 'Missing required field: url',
            'example': {'url': 'https://example.com'}
        }), 400
    
    url = data['url']
    use_cache = data.get('use_cache', True)
    refresh = data.get('refresh', False)
    max_recommendations = data.get('max_recommendations', 10)
    
    try:
        result = run_audit(
            url,
            use_cache=use_cache,
            refresh=refresh,
            max_recommendations=max_recommendations
        )
        return jsonify(result)
    except Exception as e:
        logger.exception(f"Audit failed for {url}")
        return jsonify({'error': str(e)}), 500


# Technical analysis endpoint
@app.route('/api/v1/technical', methods=['POST'])
@require_api_key
def api_technical():
    """Run technical SEO analysis"""
    if not WORKFLOW_AVAILABLE:
        return jsonify({'error': 'Workflow engine not available'}), 503
    
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'Missing required field: url'}), 400
    
    try:
        result = run_technical(data['url'])
        return jsonify(result)
    except Exception as e:
        logger.exception(f"Technical analysis failed for {data['url']}")
        return jsonify({'error': str(e)}), 500


# Content analysis endpoint
@app.route('/api/v1/content', methods=['POST'])
@require_api_key
def api_content():
    """Run content quality analysis"""
    if not WORKFLOW_AVAILABLE:
        return jsonify({'error': 'Workflow engine not available'}), 503
    
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'Missing required field: url'}), 400
    
    try:
        result = run_content(data['url'])
        return jsonify(result)
    except Exception as e:
        logger.exception(f"Content analysis failed for {data['url']}")
        return jsonify({'error': str(e)}), 500


# Schema analysis endpoint
@app.route('/api/v1/schema', methods=['POST'])
@require_api_key
def api_schema():
    """Run schema markup analysis"""
    if not WORKFLOW_AVAILABLE:
        return jsonify({'error': 'Workflow engine not available'}), 503
    
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'Missing required field: url'}), 400
    
    try:
        result = run_schema(data['url'])
        return jsonify(result)
    except Exception as e:
        logger.exception(f"Schema analysis failed for {data['url']}")
        return jsonify({'error': str(e)}), 500


# Drift baseline endpoint
@app.route('/api/v1/drift/baseline', methods=['POST'])
@require_api_key
def api_drift_baseline():
    """Capture drift monitoring baseline"""
    if not WORKFLOW_AVAILABLE:
        return jsonify({'error': 'Workflow engine not available'}), 503
    
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'Missing required field: url'}), 400
    
    try:
        result = run_drift_baseline(data['url'])
        return jsonify(result)
    except Exception as e:
        logger.exception(f"Drift baseline failed for {data['url']}")
        return jsonify({'error': str(e)}), 500


# Drift compare endpoint
@app.route('/api/v1/drift/compare', methods=['POST'])
@require_api_key
def api_drift_compare():
    """Compare current state against baseline"""
    if not WORKFLOW_AVAILABLE:
        return jsonify({'error': 'Workflow engine not available'}), 503
    
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'Missing required field: url'}), 400
    
    try:
        result = run_drift_compare(data['url'])
        return jsonify(result)
    except Exception as e:
        logger.exception(f"Drift compare failed for {data['url']}")
        return jsonify({'error': str(e)}), 500


# Batch audit endpoint
@app.route('/api/v1/batch', methods=['POST'])
@require_api_key
def api_batch():
    """Run audits on multiple URLs"""
    if not WORKFLOW_AVAILABLE:
        return jsonify({'error': 'Workflow engine not available'}), 503
    
    data = request.get_json()
    if not data or 'urls' not in data:
        return jsonify({
            'error': 'Missing required field: urls',
            'example': {'urls': ['https://example.com', 'https://example.org']}
        }), 400
    
    urls = data['urls']
    if not isinstance(urls, list):
        return jsonify({'error': 'urls must be an array'}), 400
    
    if len(urls) > 10:
        return jsonify({'error': 'Maximum 10 URLs per batch request'}), 400
    
    results = []
    for url in urls:
        try:
            result = run_audit(url, use_cache=True, max_recommendations=5)
            results.append({'url': url, 'success': True, 'data': result})
        except Exception as e:
            results.append({'url': url, 'success': False, 'error': str(e)})
    
    return jsonify({'results': results})


# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(429)
def rate_limited(error):
    return jsonify({'error': 'Rate limit exceeded'}), 429


@app.errorhandler(500)
def internal_error(error):
    logger.exception("Internal server error")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting API server on port {port}")
    logger.info(f"API keys configured: {len(API_KEYS)}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
