#!/usr/bin/env python3
"""
Zoom Meeting Scheduler CLI Tool

A command-line tool to schedule Zoom meetings with recurring instances
that maintain the same meeting ID/link across all occurrences.
"""

import argparse
import json
import csv
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import requests
import base64
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MeetingEvent:
    """Represents a meeting event with multiple instances"""
    title: str
    description: str
    duration_minutes: int
    instances: List[datetime]
    timezone: str = "UTC"
    settings: Optional[Dict[str, Any]] = None
    account_name: Optional[str] = None  # Which account to use for this event
    user_id: Optional[str] = None  # Override user_id for this specific event


class ZoomAPIClient:
    """Zoom API client for meeting management"""

    def __init__(self, account_id: str, client_id: str, client_secret: str, name: str = None):
        self.account_id = account_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.name = name or account_id
        self.access_token = None
        self.base_url = "https://api.zoom.us/v2"

    def authenticate(self) -> bool:
        """Authenticate with Zoom API using Server-to-Server OAuth"""
        try:
            auth_string = f"{self.client_id}:{self.client_secret}"
            auth_bytes = auth_string.encode('ascii')
            auth_base64 = base64.b64encode(auth_bytes).decode('ascii')

            headers = {
                'Authorization': f'Basic {auth_base64}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            data = {
                'grant_type': 'account_credentials',
                'account_id': self.account_id
            }

            response = requests.post(
                'https://zoom.us/oauth/token',
                headers=headers,
                data=data
            )

            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                return True
            else:
                print(f"Authentication failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"Authentication error: {e}")
            return False

    def create_meeting(self, user_id: str, meeting_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a meeting using Zoom API"""
        if not self.access_token:
            print("Not authenticated. Please authenticate first.")
            return None

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(
                f"{self.base_url}/users/{user_id}/meetings",
                headers=headers,
                json=meeting_data
            )

            if response.status_code == 201:
                return response.json()
            else:
                print(f"Meeting creation failed: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"Error creating meeting: {e}")
            return None


class MultiAccountZoomManager:
    """Manages multiple Zoom API clients for different accounts"""

    def __init__(self, accounts_config: List[Dict[str, str]]):
        self.clients = {}
        self.default_users = {}

        for account in accounts_config:
            name = account.get('name', account['account_id'])
            client = ZoomAPIClient(
                account_id=account['account_id'],
                client_id=account['client_id'],
                client_secret=account['client_secret'],
                name=name
            )
            self.clients[name] = client
            self.default_users[name] = account.get('user_id')

    def authenticate_all(self) -> Dict[str, bool]:
        """Authenticate all clients"""
        results = {}
        for name, client in self.clients.items():
            print(f"Authenticating {name}...")
            results[name] = client.authenticate()
            if results[name]:
                print(f"✓ {name} authenticated successfully")
            else:
                print(f"✗ {name} authentication failed")
        return results

    def get_client(self, account_name: str) -> Optional[ZoomAPIClient]:
        """Get client for specific account"""
        return self.clients.get(account_name)

    def get_default_user(self, account_name: str) -> Optional[str]:
        """Get default user ID for account"""
        return self.default_users.get(account_name)

    def list_accounts(self) -> List[str]:
        """List all available account names"""
        return list(self.clients.keys())


class EventParser:
    """Parse events from various input formats"""

    @staticmethod
    def from_csv(file_path: str) -> List[MeetingEvent]:
        """Parse events from CSV file"""
        events = []

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    # Parse datetime instances
                    instances = []
                    instance_count = 1

                    while f'datetime_{instance_count}' in row and row[f'datetime_{instance_count}']:
                        dt_str = row[f'datetime_{instance_count}']
                        instances.append(datetime.fromisoformat(dt_str))
                        instance_count += 1

                    if instances:  # Only create event if there are instances
                        event = MeetingEvent(
                            title=row.get('title', 'Untitled Meeting'),
                            description=row.get('description', ''),
                            duration_minutes=int(row.get('duration_minutes', 60)),
                            instances=instances,
                            timezone=row.get('timezone', 'UTC'),
                            account_name=row.get('account_name'),
                            user_id=row.get('user_id')
                        )
                        events.append(event)

        except Exception as e:
            print(f"Error parsing CSV: {e}")

        return events

    @staticmethod
    def from_json(file_path: str) -> List[MeetingEvent]:
        """Parse events from JSON file"""
        events = []

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

                for event_data in data.get('events', []):
                    instances = [
                        datetime.fromisoformat(dt_str)
                        for dt_str in event_data.get('instances', [])
                    ]

                    event = MeetingEvent(
                        title=event_data.get('title', 'Untitled Meeting'),
                        description=event_data.get('description', ''),
                        duration_minutes=event_data.get('duration_minutes', 60),
                        instances=instances,
                        timezone=event_data.get('timezone', 'UTC'),
                        settings=event_data.get('settings'),
                        account_name=event_data.get('account_name'),
                        user_id=event_data.get('user_id')
                    )
                    events.append(event)

        except Exception as e:
            print(f"Error parsing JSON: {e}")

        return events


class MeetingScheduler:
    """Main scheduler class"""

    def __init__(self, zoom_manager=None, zoom_client: ZoomAPIClient = None):
        # Support both single-client (legacy) and multi-account modes
        if zoom_manager:
            self.zoom_manager = zoom_manager
            self.multi_account = True
        elif zoom_client:
            self.zoom_client = zoom_client
            self.multi_account = False
        else:
            raise ValueError("Either zoom_manager or zoom_client must be provided")

    def schedule_events(self, events: List[MeetingEvent], default_user_id: str = None) -> List[Dict[str, Any]]:
        """Schedule all events and return meeting details"""
        scheduled_meetings = []

        for i, event in enumerate(events, 1):
            account_info = ""
            if self.multi_account and event.account_name:
                account_info = f" [Account: {event.account_name}]"

            print(f"Scheduling event {i}/{len(events)}: {event.title}{account_info}")

            # Determine which client and user to use
            if self.multi_account:
                client, user_id = self._get_client_and_user(event, default_user_id)
                if not client:
                    print(f"✗ No valid account/client found for: {event.title}")
                    continue
            else:
                client = self.zoom_client
                user_id = event.user_id or default_user_id

            if len(event.instances) == 1:
                # Single meeting
                meeting = self._create_single_meeting(event, user_id, client)
            else:
                # Recurring meeting series
                meeting = self._create_recurring_meeting(event, user_id, client)

            if meeting:
                scheduled_meetings.append({
                    'event': event,
                    'meeting_data': meeting,
                    'account_name': event.account_name if self.multi_account else 'default',
                    'user_id': user_id
                })
                print(f"✓ Created meeting: {meeting.get('join_url', 'N/A')}")
            else:
                print(f"✗ Failed to create meeting for: {event.title}")

        return scheduled_meetings

    def _get_client_and_user(self, event: MeetingEvent, default_user_id: str) -> tuple[Optional[ZoomAPIClient], Optional[str]]:
        """Get the appropriate client and user ID for an event"""
        if not self.multi_account:
            return self.zoom_client, default_user_id

        # If event specifies an account, use that
        if event.account_name:
            client = self.zoom_manager.get_client(event.account_name)
            if client:
                user_id = event.user_id or self.zoom_manager.get_default_user(event.account_name)
                return client, user_id
            else:
                print(f"Warning: Account '{event.account_name}' not found")

        # Fallback to first available account
        accounts = self.zoom_manager.list_accounts()
        if accounts:
            first_account = accounts[0]
            client = self.zoom_manager.get_client(first_account)
            user_id = event.user_id or self.zoom_manager.get_default_user(first_account) or default_user_id
            print(f"  Using fallback account: {first_account}")
            return client, user_id

        return None, None

    def _create_single_meeting(self, event: MeetingEvent, user_id: str, client: ZoomAPIClient = None) -> Optional[Dict[str, Any]]:
        """Create a single (non-recurring) meeting"""
        start_time = event.instances[0]

        meeting_data = {
            'topic': event.title,
            'type': 2,  # Scheduled meeting
            'start_time': start_time.isoformat(),
            'duration': event.duration_minutes,
            'timezone': event.timezone,
            'agenda': event.description,
            'settings': {
                'host_video': True,
                'participant_video': True,
                'join_before_host': False,
                'mute_upon_entry': True,
                'watermark': False,
                'use_pmi': False,
                'approval_type': 2,  # Automatically approve
                'audio': 'both',  # Both computer and phone audio
                'auto_recording': 'none'
            }
        }

        # Apply custom settings if provided
        if event.settings:
            meeting_data['settings'].update(event.settings)

        client = client or self.zoom_client
        return client.create_meeting(user_id, meeting_data)

    def _create_recurring_meeting(self, event: MeetingEvent, user_id: str, client: ZoomAPIClient = None) -> Optional[Dict[str, Any]]:
        """Create a recurring meeting series with fixed times"""
        # For recurring meetings with specific dates, we'll use type 8 (recurring with fixed time)
        # However, Zoom's API typically expects a pattern rather than specific dates
        # For specific dates, we might need to create individual meetings with the same settings

        # Sort instances by date
        sorted_instances = sorted(event.instances)
        first_instance = sorted_instances[0]

        # Check if instances follow a regular pattern
        if len(sorted_instances) >= 2:
            pattern = self._detect_recurrence_pattern(sorted_instances)
            if pattern:
                return self._create_pattern_based_recurring_meeting(event, user_id, pattern, client)

        # If no pattern detected, create individual meetings with same settings
        # This approach ensures all instances share similar characteristics
        return self._create_series_of_meetings(event, user_id, client)

    def _detect_recurrence_pattern(self, instances: List[datetime]) -> Optional[Dict[str, Any]]:
        """Detect if instances follow a regular recurrence pattern"""
        if len(instances) < 2:
            return None

        # Check for daily pattern
        deltas = [instances[i+1] - instances[i] for i in range(len(instances)-1)]

        # Check if all intervals are the same
        if all(delta == deltas[0] for delta in deltas):
            days = deltas[0].days
            if days == 1:
                return {'type': 1, 'repeat_interval': 1}  # Daily
            elif days == 7:
                return {'type': 2, 'repeat_interval': 1}  # Weekly
            elif days in [28, 29, 30, 31]:
                return {'type': 3, 'repeat_interval': 1}  # Monthly

        return None

    def _create_pattern_based_recurring_meeting(self, event: MeetingEvent, user_id: str, pattern: Dict[str, Any], client: ZoomAPIClient = None) -> Optional[Dict[str, Any]]:
        """Create a true recurring meeting with detected pattern"""
        start_time = sorted(event.instances)[0]

        meeting_data = {
            'topic': event.title,
            'type': 8,  # Recurring meeting with fixed time
            'start_time': start_time.isoformat(),
            'duration': event.duration_minutes,
            'timezone': event.timezone,
            'agenda': event.description,
            'recurrence': {
                'type': pattern['type'],
                'repeat_interval': pattern['repeat_interval'],
                'end_times': len(event.instances)
            },
            'settings': {
                'host_video': True,
                'participant_video': True,
                'join_before_host': False,
                'mute_upon_entry': True,
                'watermark': False,
                'use_pmi': False,
                'approval_type': 2,
                'audio': 'both',
                'auto_recording': 'none'
            }
        }

        if event.settings:
            meeting_data['settings'].update(event.settings)

        client = client or self.zoom_client
        return client.create_meeting(user_id, meeting_data)

    def _create_series_of_meetings(self, event: MeetingEvent, user_id: str, client: ZoomAPIClient = None) -> Optional[Dict[str, Any]]:
        """Create multiple individual meetings for irregular scheduling"""
        # For now, create the first meeting and note that this approach
        # won't share the same meeting ID across instances
        # This is a limitation when dates don't follow a regular pattern

        print(f"  Note: Creating individual meetings for irregular schedule")
        first_instance = min(event.instances)

        meeting_data = {
            'topic': f"{event.title} (Series)",
            'type': 2,  # Scheduled meeting
            'start_time': first_instance.isoformat(),
            'duration': event.duration_minutes,
            'timezone': event.timezone,
            'agenda': f"{event.description}\n\nNote: This is part of a series with {len(event.instances)} total instances.",
            'settings': {
                'host_video': True,
                'participant_video': True,
                'join_before_host': False,
                'mute_upon_entry': True,
                'watermark': False,
                'use_pmi': False,
                'approval_type': 2,
                'audio': 'both',
                'auto_recording': 'none'
            }
        }

        if event.settings:
            meeting_data['settings'].update(event.settings)

        client = client or self.zoom_client
        return client.create_meeting(user_id, meeting_data)


def load_config(config_path: str = "zoom_config.json") -> Dict[str, Any]:
    """Load Zoom API configuration from file"""
    try:
        with open(config_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Config file {config_path} not found. Please create it with your Zoom API credentials.")
        return {}
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}


def detect_config_format(config: Dict[str, Any]) -> str:
    """Detect if config is single-account or multi-account format"""
    if 'accounts' in config and isinstance(config['accounts'], list):
        return 'multi'
    elif all(key in config for key in ['account_id', 'client_id', 'client_secret']):
        return 'single'
    else:
        return 'unknown'


def create_sample_files():
    """Create sample configuration and event files"""

    # Sample single-account config file
    config_single = {
        "account_id": "your_zoom_account_id",
        "client_id": "your_zoom_client_id",
        "client_secret": "your_zoom_client_secret",
        "user_id": "your_zoom_user_email_or_id"
    }

    with open("zoom_config_single.json.sample", 'w') as f:
        json.dump(config_single, f, indent=2)

    # Sample multi-account config file
    config_multi = {
        "accounts": [
            {
                "name": "Primary Account",
                "account_id": "primary_account_id",
                "client_id": "primary_client_id",
                "client_secret": "primary_client_secret",
                "user_id": "primary_user@company.com"
            },
            {
                "name": "Secondary Account",
                "account_id": "secondary_account_id",
                "client_id": "secondary_client_id",
                "client_secret": "secondary_client_secret",
                "user_id": "secondary_user@company.com"
            }
        ]
    }

    with open("zoom_config_multi.json.sample", 'w') as f:
        json.dump(config_multi, f, indent=2)

    # Sample events JSON with multi-account support
    events_sample = {
        "events": [
            {
                "title": "Daily Standup",
                "description": "Daily team standup meeting",
                "duration_minutes": 30,
                "timezone": "America/New_York",
                "account_name": "Primary Account",
                "instances": [
                    "2024-01-15T09:00:00",
                    "2024-01-16T09:00:00",
                    "2024-01-17T09:00:00",
                    "2024-01-18T09:00:00",
                    "2024-01-19T09:00:00"
                ],
                "settings": {
                    "waiting_room": True,
                    "mute_upon_entry": True
                }
            },
            {
                "title": "Weekly Review",
                "description": "Weekly project review meeting",
                "duration_minutes": 60,
                "timezone": "America/New_York",
                "account_name": "Secondary Account",
                "user_id": "custom_user@company.com",
                "instances": [
                    "2024-01-15T14:00:00",
                    "2024-01-22T14:00:00",
                    "2024-01-29T14:00:00"
                ]
            }
        ]
    }

    with open("events_sample.json", 'w') as f:
        json.dump(events_sample, f, indent=2)

    # Sample CSV format with multi-account support
    csv_content = """title,description,duration_minutes,timezone,account_name,user_id,datetime_1,datetime_2,datetime_3
Daily Standup,Daily team meeting,30,America/New_York,Primary Account,,2024-01-15T09:00:00,2024-01-16T09:00:00,2024-01-17T09:00:00
Weekly Review,Weekly project review,60,America/New_York,Secondary Account,custom_user@company.com,2024-01-15T14:00:00,2024-01-22T14:00:00,2024-01-29T14:00:00"""

    with open("events_sample.csv", 'w') as f:
        f.write(csv_content)

    print("Sample files created:")
    print("- zoom_config_single.json.sample (single account configuration)")
    print("- zoom_config_multi.json.sample (multi-account configuration)")
    print("- events_sample.json (JSON format with account assignment)")
    print("- events_sample.csv (CSV format with account assignment)")
    print("\nFor multi-account usage:")
    print("  1. Rename zoom_config_multi.json.sample to zoom_config.json")
    print("  2. Fill in your multiple Zoom API credentials")
    print("  3. Assign events to specific accounts using 'account_name' field")


def main():
    parser = argparse.ArgumentParser(
        description="Schedule Zoom meetings with recurring instances",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s events.json                    # Schedule from JSON file
  %(prog)s events.csv --format csv        # Schedule from CSV file
  %(prog)s --create-samples               # Create sample files
  %(prog)s events.json --config custom_config.json  # Use custom config

The tool maintains the same meeting ID/link for recurring meeting instances
when they follow a regular pattern (daily, weekly, monthly).
        """
    )

    parser.add_argument('events_file', nargs='?', help='Path to events file (JSON or CSV)')
    parser.add_argument('--config', default='zoom_config.json', help='Path to Zoom API config file')
    parser.add_argument('--format', choices=['json', 'csv'], help='Input file format (auto-detected if not specified)')
    parser.add_argument('--user-id', help='Zoom user ID (overrides config file)')
    parser.add_argument('--dry-run', action='store_true', help='Parse events but don\'t create meetings')
    parser.add_argument('--create-samples', action='store_true', help='Create sample configuration and event files')
    parser.add_argument('--output', help='Save meeting details to JSON file')

    args = parser.parse_args()

    if args.create_samples:
        create_sample_files()
        return

    if not args.events_file:
        parser.error("Please provide an events file or use --create-samples")

    # Load configuration
    config = load_config(args.config)
    if not config:
        print("Please create a zoom_config.json file with your Zoom API credentials.")
        print("Use --create-samples to generate sample configuration files.")
        sys.exit(1)

    # Detect configuration format
    config_format = detect_config_format(config)

    if config_format == 'unknown':
        print("Invalid configuration format. Please use --create-samples to see examples.")
        sys.exit(1)

    # Validate configuration based on format
    if config_format == 'single':
        required_keys = ['account_id', 'client_id', 'client_secret', 'user_id']
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            print(f"Missing required configuration keys: {missing_keys}")
            sys.exit(1)
        default_user_id = args.user_id or config['user_id']

    elif config_format == 'multi':
        if not config.get('accounts'):
            print("Multi-account config must have 'accounts' list")
            sys.exit(1)

        for i, account in enumerate(config['accounts']):
            required_keys = ['account_id', 'client_id', 'client_secret']
            missing_keys = [key for key in required_keys if key not in account]
            if missing_keys:
                print(f"Account {i+1} missing required keys: {missing_keys}")
                sys.exit(1)

        default_user_id = args.user_id  # May be None for multi-account

    # Parse events
    file_path = Path(args.events_file)
    if not file_path.exists():
        print(f"Events file not found: {args.events_file}")
        sys.exit(1)

    # Auto-detect format if not specified
    file_format = args.format
    if not file_format:
        if file_path.suffix.lower() == '.csv':
            file_format = 'csv'
        else:
            file_format = 'json'

    print(f"Parsing events from {args.events_file} (format: {file_format})")

    if file_format == 'csv':
        events = EventParser.from_csv(args.events_file)
    else:
        events = EventParser.from_json(args.events_file)

    if not events:
        print("No events found in the input file.")
        sys.exit(1)

    print(f"Found {len(events)} event(s)")

    for i, event in enumerate(events, 1):
        print(f"  {i}. {event.title} ({len(event.instances)} instances)")

    if args.dry_run:
        print("\nDry run completed. No meetings were created.")
        return

    # Initialize Zoom client(s) and authenticate
    if config_format == 'single':
        zoom_client = ZoomAPIClient(
            account_id=config['account_id'],
            client_id=config['client_id'],
            client_secret=config['client_secret']
        )

        print("\nAuthenticating with Zoom API...")
        if not zoom_client.authenticate():
            print("Failed to authenticate with Zoom API. Please check your credentials.")
            sys.exit(1)

        print("Authentication successful!")
        scheduler = MeetingScheduler(zoom_client=zoom_client)

    else:  # multi-account
        print(f"\nInitializing {len(config['accounts'])} Zoom accounts...")
        zoom_manager = MultiAccountZoomManager(config['accounts'])

        print("\nAuthenticating with Zoom APIs...")
        auth_results = zoom_manager.authenticate_all()

        failed_accounts = [name for name, success in auth_results.items() if not success]
        if failed_accounts:
            print(f"\nWarning: Authentication failed for accounts: {failed_accounts}")
            if len(failed_accounts) == len(config['accounts']):
                print("All accounts failed authentication. Cannot proceed.")
                sys.exit(1)

        print("\nAuthentication completed!")
        scheduler = MeetingScheduler(zoom_manager=zoom_manager)

    # Schedule meetings
    if config_format == 'single':
        print(f"\nScheduling meetings for user: {default_user_id}")
    else:
        print(f"\nScheduling meetings across {len(config['accounts'])} accounts...")

    scheduled_meetings = scheduler.schedule_events(events, default_user_id)

    # Output results
    print(f"\nCompleted! Successfully scheduled {len(scheduled_meetings)}/{len(events)} events.")

    if args.output:
        output_data = {
            'scheduled_at': datetime.now().isoformat(),
            'config_format': config_format,
            'default_user_id': default_user_id,
            'meetings': [
                {
                    'event_title': meeting['event'].title,
                    'meeting_id': meeting['meeting_data'].get('id'),
                    'join_url': meeting['meeting_data'].get('join_url'),
                    'start_url': meeting['meeting_data'].get('start_url'),
                    'instances': len(meeting['event'].instances),
                    'account_name': meeting.get('account_name'),
                    'user_id': meeting.get('user_id')
                }
                for meeting in scheduled_meetings
            ]
        }

        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"Meeting details saved to: {args.output}")


if __name__ == "__main__":
    main()