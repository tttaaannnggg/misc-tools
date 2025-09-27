# Zoom Scheduler Usage Examples

## 🎯 Common Use Cases

### **1. IGRC Conference Scheduling (Pacific Time)**

Schedule specific rooms for the IGRC conference in Pacific timezone:

```bash
cd tool/
python3 zoom_scheduler.py ../events/igrc_sample_rooms_pacific.json --output ../results/igrc_pacific_results.json
```

**What this schedules:**
- **SSG Room 1**: 3 sessions across multiple days
- **RAG 1**: 5 daily sessions (9:15 PM Pacific)
- **IE Room 1**: 3 sessions on Sunday
- **All LSG Sessions**: 4 sessions with **same meeting ID**

### **2. Multi-Account Event Distribution**

```bash
cd tool/
python3 zoom_scheduler.py ../events/igrc_events_multiacccount.json --dry-run
```

**Features:**
- Events distributed across Primary and Secondary accounts
- Account-specific settings and permissions
- Unified scheduling across multiple Zoom licenses

### **3. Basic Sample Events**

```bash
cd tool/
python3 zoom_scheduler.py ../events/events_sample.json --dry-run
```

**Includes:**
- Daily standup meetings (5 instances)
- Weekly review meetings (3 instances)
- Multi-account assignment examples

## 📅 Scheduling Patterns

### **Same Meeting ID for Recurring Sessions**

The **Large Study Group (LSG)** events demonstrate how all 4 sessions share the same Zoom meeting ID:

```json
{
  "title": "Large Study Group (LSG) - ALL SESSIONS",
  "instances": [
    "2024-10-03T18:30:00",  // LSG 1
    "2024-10-04T17:15:00",  // LSG 2
    "2024-10-06T18:30:00",  // LSG 3
    "2024-10-07T16:00:00"   // LSG 4
  ]
}
```

**Result**: All 4 LSG sessions will have the same `meeting_id` and `join_url`.

### **Individual Meeting for Each Session**

The **RAG 1** events show daily sessions that could be individual meetings:

```json
{
  "title": "RAG 1",
  "instances": [
    "2024-10-03T21:15:00",  // Day 1
    "2024-10-04T21:15:00",  // Day 2
    "2024-10-05T21:15:00",  // Day 3
    "2024-10-06T21:15:00",  // Day 4
    "2024-10-07T19:45:00"   // Day 5 (different time)
  ]
}
```

**Result**: Since these follow a regular daily pattern, they'll be created as a recurring meeting series.

## 🌍 Timezone Examples

### **Pacific Time Schedule**
```bash
# Events scheduled for Pacific timezone participants
python3 zoom_scheduler.py ../events/igrc_sample_rooms_pacific.json
```

**Times:**
- **Afternoon sessions**: 4:00-6:30 PM Pacific
- **Evening sessions**: 5:15-8:00 PM Pacific
- **Late evening**: 9:15-10:15 PM Pacific

### **Shanghai Time Schedule**
```bash
# Events scheduled for Asia/Shanghai timezone
python3 zoom_scheduler.py ../events/igrc_sample_rooms.json
```

**Times:**
- **Morning sessions**: 7:00-11:00 AM Shanghai
- **Afternoon sessions**: 12:15-1:15 PM Shanghai

## 🔧 Configuration Examples

### **Single Account Setup**
```bash
cp configs/zoom_config_single.json.sample configs/zoom_config.json
```

```json
{
  "account_id": "your_zoom_account_id",
  "client_id": "your_zoom_client_id",
  "client_secret": "your_zoom_client_secret",
  "user_id": "your_email@company.com"
}
```

### **Multi-Account Setup**
```bash
cp configs/zoom_config_multi.json.sample configs/zoom_config.json
```

```json
{
  "accounts": [
    {
      "name": "Primary Account",
      "account_id": "primary_account_id",
      "client_id": "primary_client_id",
      "client_secret": "primary_client_secret",
      "user_id": "primary@company.com"
    },
    {
      "name": "Secondary Account",
      "account_id": "secondary_account_id",
      "client_id": "secondary_client_id",
      "client_secret": "secondary_client_secret",
      "user_id": "secondary@company.com"
    }
  ]
}
```

## 📊 Output Examples

### **Dry Run Output**
```bash
python3 zoom_scheduler.py ../events/igrc_sample_rooms_pacific.json --dry-run
```

```
Parsing events from ../events/igrc_sample_rooms_pacific.json (format: json)
Found 4 event(s)
  1. SSG Room 1 小型学习团体1 (3 instances)
  2. RAG 1 回顾与应用团体1 (5 instances)
  3. IE Room 1 机构活动室1 (3 instances)
  4. Large Study Group (LSG) 大型学习团体 - ALL SESSIONS (4 instances)

Dry run completed. No meetings were created.
```

### **Actual Scheduling Output**
```bash
python3 zoom_scheduler.py ../events/igrc_sample_rooms_pacific.json --output results.json
```

```
Initializing 2 Zoom accounts...
Authenticating Primary Account...
✓ Primary Account authenticated successfully
Authenticating Secondary Account...
✓ Secondary Account authenticated successfully

Scheduling meetings across 2 accounts...
Scheduling event 1/4: SSG Room 1 小型学习团体1 [Account: Primary Account]
✓ Created meeting: https://zoom.us/j/123456789
Scheduling event 2/4: RAG 1 回顾与应用团体1 [Account: Secondary Account]
✓ Created meeting: https://zoom.us/j/987654321
Scheduling event 3/4: IE Room 1 机构活动室1 [Account: Primary Account]
✓ Created meeting: https://zoom.us/j/111222333
Scheduling event 4/4: Large Study Group (LSG) [Account: Primary Account]
✓ Created meeting: https://zoom.us/j/444555666

Completed! Successfully scheduled 4/4 events.
Meeting details saved to: results.json
```

### **Results File Content**
```json
{
  "scheduled_at": "2024-10-03T10:30:00",
  "config_format": "multi",
  "meetings": [
    {
      "event_title": "Large Study Group (LSG) - ALL SESSIONS",
      "meeting_id": "444555666",
      "join_url": "https://zoom.us/j/444555666",
      "instances": 4,
      "account_name": "Primary Account",
      "user_id": "primary@company.com"
    }
  ]
}
```

## 🎯 Pro Tips

### **Testing Strategy**
1. **Always dry run first**: `--dry-run` to test parsing
2. **Start small**: Test with single events before bulk scheduling
3. **Check timezones**: Verify meeting times match expectations
4. **Account verification**: Ensure proper account assignment

### **Recurring Meeting Benefits**
- **Same URL**: Participants bookmark one link for all sessions
- **Consistent ID**: Meeting ID stays the same across all instances
- **Easy management**: Update settings for all instances at once

### **Multi-Account Strategy**
- **Load balancing**: Distribute events across accounts
- **Organizational separation**: Internal vs external meetings
- **Redundancy**: Backup accounts for critical meetings

---

*For more detailed documentation, see the `documentation/` folder.*