# User Guide

## Getting Started

### Accessing the System
1. Open your web browser
2. Navigate to `http://localhost:6247`
3. Login with your credentials

### Default Accounts
- **Admin**: `admin` / `admin123`
- **Manager**: `manager` / `manager123`

## Features

### Viewing Your Schedule

#### Team Calendar View
1. Click **"View Schedule"** from the home page
2. Use the form to customize:
   - **Weeks**: Number of weeks to display (1-104)
   - **Config**: Team size (5, 6, or 7 engineers)
   - **Start Date**: Custom start date
3. Click **"Update"** to refresh the view

#### Understanding the Calendar
- **Green**: Regular work days (4x10 schedule)
- **Orange**: On-call duty (5x8 schedule)
- **Blue**: Required day (Tuesday - everyone works)
- **Red**: Day off
- **Purple**: Statutory holiday
- **Dashed border**: Swapped schedule

### Managing Shift Swaps

#### Requesting a Swap
1. Click **"Manage Swaps"** from the home page
2. Fill out the swap request form:
   - **Your Name**: Select yourself
   - **Swap With**: Select colleague
   - **Date**: Choose the date
   - **Reason**: Brief explanation
3. Click **"Request Swap"**

#### Swap Rules
- Only people scheduled **off** and **on** can swap
- **Tuesday is required** for everyone (no swaps)
- Swaps are for **days off only**
- One person must be off, the other on
- Approved swaps don't change the base rotation

#### Approving Swaps (Managers/Admins)
1. View pending swaps in the **"Pending Swaps"** section
2. Click **"Approve"** or **"Reject"** for each request
3. Approved swaps appear in **"Approved Swaps"**

### Calendar Subscriptions

#### Personal Calendar Integration
1. Copy your personal calendar URL:
   - **Alex**: `webcal://localhost:6247/engineer/alex.ics`
   - **Blake**: `webcal://localhost:6247/engineer/blake.ics`
   - (etc. for each engineer)

#### Adding to Your Calendar App
- **iPhone/iPad**: Settings → Calendar → Accounts → Add Account → Other → Add Subscribed Calendar
- **Google Calendar**: Settings → Add calendar → From URL
- **Outlook**: File → Account Settings → Internet Calendars → New
- **Apple Calendar**: File → New Calendar Subscription

#### Team Calendar
- Full team calendar: `webcal://localhost:6247/calendar.ics`
- Custom weeks: `webcal://localhost:6247/calendar.ics?weeks=24`

### Downloading Calendars
1. Click **"Download Calendar"** for immediate download
2. Import the `.ics` file into your calendar application

## Troubleshooting

### Common Issues

**Can't see my schedule**
- Ensure you're logged in
- Check that your name appears in the engineer list
- Contact your administrator

**Swap request rejected**
- Verify swap rules are followed
- Check that both people have opposite schedules on that date
- Ensure the date isn't a Tuesday (required day)

**Calendar not updating**
- Refresh your browser
- Clear browser cache
- Re-subscribe to calendar feed

### Getting Help
Contact your system administrator for:
- Account issues
- Missing engineer names
- Technical problems
- Feature requests
