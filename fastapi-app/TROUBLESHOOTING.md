# Troubleshooting Guide

## "This site can't be reached" Error

If you're getting a "This site can't be reached" error when accessing http://localhost:9001/, follow these steps:

### 1. Check if Docker containers are running

```bash
cd fastapi-app
docker-compose ps
```

You should see three services:
- `techliv_db` (PostgreSQL) - should be "Up" and "healthy"
- `techliv_redis` (Redis) - should be "Up" and "healthy"
- `techliv_api` (FastAPI) - should be "Up" and "healthy"

### 2. Check API container logs

```bash
docker-compose logs api --tail 100
```

Look for:
- ✅ `Uvicorn running on http://0.0.0.0:9001` - Server is running
- ❌ Any error messages or tracebacks
- ❌ `ModuleNotFoundError` or import errors
- ❌ Database connection errors

### 3. Check if port 9001 is in use

```bash
# On macOS/Linux
lsof -i :9001

# On Windows
netstat -ano | findstr :9001
```

If another process is using port 9001, either:
- Stop that process, or
- Change the port in `docker-compose.yml` (e.g., `"9002:9001"`)

### 4. Verify Docker is running

```bash
docker ps
```

If this fails, make sure Docker Desktop (or Docker daemon) is running.

### 5. Check container health

```bash
docker-compose ps
```

If the API container shows as "unhealthy" or keeps restarting:
- Check logs: `docker-compose logs api`
- Check database connection: `docker-compose logs db`
- Verify environment variables are set correctly

### 6. Restart all services

```bash
docker-compose down
docker-compose up --build -d
```

Then check logs:
```bash
docker-compose logs -f api
```

### 7. Test the health endpoint directly

```bash
# From inside the container
docker-compose exec api curl http://localhost:9001/health

# Or from your host (if curl is available)
curl http://localhost:9001/health
```

### 8. Check firewall settings

- macOS: System Preferences → Security & Privacy → Firewall
- Windows: Windows Defender Firewall
- Linux: `sudo ufw status`

Make sure port 9001 is not blocked.

### 9. Verify port mapping

Check `docker-compose.yml` has:
```yaml
ports:
  - "9001:9001"
```

This maps host port 9001 to container port 9001.

### 10. Try accessing from container

```bash
docker-compose exec api curl http://localhost:9001/
```

If this works but localhost doesn't, it's a port mapping issue.

## Common Issues and Solutions

### Issue: Container keeps restarting

**Solution:**
1. Check logs: `docker-compose logs api`
2. Look for import errors or missing dependencies
3. Rebuild: `docker-compose up --build`

### Issue: Database connection failed

**Solution:**
1. Ensure database container is healthy: `docker-compose ps db`
2. Check database logs: `docker-compose logs db`
3. Wait for database to be ready (it may take 10-30 seconds on first start)

### Issue: Port already in use

**Solution:**
1. Find what's using the port: `lsof -i :9001`
2. Stop that process or change the port in `docker-compose.yml`

### Issue: ModuleNotFoundError

**Solution:**
1. Rebuild the container: `docker-compose up --build`
2. Check `requirements.txt` includes all dependencies
3. Check logs for specific missing module

### Issue: Migration errors

**Solution:**
1. Check migration logs: `docker-compose logs api | grep -i migration`
2. If migrations fail, you may need to reset:
   ```bash
   docker-compose down -v  # WARNING: This deletes all data
   docker-compose up --build
   ```

## Quick Health Check Script

Create a file `check-health.sh`:

```bash
#!/bin/bash
echo "Checking Docker containers..."
docker-compose ps

echo -e "\nChecking API health..."
curl -f http://localhost:9001/health && echo "✅ API is healthy" || echo "❌ API is not responding"

echo -e "\nRecent API logs:"
docker-compose logs api --tail 20
```

Run it:
```bash
chmod +x check-health.sh
./check-health.sh
```

## Still having issues?

1. **Check all logs:**
   ```bash
   docker-compose logs
   ```

2. **Restart everything:**
   ```bash
   docker-compose down
   docker-compose up --build
   ```

3. **Verify Docker Desktop is running** (if on macOS/Windows)

4. **Check Docker resources** - Ensure Docker has enough memory/CPU allocated

5. **Try a different port** - Change `9001:9001` to `9002:9001` in docker-compose.yml

