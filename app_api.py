#!/usr/bin/env python3
"""
Production-Ready SearXNG API Wrapper
Optimized for MVP production use with predefined search modes.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
from urllib.parse import urlencode
import logging
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import time
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for production use

# Configuration
SEARXNG_BASE_URL = os.getenv('SEARXNG_BASE_URL', 'http://searxng:8080/')
API_PORT = int(os.getenv('API_PORT', '5001'))
VERIFY_SSL = os.getenv('VERIFY_SSL', 'false').lower() == 'true'
MAX_RESULTS_LIMIT = int(os.getenv('MAX_RESULTS_LIMIT', '50'))
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', '1000'))
RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', '3600'))  # 1 hour

class SearchMode(Enum):
    """Predefined search modes with optimized engine combinations"""
    GENERAL = "general"
    ACADEMIC = "academic"
    NEWS = "news"
    IMAGES = "images"
    VIDEOS = "videos"
    SOCIAL = "social"
    SHOPPING = "shopping"
    TECH = "tech"
    LOCAL = "local"
    FAST = "fast"

@dataclass
class SearchModeConfig:
    """Configuration for search modes"""
    engines: List[str]
    categories: List[str]
    description: str
    max_results: int = 10
    safesearch: int = 1

# Predefined search mode configurations
SEARCH_MODES = {
    SearchMode.GENERAL: SearchModeConfig(
        engines=['google', 'bing', 'duckduckgo'],
        categories=['general'],
        description="General web search using major search engines",
        max_results=15
    ),
    SearchMode.ACADEMIC: SearchModeConfig(
        engines=['google scholar', 'arxiv', 'pubmed', 'semantic scholar'],
        categories=['science'],
        description="Academic papers and scholarly content",
        max_results=20
    ),
    SearchMode.NEWS: SearchModeConfig(
        engines=['google news', 'bing news', 'yahoo news', 'reuters'],
        categories=['news'],
        description="Latest news and current events",
        max_results=25
    ),
    SearchMode.IMAGES: SearchModeConfig(
        engines=['google images', 'bing images', 'flickr', 'unsplash'],
        categories=['images'],
        description="Image search across multiple platforms",
        max_results=30
    ),
    SearchMode.VIDEOS: SearchModeConfig(
        engines=['youtube', 'vimeo', 'dailymotion'],
        categories=['videos'],
        description="Video content search",
        max_results=20
    ),
    SearchMode.SOCIAL: SearchModeConfig(
        engines=['twitter', 'reddit', 'mastodon'],
        categories=['social media'],
        description="Social media and community content",
        max_results=25
    ),
    SearchMode.SHOPPING: SearchModeConfig(
        engines=['amazon', 'ebay', 'shopping'],
        categories=['shopping'],
        description="Product search and shopping",
        max_results=20
    ),
    SearchMode.TECH: SearchModeConfig(
        engines=['github', 'stackoverflow', 'hacker news'],
        categories=['it'],
        description="Technical content and development resources",
        max_results=20
    ),
    SearchMode.LOCAL: SearchModeConfig(
        engines=['google maps', 'openstreetmap', 'yelp'],
        categories=['map'],
        description="Local business and location search",
        max_results=15
    ),
    SearchMode.FAST: SearchModeConfig(
        engines=['duckduckgo'],
        categories=['general'],
        description="Fast single-engine search for quick results",
        max_results=10
    )
}

# Simple rate limiting
request_counts = {}

def rate_limit(f):
    """Simple rate limiting decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        current_time = time.time()
        
        if client_ip not in request_counts:
            request_counts[client_ip] = []
        
        # Clean old requests
        request_counts[client_ip] = [
            req_time for req_time in request_counts[client_ip]
            if current_time - req_time < RATE_LIMIT_WINDOW
        ]
        
        # Check rate limit
        if len(request_counts[client_ip]) >= RATE_LIMIT_REQUESTS:
            return jsonify({
                "error": "Rate limit exceeded",
                "limit": RATE_LIMIT_REQUESTS,
                "window": RATE_LIMIT_WINDOW
            }), 429
        
        request_counts[client_ip].append(current_time)
        return f(*args, **kwargs)
    
    return decorated_function

class SearXNGAPI:
    """Production-ready SearXNG API wrapper"""
    
    def __init__(self, base_url: str, verify_ssl: bool = False):
        self.base_url = base_url
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        
        # Configure session
        self.session.headers.update({
            'User-Agent': 'SearXNG-API-Wrapper/1.0.0',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate'
        })
        
        if not verify_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def search(self, query: str, mode: Optional[SearchMode] = None, 
               engines: Optional[List[str]] = None, categories: Optional[List[str]] = None,
               language: str = 'en', pageno: int = 1, safesearch: int = 1,
               time_range: Optional[str] = None, max_results: int = 10,
               **kwargs) -> Dict[str, Any]:
        """
        Perform a search using SearXNG with mode support
        
        Args:
            query: Search query
            mode: Predefined search mode (overrides engines/categories)
            engines: List of search engines
            categories: List of categories
            language: Search language
            pageno: Page number
            safesearch: Safe search level (0=off, 1=moderate, 2=strict)
            time_range: Time range filter
            max_results: Maximum number of results
            
        Returns:
            Search results dictionary
        """
        try:
            # Apply search mode configuration
            if mode and mode in SEARCH_MODES:
                mode_config = SEARCH_MODES[mode]
                engines = mode_config.engines
                categories = mode_config.categories
                max_results = min(max_results, mode_config.max_results)
                safesearch = mode_config.safesearch
            
            # Validate parameters
            max_results = min(max_results, MAX_RESULTS_LIMIT)
            
            params = {
                'q': query,
                'format': 'json',
                'pageno': pageno,
                'safesearch': safesearch,
                'language': language
            }
            
            if engines:
                params['engines'] = ','.join(engines)
            if categories:
                params['categories'] = ','.join(categories)
            if time_range:
                params['time_range'] = time_range
            
            # Add custom parameters
            params.update(kwargs)
            
            url = f"{self.base_url}/search"
            logger.info(f"Search request: {query} (mode: {mode}, engines: {engines})")
            
            response = self.session.get(
                url, 
                params=params,
                verify=self.verify_ssl, 
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Limit results
            if 'results' in data and len(data['results']) > max_results:
                data['results'] = data['results'][:max_results]
            
            # Add metadata
            data['metadata'] = {
                'query': query,
                'mode': mode.value if mode else None,
                'engines_used': engines,
                'total_results': len(data.get('results', [])),
                'search_time': response.elapsed.total_seconds(),
                'timestamp': time.time()
            }
            
            return data
                
        except requests.exceptions.Timeout:
            logger.error(f"Search timeout for query: {query}")
            return {"error": "Search request timed out"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Search request failed: {e}")
            return {"error": f"Search request failed: {str(e)}"}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            return {"error": "Invalid response format"}
        except Exception as e:
            logger.error(f"Unexpected error in search: {e}")
            return {"error": f"Internal search error: {str(e)}"}
    
    def get_config(self) -> Dict[str, Any]:
        """Get SearXNG configuration"""
        try:
            url = f"{self.base_url}/config"
            response = self.session.get(url, verify=self.verify_ssl, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Config request failed: {e}")
            return {"error": f"Config request failed: {str(e)}"}
    
    def health_check(self) -> Dict[str, Any]:
        """Check SearXNG health"""
        try:
            url = f"{self.base_url}/healthz"
            response = self.session.get(url, verify=self.verify_ssl, timeout=5)
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time": response.elapsed.total_seconds(),
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

# Initialize API wrapper
searxng = SearXNGAPI(SEARXNG_BASE_URL, VERIFY_SSL)

# API Routes

@app.route('/api/search', methods=['GET', 'POST'])
@rate_limit
def search():
    """Enhanced search endpoint with mode support"""
    try:
        # Handle both GET and POST requests
        if request.method == 'POST':
            data = request.get_json() or {}
            query = data.get('q', '')
            mode = data.get('mode')
            engines = data.get('engines')
            max_results = data.get('max_results', 10)
            language = data.get('language', 'en')
            safesearch = data.get('safesearch', 1)
            time_range = data.get('time_range')
            pageno = data.get('pageno', 1)
        else:
            query = request.args.get('q', '')
            mode = request.args.get('mode')
            engines = request.args.get('engines', '').split(',') if request.args.get('engines') else None
            max_results = int(request.args.get('max_results', '10'))
            language = request.args.get('language', 'en')
            safesearch = int(request.args.get('safesearch', '1'))
            time_range = request.args.get('time_range')
            pageno = int(request.args.get('pageno', '1'))
        
        if not query:
            return jsonify({"error": "Query parameter 'q' is required"}), 400
        
        # Validate mode
        search_mode = None
        if mode:
            try:
                search_mode = SearchMode(mode)
            except ValueError:
                return jsonify({
                    "error": f"Invalid search mode: {mode}",
                    "available_modes": [m.value for m in SearchMode]
                }), 400
        
        # Perform search
        result = searxng.search(
            query=query,
            mode=search_mode,
            engines=engines,
            language=language,
            pageno=pageno,
            safesearch=safesearch,
            time_range=time_range,
            max_results=max_results
        )
        
        if "error" in result:
            return jsonify(result), 500
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({"error": f"Invalid parameter: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/modes', methods=['GET'])
def get_search_modes():
    """Get available search modes"""
    try:
        modes = {}
        for mode, config in SEARCH_MODES.items():
            modes[mode.value] = {
                "description": config.description,
                "engines": config.engines,
                "categories": config.categories,
                "max_results": config.max_results,
                "safesearch": config.safesearch
            }
        
        return jsonify({
            "modes": modes,
            "default_mode": SearchMode.GENERAL.value
        })
    except Exception as e:
        logger.error(f"Modes error: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        searxng_health = searxng.health_check()
        api_health = {
            "api_status": "healthy",
            "searxng_status": searxng_health.get("status", "unknown"),
            "timestamp": time.time(),
            "version": "1.0.0"
        }
        
        if searxng_health.get("status") == "unhealthy":
            api_health["api_status"] = "degraded"
            return jsonify(api_health), 503
        
        return jsonify(api_health)
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            "api_status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get API and SearXNG configuration"""
    try:
        searxng_config = searxng.get_config()
        
        api_config = {
            "api_version": "1.0.0",
            "max_results_limit": MAX_RESULTS_LIMIT,
            "request_timeout": REQUEST_TIMEOUT,
            "rate_limit": {
                "requests": RATE_LIMIT_REQUESTS,
                "window": RATE_LIMIT_WINDOW
            },
            "search_modes": len(SEARCH_MODES),
            "searxng_url": SEARXNG_BASE_URL
        }
        
        return jsonify({
            "api_config": api_config,
            "searxng_config": searxng_config
        })
    except Exception as e:
        logger.error(f"Config error: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/engines', methods=['GET'])
def get_engines():
    """Get available engines by category"""
    try:
        config = searxng.get_config()
        if "error" in config:
            return jsonify(config), 500
        
        engines_by_category = {}
        all_engines = []
        
        if "engines" in config:
            for engine in config["engines"]:
                if engine.get("enabled", False):
                    engine_info = {
                        "name": engine.get("name", ""),
                        "shortcut": engine.get("shortcut", ""),
                        "categories": engine.get("categories", []),
                        "timeout": engine.get("timeout", 3.0)
                    }
                    
                    all_engines.append(engine_info)
                    
                    # Group by category
                    for category in engine_info["categories"]:
                        if category not in engines_by_category:
                            engines_by_category[category] = []
                        engines_by_category[category].append(engine_info)
        
        return jsonify({
            "engines_by_category": engines_by_category,
            "all_engines": all_engines,
            "total_engines": len(all_engines)
        })
    except Exception as e:
        logger.error(f"Engines error: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get API usage statistics"""
    try:
        total_requests = sum(len(reqs) for reqs in request_counts.values())
        active_ips = len(request_counts)
        
        return jsonify({
            "total_requests": total_requests,
            "active_ips": active_ips,
            "available_modes": len(SEARCH_MODES),
            "uptime": time.time(),
            "version": "1.0.0"
        })
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api', methods=['GET'])
def api_info():
    """API information and documentation"""
    return jsonify({
        "name": "SearXNG API Wrapper",
        "version": "1.0.0",
        "description": "Production-ready API wrapper for SearXNG search engine",
        "endpoints": {
            "POST|GET /api/search": "Perform search with mode support",
            "GET /api/modes": "Get available search modes",
            "GET /api/health": "Health check",
            "GET /api/config": "Get configuration",
            "GET /api/engines": "Get available engines",
            "GET /api/stats": "Get usage statistics",
            "GET /api": "API information"
        },
        "search_modes": [mode.value for mode in SearchMode],
        "examples": {
            "general_search": "/api/search?q=python&mode=general&max_results=10",
            "academic_search": "/api/search?q=machine learning&mode=academic",
            "news_search": "/api/search?q=latest news&mode=news",
            "image_search": "/api/search?q=sunset&mode=images"
        }
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({"error": "Rate limit exceeded"}), 429

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    print("=== Production SearXNG API Wrapper ===")
    print(f"Version: 1.0.0")
    print(f"SearXNG URL: {SEARXNG_BASE_URL}")
    print(f"API Port: {API_PORT}")
    print(f"SSL Verification: {VERIFY_SSL}")
    print(f"Max Results Limit: {MAX_RESULTS_LIMIT}")
    print(f"Rate Limit: {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW}s")
    
    # Test connection
    print("\nTesting SearXNG connection...")
    health = searxng.health_check()
    print(f"Health Status: {health}")
    
    print(f"\nAvailable Search Modes ({len(SEARCH_MODES)}):")
    for mode, config in SEARCH_MODES.items():
        print(f"  {mode.value}: {config.description}")
    
    print(f"\nStarting server on http://0.0.0.0:{API_PORT}")
    app.run(host='0.0.0.0', port=API_PORT, debug=False)