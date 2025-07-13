# Configuration Guide

## Overview
Configuration options for the 4x10 Schedule Manager system.

## Environment Variables

### Server Configuration
```bash
# Server port (default: 6247)
export PORT=6247

# Configuration directory
export CONFIG_PATH=/path/to/config

# Log level
export LOG_LEVEL=INFO
```

### Docker Environment
```bash
# docker-compose.yml
environment:
  - PORT=6247
  - CONFIG_PATH=/app/config
```

## Team Configuration Files

### Default Team (6 Engineers)
Default configuration with 6 engineers is built-in.

### Custom Team Sizes

#### 5 Engineers (config/team_5.json)
```json
{
  "engineers": [
    {"name": "Alex", "letter": "A", "country": "US", "state_province": "CA"},
    {"name": "Blake", "letter": "B", "country": "US", "state_province": "NY"},
    {"name": "Casey", "letter": "C", "country": "CA", "state_province": "ON"},
    {"name": "Dana", "letter": "D", "country": "US", "state_province": "TX"},
    {"name": "Evan", "letter": "E", "country": "CA", "state_province": "BC"}
  ],
  "rotation_weeks": 5,
  "start_date": "2024-01-01"
}
```

#### 7 Engineers (config/team_7.json)
```json
{
  "engineers": [
    {"name": "Alex", "letter": "A", "country": "US", "state_province": "CA"},
    {"name": "Blake", "letter": "B", "country": "US", "state_province": "NY"},
    {"name": "Casey", "letter": "C", "country": "CA", "state_province": "ON"},
    {"name": "Dana", "letter": "D", "country": "US", "state_province": "TX"},
    {"name": "Evan", "letter": "E", "country": "CA", "state_province": "BC"},
    {"name": "Fiona", "letter": "F", "country": "US", "state_province": "FL"},
    {"name": "Grace", "letter": "G", "country": "CA", "state_province": "AB"}
  ],
  "rotation_weeks": 7,
  "start_date": "2024-01-01"
}
```

## User Configuration

### Default Users
```json
{
  "users": [
    {
      "username": "admin",
      "password_hash": "hashed_password",
      "role": "admin",
      "engineer_name": null
    },
    {
      "username": "manager",
      "password_hash": "hashed_password",
      "role": "manager",
      "engineer_name": null
    }
  ]
}
```

### Adding Engineers as Users
```json
{
  "username": "alex",
  "password_hash": "hashed_password",
  "role": "engineer",
  "engineer_name": "Alex"
}
```

## Holiday Configuration

### Supported Regions
- **US States**: All 50 states
- **Canadian Provinces**: All provinces and territories

### Holiday Sources
- US Federal holidays
- State-specific holidays
- Canadian federal holidays
- Provincial holidays

### Custom Holidays
Add to `config/custom_holidays.json`:
```json
{
  "2024": {
    "company_day": "2024-07-15",
    "team_building": "2024-09-20"
  }
}
```

## Database Configuration

### JSON File Storage (Default)
```json
{
  "storage_type": "json",
  "data_directory": "./data",
  "backup_enabled": true,
  "backup_interval": "daily"
}
```

### Future: Database Support
```json
{
  "storage_type": "postgresql",
  "connection_string": "postgresql://user:pass@localhost/scheduledb",
  "pool_size": 10
}
```

## Logging Configuration

### Log Levels
- `DEBUG`: Detailed debugging information
- `INFO`: General information (default)
- `WARNING`: Warning messages
- `ERROR`: Error messages only

### Log Format
```json
{
  "event": "user_login",
  "username": "alex",
  "timestamp": "2024-01-15T10:30:00Z",
  "ip_address": "192.168.1.100"
}
```

## Security Configuration

### Session Settings
```python
# app/core/config.py
SESSION_TIMEOUT = 3600  # 1 hour
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True
```

### Password Requirements
```python
MIN_PASSWORD_LENGTH = 8
REQUIRE_SPECIAL_CHARS = True
REQUIRE_NUMBERS = True
```

## Performance Configuration

### Caching
```python
# Cache settings
CACHE_CALENDAR_SECONDS = 300  # 5 minutes
CACHE_STATIC_ASSETS = True
```

### Rate Limiting
```python
# API rate limits
MAX_REQUESTS_PER_MINUTE = 60
MAX_SWAP_REQUESTS_PER_DAY = 10
```

## Deployment Configuration

### Docker Compose
```yaml
version: '3.8'
services:
  schedule-manager:
    build: .
    ports:
      - "6247:6247"
    environment:
      - PORT=6247
      - CONFIG_PATH=/app/config
    volumes:
      - ./config:/app/config
      - ./data:/app/data
    restart: unless-stopped
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: schedule-manager
spec:
  replicas: 2
  selector:
    matchLabels:
      app: schedule-manager
  template:
    spec:
      containers:
      - name: schedule-manager
        image: schedule-manager:latest
        ports:
        - containerPort: 6247
        env:
        - name: PORT
          value: "6247"
        - name: CONFIG_PATH
          value: "/app/config"
```

## Monitoring Configuration

### Health Checks
```bash
# Health check endpoint
curl http://localhost:6247/health
```

### Metrics Collection
```python
# Enable metrics
ENABLE_METRICS = True
METRICS_PORT = 9090
```

### Alerting
```yaml
# Prometheus alerts
groups:
- name: schedule-manager
  rules:
  - alert: ServiceDown
    expr: up{job="schedule-manager"} == 0
    for: 1m
```

## Backup Configuration

### Automated Backups
```json
{
  "backup_enabled": true,
  "backup_schedule": "0 2 * * *",  # Daily at 2 AM
  "backup_retention_days": 30,
  "backup_location": "/backups"
}
```

### Manual Backup
```bash
# Backup data directory
tar -czf backup-$(date +%Y%m%d).tar.gz data/
```

## Troubleshooting

### Common Configuration Issues

**Port already in use**
```bash
# Change port
export PORT=8080
```

**Configuration file not found**
```bash
# Check path
export CONFIG_PATH=/correct/path/to/config
```

**Permission denied**
```bash
# Fix permissions
chmod 644 config/*.json
chmod 755 data/
```
