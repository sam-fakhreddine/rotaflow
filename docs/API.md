# API Documentation

## Overview
REST API endpoints for the 4x10 Schedule Manager system.

## Base URL
```
http://localhost:6247
```

## Authentication
All API endpoints require session-based authentication via login.

## Endpoints

### Authentication

#### POST /api/login
Login to the system.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
- `302` - Redirect to home page with session cookie
- `302` - Redirect to login with error message

### Calendar

#### GET /calendar.ics
Download team calendar in iCal format.

**Query Parameters:**
- `weeks` (optional) - Number of weeks to generate (default: 52)
- `config` (optional) - Configuration file name

**Response:**
- `200` - iCal file download
- `500` - Error generating calendar

#### GET /engineer/{name}.ics
Download individual engineer calendar.

**Path Parameters:**
- `name` - Engineer name

**Query Parameters:**
- `weeks` (optional) - Number of weeks (default: 52)
- `config` (optional) - Configuration file

**Response:**
- `200` - Individual iCal file
- `404` - Engineer not found

### Swap Management

#### POST /api/swap
Create, approve, or reject swap requests.

**Request Body (Create):**
```json
{
  "action": "request",
  "requester": "string",
  "target": "string", 
  "date": "YYYY-MM-DD",
  "reason": "string"
}
```

**Request Body (Approve/Reject):**
```json
{
  "action": "approve|reject",
  "swap_id": "string",
  "approver": "string"
}
```

**Response:**
- `302` - Redirect with success/error message

### Views

#### GET /view
HTML calendar view with interactive interface.

**Query Parameters:**
- `weeks` (optional) - Number of weeks to display
- `config` (optional) - Team configuration
- `start_date` (optional) - Start date (YYYY-MM-DD)

#### GET /swaps
Swap management interface.

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Error Codes
- `200` - Success
- `302` - Redirect
- `403` - Insufficient permissions
- `404` - Resource not found
- `500` - Internal server error