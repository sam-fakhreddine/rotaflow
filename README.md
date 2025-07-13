# 4x10 Schedule Manager

A web-based schedule management system for 4-day work weeks with swap functionality.

## Features

- **4x10 Rotation**: Automated fair rotation of days off
- **Swap Management**: Request and approve day-off swaps
- **User Management**: Role-based access (admin, manager, engineer)
- **Web Interface**: Complete GUI for all operations
- **Calendar Export**: iCal format for calendar subscriptions
- **Multi-tenant**: Support for multiple teams
- **Holiday Support**: US/Canadian statutory holidays

## Quick Start

### Local Development
```bash
cd schedule_manager
python main.py
```

### Docker
```bash
docker-compose up -d
```

Visit http://localhost:6247

## Default Login
- Admin: admin/admin123
- Manager: manager/manager123

## Documentation

📚 **Complete Documentation Available:**
- [API Documentation](docs/API.md) - REST API endpoints and examples
- [User Guide](docs/USER_GUIDE.md) - End-user instructions and tutorials
- [Developer Guide](docs/DEVELOPER_GUIDE.md) - Technical implementation details
- [Configuration Guide](docs/CONFIGURATION.md) - Setup and deployment options
- [Architecture Documentation](docs/ARCHITECTURE.md) - System design and structure

## Project Structure

```
schedule_manager/
├── app/
│   ├── handlers/        # HTTP request handlers
│   ├── services/        # Business logic services
│   ├── models/          # Data models and persistence
│   ├── templates/       # HTML/CSS/JS templates
│   ├── auth/            # Authentication system
│   └── core/            # Core utilities and config
├── config/              # Configuration files
├── data/                # Runtime data (JSON files)
├── docs/                # Documentation
└── tests/               # Test files
```

## Architecture Highlights

- **Clean Architecture**: SOLID principles, separation of concerns
- **Template Separation**: HTML/CSS/JS in external files
- **Service Layer**: Business logic isolated from HTTP handling
- **Modular Design**: Easy to extend and maintain
- **Docker Ready**: Production deployment with Docker Compose

## Contributing

See [Developer Guide](docs/DEVELOPER_GUIDE.md) for development setup, coding standards, and contribution guidelines.