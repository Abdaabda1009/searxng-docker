# SearXNG Production API Integration with Docker

This setup includes a production-ready Python API wrapper for SearXNG with advanced features like search modes, retry mechanisms, and comprehensive health monitoring.

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
3. **API** - Production Python Flask API wrapper with search modes
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

4. **Test the API:**
   ```bash
   # Health check
   curl "http://localhost:5001/api/health"
   
   # Basic search
   curl "http://localhost:5001/api/search?q=python&mode=general"
   ```

## API Endpoints

### Base URL: `http://localhost:5001/api`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/search` | GET/POST | Perform search with mode support |
| `/modes` | GET | Get available search modes |
| `/health` | GET | Health check with status reporting |
| `/config` | GET | Get API and SearXNG configuration |
| `/engines` | GET | Get available engines by category |
| `/stats` | GET | Get usage statistics and metrics |
| `/` | GET | API information and documentation |

## Search Modes

The API provides 10 predefined search modes optimized for different use cases:

| Mode | Description | Engines | Max Results | Use Case |
|------|-------------|---------|-------------|----------|
| **general** | General web search | Google, Bing, DuckDuckGo | 15 | Everyday searches |
| **academic** | Academic papers | Google Scholar, arXiv, PubMed, Semantic Scholar | 20 | Research and papers |
| **news** | Latest news | Google News, Bing News, Yahoo News, Reuters | 25 | Current events |
| **images** | Image search | Google Images, Bing Images, Flickr, Unsplash | 30 | Visual content |
| **videos** | Video content | YouTube, Vimeo, Dailymotion | 20 | Video searches |
| **social** | Social media | Twitter, Reddit, Mastodon | 25 | Social content |
| **shopping** | Product search | Amazon, eBay, Shopping | 20 | E-commerce |
| **tech** | Technical content | GitHub, Stack Overflow, Hacker News | 20 | Development |
| **local** | Local business | Google Maps, OpenStreetMap, Yelp | 15 | Local search |
| **fast** | Quick search | DuckDuckGo | 10 | Fast results |

## Usage Examples

### Basic Search
```bash
curl "http://localhost:5001/api/search?q=python&mode=general"
```

### Academic Search
```bash
curl "http://localhost:5001/api/search?q=machine+learning&mode=academic&max_results=20"
```

### News Search with Time Filter
```bash
curl "http://localhost:5001/api/search?q=latest+news&mode=news&time_range=day&max_results=25"
```

### Image Search
```bash
curl "http://localhost:5001/api/search?q=sunset&mode=images&max_results=30"
```

### POST Request with JSON
```bash
curl -X POST "http://localhost:5001/api/search" \
  -H "Content-Type: application/json" \
  -d '{
    "q": "python programming",
    "mode": "tech",
    "max_results": 15,
    "language": "en",
    "safesearch": 1
  }'
```

### Get Available Modes
```bash
curl "http://localhost:5001/api/modes"
```

### Health Check
```bash
curl "http://localhost:5001/api/health"
```

## Health Monitoring

The API includes comprehensive health monitoring:

### Health Status Response
```json
{
  "api_status": "healthy",
  "searxng_status": "healthy",
  "timestamp": 1752190840.8051653,
  "version": "1.0.0"
}
```

### Status Values
- **healthy** - Service is fully operational
- **degraded** - API is working but SearXNG has issues
- **unhealthy** - Service is not responding

### Retry Mechanism
- **Startup Retries**: API retries connecting to SearXNG up to 10 times during startup
- **Exponential Backoff**: Increasing delays between retry attempts
- **Graceful Degradation**: API starts even if SearXNG is unavailable

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
SEARXNG_BASE_URL=http://searxng:8080/
SEARXNG_HOSTNAME=localhost
SEARXNG_TLS=internal
SEARXNG_UWSGI_WORKERS=4
SEARXNG_UWSGI_THREADS=4
```

## Features

### ✅ Production Features
- **Search Modes**: 10 predefined search modes for different use cases
- **Retry Mechanism**: Automatic retry during startup and connection issues
- **Health Monitoring**: Comprehensive health checks with status reporting
- **Rate Limiting**: Configurable per-IP rate limiting (100 req/hour default)
- **Error Handling**: Graceful degradation and detailed error responses
- **CORS Support**: Cross-origin request support
- **Logging**: Structured logging for debugging and monitoring
- **Security**: Non-root container execution and input validation

### 🔧 Advanced Configuration
- **Health Checks**: Built-in container health monitoring
- **Startup Coordination**: Proper sequencing of service startup
- **Connection Pooling**: Efficient connection management
- **Request Validation**: Comprehensive parameter validation
- **Response Caching**: Optional response caching for performance

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
curl "http://localhost:5001/api/health"

# Container health
docker-compose ps

# SearXNG direct health
curl "http://localhost:4000/"
```

### Statistics
```bash
curl "http://localhost:5001/api/stats"
```

### Real-time Monitoring
```bash
# Watch container status
watch -n 5 'docker-compose ps'

# Monitor API logs
docker-compose logs -f api | grep -E "(ERROR|WARNING|INFO)"
```

## Troubleshooting

### API Not Responding
1. Check if containers are running: `docker-compose ps`
2. Check API logs: `docker-compose logs api`
3. Verify health: `curl "http://localhost:5001/api/health"`
4. Check startup retries in logs

### Search Issues
1. Check SearXNG logs: `docker-compose logs searxng`
2. Verify SearXNG health: `curl "http://localhost:4000/"`
3. Check API configuration: `curl "http://localhost:5001/api/config"`
4. Test specific search modes: `curl "http://localhost:5001/api/modes"`

### Health Check Issues
1. **API Shows as Unhealthy**: Check container logs for connection errors
2. **SearXNG Shows as Unhealthy**: Verify SearXNG is running and accessible
3. **Degraded Status**: API is working but SearXNG has issues

### SSL/HTTPS Issues
1. Check Caddy logs: `docker-compose logs caddy`
2. Verify certificate generation
3. Check hostname configuration

### Rate Limiting
1. Check current usage: `curl "http://localhost:5001/api/stats"`
2. Monitor rate limit headers in responses
3. Adjust limits in environment variables if needed

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

### Adding New Search Modes
1. **Edit `app_api.py`**: Add new mode to `SearchMode` enum
2. **Configure Engines**: Add to `SEARCH_MODES` dictionary
3. **Test**: Verify the new mode works
4. **Document**: Update documentation

### Local Development
```bash
# Run API locally (outside Docker)
pip install -r requirements.txt
python app_api.py
```

### Testing
```bash
# Test all endpoints
curl "http://localhost:5001/api/health"
curl "http://localhost:5001/api/modes"
curl "http://localhost:5001/api/search?q=test&mode=general"
curl "http://localhost:5001/api/config"
curl "http://localhost:5001/api/engines"
curl "http://localhost:5001/api/stats"
```

## Performance

### Optimization Features
- **Connection Pooling**: Efficient HTTP connection reuse
- **Request Timeouts**: Configurable timeouts to prevent hanging
- **Rate Limiting**: Protection against abuse
- **Health Checks**: Fast health status responses
- **Error Caching**: Prevents repeated failed requests

### Monitoring Performance
```bash
# Check response times
curl -w "@curl-format.txt" "http://localhost:5001/api/health"

# Monitor resource usage
docker stats

# Check API statistics
curl "http://localhost:5001/api/stats"
```

## Security

### Security Features
- **Input Validation**: All parameters validated and sanitized
- **Rate Limiting**: Protection against abuse and DoS
- **Non-root Execution**: Containers run as non-root users
- **SSL Verification**: Configurable SSL certificate verification
- **Error Handling**: No sensitive information in error responses
- **CORS Configuration**: Controlled cross-origin access

### Security Best Practices
1. **Enable SSL Verification** in production
2. **Set Appropriate Rate Limits** for your use case
3. **Monitor Logs** for suspicious activity
4. **Keep Dependencies Updated** regularly
5. **Use Environment Variables** for sensitive configuration 