# Zoom Meeting Scheduler CLI Tool

A command-line tool to schedule Zoom meetings with recurring instances that maintain the same meeting ID/link across all occurrences.

## Features

- **Recurring Meetings with Same ID**: Automatically creates recurring meetings that share the same meeting ID and join URL
- **Multiple Input Formats**: Supports both JSON and CSV input formats
- **Pattern Detection**: Detects regular patterns (daily, weekly, monthly) for optimal recurring meeting setup
- **Flexible Scheduling**: Handles irregular schedules by creating series of individual meetings
- **Zoom API Integration**: Uses Server-to-Server OAuth for secure API access
- **Dry Run Mode**: Test your event parsing without creating actual meetings

## Prerequisites

- Python 3.7+
- Zoom account with API access
- Zoom Server-to-Server OAuth app credentials

## Installation

1. Clone or download the tool:
```bash
git clone <repository> # or download zoom_scheduler.py
cd chinaconference
```

2. Create a virtual environment and install dependencies:
```bash
python3 -m venv zoom_env
source zoom_env/bin/activate  # On Windows: zoom_env\Scripts\activate
pip install -r requirements.txt
```

3. Make the script executable (optional):
```bash
chmod +x zoom_scheduler.py
```

## Zoom API Setup

1. Go to [Zoom App Marketplace](https://marketplace.zoom.us/)
2. Click "Develop" → "Build App"
3. Choose "Server-to-Server OAuth" app type
4. Fill in app information and get your credentials:
   - Account ID
   - Client ID
   - Client Secret
5. Add required scopes:
   - `meeting:write`
   - `meeting:read`

## Configuration

1. Create sample configuration files:
```bash
python3 zoom_scheduler.py --create-samples
```

2. Rename and edit the configuration file:
```bash
cp zoom_config.json.sample zoom_config.json
```

3. Edit `zoom_config.json` with your Zoom API credentials:
```json
{
  "account_id": "your_zoom_account_id",
  "client_id": "your_zoom_client_id",
  "client_secret": "your_zoom_client_secret",
  "user_id": "your_zoom_user_email_or_id"
}
```

## Usage

### Basic Usage

```bash
# Schedule meetings from JSON file
python3 zoom_scheduler.py events.json

# Schedule meetings from CSV file
python3 zoom_scheduler.py events.csv --format csv

# Dry run (parse events but don't create meetings)
python3 zoom_scheduler.py events.json --dry-run

# Save meeting details to file
python3 zoom_scheduler.py events.json --output scheduled_meetings.json
```

### Command Line Options

```
positional arguments:
  events_file           Path to events file (JSON or CSV)

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG       Path to Zoom API config file (default: zoom_config.json)
  --format {json,csv}   Input file format (auto-detected if not specified)
  --user-id USER_ID     Zoom user ID (overrides config file)
  --dry-run             Parse events but don't create meetings
  --create-samples      Create sample configuration and event files
  --output OUTPUT       Save meeting details to JSON file
```

## Input Formats

### JSON Format

```json
{
  "events": [
    {
      "title": "Daily Standup",
      "description": "Daily team standup meeting",
      "duration_minutes": 30,
      "timezone": "America/New_York",
      "instances": [
        "2024-01-15T09:00:00",
        "2024-01-16T09:00:00",
        "2024-01-17T09:00:00",
        "2024-01-18T09:00:00",
        "2024-01-19T09:00:00"
      ],
      "settings": {
        "waiting_room": true,
        "mute_upon_entry": true
      }
    }
  ]
}
```

### CSV Format

```csv
title,description,duration_minutes,timezone,datetime_1,datetime_2,datetime_3
Daily Standup,Daily team meeting,30,America/New_York,2024-01-15T09:00:00,2024-01-16T09:00:00,2024-01-17T09:00:00
```

## How Recurring Meetings Work

### Same Meeting ID Across Instances

The tool creates recurring meetings that maintain the **same meeting ID** for all instances:

- **Regular Patterns**: Daily, weekly, or monthly patterns use Zoom's native recurring meeting feature (Type 8)
- **Same Join URL**: All instances share the same join URL: `https://zoom.us/j/MEETING_ID`
- **Stable Links**: Participants can bookmark one URL for the entire series

### Meeting Types Created

1. **Type 2**: Single scheduled meeting (one instance)
2. **Type 8**: Recurring meeting with fixed time (regular patterns)
3. **Type 2 Series**: Individual meetings for irregular schedules

### Pattern Detection

The tool automatically detects patterns:
- **Daily**: Instances 1 day apart
- **Weekly**: Instances 7 days apart
- **Monthly**: Instances 28-31 days apart

For irregular schedules, it creates individual meetings with consistent settings.

## Examples

### Convert IGRC Schedule

To convert the IGRC conference schedule:

1. Create events JSON from the CSV data:
```json
{
  "events": [
    {
      "title": "Opening Plenary",
      "description": "IGRC Conference Opening Session",
      "duration_minutes": 50,
      "timezone": "Asia/Shanghai",
      "instances": ["2024-03-15T07:00:00"]
    },
    {
      "title": "Small Study Group 1 (SSG)",
      "description": "Small Study Group Session 1",
      "duration_minutes": 60,
      "timezone": "Asia/Shanghai",
      "instances": [
        "2024-03-15T08:15:00",
        "2024-03-16T09:30:00",
        "2024-03-17T11:00:00"
      ]
    }
  ]
}
```

2. Schedule the meetings:
```bash
python3 zoom_scheduler.py igrc_events.json --output igrc_meetings.json
```

### Daily Recurring Meeting

For a daily standup at 9 AM for a week:

```json
{
  "events": [
    {
      "title": "Daily Standup",
      "description": "Team daily standup",
      "duration_minutes": 15,
      "timezone": "America/New_York",
      "instances": [
        "2024-01-15T09:00:00",
        "2024-01-16T09:00:00",
        "2024-01-17T09:00:00",
        "2024-01-18T09:00:00",
        "2024-01-19T09:00:00"
      ]
    }
  ]
}
```

This creates a recurring meeting with:
- Same meeting ID for all 5 days
- Same join URL for all instances
- Automatic daily recurrence pattern

## Output

After scheduling, the tool provides:

```
Scheduling event 1/2: Daily Standup
  Note: Creating individual meetings for irregular schedule
✓ Created meeting: https://zoom.us/j/123456789

Completed! Successfully scheduled 2/2 events.
```

If using `--output`, it saves meeting details:

```json
{
  "scheduled_at": "2024-01-15T10:30:00",
  "user_id": "user@example.com",
  "meetings": [
    {
      "event_title": "Daily Standup",
      "meeting_id": "123456789",
      "join_url": "https://zoom.us/j/123456789",
      "start_url": "https://zoom.us/s/123456789?zak=...",
      "instances": 5
    }
  ]
}
```

## Error Handling

Common issues and solutions:

### Authentication Errors
- Verify your Zoom API credentials in `zoom_config.json`
- Ensure your OAuth app has the required scopes
- Check that the user_id exists in your Zoom account

### Meeting Creation Failures
- Verify user has meeting scheduling permissions
- Check rate limits (Zoom has API rate limiting)
- Ensure datetime formats are correct (ISO 8601)

### File Format Issues
- Use `--dry-run` to test parsing before creating meetings
- Check sample files created by `--create-samples`
- Verify CSV headers match expected format

## Limitations

1. **Irregular Patterns**: For irregular schedules, individual meetings are created rather than true recurring meetings
2. **Rate Limits**: Zoom API has rate limits; large batches may need delays
3. **Timezone Handling**: Ensure timezone strings are valid (e.g., "America/New_York")
4. **API Permissions**: Requires appropriate Zoom account permissions

## Development

To extend the tool:

1. **Add New Input Formats**: Extend `EventParser` class
2. **Custom Meeting Settings**: Modify meeting creation in `MeetingScheduler`
3. **Different Recurrence Patterns**: Enhance pattern detection logic
4. **Integration**: Use as a library by importing classes

## License

This tool is provided as-is for educational and practical use. Ensure compliance with Zoom's API terms of service.

## Support

For issues:
1. Check your Zoom API configuration
2. Verify input file format with `--dry-run`
3. Review Zoom API documentation for additional settings
4. Test with sample files first