# SearXNG Simple API Wrapper

This is a simple Flask API wrapper for your SearXNG instance that provides a clean interface for your external application.

## 🎉 Status: FIXED!

The 403 Forbidden issue has been resolved by clearing the Redis data. Your SearXNG search API is now working perfectly!

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the API Server

```bash
python3 simple_api.py
```

The server will start on `http://localhost:5000`

### 3. Test the API

```bash
python3 test_simple_api.py
```

## API Endpoints

### Search
```
GET /api/search?q=<query>&engines=<engine1,engine2>&max_results=<number>&categories=<images>
```

**Parameters:**
- `q` (required): Search query
- `engines` (optional): Comma-separated list of search engines (e.g., "google,bing,duckduckgo")
- `max_results` (optional): Maximum number of results (default: 10)
- `format` (optional): Response format (default: "json")
- `categories` (optional): Comma-separated list of categories (e.g., "images" for image search)

### Configuration
```
GET /api/config
```
Returns the complete SearXNG configuration including available engines.

### Health Check
```
GET /api/health
```
Returns the health status of the SearXNG instance.

### Available Engines
```
GET /api/engines
```
Returns a list of available and enabled search engines.

### API Information
```
GET /api
```
Returns information about the API and available endpoints.

## Usage Examples

### Regular Search
```bash
curl "http://localhost:5000/api/search?q=python&engines=google&max_results=5"
```

### Image Search
```bash
curl "http://localhost:5000/api/search?q=cats&categories=images&engines=bing_images,google_images&max_results=10"
```

### Get Available Engines
```bash
curl "http://localhost:5000/api/engines"
```

### Health Check
```bash
curl "http://localhost:5000/api/health"
```

## Integration with Your Application

### TypeScript/JavaScript Integration

Update your `searxng.ts` file to point to the Flask API:

```typescript
export const searchSearxng = async (
  query: string,
  opts?: SearxngSearchOptions,
): Promise<{ results: SearxngSearchResult[]; suggestions: string[] }> => {
  // Point to your Flask API instead of direct SearXNG instance
  const searxngURL = process.env.SEARXNG_API_URL || 'http://localhost:5000';
  // ... rest of the function remains the same ...
```

### Image Search Agent

Update your `imageSearchAgent.ts` to use proper engine identifiers:

```typescript
RunnableLambda.from(async (input: string) => {
  input = input.replace(/.*?<\/think>/g, '');
  const res = await searchSearxng(input, {
    engines: ['bing_images', 'google_images'], // Use underscores instead of spaces
    max_results: 10,
    categories: ['images'] // Add category filter
  });
  // ... rest of the processing ...
```

## Environment Variables

Create a `.env` file in your application:

```bash
# API Configuration
SEARXNG_API_URL=http://localhost:5000  # Points to Flask API
SEARXNG_INSTANCE_URL=https://localhost  # Direct SearXNG access (if needed)

# Optional: SSL verification
SEARXNG_VERIFY_SSL=false  # Set to true in production
```

## Features

### ✅ Working Features
- **Regular Search**: Full text search with multiple engines
- **Image Search**: Specialized image search with validation
- **Engine Selection**: Choose specific search engines
- **Result Filtering**: Automatic filtering for image results
- **Health Monitoring**: Check service status
- **Configuration Access**: Get available engines and settings

### 🔧 Configuration
- **Port**: 5000 (configurable in `simple_api.py`)
- **SSL**: Disabled for local development
- **CORS**: Enabled for cross-origin requests
- **Rate Limiting**: Disabled (handled by SearXNG)

### 🛡️ Security
- **Input Validation**: All parameters are validated
- **Error Handling**: Comprehensive error responses
- **Logging**: Request and error logging
- **SSL Verification**: Configurable SSL verification

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using port 5000
   lsof -i :5000
   # Kill the process or change the port in simple_api.py
   ```

2. **SearXNG Not Responding**
   ```bash
   # Check if SearXNG is running
   curl -k https://localhost/healthz
   # Restart the containers
   docker compose restart
   ```

3. **Image Search Not Working**
   ```bash
   # Check available engines
   curl "http://localhost:5000/api/engines"
   # Ensure image engines are enabled in SearXNG
   ```

### Debug Mode

The API runs in debug mode by default. Check the console output for detailed logs and error messages.

## Development

### Adding New Features

1. **New Endpoints**: Add new routes to `simple_api.py`
2. **Parameter Validation**: Use the existing validation patterns
3. **Error Handling**: Follow the existing error response format
4. **Testing**: Update `test_simple_api.py` with new tests

### Testing

```bash
# Run the test suite
python3 test_simple_api.py

# Manual testing
curl "http://localhost:5000/api/search?q=test&engines=google"
```

## Production Deployment

For production deployment:

1. **Enable SSL**: Set `VERIFY_SSL = True` in `simple_api.py`
2. **Use Production WSGI**: Use Gunicorn or uWSGI instead of Flask development server
3. **Environment Variables**: Set proper environment variables
4. **Logging**: Configure proper logging
5. **Monitoring**: Add health checks and monitoring

Example production command:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 simple_api:app
```

## Files

- `simple_api.py` - Main API wrapper
- `test_simple_api.py` - Test script
- `requirements.txt` - Python dependencies
- `API_README.md` - This file

## Support

If you encounter any issues:
1. Check the SearXNG logs: `docker compose logs searxng`
2. Check the API logs (printed to console)
3. Verify your SearXNG instance is working: `curl https://localhost/search?q=test&format=json` 