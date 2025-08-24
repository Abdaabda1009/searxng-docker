#!/usr/bin/env python3
"""
Production-Ready YouTube API Wrapper (FastAPI Version)
Maintains compatibility with SearXNG API structure while adding YouTube-specific features
"""

from fastapi import FastAPI, Request, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json
from urllib.parse import urlencode
import logging
import os
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import time
import re
from datetime import datetime
import uvicorn

# --- Configuration ---
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variables
SEARXNG_BASE_URL = os.getenv('SEARXNG_BASE_URL', 'https://search.nexalexica.com/')
API_PORT = int(os.getenv('API_PORT', '5002'))
VERIFY_SSL = os.getenv('VERIFY_SSL', 'false').lower() == 'true'
MAX_RESULTS_LIMIT = int(os.getenv('MAX_RESULTS_LIMIT', '500'))
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', '1000'))
RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', '3600'))
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', 'AIzaSyA9pRLOWax2I8ZSQ1ZbaPnUkhjOZyvltzk')

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://172.20.10.2:3000",
    "https://nexalexica.com",
    "https://app.nexalexica.com",
    "http://192.168.1.105:5002"
]

# --- Pydantic Data Models ---
class YouTubeVideo(BaseModel):
    video_id: str
    title: str
    author: str
    channel_id: str
    thumbnail: str
    length: Optional[str] = None
    views: Optional[str] = None
    publish_date: Optional[str] = None
    description: Optional[str] = None
    url: str
    embed_url: str
    likes: Optional[str] = None
    channel_avatar: Optional[str] = None

# --- API and Processing Logic ---
class YouTubeAPI:
    """Asynchronous YouTube API handler with SearXNG compatibility"""
    def __init__(self, base_url: str, verify_ssl: bool = True):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(verify=verify_ssl, timeout=REQUEST_TIMEOUT)

    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        params = {
            'q': query,
            'format': 'json',
            'engines': 'youtube',
            'safesearch': kwargs.get('safesearch', '1'),
            'pageno': kwargs.get('page', 1)
        }
        # Use MAX_RESULTS_LIMIT as the upper bound for results_per_page
        params['results_per_page'] = min(kwargs.get('results_per_page', 100), MAX_RESULTS_LIMIT)

        param_mapping = {'duration': 'duration', 'time_range': 'time_range', 'sort_by': 'sort'}
        for key, param_name in param_mapping.items():
            if value := kwargs.get(key):
                params[param_name] = value

        logger.info(f"Requesting SearXNG with params: {params}")
        try:
            response = await self.client.get(f"{self.base_url}/search", params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")
            return {"error": f"Search failed with status code: {e.response.status_code}"}
        except (json.JSONDecodeError, httpx.RequestError) as e:
            logger.error(f"Request or JSON parsing error: {e}")
            return {"error": "Failed to communicate with the search API"}


class BaseProcessor:
    @classmethod
    def extract_video_id(cls, url: str) -> Optional[str]:
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/v/([a-zA-Z0-9_-]{11})',
        ]
        for pattern in patterns:
            if match := re.search(pattern, url):
                return match.group(1)
        return None

    @classmethod
    def format_metadata(cls, value: Any, metadata_type: str) -> Optional[str]:
        # (This method re"main"s unchanged as it contains no I/O)
        if not value: return None
        if metadata_type == "duration":
            if isinstance(value, (int, float)):
                mins, secs = divmod(int(value), 60); return f"{mins}:{secs:02d}"
            return str(value)
        elif metadata_type == "views":
            if isinstance(value, (int, float)):
                if value >= 1_000_000: return f"{value / 1_000_000:.1f}M views"
                if value >= 1_000: return f"{value / 1_000:.1f}K views"
                return f"{value} views"
            return str(value)
        elif metadata_type == "date":
            if isinstance(value, str):
                try:
                    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    return dt.strftime("%Y-%m-%d")
                except ValueError: return value
            return str(value)
        return str(value)


class YouTubeProcessor(BaseProcessor):
    YT_API_URL = "https://www.googleapis.com/youtube/v3"

    @classmethod
    async def get_channel_avatar(cls, channel_id: str, client: httpx.AsyncClient) -> Optional[str]:
        if not YOUTUBE_API_KEY: return None
        try:
            params = {"id": channel_id, "part": "snippet", "key": YOUTUBE_API_KEY}
            r = await client.get(f"{cls.YT_API_URL}/channels", params=params)
            r.raise_for_status()
            data = r.json()
            if items := data.get("items", []):
                thumbnails = items[0].get("snippet", {}).get("thumbnails", {})
                return thumbnails.get("default", {}).get("url")
        except Exception as e:
            logger.error(f"Error fetching channel avatar: {e}")
        return None

    @classmethod
    async def get_video_stats(cls, video_id: str, client: httpx.AsyncClient) -> Dict[str, Any]:
        stats = {"likes": None, "channel_avatar": None}
        if not YOUTUBE_API_KEY:
            logger.warning("No YOUTUBE_API_KEY set. Skipping enrichment.")
            return stats
        try:
            params = {"id": video_id, "part": "statistics,snippet", "key": YOUTUBE_API_KEY}
            r = await client.get(f"{cls.YT_API_URL}/videos", params=params)
            r.raise_for_status()
            data = r.json()
            if items := data.get("items", []):
                item = items[0]
                stats["likes"] = item.get("statistics", {}).get("likeCount")
                if channel_id := item.get("snippet", {}).get("channelId"):
                    stats["channel_avatar"] = await cls.get_channel_avatar(channel_id, client)
        except Exception as e:
            logger.error(f"Error fetching likes/avatar for video {video_id}: {e}")
        return stats

    @classmethod
    async def process_result(cls, result: Dict[str, Any], client: httpx.AsyncClient) -> Optional[YouTubeVideo]:
        try:
            url = result.get("url", "")
            if not (video_id := cls.extract_video_id(url)):
                return None

            video_data = {
                "video_id": video_id,
                "title": result.get("title", ""),
                "author": result.get("author", "Unknown"),
                "channel_id": result.get("channel_id", ""),
                "thumbnail": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
                "length": cls.format_metadata(result.get("length"), "duration"),
                "views": cls.format_metadata(result.get("views"), "views"),
                "publish_date": cls.format_metadata(result.get("publishedDate"), "date"),
                "description": (result.get("content", "")[:200] + "...") if result.get("content") else "",
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "embed_url": f"https://www.youtube.com/embed/{video_id}"
            }

            extra_stats = await cls.get_video_stats(video_id, client)
            video_data.update(extra_stats)

            return YouTubeVideo(**video_data)
        except Exception as e:
            logger.error(f"Processing error: {e}")
            return None

# --- FastAPI App Initialization ---
app = FastAPI(
    title="YouTube API Wrapper",
    description="A production-ready API wrapper for YouTube, compatible with the SearXNG structure.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize API components
youtube_api = YouTubeAPI(SEARXNG_BASE_URL, VERIFY_SSL)
processor = YouTubeProcessor()
http_client = httpx.AsyncClient(timeout=10) # Shared client for enrichment

# --- Rate Limiting Dependency ---
request_counts: Dict[str, List[float]] = {}

async def rate_limit_dependency(request: Request):
    client_ip = request.client.host
    current_time = time.time()
    
    request_counts.setdefault(client_ip, [])
    # Remove timestamps outside the window
    request_counts[client_ip] = [t for t in request_counts[client_ip] if current_time - t < RATE_LIMIT_WINDOW]
    
    if len(request_counts[client_ip]) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
    request_counts[client_ip].append(current_time)

# --- API Endpoints ---
@app.get(
    "/api/youtube/search",
    response_model=Dict[str, Any],
    summary="Search for YouTube videos",
    dependencies=[Depends(rate_limit_dependency)]
)
async def youtube_search(
    q: str = Query(..., description="The search query."),
    page: int = Query(1, ge=1, description="Page number."),
    results_per_page: int = Query(50, ge=1, le=MAX_RESULTS_LIMIT, description="Number of results per page."),
    # Add other filters as needed
    duration: Optional[str] = Query(None, description="Filter by duration (e.g., 'short', 'long')"),
    time_range: Optional[str] = Query(None, description="Filter by upload date (e.g., 'today', 'this_week')"),
    sort_by: Optional[str] = Query(None, description="Sorting order (e.g., 'relevance', 'rating')")
):
    start_time = time.time()
    
    search_params = {
        'page': page,
        'results_per_page': results_per_page,
        'duration': duration,
        'time_range': time_range,
        'sort_by': sort_by
    }
    # Filter out None values before passing to search
    search_params = {k: v for k, v in search_params.items() if v is not None}
    
    results = await youtube_api.search(q, **search_params)
    
    if 'error' in results:
        raise HTTPException(status_code=502, detail=results['error'])

    processed = []
    for result in results.get('results', []):
        if video := await processor.process_result(result, http_client):
            processed.append(video)

    return {
        "status": "success",
        "results": processed,
        "metadata": {
            "query": q,
            "count": len(processed),
            "time": f"{time.time() - start_time:.3f}s",
            "engine": "youtube"
        },
        "suggestions": results.get('suggestions', []),
        "corrections": results.get('corrections', {})
    }

@app.get(
    "/api/youtube/video/{video_id}",
    response_model=Dict[str, Any],
    summary="Get details for a single video",
    dependencies=[Depends(rate_limit_dependency)]
)
async def video_details(video_id: str):
    # This is an approximation. A direct fetch would be better if SearXNG supported it.
    results = await youtube_api.search(f"site:youtube.com \"{video_id}\"")
    for result in results.get('results', []):
        if (extracted_id := processor.extract_video_id(result.get("url", ""))) and extracted_id == video_id:
            if video := await processor.process_result(result, http_client):
                return {"status": "success", "result": video}
    raise HTTPException(status_code=404, detail="Video not found")


@app.get("/api/youtube/health", summary="Health check endpoint")
async def health_check():
    try:
        test = await youtube_api.search("test", results_per_page=1)
        if test.get('error'):
            raise HTTPException(status_code=503, detail={"status": "degraded", "reason": test['error']})
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail={"status": "unhealthy", "error": str(e)})


@app.get("/api/youtube/config", summary="Configuration endpoint")
def get_config():
    return {
        "max_results": MAX_RESULTS_LIMIT,
        "timeout": REQUEST_TIMEOUT,
        "rate_limit": {
            "requests": RATE_LIMIT_REQUESTS,
            "window": RATE_LIMIT_WINDOW
        }
    }


# --- Server Startup ---
if __name__ == '__main__':
    logger.info("Starting YouTube API with SearXNG compatibility (FastAPI)...")
    debug_mode = os.getenv('DEBUG', 'false').lower() == 'true'
    uvicorn.run("Youtube:app", host='0.0.0.0', port=API_PORT, reload=debug_mode)