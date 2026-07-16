# Usage

## Daily Workflow

### 1. Create Today's Log

```bash
python cli.py new
```

This creates `logs/YYYY/MM/YYYY-MM-DD.md` with structured sections.

### 2. Write Your Notes

Open the log file and fill in:
- **Goals** — What you plan to accomplish
- **Completed Tasks** — What you finished
- **Study Notes** — What you learned
- **Coding Notes** — Technical notes and snippets
- **Bugs Fixed** — Issues resolved
- **Learnings** — Key insights
- **Tomorrow Plan** — What's next

### 3. Generate AI Summary

```bash
python cli.py summary
```

The AI reads your raw notes and generates a professional summary with key takeaways and action items.

### 4. Commit & Push

```bash
git add .
git commit -m "📝 Daily log: $(date +%Y-%m-%d)"
git push
```

## Commands Reference

### `new [DATE]`

Create a new daily log.

```bash
python cli.py new              # Today
python cli.py new 2024-03-15   # Specific date
```

### `summary [DATE]`

Generate an AI summary for a log.

```bash
python cli.py summary              # Today's log
python cli.py summary 2024-03-15   # Specific date
```

### `weekly`

Generate a weekly report.

```bash
python cli.py weekly                     # Current week
python cli.py weekly --week 12           # Week 12
python cli.py weekly --week 12 --year 2024
```

### `monthly`

Generate a monthly report.

```bash
python cli.py monthly                      # Current month
python cli.py monthly --month 3            # March
python cli.py monthly --month 3 --year 2024
```

### `stats`

Show streak and repository statistics.

```bash
python cli.py stats
```

### `dashboard`

Regenerate the README dashboard.

```bash
python cli.py dashboard
```

### `help`

Show detailed help.

```bash
python cli.py help
```

## Weekly Workflow

At the end of each week:

```bash
python cli.py weekly
python cli.py dashboard
git add reports/ README.md
git commit -m "📊 Weekly report: Week $(date +%V)"
git push
```

## Monthly Workflow

At the end of each month:

```bash
python cli.py monthly
python cli.py dashboard
git add reports/ README.md
git commit -m "📅 Monthly report: $(date +%Y-%m)"
git push
```

## Automated Workflows

When you push logs to the `main` branch, GitHub Actions automatically:
1. Generates/updates weekly and monthly reports
2. Updates the README dashboard
3. Commits changes (only if content changed)
4. Checks for missing daily logs and opens reminder issues
