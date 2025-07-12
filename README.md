# 4x10 Schedule Manager

A web-based schedule management system for 4-day work weeks with swap functionality.

## Features

- **4x10 Rotation**: Automated fair rotation of days off
- **Swap Management**: Request and approve day-off swaps
- **User Management**: Role-based access (admin, manager, engineer)
- **Web Interface**: Complete GUI for all operations
- **Calendar Export**: iCal format for calendar subscriptions

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

## Project Structure

```
schedule_manager/
├── app/
│   ├── models/          # Data models
│   ├── views/           # Web interface
│   ├── auth/            # Authentication
│   └── utils/           # Utilities
├── config/              # Configuration files
├── data/                # Runtime data (JSON files)
└── tests/               # Test files
```