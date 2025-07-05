#!/bin/bash ./check_stats.sh, docker stats  docker-compose logs api

echo "=== SearXNG API Stats Checker ==="
echo ""

# Check if containers are running
echo "📦 Container Status:"
docker-compose ps
echo ""

# Check API health
echo "🏥 API Health Check:"
if curl -s "http://localhost/api/health" > /dev/null; then
    echo "✅ API is healthy"
    curl -s "http://localhost/api/health" | jq . 2>/dev/null || curl -s "http://localhost/api/health"
else
    echo "❌ API is not responding"
fi
echo ""

# Check API stats
echo "📊 API Statistics:"
if curl -s "http://localhost/api/stats" > /dev/null; then
    curl -s "http://localhost/api/stats" | jq . 2>/dev/null || curl -s "http://localhost/api/stats"
else
    echo "❌ Could not fetch API stats"
fi
echo ""

# Check SearXNG health
echo "🔍 SearXNG Health:"
if curl -s "http://localhost/healthz" > /dev/null; then
    echo "✅ SearXNG is healthy"
else
    echo "❌ SearXNG is not responding"
fi
echo ""

# Check port status
echo "🌐 Port Status:"
echo "Port 80 (HTTP): $(netstat -tulpn 2>/dev/null | grep :80 | wc -l) listeners"
echo "Port 443 (HTTPS): $(netstat -tulpn 2>/dev/null | grep :443 | wc -l) listeners"
echo "Port 4000 (SearXNG): $(netstat -tulpn 2>/dev/null | grep :4000 | wc -l) listeners"
echo "Port 5001 (API): $(netstat -tulpn 2>/dev/null | grep :5001 | wc -l) listeners"
echo ""

# Check recent logs
echo "📝 Recent API Logs (last 10 lines):"
docker-compose logs --tail=10 api
echo ""

# Check resource usage
echo "💾 Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
echo ""

echo "=== Quick Test Commands ==="
echo "Test API search: curl 'http://localhost/api/search?q=test&mode=general'"
echo "Test API modes: curl 'http://localhost/api/modes'"
echo "View all logs: docker-compose logs -f"
echo "Restart API: docker-compose restart api" 