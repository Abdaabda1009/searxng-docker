# SearXNG API Integration with Docker

This setup includes a production-ready Python API wrapper for SearXNG, containerized with Docker.

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Caddy     │    │   SearXNG   │    │     API     │
│  (Reverse   │───▶│  (Search    │───▶│  (Python    │
│   Proxy)    │    │  Engine)    │    │  Wrapper)   │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌─────────────┐
                    │    Redis    │
                    │   (Cache)   │
                    └─────────────┘
```

## Services

1. **Caddy** - Reverse proxy and SSL termination
2. **SearXNG** - Search engine backend
3. **API** - Python Flask API wrapper
4. **Redis** - Caching and session storage

## Quick Start

1. **Start all services:**
   ```bash
   ./start.sh
   ```

2. **Or manually:**
   ```bash
   docker-compose up -d --build
   ```

3. **Check status:**
   ```bash
   docker-compose ps
   ```

## API Endpoints

### Base URL: `http://localhost/api`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/search` | GET/POST | Perform search with mode support |
| `/modes` | GET | Get available search modes |
| `/health` | GET | Health check |
| `/config` | GET | Get configuration |
| `/engines` | GET | Get available engines |
| `/stats` | GET | Get usage statistics |
| `/` | GET | API information |

## Search Modes

The API provides predefined search modes for different use cases:

- **general** - General web search (Google, Bing, DuckDuckGo)
- **academic** - Academic papers (Google Scholar, arXiv, PubMed)
- **news** - Latest news (Google News, Reuters, etc.)
- **images** - Image search (Google Images, Flickr, Unsplash)
- **videos** - Video content (YouTube, Vimeo)
- **social** - Social media (Twitter, Reddit, Mastodon)
- **shopping** - Product search (Amazon, eBay)
- **tech** - Technical content (GitHub, Stack Overflow)
- **local** - Local business search (Google Maps, Yelp)
- **fast** - Quick single-engine search (DuckDuckGo)

## Usage Examples

### Basic Search
```bash
curl "http://localhost/api/search?q=python&mode=general"
```

### Academic Search
```bash
curl "http://localhost/api/search?q=machine+learning&mode=academic&max_results=20"
```

### News Search
```bash
curl "http://localhost/api/search?q=latest+news&mode=news&time_range=day"
```

### POST Request
```bash
curl -X POST "http://localhost/api/search" \
  -H "Content-Type: application/json" \
  -d '{"q": "python", "mode": "tech", "max_results": 15}'
```

### Get Available Modes
```bash
curl "http://localhost/api/modes"
```

### Health Check
```bash
curl "http://localhost/api/health"
```

## Configuration

Environment variables can be set in the `.env` file:

```env
# API Configuration
API_PORT=5001
VERIFY_SSL=false
MAX_RESULTS_LIMIT=50
REQUEST_TIMEOUT=30
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# SearXNG Configuration
SEARXNG_HOSTNAME=localhost
SEARXNG_TLS=internal
SEARXNG_UWSGI_WORKERS=4
SEARXNG_UWSGI_THREADS=4
```

## Features

- **Rate Limiting** - Configurable per-IP rate limiting
- **Health Checks** - Built-in health monitoring
- **CORS Support** - Cross-origin request support
- **Error Handling** - Comprehensive error responses
- **Logging** - Structured logging for debugging
- **Security** - Non-root container execution
- **Caching** - Request caching and optimization

## Monitoring

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f searxng
docker-compose logs -f caddy
```

### Health Status
```bash
# API health
curl "http://localhost/api/health"

# Container health
docker-compose ps
```

### Statistics
```bash
curl "http://localhost/api/stats"
```

## Troubleshooting

### API Not Responding
1. Check if containers are running: `docker-compose ps`
2. Check API logs: `docker-compose logs api`
3. Verify health: `curl "http://localhost/api/health"`

### Search Issues
1. Check SearXNG logs: `docker-compose logs searxng`
2. Verify SearXNG health: `curl "http://localhost/healthz"`
3. Check API configuration: `curl "http://localhost/api/config"`

### SSL/HTTPS Issues
1. Check Caddy logs: `docker-compose logs caddy`
2. Verify certificate generation
3. Check hostname configuration

## Development

### Rebuild API Container
```bash
docker-compose build api
docker-compose up -d api
```

### Update Dependencies
```bash
# Edit requirements.txt
docker-compose build --no-cache api
docker-compose up -d api
```

### Local Development
```bash
# Run API locally (outside Docker)
pip install -r requirements.txt
python simple_api.py
```

## Security Considerations

- API runs as non-root user
- Rate limiting prevents abuse
- CORS headers configured for production
- SSL termination handled by Caddy
- Container isolation and networking

## Performance

- Request caching with Redis
- Optimized search engine combinations
- Configurable worker processes
- Health monitoring and auto-restart
- Log rotation and size limits 