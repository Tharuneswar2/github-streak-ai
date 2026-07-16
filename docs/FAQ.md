# FAQ

## General

### What is GitHub Streak AI?

GitHub Streak AI is a CLI tool that helps you maintain meaningful GitHub contribution streaks. Instead of fake commits, it encourages real work through daily logging, AI-powered summaries, and automated reporting.

### Does this create fake commits?

**No.** This project explicitly rejects fake commits. Every commit represents real work — notes, code, learning, documentation. The GitHub Actions workflows will never create empty commits.

### Do I need an NVIDIA API key?

The API key is **recommended** but not required. Without it, all features work except AI-powered summaries and analysis. You can still create logs, track streaks, generate reports (without AI sections), and update the dashboard.

### Is this free?

The software is free and open source (MIT License). The NVIDIA NIM API has a free tier that is sufficient for daily use.

---

## Technical

### What Python version do I need?

Python 3.12 or higher.

### Can I use a different AI model?

Yes! Set the `MODEL` environment variable to any model available on the NVIDIA NIM platform. See [Configuration.md](Configuration.md) for compatible models.

### How are study hours calculated?

Study hours are estimated from the total lines in your log files (~50 lines per hour of notes). This is a rough heuristic — for more accurate tracking, note your hours in the log.

### How does streak tracking work?

A streak counts consecutive days with a log file. The streak is:
- **🔥 Active** — Today's log exists
- **⚠️ At Risk** — Yesterday's log exists but today's doesn't
- **❌ Broken** — No log for yesterday or today

### Can I customize the log template?

Yes! Edit `templates/daily_log.md.j2` to change the structure. All templates use Jinja2 syntax.

---

## Workflow

### What if I miss a day?

Your streak will be at risk (⚠️) until the end of the day, then broken (❌). You can backfill a log with:

```bash
python cli.py new 2024-03-15
```

### How do I use this with an existing repository?

Copy the project files into your repo, install dependencies, and run `python cli.py new` to start logging.

### Can I use this for multiple projects?

Each project gets its own `github-streak-ai` setup. Logs, reports, and dashboards are per-repository.
