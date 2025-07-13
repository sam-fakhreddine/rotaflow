# Architecture Documentation

## System Overview

The 4x10 Schedule Manager is a web-based application that manages 4-day work week rotations with swap functionality. The system follows clean architecture principles with clear separation of concerns.

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │    │  Calendar Apps  │    │   Mobile Apps   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   HTTP Server   │
                    │   (Port 6247)   │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │    Handlers     │
                    │  (HTTP Layer)   │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │    Services     │
                    │ (Business Logic)│
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │     Models      │
                    │  (Data Layer)   │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   JSON Files    │
                    │   (Storage)     │
                    └─────────────────┘
```

## Component Architecture

### 1. HTTP Layer (Handlers)
**Purpose**: Handle HTTP requests and responses
**Location**: `app/handlers/`

```python
BaseHandler          # Common HTTP functionality
├── CalendarHandler  # Calendar endpoints (/calendar.ics, /view)
├── SwapHandler      # Swap management (/swaps, /api/swap)
└── AuthHandler      # Authentication (/login, /logout)
```

**Responsibilities**:
- Parse HTTP requests
- Route to appropriate services
- Format HTTP responses
- Handle authentication/authorization

### 2. Business Logic Layer (Services)
**Purpose**: Core business logic and rules
**Location**: `app/services/`

```python
CalendarService  # Calendar generation and iCal export
SwapService      # Swap request validation and processing
AuthService      # User authentication and session management
CoverageService  # Schedule coverage optimization
```

**Responsibilities**:
- Implement business rules
- Coordinate between models
- Validate business logic
- Transform data for presentation

### 3. Data Layer (Models)
**Purpose**: Data management and persistence
**Location**: `app/models/`

```python
RotationManager  # Schedule rotation algorithms
SwapManager      # Swap data persistence
UserManager      # User account management
```

**Responsibilities**:
- Data persistence
- Data validation
- Business entity representation
- Database abstraction

### 4. Presentation Layer (Templates)
**Purpose**: User interface rendering
**Location**: `app/templates/`

```
templates/
├── html/           # HTML templates
├── css/            # Stylesheets
├── js/             # JavaScript
└── renderers/      # Template engines
```

**Responsibilities**:
- HTML generation
- CSS styling
- JavaScript behavior
- Template rendering

## Data Flow

### 1. Calendar Generation Flow
```
HTTP Request → CalendarHandler → CalendarService → RotationManager → JSON Storage
                     ↓
Template Renderer ← CalendarService ← SwapManager ← CoverageService
                     ↓
HTTP Response ← HTML/iCal Output
```

### 2. Swap Request Flow
```
HTTP POST → SwapHandler → SwapService → SwapManager → JSON Storage
                ↓              ↓
         Validation    RotationManager (business rules)
                ↓
         HTTP Redirect ← Success/Error Message
```

### 3. Authentication Flow
```
Login Form → AuthHandler → AuthService → UserManager → JSON Storage
                ↓              ↓
         Session Cookie  Password Validation
                ↓
         HTTP Redirect ← Success/Error
```

## Design Patterns

### 1. Model-View-Controller (MVC)
- **Model**: Data layer (models/)
- **View**: Presentation layer (templates/)
- **Controller**: HTTP handlers (handlers/)

### 2. Service Layer Pattern
- Business logic isolated in services
- Handlers delegate to services
- Services coordinate models

### 3. Repository Pattern
- Models abstract data access
- JSON file storage hidden behind interfaces
- Easy to swap storage backends

### 4. Template Method Pattern
- BaseHandler provides common HTTP functionality
- Specific handlers implement specialized behavior

### 5. Strategy Pattern
- Different calendar generation strategies
- Configurable team sizes and rotations

## SOLID Principles Implementation

### Single Responsibility Principle (SRP)
- Each handler handles one type of request
- Each service handles one business domain
- Each model manages one type of data

### Open/Closed Principle (OCP)
- New handlers can be added without modifying existing code
- Router pattern allows easy extension
- Template system allows UI changes without code changes

### Liskov Substitution Principle (LSP)
- All handlers inherit from BaseHandler
- Services implement consistent interfaces
- Models can be substituted for testing

### Interface Segregation Principle (ISP)
- Small, focused interfaces
- Handlers only depend on needed services
- Services only use required model methods

### Dependency Inversion Principle (DIP)
- Handlers depend on service abstractions
- Services depend on model interfaces
- High-level modules don't depend on low-level details

## Security Architecture

### Authentication
```
User Login → Password Hash Verification → Session Creation → Cookie Setting
```

### Authorization
```
HTTP Request → Session Validation → Role Check → Access Grant/Deny
```

### Data Protection
- Session-based authentication
- HttpOnly cookies
- CSRF protection via form tokens
- Input validation and sanitization

## Scalability Considerations

### Current Architecture
- Single-process HTTP server
- In-memory session storage
- JSON file persistence
- Suitable for small teams (5-20 engineers)

### Future Scaling Options
1. **Database Backend**: Replace JSON with PostgreSQL/MySQL
2. **Session Store**: Redis for distributed sessions
3. **Load Balancing**: Multiple server instances
4. **Caching**: Redis for calendar caching
5. **Microservices**: Split into separate services

## Performance Characteristics

### Response Times
- Calendar view: <200ms
- iCal generation: <500ms
- Swap operations: <100ms

### Memory Usage
- Base application: ~50MB
- Per user session: ~1KB
- Calendar cache: ~10MB per team

### Disk Usage
- Application code: ~5MB
- Data files: ~1MB per team
- Logs: ~10MB per month

## Deployment Architecture

### Development
```
Developer Machine → Python Process → Local Files
```

### Production
```
Docker Container → HTTP Server → Mounted Volumes
       ↓
Load Balancer → Multiple Instances → Shared Storage
```

### High Availability
```
┌─────────────┐    ┌─────────────┐
│  Instance 1 │    │  Instance 2 │
└─────────────┘    └─────────────┘
       │                  │
       └────────┬─────────┘
                │
    ┌─────────────────┐
    │ Shared Storage  │
    └─────────────────┘
```

## Integration Points

### External Systems
- **Calendar Applications**: iCal/WebDAV protocols
- **Email Systems**: SMTP for notifications (future)
- **LDAP/AD**: User authentication (future)
- **Monitoring**: Prometheus metrics (future)

### API Interfaces
- REST API for programmatic access
- WebCal protocol for calendar subscriptions
- Health check endpoint for monitoring

## Error Handling Strategy

### Error Categories
1. **User Errors**: Invalid input, validation failures
2. **System Errors**: File I/O, network issues
3. **Business Errors**: Rule violations, conflicts

### Error Handling
- Graceful degradation
- User-friendly error messages
- Structured logging for debugging
- Automatic retry for transient failures

## Monitoring and Observability

### Logging
- Structured JSON logging
- Request/response logging
- Business event logging
- Error tracking

### Metrics (Future)
- Request rates and latencies
- Error rates by endpoint
- User activity metrics
- System resource usage

### Health Checks
- Application health endpoint
- Dependency health checks
- Automated monitoring integration
