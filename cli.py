"""GitHub Streak AI — Command-Line Interface.

A beautiful CLI built with Typer and Rich for managing daily logs,
generating AI summaries, creating reports, and tracking streaks.

Usage:
    python cli.py new        — Create today's daily log
    python cli.py summary    — Generate AI summary for today's log
    python cli.py weekly     — Generate weekly report
    python cli.py monthly    — Generate monthly report
    python cli.py stats      — Show repository statistics
    python cli.py dashboard  — Regenerate the README dashboard
    python cli.py help       — Show help information
"""

from __future__ import annotations

import logging
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.logging import RichHandler
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from config.settings import get_settings, Settings
from config.constants import DATE_FORMAT

# ── Logging Setup ────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, show_path=False)],
)
logger = logging.getLogger("streak")

# ── CLI App ──────────────────────────────────────────────────
app = typer.Typer(
    name="streak",
    help="🚀 GitHub Streak AI — Maintain meaningful contribution streaks with AI-powered tools.",
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
)
console = Console()


def _get_settings() -> Settings:
    """Load settings with error handling."""
    try:
        return get_settings()
    except Exception as exc:
        console.print(
            Panel(
                f"[red bold]Configuration Error[/]\n\n{exc}\n\n"
                "Run [cyan]cp .env.example .env[/] and set your NVIDIA_API_KEY.",
                title="⚠️ Setup Required",
                border_style="red",
            )
        )
        raise typer.Exit(1)


# ── NEW Command ──────────────────────────────────────────────
@app.command()
def new(
    date_str: Optional[str] = typer.Argument(
        None,
        help="Date for the log (YYYY-MM-DD). Defaults to today.",
    ),
) -> None:
    """📝 Create a new daily log file.

    Creates a structured markdown log at logs/YYYY/MM/YYYY-MM-DD.md
    with sections for goals, tasks, notes, bugs, learnings, and plans.
    """
    settings = _get_settings()
    settings.ensure_directories()

    from scripts.log_manager import LogManager

    manager = LogManager(settings)

    if date_str:
        try:
            target_date = datetime.strptime(date_str, DATE_FORMAT).date()
        except ValueError:
            console.print(f"[red]Invalid date format: {date_str}. Use YYYY-MM-DD.[/]")
            raise typer.Exit(1)
    else:
        target_date = date.today()

    if manager.log_exists(target_date):
        console.print(
            Panel(
                f"Log already exists for [cyan]{target_date}[/].\n"
                f"📂 {manager.get_log_path(target_date)}",
                title="📝 Existing Log",
                border_style="yellow",
            )
        )
        if not typer.confirm("Open/overwrite it?", default=False):
            raise typer.Exit(0)

    log_path = manager.create_daily_log(target_date)

    console.print(
        Panel(
            f"✅ Daily log created for [bold cyan]{target_date.strftime('%B %d, %Y')}[/]\n\n"
            f"📂 [dim]{log_path}[/]\n\n"
            "📝 Open the file and fill in your notes, then run:\n"
            "   [green]python cli.py summary[/] to generate an AI summary.",
            title="🎉 New Log Created",
            border_style="green",
        )
    )


# ── SUMMARY Command ─────────────────────────────────────────
@app.command()
def summary(
    date_str: Optional[str] = typer.Argument(
        None,
        help="Date of the log to summarize (YYYY-MM-DD). Defaults to today.",
    ),
) -> None:
    """🤖 Generate an AI summary for a daily log.

    Reads today's log, sends the raw notes to the NVIDIA NIM API,
    and updates the AI Summary section with professional formatting.
    """
    settings = _get_settings()

    from scripts.ai_client import AIClientError, NvidiaAIClient
    from scripts.log_manager import LogManager, LogNotFoundError

    manager = LogManager(settings)

    if date_str:
        try:
            target_date = datetime.strptime(date_str, DATE_FORMAT).date()
        except ValueError:
            console.print(f"[red]Invalid date format: {date_str}. Use YYYY-MM-DD.[/]")
            raise typer.Exit(1)
    else:
        target_date = date.today()

    # Read the log
    try:
        content = manager.get_log(target_date)
    except LogNotFoundError:
        console.print(
            Panel(
                f"No log found for [cyan]{target_date}[/].\n"
                "Create one first with: [green]python cli.py new[/]",
                title="❌ Log Not Found",
                border_style="red",
            )
        )
        raise typer.Exit(1)

    if not settings.has_api_key:
        console.print(
            Panel(
                "NVIDIA_API_KEY is not set.\n"
                "Set it in your [cyan].env[/] file to enable AI summaries.\n"
                "See [dim].env.example[/] for details.",
                title="⚠️ API Key Missing",
                border_style="yellow",
            )
        )
        raise typer.Exit(1)

    # Generate summary
    with console.status("[bold green]Generating AI summary...", spinner="dots"):
        try:
            client = NvidiaAIClient(settings)
            response = client.generate_summary(content)
        except AIClientError as exc:
            console.print(
                Panel(
                    f"[red]AI generation failed:[/]\n{exc}",
                    title="❌ AI Error",
                    border_style="red",
                )
            )
            raise typer.Exit(1)

    # Update the log
    try:
        manager.update_section(target_date, "AI Summary", response.content)
    except Exception:
        # If section update fails, just show the summary
        logger.warning("Could not auto-update AI Summary section.")

    console.print(
        Panel(
            Markdown(response.content),
            title=f"🤖 AI Summary — {target_date}",
            border_style="cyan",
        )
    )

    if response.usage:
        tokens = response.usage.get("total_tokens", "?")
        console.print(f"[dim]Tokens used: {tokens}[/]")


# ── WEEKLY Command ───────────────────────────────────────────
@app.command()
def weekly(
    week: Optional[int] = typer.Option(
        None, "--week", "-w", help="ISO week number (1-53). Defaults to current week."
    ),
    year: Optional[int] = typer.Option(
        None, "--year", "-y", help="Year. Defaults to current year."
    ),
) -> None:
    """📊 Generate a weekly report.

    Aggregates daily logs for the specified week, calculates statistics,
    and generates an AI-powered analysis.
    """
    settings = _get_settings()
    settings.ensure_directories()

    from scripts.report_generator import ReportGenerator

    with console.status("[bold green]Generating weekly report...", spinner="dots"):
        try:
            generator = ReportGenerator(settings)
            report_path = generator.generate_weekly_report(
                week_number=week, year=year
            )
        except Exception as exc:
            console.print(
                Panel(f"[red]Report generation failed:[/]\n{exc}", title="❌ Error", border_style="red")
            )
            raise typer.Exit(1)

    console.print(
        Panel(
            f"✅ Weekly report generated!\n\n📂 [cyan]{report_path}[/]",
            title="📊 Weekly Report",
            border_style="green",
        )
    )


# ── MONTHLY Command ─────────────────────────────────────────
@app.command()
def monthly(
    month: Optional[int] = typer.Option(
        None, "--month", "-m", help="Month (1-12). Defaults to current month."
    ),
    year: Optional[int] = typer.Option(
        None, "--year", "-y", help="Year. Defaults to current year."
    ),
) -> None:
    """📅 Generate a monthly report.

    Aggregates all daily logs for the month, calculates statistics,
    and generates AI-powered insights and achievements.
    """
    settings = _get_settings()
    settings.ensure_directories()

    from scripts.report_generator import ReportGenerator

    with console.status("[bold green]Generating monthly report...", spinner="dots"):
        try:
            generator = ReportGenerator(settings)
            report_path = generator.generate_monthly_report(year=year, month=month)
        except Exception as exc:
            console.print(
                Panel(f"[red]Report generation failed:[/]\n{exc}", title="❌ Error", border_style="red")
            )
            raise typer.Exit(1)

    console.print(
        Panel(
            f"✅ Monthly report generated!\n\n📂 [cyan]{report_path}[/]",
            title="📅 Monthly Report",
            border_style="green",
        )
    )


# ── STATS Command ────────────────────────────────────────────
@app.command()
def stats() -> None:
    """📈 Show repository and streak statistics.

    Displays commit count, active days, LOC, streak info,
    and recent activity in a beautiful table.
    """
    settings = _get_settings()

    from scripts.streak_tracker import StreakTracker

    tracker = StreakTracker(settings)
    streak_info = tracker.get_streak_info()

    # Streak info table
    table = Table(title="📈 Streak Statistics", border_style="cyan", show_lines=True)
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")

    table.add_row("🔥 Current Streak", f"{streak_info['current_streak']} days")
    table.add_row("🏆 Longest Streak", f"{streak_info['longest_streak']} days")
    table.add_row("🎯 Status", streak_info["status"])
    table.add_row("📝 Total Logged Days", str(streak_info["total_logged_days"]))
    table.add_row("📅 Today Logged", "✅ Yes" if streak_info["today_logged"] else "❌ Not yet")
    if streak_info["first_log"]:
        table.add_row("📅 First Log", streak_info["first_log"])
    if streak_info["last_log"]:
        table.add_row("📅 Last Log", streak_info["last_log"])

    console.print(table)

    # Try git stats
    try:
        from scripts.git_stats import GitStatsCollector

        collector = GitStatsCollector(settings)
        git_data = collector.get_stats_dict()

        git_table = Table(title="📊 Git Statistics", border_style="blue", show_lines=True)
        git_table.add_column("Metric", style="bold")
        git_table.add_column("Value", justify="right")

        git_table.add_row("📊 Total Commits", str(git_data["total_commits"]))
        git_table.add_row("📁 Total Files", str(git_data["total_files"]))
        git_table.add_row("📝 Total LOC", f"{git_data['total_loc']:,}")
        git_table.add_row("📅 Active Days", str(git_data["active_days"]))

        console.print(git_table)

        if git_data["recent_commits"]:
            activity_table = Table(title="🕐 Recent Commits", border_style="green")
            activity_table.add_column("SHA", style="dim")
            activity_table.add_column("Message")
            activity_table.add_column("Date", style="cyan")

            for commit in git_data["recent_commits"][:5]:
                activity_table.add_row(
                    commit["sha"], commit["message"][:60], commit["date"]
                )
            console.print(activity_table)

    except Exception as exc:
        console.print(f"[dim]Git statistics unavailable: {exc}[/]")


# ── DASHBOARD Command ────────────────────────────────────────
@app.command()
def dashboard() -> None:
    """🖥️ Regenerate the README dashboard.

    Updates the README.md with current streak stats, badges,
    progress bars, technologies, and recent activity.
    """
    settings = _get_settings()
    settings.ensure_directories()

    from dashboard.generator import DashboardGenerator

    with console.status("[bold green]Generating dashboard...", spinner="dots"):
        try:
            generator = DashboardGenerator(settings)
            output_path = generator.generate()
        except Exception as exc:
            console.print(
                Panel(f"[red]Dashboard generation failed:[/]\n{exc}", title="❌ Error", border_style="red")
            )
            raise typer.Exit(1)

    console.print(
        Panel(
            f"✅ Dashboard updated!\n\n📂 [cyan]{output_path}[/]",
            title="🖥️ Dashboard",
            border_style="green",
        )
    )


# ── HELP Command ─────────────────────────────────────────────
@app.command(name="help")
def show_help() -> None:
    """❓ Show detailed help and usage examples."""
    help_text = """
# 🚀 GitHub Streak AI — Help

## Commands

| Command | Description |
|---------|-------------|
| `new [DATE]` | Create a daily log (default: today) |
| `summary [DATE]` | Generate AI summary for a log |
| `weekly` | Generate weekly report |
| `monthly` | Generate monthly report |
| `stats` | Show streak & git statistics |
| `dashboard` | Regenerate README dashboard |
| `help` | Show this help message |

## Examples

```bash
# Create today's log
python cli.py new

# Create a log for a specific date
python cli.py new 2024-03-15

# Generate AI summary for today
python cli.py summary

# Generate weekly report for week 12
python cli.py weekly --week 12

# Generate monthly report for March
python cli.py monthly --month 3 --year 2024
```

## Setup

1. Copy `.env.example` to `.env`
2. Set your `NVIDIA_API_KEY`
3. Run `pip install -r requirements.txt`
4. Start with `python cli.py new`

## Workflow

1. Run `python cli.py new` to create today's log
2. Edit the log file with your notes
3. Run `python cli.py summary` to get an AI summary
4. Run `python cli.py dashboard` to update the README
5. Commit and push!
"""
    console.print(Markdown(help_text))


# ── Entry Point ──────────────────────────────────────────────
if __name__ == "__main__":
    app()
