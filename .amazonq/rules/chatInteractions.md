# Amazon Q Rule: Minimize Chat Interactions Through Command Chaining

## Overview

This rule establishes guidelines to minimize the number of chat interactions by encouraging command chaining, comprehensive requests, and efficient workflows that deliver faster, better results.

## Core Principles

### 1. Chain Commands for Related Tasks

- **Always** combine related commands using `&&` for sequential execution
- **Always** group file operations, builds, tests, and deployments in single commands
- **Examples:**

  ```bash
  # Instead of 3 separate interactions:
  npm install && npm run build && npm test

  # Instead of multiple git commands:
  git add . && git commit -m "feature: add new component" && git push

  # For Python projects:
  pip install -r requirements.txt && python -m pytest && python main.py
  ```

### 2. Request Comprehensive Solutions

- **Always** ask for complete implementations rather than partial solutions
- **Always** request error handling, validation, and edge cases in initial ask
- **Always** specify desired file structure, dependencies, and configuration needs upfront
- **Example:** "Create a complete user authentication system with login/logout routes, middleware, error handling, tests, and proper TypeScript types"

### 3. Batch File Operations

- **Always** request multiple related file changes in a single interaction
- **Always** specify all files that need updates when implementing features
- **Examples:**
  - "Update the user model, controller, routes, and tests for the new email validation feature"
  - "Create component, styles, tests, and story file for the new button component"

### 4. Include Context and Requirements Upfront

- **Always** provide full context, tech stack, and requirements in initial request
- **Always** specify coding standards, patterns, and architectural preferences
- **Always** mention related files, dependencies, or constraints that might affect the solution
- **Example:** "Using FastAPI with SQLAlchemy, create a REST API for user management with JWT auth, following our existing patterns in auth_service.py, including proper error responses and OpenAPI documentation"

### 5. Request Validation and Testing Together

- **Always** ask for implementation + tests + validation in single request
- **Always** request error scenarios and edge case handling
- **Examples:**
  - "Implement user registration with input validation, unit tests, and integration tests"
  - "Create API endpoint with proper error handling, response schemas, and test coverage"

### 6. Specify Output Format and Structure

- **Always** specify desired file organization and naming conventions
- **Always** request documentation, comments, and type definitions together
- **Example:** "Create a modular calendar service with TypeScript interfaces, JSDoc comments, unit tests in **tests** folder, and README with usage examples"

## Command Chaining Best Practices

### Development Workflow Chains

```bash
# Full development cycle
git pull && npm install && npm run lint && npm run test && npm run build

# Database operations
docker-compose down && docker-compose up -d db && npm run migrate && npm run seed

# Testing pipeline
npm run lint:fix && npm run test:unit && npm run test:integration && npm run test:e2e

# Deployment chain
npm run build && npm run test && docker build -t app . && docker push registry/app
```

### Python Project Chains

```bash
# Setup and validate
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python -m pytest

# Code quality chain
black . && isort . && flake8 . && mypy . && pytest --cov=app

# FastAPI development
uvicorn main:app --reload --host 0.0.0.0 --port 8000 & sleep 2 && curl http://localhost:8000/health
```

### Docker Workflow Chains

```bash
# Clean rebuild
docker-compose down -v && docker-compose build --no-cache && docker-compose up -d

# Health check chain
docker-compose up -d && sleep 10 && docker-compose ps && docker-compose logs
```

## Interaction Optimization Strategies

### 1. Use Parallel Tool Calls

- Request multiple file reads simultaneously
- Batch related operations when possible
- Group validation checks together

### 2. Provide Complete Specifications

- Include all requirements, constraints, and preferences
- Specify error handling and edge case requirements
- Request documentation and examples together

### 3. Think in Features, Not Files

- Request complete feature implementation with all supporting files
- Ask for end-to-end solutions including tests and documentation
- Specify integration points and dependencies upfront

### 4. Optimize Follow-up Requests

- If requesting changes, specify all modifications at once
- Include related refactoring needs in initial request
- Request performance optimizations with initial implementation

## Examples of Efficient Requests

### Good: Comprehensive Feature Request

"Create a complete swap request system for the schedule manager:

- FastAPI endpoints for creating, approving, and listing swaps
- SQLAlchemy models with proper relationships
- Pydantic schemas for request/response validation
- Service layer with business logic and error handling
- Unit tests with pytest covering all scenarios
- Integration with existing auth system
- Proper logging and error responses
- Update the router to include new endpoints"

### Bad: Incremental Requests

❌ "Create a swap model"
❌ "Now add the endpoint"
❌ "Add validation"
❌ "Add tests"
❌ "Fix the import error"

### Good: Chained Development Workflow

"Set up the development environment and run the full test suite:
`python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python -m pytest -v && uvicorn main:app --reload`"

### Good: Comprehensive Debugging Request

"Debug and fix the authentication issue:

- Check the auth service, middleware, and routes
- Verify JWT token handling and validation
- Update error responses to be more descriptive
- Add proper logging for auth failures
- Include tests for the fixed scenarios
- Update the API documentation if needed"

## Measurement and Success Criteria

### Target Metrics

- Reduce average interactions per feature from 5-8 to 2-3
- Increase successful first-attempt implementations by 60%
- Reduce context-switching and clarification requests by 70%
- Achieve 90% of requests completed in single comprehensive response

### Quality Indicators

- Complete, working solutions delivered in first response
- Minimal follow-up questions for clarification
- Comprehensive error handling and edge case coverage
- Proper tests and documentation included automatically
- Integration with existing codebase without additional fixes

## Implementation Guidelines

1. **Always** think holistically about the request
2. **Always** consider dependencies and related components
3. **Always** include error handling and validation
4. **Always** provide tests and documentation
5. **Always** use command chaining for related operations
6. **Always** optimize for single-interaction completeness

By following these guidelines, we achieve faster development cycles, more reliable solutions, and significantly reduced chat overhead while maintaining high code quality and comprehensive implementations.
