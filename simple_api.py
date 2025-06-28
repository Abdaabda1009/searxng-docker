#!/usr/bin/env python3
"""
Simple API Wrapper for SearXNG
This provides a clean API interface for your external application.
"""

from flask import Flask, request, jsonify
import requests
import json
from urllib.parse import urlencode
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
SEARXNG_BASE_URL = "https://localhost"
VERIFY_SSL = False  # Set to True in production

class SearXNGAPI:
    """Wrapper class for SearXNG API calls"""
    
    def __init__(self, base_url, verify_ssl=False):
        self.base_url = base_url
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        if not verify_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def search(self, query, engines=None, categories=None, language='en', 
          pageno=1, safesearch=1, time_range=None, format="json", 
          max_results=10, **kwargs):
        """Perform a search using SearXNG"""
        try:
            params = {
                'q': query,
                'format': format,
                'max_results': max_results,
                'pageno': pageno,
                'safesearch': safesearch,
                'language': language
            }
            
            if engines:
                params['engines'] = ','.join(engines) if isinstance(engines, list) else engines
            if categories:
                params['categories'] = ','.join(categories) if isinstance(categories, list) else categories
            if time_range:
                params['time_range'] = time_range
            
            # Add any additional parameters
            params.update(kwargs)
            
            url = f"{self.base_url}/search?{urlencode(params)}"
            logger.info(f"Making request to: {url}")
            
            response = self.session.get(url, verify=self.verify_ssl, timeout=30)
            response.raise_for_status()
            
            if format == "json":
                return response.json()
            else:
                return response.text
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return {"error": f"Request failed: {str(e)}"}
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return {"error": f"Invalid JSON response: {str(e)}"}
    
    def get_config(self):
        """Get SearXNG configuration"""
        try:
            url = f"{self.base_url}/config"
            response = self.session.get(url, verify=self.verify_ssl, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Config request failed: {e}")
            return {"error": f"Config request failed: {str(e)}"}
    
    def health_check(self):
        """Check if SearXNG is healthy"""
        try:
            url = f"{self.base_url}/healthz"
            response = self.session.get(url, verify=self.verify_ssl, timeout=5)
            return {"status": "healthy" if response.status_code == 200 else "unhealthy"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

# Initialize the SearXNG API wrapper
searxng = SearXNGAPI(SEARXNG_BASE_URL, VERIFY_SSL)

@app.route('/api/search', methods=['GET'])
def search():
    """Search endpoint for your application"""
    try:
        # Get and validate parameters
        query = request.args.get('q', '')
        engines = request.args.get('engines', '')
        categories = request.args.get('categories', '')
        language = request.args.get('language', 'en')
        format_type = request.args.get('format', 'json')
        safesearch = request.args.get('safesearch', '1')
        time_range = request.args.get('time_range')
        pageno = request.args.get('pageno', '1')
        max_results = request.args.get('max_results', '10')

        if not query:
            return jsonify({"error": "Query parameter 'q' is required"}), 400

        # Validate and convert numeric parameters
        try:
            max_results = int(max_results)
            pageno = int(pageno)
            safesearch = int(safesearch)
        except ValueError:
            return jsonify({"error": "Invalid numeric parameter"}), 400

        if safesearch not in (0, 1, 2):
            return jsonify({"error": "Invalid safesearch value"}), 400

        if time_range and time_range not in ('day', 'week', 'month', 'year'):
            return jsonify({"error": "Invalid time range"}), 400

        engine_list = [e.strip() for e in engines.split(',')] if engines else None
        category_list = [c.strip() for c in categories.split(',')] if categories else None

        # Perform search with all parameters
        result = searxng.search(
            query=query,
            engines=engine_list,
            categories=category_list,
            language=language,
            pageno=pageno,
            safesearch=safesearch,
            time_range=time_range,
            format=format_type,
            max_results=max_results
        )
        
        if "error" in result:
            return jsonify(result), 500
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get SearXNG configuration"""
    try:
        config = searxng.get_config()
        if "error" in config:
            return jsonify(config), 500
        return jsonify(config)
    except Exception as e:
        logger.error(f"Config error: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        health_status = searxng.health_check()
        return jsonify(health_status)
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route('/api/engines', methods=['GET'])
def get_engines():
    """Get available search engines"""
    try:
        config = searxng.get_config()
        if "error" in config:
            return jsonify(config), 500
        
        engines = []
        if "engines" in config:
            for engine in config["engines"]:
                if engine.get("enabled", False):
                    engines.append({
                        "name": engine.get("name", ""),
                        "shortcut": engine.get("shortcut", ""),
                        "categories": engine.get("categories", []),
                        "timeout": engine.get("timeout", 3.0)
                    })
        
        return jsonify({"engines": engines})
    except Exception as e:
        logger.error(f"Engines error: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        "name": "SearXNG API Wrapper",
        "version": "1.0.0",
        "description": "Simple API wrapper for SearXNG search engine",
        "endpoints": {
            "/api/search": "Perform a search (GET, params: q, engines, max_results, format)",
            "/api/config": "Get SearXNG configuration",
            "/api/health": "Health check",
            "/api/engines": "Get available search engines",
            "/api": "This information"
        },
        "example": {
            "search": "/api/search?q=python&engines=google,bing&max_results=5",
            "config": "/api/config",
            "health": "/api/health"
        }
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    print("=== SearXNG API Wrapper ===")
    print("Starting API server...")
    print(f"Connecting to SearXNG at: {SEARXNG_BASE_URL}")
    
    # Test connection
    health = searxng.health_check()
    print(f"Health check: {health}")
    
    print("\nAvailable endpoints:")
    print("  GET /api/search?q=<query>&engines=<engine1,engine2>&max_results=<number>")
    print("  GET /api/config")
    print("  GET /api/health")
    print("  GET /api/engines")
    print("  GET /api")
    
    print("\nExample usage:")
    print("  curl 'http://localhost:8080/api/search?q=python&engines=google&max_results=5'")
    
    print("\nStarting server on http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=True) 