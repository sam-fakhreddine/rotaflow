# PTO Integration Implementation

## Objective
Implement PTO (Paid Time Off) management system that integrates with the 4x10 schedule policy.

## Requirements from Policy
- Each PTO day reduces weekly requirement by 8 hours
- Engineers maintain their scheduled day off and work reduced hours across remaining days
- PTO on Tuesday (required day) needs manager approval due to missed team meetings
- Multiple PTO days: 2 days = 24 hours required, 3 days = 16 hours required, etc.
- Holiday weeks reduce work requirement from 40 to 32 hours
- Tuesday remains required unless Tuesday is the statutory holiday

## Implementation Tasks

### 1. PTO Data Model
- Create PTO request system with approval workflow
- Track PTO days per engineer per week
- Store statutory holidays configuration
- Link PTO to specific dates and engineers

### 2. Schedule Calculation Updates
- Modify rotation manager to account for PTO hour reductions
- Calculate remaining work hours after PTO deductions
- Distribute reduced hours across available work days
- Handle Tuesday PTO special approval requirements

### 3. Web Interface Updates
- PTO request form for engineers
- Manager approval interface for PTO requests
- Calendar view showing PTO days and reduced schedules
- Holiday configuration management

### 4. Validation Rules
- Prevent excessive PTO that would create coverage gaps
- Enforce manager approval for Tuesday PTO
- Validate PTO doesn't conflict with on-call duties
- Check minimum staffing requirements

## Files to Modify
- `app/models/` - New PTO manager class
- `app/models/rotation.py` - Update schedule generation
- `app/views/http_server.py` - Add PTO management endpoints
- `config/team_config.json` - Add holiday configuration

## Success Criteria
- Engineers can request PTO through web interface
- Managers can approve/reject PTO requests
- Schedule automatically adjusts work hours based on PTO
- Tuesday PTO requires special approval workflow
- Holiday weeks show 32-hour requirements
