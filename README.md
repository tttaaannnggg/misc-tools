# Zoom Meeting Scheduler - Multi-Account Edition

A comprehensive CLI tool for scheduling Zoom meetings across multiple accounts with recurring meeting support and timezone management.

## 📁 Project Structure

```
zoom_scheduler/
├── tool/                    # Main application files
│   ├── zoom_scheduler.py    # Main CLI tool (executable)
│   └── requirements.txt     # Python dependencies
├── configs/                 # Configuration files
│   ├── zoom_config.json           # Active multi-account config
│   ├── zoom_config_single.json.sample  # Single account template
│   ├── zoom_config_multi.json.sample   # Multi-account template
│   └── zoom_config.json.sample         # Legacy template
├── events/                  # Event definition files
│   ├── events_sample.json           # Basic sample events
│   ├── events_sample.csv            # CSV format sample
│   ├── igrc_events.json             # IGRC conference (Asia/Shanghai)
│   ├── igrc_events_multiacccount.json  # IGRC multi-account version
│   ├── igrc_sample_rooms.json       # Specific room scheduling (Shanghai)
│   ├── igrc_sample_rooms.csv        # CSV version (Shanghai)
│   ├── igrc_sample_rooms_pacific.json  # Pacific timezone version
│   └── igrc_sample_rooms_pacific.csv   # CSV Pacific version
├── schedules/               # Source schedule files
│   ├── 2025 STAFF IGRC Schedules - Pacific.csv  # 2025 Pacific schedule
│   └── comma-separated values.csv               # Original Shanghai schedule
└── documentation/           # Documentation and references
    ├── README.md                    # Main documentation
    ├── MULTI_ACCOUNT_README.md      # Multi-account feature guide
    ├── TIMEZONE_CONVERSION.md       # Timezone conversion reference
    └── Meetings.json                # Zoom API specification
```

## 🚀 Quick Start

### 1. Setup
```bash
cd zoom_scheduler/tool/
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure
```bash
# Copy and edit configuration
cp ../configs/zoom_config_multi.json.sample ../configs/zoom_config.json
# Edit zoom_config.json with your Zoom API credentials
```

### 3. Test
```bash
# Test with sample events
python3 zoom_scheduler.py ../events/events_sample.json --dry-run

# Test IGRC Pacific schedule
python3 zoom_scheduler.py ../events/igrc_sample_rooms_pacific.json --dry-run
```

### 4. Schedule Meetings
```bash
# Schedule IGRC rooms (Pacific time)
python3 zoom_scheduler.py ../events/igrc_sample_rooms_pacific.json --output results.json
```

## 📋 Key Features

### **Multi-Account Support**
- Schedule meetings across multiple Zoom accounts
- Account-specific event assignment
- Parallel authentication and management

### **Recurring Meetings**
- Same meeting ID across recurring instances
- Smart pattern detection (daily, weekly, monthly)
- Stable meeting URLs for participants

### **Timezone Management**
- Full timezone support (`Asia/Shanghai`, `America/Los_Angeles`)
- Automatic timezone conversions
- Pacific and Shanghai time examples included

### **Flexible Input Formats**
- JSON format with detailed settings
- CSV format for easy editing
- Event-level account and user assignment

## 📖 Documentation

- **[Main Documentation](documentation/README.md)** - Complete setup and usage guide
- **[Multi-Account Guide](documentation/MULTI_ACCOUNT_README.md)** - Multi-account feature details
- **[Timezone Reference](documentation/TIMEZONE_CONVERSION.md)** - Timezone conversion examples

## 🎯 IGRC Conference Examples

The project includes complete examples for the IGRC conference:

### **Room-Specific Scheduling**
- **SSG Room 1**: Small Study Group sessions
- **RAG 1**: Review and Application Group (5 daily sessions)
- **IE Room 1**: Institutional Event sessions
- **All LSG Sessions**: Large Study Groups with same meeting ID

### **Pacific Time Support**
All IGRC examples include Pacific timezone versions for US-based participants.

## 🔧 Advanced Usage

### **Create Custom Events**
```bash
# Generate sample files
python3 zoom_scheduler.py --create-samples

# Use generated templates in ../events/ folder
```

### **Multi-Account Configuration**
```json
{
  "accounts": [
    {
      "name": "Primary Account",
      "account_id": "your_account_id",
      "client_id": "your_client_id",
      "client_secret": "your_client_secret",
      "user_id": "user@company.com"
    }
  ]
}
```

### **Event Assignment**
```json
{
  "events": [
    {
      "title": "Meeting Name",
      "account_name": "Primary Account",
      "timezone": "America/Los_Angeles",
      "instances": ["2024-10-03T17:15:00"]
    }
  ]
}
```

## 🆘 Support

For issues and questions:
1. Check the documentation in the `documentation/` folder
2. Review sample files in the `events/` folder
3. Test with `--dry-run` before scheduling
4. Verify Zoom API credentials in `configs/zoom_config.json`

---

*Enhanced with multi-account support and timezone management for complex conference scheduling.*