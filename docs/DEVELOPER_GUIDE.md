# Developer Guide

## Architecture Overview

### System Design
The 4x10 Schedule Manager follows a clean, modular architecture:

```
app/
├── handlers/          # HTTP request handlers (SRP)
├── services/          # Business logic services
├── models/            # Data models and persistence
├── templates/         # HTML/CSS/JS templates
├── auth/              # Authentication system
└── core/              # Core utilities and configuration
```

### Design Principles
- **SOLID Principles**: Single responsibility, dependency injection
- **DRY**: Centralized configuration and templates
- **Separation of Concerns**: HTML/CSS/JS in separate files
- **Clean Architecture**: Business logic isolated from framework

## Development Setup

### Prerequisites
- Python 3.8+
- Git

### Local Development
```bash
git clone <repository>
cd schedule_manager
python main.py
```

### Project Structure
```
schedule_manager/
├── app/
│   ├── handlers/           # HTTP handlers
│   │   ├── base_handler.py    # Common HTTP functionality
│   │   ├── calendar_handler.py # Calendar endpoints
│   │   ├── swap_handler.py     # Swap management
│   │   └── auth_handler.py     # Authentication
│   ├── services/           # Business logic
│   │   ├── calendar_service.py # Calendar generation
│   │   ├── swap_service.py     # Swap operations
│   │   └── auth_service.py     # Authentication logic
│   ├── templates/          # Frontend assets
│   │   ├── html/              # HTML templates
│   │   ├── css/               # Stylesheets
│   │   ├── js/                # JavaScript
│   │   └── renderers/         # Template engines
│   ├── models/             # Data layer
│   │   ├── rotation.py        # Schedule rotation logic
│   │   └── swap_manager.py    # Swap data management
│   └── core/               # Core utilities
│       ├── config.py          # Configuration constants
│       └── router.py          # URL routing
├── config/                 # Configuration files
├── data/                   # Runtime data storage
└── docs/                   # Documentation
```

## Key Components

### HTTP Handlers
Each handler focuses on a single responsibility:

```python
class CalendarHandler(BaseHandler):
    def serve_calendar(self):
        # Generate iCal calendar

    def serve_engineer_calendar(self):
        # Generate individual calendar
```

### Services
Business logic separated from HTTP concerns:

```python
class CalendarService:
    def generate_team_calendar(self, weeks=52, config=None):
        # Pure business logic
```

### Template System
HTML/CSS/JS completely separated:

```python
class TemplateRenderer:
    def render(self, template_name, **context):
        # Load external HTML file
        # Substitute variables
```

## Adding New Features

### 1. Create Handler
```python
# app/handlers/new_handler.py
class NewHandler(BaseHandler):
    def handle_request(self):
        # HTTP-specific logic
```

### 2. Create Service
```python
# app/services/new_service.py
class NewService:
    def business_method(self):
        # Pure business logic
```

### 3. Create Templates
```html
<!-- app/templates/html/new_page.html -->
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="/css/base.css">
</head>
<body>{{content}}</body>
</html>
```

### 4. Add Routes
```python
# app/views/http_server.py
router.get(r"^/new$", self.new_handler.handle_request)
```

## Testing

### Unit Testing
```python
# Test services independently
def test_calendar_service():
    service = CalendarService()
    result = service.generate_team_calendar(weeks=1)
    assert result is not None
```

### Integration Testing
```python
# Test handlers with mock services
def test_calendar_handler():
    handler = CalendarHandler()
    # Mock dependencies
    # Test HTTP behavior
```

## Code Standards

### Python Style
- Follow PEP 8
- Use type hints
- Document with docstrings
- Keep functions small (<20 lines)

### HTML/CSS/JS
- Semantic HTML
- External stylesheets and scripts
- Modern JavaScript (ES6+)
- Responsive design

### File Organization
- One class per file
- Group related functionality
- Clear naming conventions
- Consistent directory structure

## Performance Considerations

### Caching
- Static assets (CSS/JS) cached by browser
- iCal files generated on-demand
- Session data stored in memory

### Optimization
- Minimal HTTP requests
- Efficient template rendering
- Lazy loading where appropriate

## Security

### Authentication
- Session-based authentication
- HttpOnly cookies
- CSRF protection via form tokens

### Input Validation
- All user inputs validated
- SQL injection prevention
- XSS protection via template escaping

## Deployment

### Docker
```bash
docker-compose up -d
```

### Environment Variables
- `PORT`: Server port (default: 6247)
- `CONFIG_PATH`: Configuration directory

### Monitoring
- Health check endpoint: `/health`
- Structured logging for debugging
- Error tracking and alerting

## Contributing

### Pull Request Process
1. Create feature branch
2. Follow coding standards
3. Add tests for new functionality
4. Update documentation
5. Submit pull request

### Code Review Checklist
- [ ] Follows SOLID principles
- [ ] Templates separated from logic
- [ ] Tests included
- [ ] Documentation updated
- [ ] No security vulnerabilities
