# Docker Best Practices Rules

## Docker Compose Rules

### Obsolete Fields
- **NEVER** use `version` field in docker-compose.yml files - it's obsolete and ignored
- Remove any existing `version:` declarations from compose files

### Service Configuration
- Use specific image tags, avoid `latest` in production
- Always set `restart: unless-stopped` for production services
- Use named volumes instead of bind mounts for data persistence
- Set resource limits with `deploy.resources` for production

### Environment Variables
- Use `.env` files for environment configuration
- Never hardcode secrets in compose files
- Use `env_file` directive for loading environment files
- Prefix environment variables with service name for clarity

### Networking
- Create explicit networks instead of using default
- Use internal networks for service-to-service communication
- Only expose necessary ports to host

## Dockerfile Rules

### Base Images
- Use official images from Docker Hub
- Pin specific versions, not `latest`
- Use slim/alpine variants when possible for smaller images
- Use multi-stage builds for production images

### Security
- Run as non-root user with `USER` directive
- Use `COPY` instead of `ADD` unless extracting archives
- Set proper file permissions with `--chown` flag
- Scan images for vulnerabilities regularly

### Optimization
- Order instructions from least to most frequently changing
- Combine RUN commands to reduce layers
- Use `.dockerignore` to exclude unnecessary files
- Clean up package caches in same RUN command

### Best Practices
- Use `WORKDIR` instead of `cd` commands
- Set `LABEL` metadata for image documentation
- Use `HEALTHCHECK` for service monitoring
- Avoid installing unnecessary packages

## Example Good Compose File

```yaml
services:
  app:
    build: .
    restart: unless-stopped
    environment:
      - NODE_ENV=production
    volumes:
      - app_data:/app/data
    networks:
      - app_network
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  db:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - db_data:/var/lib/postgresql/data
    networks:
      - app_network

volumes:
  app_data:
  db_data:

networks:
  app_network:
    driver: bridge
```

## Example Good Dockerfile

```dockerfile
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Install dependencies first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["python", "app.py"]
```