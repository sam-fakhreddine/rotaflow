# Python Best Practices Rules

## SOLID Principles

### Single Responsibility Principle (SRP)
- Each class should have only one reason to change
- Separate concerns into different classes/modules
- Avoid god classes that do everything

### Open/Closed Principle (OCP)
- Classes should be open for extension, closed for modification
- Use inheritance, composition, and dependency injection
- Prefer abstract base classes and interfaces

### Liskov Substitution Principle (LSP)
- Derived classes must be substitutable for their base classes
- Maintain behavioral contracts in inheritance hierarchies

### Interface Segregation Principle (ISP)
- Clients should not depend on interfaces they don't use
- Create specific, focused interfaces rather than large general ones

### Dependency Inversion Principle (DIP)
- Depend on abstractions, not concretions
- High-level modules should not depend on low-level modules
- Use dependency injection and inversion of control

## DRY Principle (Don't Repeat Yourself)

### Code Duplication
- Extract common functionality into reusable functions/classes
- Use constants for repeated values
- Create utility modules for shared logic
- Avoid copy-paste programming

### Configuration Management
- Centralize configuration in one place
- Use environment variables for deployment-specific settings
- Avoid hardcoded values scattered throughout code

## Code Organization

### Module Structure
- Group related functionality together
- Use clear, descriptive module names
- Keep modules focused and cohesive
- Avoid circular imports

### Function Design
- Functions should do one thing well
- Keep functions small (< 20 lines ideally)
- Use descriptive function names
- Minimize function parameters (< 5 parameters)

### Class Design
- Use composition over inheritance when possible
- Keep class interfaces minimal and focused
- Use properties for computed attributes
- Implement `__str__` and `__repr__` methods

## Error Handling

### Exception Management
- Use specific exception types, not generic Exception
- Handle exceptions at the appropriate level
- Use try-except-finally appropriately
- Don't suppress exceptions without good reason

### Validation
- Validate inputs early and explicitly
- Use type hints for better code documentation
- Implement proper error messages for users

## Performance & Memory

### Efficiency
- Use appropriate data structures (dict vs list vs set)
- Avoid premature optimization
- Profile before optimizing
- Use generators for large datasets

### Resource Management
- Use context managers (with statements) for resources
- Close files, database connections, etc.
- Avoid memory leaks in long-running processes

## Testing & Documentation

### Testability
- Write testable code with dependency injection
- Separate business logic from framework code
- Use mocks and stubs appropriately
- Aim for high test coverage on critical paths

### Documentation
- Use docstrings for all public functions/classes
- Keep comments focused on "why", not "what"
- Use type hints consistently
- Maintain up-to-date README files

## Security Best Practices

### Input Validation
- Sanitize all user inputs
- Use parameterized queries for databases
- Validate file uploads and paths
- Implement proper authentication/authorization

### Secrets Management
- Never hardcode secrets in source code
- Use environment variables or secret management systems
- Rotate secrets regularly
- Use secure random number generation

## Example Good Patterns

```python
# Good: Single Responsibility
class UserValidator:
    def validate_email(self, email: str) -> bool:
        return "@" in email and "." in email
    
    def validate_password(self, password: str) -> bool:
        return len(password) >= 8

class UserRepository:
    def save_user(self, user: User) -> None:
        # Database logic only
        pass

# Good: DRY with constants
class Config:
    DEFAULT_PORT = 8080
    MAX_RETRIES = 3
    TIMEOUT_SECONDS = 30

# Good: Dependency Injection
class UserService:
    def __init__(self, repository: UserRepository, validator: UserValidator):
        self._repository = repository
        self._validator = validator
    
    def create_user(self, email: str, password: str) -> User:
        if not self._validator.validate_email(email):
            raise ValueError("Invalid email")
        # ... rest of logic
```

## Anti-Patterns to Avoid

### God Classes
```python
# Bad: Does everything
class UserManager:
    def validate_email(self): pass
    def send_email(self): pass
    def save_to_database(self): pass
    def generate_reports(self): pass
    def handle_payments(self): pass
```

### Magic Numbers/Strings
```python
# Bad
if user.age > 18:  # What's special about 18?
    
# Good
LEGAL_AGE = 18
if user.age > LEGAL_AGE:
```

### Tight Coupling
```python
# Bad: Hard to test/change
class OrderService:
    def process_order(self):
        db = MySQLDatabase()  # Tightly coupled
        email = SMTPEmailer()  # Tightly coupled
```