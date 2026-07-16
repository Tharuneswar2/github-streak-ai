# API Reference

## Core Modules

### `scripts.ai_client.NvidiaAIClient`

NVIDIA NIM API client for AI-powered text generation.

```python
from scripts.ai_client import NvidiaAIClient

client = NvidiaAIClient()

# Generate summary from raw notes
response = client.generate_summary("Today I worked on...")
print(response.content)

# Generate weekly analysis
response = client.generate_weekly_analysis(
    daily_logs="...",
    stats={"active_days": 5, "commits": 12}
)

# Generate monthly insights
response = client.generate_monthly_insights(
    monthly_data="...",
    stats={"active_days": 22}
)
```

**Returns:** `AIResponse(content, model, usage, finish_reason)`

**Exceptions:**
- `APIKeyMissingError` — NVIDIA_API_KEY not set
- `APIRequestError` — Network or HTTP errors
- `APIResponseError` — Malformed API response

---

### `scripts.log_manager.LogManager`

Daily log file CRUD operations.

```python
from scripts.log_manager import LogManager

manager = LogManager()

# Create today's log
path = manager.create_daily_log()

# Create log for specific date
from datetime import date
path = manager.create_daily_log(date(2024, 3, 15))

# Read a log
content = manager.get_log(date(2024, 3, 15))

# Update a log
manager.update_log(date.today(), "# New content\n")

# Update a specific section
manager.update_section(date.today(), "AI Summary", "AI-generated text")

# Check if log exists
exists = manager.log_exists(date.today())

# List all logs
all_logs = manager.list_logs()

# Get dates with logs
dates = manager.get_log_dates()

# Get logs in a date range
logs = manager.get_logs_for_range(date(2024, 3, 1), date(2024, 3, 31))
```

---

### `scripts.streak_tracker.StreakTracker`

Contribution streak tracking.

```python
from scripts.streak_tracker import StreakTracker

tracker = StreakTracker()

# Get current streak
current = tracker.get_current_streak()

# Get longest streak
longest = tracker.get_longest_streak()

# Get status (🔥 Active / ⚠️ At Risk / ❌ Broken)
status = tracker.get_status()

# Get comprehensive info
info = tracker.get_streak_info()
# Returns: {current_streak, longest_streak, status, total_logged_days, today_logged, first_log, last_log}

# Get activity calendar
calendar = tracker.get_activity_calendar(year=2024, month=3)
# Returns: {"2024-03-01": True, "2024-03-02": False, ...}
```

---

### `scripts.report_generator.ReportGenerator`

Weekly and monthly report generation.

```python
from scripts.report_generator import ReportGenerator

generator = ReportGenerator()

# Generate weekly report
path = generator.generate_weekly_report(week_number=12, year=2024)

# Generate monthly report
path = generator.generate_monthly_report(year=2024, month=3)
```

---

### `scripts.git_stats.GitStatsCollector`

Git repository statistics.

```python
from scripts.git_stats import GitStatsCollector

collector = GitStatsCollector()

stats = collector.get_full_stats()
# Returns RepoStatistics with:
# total_commits, total_files, total_loc, active_days,
# current_streak, longest_streak, top_authors,
# recent_commits, files_by_type
```

---

### `dashboard.generator.DashboardGenerator`

README dashboard generation.

```python
from dashboard.generator import DashboardGenerator

gen = DashboardGenerator()
path = gen.generate()  # Writes to README.md
```

---

### `dashboard.badges.BadgeGenerator`

Shields.io badge creation.

```python
from dashboard.badges import BadgeGenerator

badges = BadgeGenerator()
md = badges.generate_all_badges(streak=42, logs=100, commits=500, hours=80.5, projects=5)
```

---

## Configuration

### `config.settings.Settings`

```python
from config.settings import get_settings

settings = get_settings()
print(settings.nvidia_api_key)  # From env
print(settings.logs_dir)        # Path to logs/
print(settings.has_api_key)     # Boolean
```

### `config.constants`

All constants are importable:

```python
from config.constants import DATE_FORMAT, LOG_SECTIONS, STREAK_ACTIVE
```
