# SearXNG Production API Wrapper

This is a production-ready Flask API wrapper for your SearXNG instance that provides a clean interface with predefined search modes and robust error handling.

## 🎉 Status: PRODUCTION READY!

The API now includes advanced features like search modes, retry mechanisms, and improved health monitoring.

## Quick Start

### 1. Start the Services

```bash
docker-compose up -d --build
```

The API will be available at `http://localhost:5001`

### 2. Test the API

```bash
# Health check
curl "http://localhost:5001/api/health"

# Basic search
curl "http://localhost:5001/api/search?q=python&mode=general"

# Get available modes
curl "http://localhost:5001/api/modes"
```

## API Endpoints

### Search
```
GET/POST /api/search
```

**Parameters:**
- `q` (required): Search query
- `mode` (optional): Predefined search mode (see Search Modes below)
- `engines` (optional): Comma-separated list of search engines
- `max_results` (optional): Maximum number of results (default: 10, max: 50)
- `language` (optional): Search language (default: "en")
- `safesearch` (optional): Safe search level 0-2 (default: 1)
- `time_range` (optional): Time range filter (day, week, month, year)
- `pageno` (optional): Page number (default: 1)

### Search Modes
```
GET /api/modes
```
Returns available search modes with descriptions and engine configurations.

### Health Check
```
GET /api/health
```
Returns the health status of both the API and SearXNG instance.

### Configuration
```
GET /api/config
```
Returns the complete API and SearXNG configuration.

### Available Engines
```
GET /api/engines
```
Returns available engines grouped by category.

### Statistics
```
GET /api/stats
```
Returns API usage statistics and metrics.

### API Information
```
GET /api
```
Returns information about the API and available endpoints.

## Search Modes

The API provides 10 predefined search modes optimized for different use cases:

| Mode | Description | Engines | Max Results |
|------|-------------|---------|-------------|
| **general** | General web search using major search engines | Google, Bing, DuckDuckGo | 15 |
| **academic** | Academic papers and scholarly content | Google Scholar, arXiv, PubMed, Semantic Scholar | 20 |
| **news** | Latest news and current events | Google News, Bing News, Yahoo News, Reuters | 25 |
| **images** | Image search across multiple platforms | Google Images, Bing Images, Flickr, Unsplash | 30 |
| **videos** | Video content search | YouTube, Vimeo, Dailymotion | 20 |
| **social** | Social media and community content | Twitter, Reddit, Mastodon | 25 |
| **shopping** | Product search and shopping | Amazon, eBay, Shopping | 20 |
| **tech** | Technical content and development resources | GitHub, Stack Overflow, Hacker News | 20 |
| **local** | Local business and location search | Google Maps, OpenStreetMap, Yelp | 15 |
| **fast** | Fast single-engine search for quick results | DuckDuckGo | 10 |

## Usage Examples

### General Search
```bash
curl "http://localhost:5001/api/search?q=python&mode=general&max_results=15"
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

## Health Status

The health endpoint returns detailed status information:

```json
{
  "api_status": "healthy",
  "searxng_status": "healthy",
  "timestamp": 1752190840.8051653,
  "version": "1.0.0"
}
```

**Status Values:**
- `healthy` - Service is fully operational
- `degraded` - API is working but SearXNG has issues
- `unhealthy` - Service is not responding

## Rate Limiting

The API includes configurable rate limiting:
- **Default**: 100 requests per hour per IP
- **Configurable**: Via environment variables
- **Response**: 429 status code when limit exceeded

## Environment Variables

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
```

## Features

### ✅ Production Features
- **Search Modes**: 10 predefined search modes for different use cases
- **Retry Mechanism**: Automatic retry during startup and connection issues
- **Health Monitoring**: Comprehensive health checks with status reporting
- **Rate Limiting**: Configurable per-IP rate limiting
- **Error Handling**: Graceful degradation and detailed error responses
- **CORS Support**: Cross-origin request support
- **Logging**: Structured logging for debugging and monitoring
- **Security**: Non-root container execution and input validation

### 🔧 Configuration
- **Port**: 5001 (configurable)
- **SSL**: Configurable SSL verification
- **CORS**: Enabled for cross-origin requests
- **Rate Limiting**: Configurable limits and windows
- **Health Checks**: Built-in container health monitoring

### 🛡️ Security
- **Input Validation**: All parameters are validated and sanitized
- **Error Handling**: Comprehensive error responses without information leakage
- **Logging**: Request and error logging for security monitoring
- **SSL Verification**: Configurable SSL verification for production use
- **Rate Limiting**: Protection against abuse and DoS attacks

## Troubleshooting

### Common Issues

1. **API Shows as Unhealthy**
   ```bash
   # Check container status
   docker-compose ps
   
   # Check API logs
   docker-compose logs api
   
   # Check health endpoint
   curl "http://localhost:5001/api/health"
   ```

2. **SearXNG Connection Issues**
   ```bash
   # Check SearXNG logs
   docker-compose logs searxng
   
   # Check if SearXNG is responding
   curl "http://localhost:4000/"
   
   # Restart services
   docker-compose restart
   ```

3. **Rate Limit Exceeded**
   ```bash
   # Check current rate limit status
   curl "http://localhost:5001/api/stats"
   
   # Wait for rate limit window to reset
   ```

### Debug Mode

Check the container logs for detailed information:

```bash
# All services
docker-compose logs -f

# API only
docker-compose logs -f api

# SearXNG only
docker-compose logs -f searxng
```

## Development

### Adding New Search Modes

1. **Edit `app_api.py`**: Add new mode to `SearchMode` enum and `SEARCH_MODES` dictionary
2. **Configure Engines**: Specify engines and categories for the new mode
3. **Test**: Verify the new mode works with different queries
4. **Document**: Update this README with the new mode

### Testing

```bash
# Test health endpoint
curl "http://localhost:5001/api/health"

# Test search modes
curl "http://localhost:5001/api/modes"

# Test search functionality
curl "http://localhost:5001/api/search?q=test&mode=general"
```

### Monitoring

```bash
# View real-time logs
docker-compose logs -f

# Check container health
docker-compose ps

# Monitor API statistics
curl "http://localhost:5001/api/stats"
``` 