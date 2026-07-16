# Architecture

## Overview

GitHub Streak AI follows a **layered modular architecture** designed for maintainability, testability, and extensibility.

```
┌──────────────────────────────────────────────────┐
│                   CLI Layer                       │
│              cli.py (Typer + Rich)                │
├──────────────────────────────────────────────────┤
│                Service Layer                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │   Log    │ │  Report  │ │    Dashboard     │  │
│  │ Manager  │ │Generator │ │    Generator     │  │
│  └──────────┘ └──────────┘ └──────────────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │  Streak  │ │   Git    │ │     Badge        │  │
│  │ Tracker  │ │  Stats   │ │    Generator     │  │
│  └──────────┘ └──────────┘ └──────────────────┘  │
├──────────────────────────────────────────────────┤
│              Integration Layer                    │
│  ┌──────────────┐  ┌─────────────────────────┐   │
│  │  NVIDIA NIM  │  │     GitPython           │   │
│  │   AI Client  │  │   (Repo Access)         │   │
│  └──────────────┘  └─────────────────────────┘   │
├──────────────────────────────────────────────────┤
│              Configuration Layer                  │
│  ┌──────────────┐  ┌─────────────────────────┐   │
│  │   Pydantic   │  │     Constants           │   │
│  │   Settings   │  │   (Centralized)         │   │
│  └──────────────┘  └─────────────────────────┘   │
├──────────────────────────────────────────────────┤
│              Infrastructure Layer                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │  Jinja2  │ │ File I/O │ │  GitHub Actions  │  │
│  │Templates │ │ (pathlib)│ │   (Workflows)    │  │
│  └──────────┘ └──────────┘ └──────────────────┘  │
└──────────────────────────────────────────────────┘
```

## Directory Structure

```
github-streak-ai/
├── cli.py                    # Entry point — Typer CLI application
├── config/
│   ├── __init__.py           # Package exports
│   ├── settings.py           # Pydantic settings (env loading)
│   └── constants.py          # Project-wide constants
├── scripts/
│   ├── __init__.py           # Package exports
│   ├── ai_client.py          # NVIDIA NIM API client
│   ├── log_manager.py        # Daily log CRUD operations
│   ├── report_generator.py   # Weekly/monthly report generation
│   ├── git_stats.py          # Git repository statistics
│   └── streak_tracker.py     # Contribution streak tracking
├── dashboard/
│   ├── __init__.py           # Package exports
│   ├── generator.py          # README dashboard generator
│   └── badges.py             # Shields.io badge generation
├── templates/
│   ├── daily_log.md.j2       # Daily log template
│   ├── weekly_report.md.j2   # Weekly report template
│   ├── monthly_report.md.j2  # Monthly report template
│   └── dashboard.md.j2       # README dashboard template
├── logs/                     # Generated daily logs (YYYY/MM/YYYY-MM-DD.md)
├── reports/                  # Generated reports
├── tests/                    # Pytest test suite
├── docs/                     # Documentation
└── .github/workflows/        # CI/CD automation
```

## Design Principles

### SOLID Principles

- **Single Responsibility**: Each module handles one concern (logging, reporting, AI, etc.)
- **Open/Closed**: Templates and configuration allow extension without modification
- **Liskov Substitution**: Settings can be injected as mock/test variants
- **Interface Segregation**: Small, focused public APIs per module
- **Dependency Inversion**: Services accept Settings via constructor injection

### Key Decisions

1. **Pydantic Settings**: Type-safe configuration with `.env` file support and validation
2. **Jinja2 Templates**: Separates content structure from logic; templates are customizable
3. **Constructor Injection**: All services accept optional dependencies for testability
4. **GitPython**: Read-only repository access; never modifies the git state
5. **Shields.io Badges**: Dynamic badges without any server infrastructure

## Data Flow

```
User writes raw notes
        │
        ▼
   cli.py new → LogManager.create_daily_log()
        │           │
        │           ▼
        │    logs/YYYY/MM/YYYY-MM-DD.md
        │
        ▼
   cli.py summary → NvidiaAIClient.generate_summary()
        │                    │
        │                    ▼
        │            NVIDIA NIM API
        │                    │
        │                    ▼
        │          LogManager.update_section("AI Summary", ...)
        │
        ▼
   cli.py weekly → ReportGenerator.generate_weekly_report()
        │                    │
        │           ┌───────┴───────┐
        │           ▼               ▼
        │    LogManager       NvidiaAIClient
        │    (aggregate)      (AI analysis)
        │           │               │
        │           └───────┬───────┘
        │                   ▼
        │          reports/week-XX.md
        │
        ▼
   cli.py dashboard → DashboardGenerator.generate()
                             │
                    ┌────────┼────────┐
                    ▼        ▼        ▼
              StreakTracker  LogManager  BadgeGenerator
                    │        │        │
                    └────────┼────────┘
                             ▼
                         README.md
```
