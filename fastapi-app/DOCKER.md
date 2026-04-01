# Docker Setup Guide

This guide explains how to run the TechLiv FastAPI application using Docker.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

## Quick Start

1. **Build and start all services**:
   ```bash
   docker-compose up --build
   ```

2. **Run in detached mode** (background):
   ```bash
   docker-compose up -d --build
   ```

3. **View logs**:
   ```bash
   docker-compose logs -f api
   ```

4. **Stop all services**:
   ```bash
   docker-compose down
   ```

5. **Stop and remove volumes** (clean slate):
   ```bash
   docker-compose down -v
   ```

## Services

The `docker-compose.yml` file includes three services:

### 1. **Database (PostgreSQL)**
- Container: `techliv_db`
- Port: `5432`
- Database: `techliv`
- User: `techliv`
- Password: `techliv`
- Data persisted in volume: `postgres_data`

### 2. **Redis**
- Container: `techliv_redis`
- Port: `6379`
- Data persisted in volume: `redis_data`

### 3. **FastAPI Application**
- Container: `techliv_api`
- Port: `9001`
- Automatically runs migrations on startup
- Hot-reload enabled for development

## Access Points

Once the containers are running:

- **API**: http://localhost:9001
- **Swagger UI**: http://localhost:9001/docs
- **ReDoc**: http://localhost:9001/redoc
- **Health Check**: http://localhost:9001/health

## Environment Variables

You can customize the configuration by creating a `.env` file in the `fastapi-app` directory:

```env
# Database
DB_HOST=db
DB_PORT=5432
DB_DATABASE=techliv
DB_USERNAME=techliv
DB_PASSWORD=techliv

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# App
ENV=development
DEBUG=true
PORT=9001
```

## Common Commands

### View running containers
```bash
docker-compose ps
```

### View logs for specific service
```bash
docker-compose logs -f api      # API logs
docker-compose logs -f db       # Database logs
docker-compose logs -f redis    # Redis logs
```

### Execute commands in running container
```bash
# Run Alembic migrations manually
docker-compose exec api alembic upgrade head

# Create a new migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Access Python shell
docker-compose exec api python

# Run tests
docker-compose exec api pytest
```

### Rebuild after code changes
```bash
docker-compose up --build
```

### Restart a specific service
```bash
docker-compose restart api
```

## Database Management

### Access PostgreSQL directly
```bash
docker-compose exec db psql -U techliv -d techliv
```

### Backup database
```bash
docker-compose exec db pg_dump -U techliv techliv > backup.sql
```

### Restore database
```bash
docker-compose exec -T db psql -U techliv techliv < backup.sql
```

## Troubleshooting

### Port already in use
If port 9001 is already in use, you can change it in `docker-compose.yml`:
```yaml
ports:
  - "9002:9001"  # Change 9002 to any available port
```

### Database connection issues
If the API can't connect to the database:
1. Check if the database container is running: `docker-compose ps`
2. Check database logs: `docker-compose logs db`
3. Ensure the database is healthy: `docker-compose ps` should show "healthy"

### Migration issues
If migrations fail:
```bash
# Check migration status
docker-compose exec api alembic current

# View migration history
docker-compose exec api alembic history

# Rollback if needed
docker-compose exec api alembic downgrade -1
```

### Clear everything and start fresh
```bash
# Stop and remove containers, networks, and volumes
docker-compose down -v

# Remove images
docker-compose rm -f

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up
```

## Production Considerations

For production deployment:

1. **Change default passwords** in `docker-compose.yml`
2. **Use environment variables** for sensitive data
3. **Disable debug mode**: Set `DEBUG=false`
4. **Use production database**: Point to external PostgreSQL instance
5. **Configure proper CORS**: Set `BACKEND_CORS_ORIGINS` appropriately
6. **Use secrets management**: Don't hardcode secrets in docker-compose.yml
7. **Remove `--reload` flag**: Use production ASGI server configuration
8. **Add reverse proxy**: Use nginx or similar for SSL termination

## Development Workflow

1. Make code changes in your local files
2. Changes are automatically reflected (hot-reload enabled)
3. View logs: `docker-compose logs -f api`
4. Test endpoints: http://localhost:9001/docs

## Building Docker Image Manually

If you want to build the Docker image without docker-compose:

```bash
docker build -t techliv-api:latest .
docker run -p 9001:9001 techliv-api:latest
```

