<div align="center">

# 🚀 GitHub Streak AI

### *AI-Powered Daily Logging & Streak Management for Meaningful GitHub Contributions*

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![NVIDIA NIM](https://img.shields.io/badge/NVIDIA-NIM_API-76B900?style=for-the-badge&logo=nvidia&logoColor=white)](https://build.nvidia.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](tests/)
[![Code Style](https://img.shields.io/badge/Code_Style-Ruff-D7FF64?style=for-the-badge)](https://github.com/astral-sh/ruff)

---

*Stop making fake commits. Start building real streaks through genuine daily work.*

**GitHub Streak AI** helps you maintain meaningful contribution streaks by organizing your daily coding, learning, and documentation into a professional GitHub repository — powered by NVIDIA's AI.

[📖 Documentation](docs/) · [🐛 Report Bug](https://github.com/yourusername/github-streak-ai/issues) · [💡 Request Feature](https://github.com/yourusername/github-streak-ai/issues)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📝 **Daily Logs** | Structured markdown logs at `logs/YYYY/MM/YYYY-MM-DD.md` |
| 🤖 **AI Summaries** | NVIDIA NIM converts raw notes into professional documentation |
| 📊 **Weekly Reports** | Auto-generated `reports/week-XX.md` with stats and AI analysis |
| 📅 **Monthly Reports** | Comprehensive `reports/month-YYYY-MM.md` with achievements |
| 🔥 **Streak Tracking** | Current streak, longest streak, status indicators |
| 🖥️ **README Dashboard** | Auto-updated with badges, progress bars, and activity |
| ⚡ **GitHub Actions** | Automated validation, reports, and streak reminders |
| 💻 **Beautiful CLI** | Rich-powered terminal interface with panels and tables |

---

## 🚀 Quick Start

### 1. Install

```bash
git clone https://github.com/yourusername/github-streak-ai.git
cd github-streak-ai
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env and add your NVIDIA_API_KEY
```

### 3. Start Logging

```bash
python cli.py new          # Create today's log
# ... edit the log file with your notes ...
python cli.py summary      # Generate AI summary
python cli.py dashboard    # Update README dashboard
```

---

## 💻 CLI Commands

```
Usage: python cli.py [COMMAND]

Commands:
  new [DATE]       📝  Create a new daily log
  summary [DATE]   🤖  Generate AI summary for a log
  weekly           📊  Generate weekly report
  monthly          📅  Generate monthly report
  stats            📈  Show streak & repository statistics
  dashboard        🖥️   Regenerate the README dashboard
  help             ❓  Show detailed help
```

### Examples

```bash
# Create a log for a specific date
python cli.py new 2024-03-15

# Generate summary for a past log
python cli.py summary 2024-03-15

# Generate weekly report for week 12
python cli.py weekly --week 12 --year 2024

# Generate March 2024 monthly report
python cli.py monthly --month 3 --year 2024

# View all statistics
python cli.py stats
```

---

## 📁 Project Structure

```
github-streak-ai/
├── cli.py                    # 💻 CLI entry point (Typer + Rich)
├── config/
│   ├── settings.py           # ⚙️ Pydantic settings (env loading)
│   └── constants.py          # 📋 Project-wide constants
├── scripts/
│   ├── ai_client.py          # 🤖 NVIDIA NIM API client
│   ├── log_manager.py        # 📝 Daily log operations
│   ├── report_generator.py   # 📊 Report generation
│   ├── git_stats.py          # 📈 Git repository statistics
│   └── streak_tracker.py     # 🔥 Streak tracking
├── dashboard/
│   ├── generator.py          # 🖥️ README dashboard generator
│   └── badges.py             # 🏷️ Shields.io badges
├── templates/                # 📄 Jinja2 templates
├── logs/                     # 📝 Daily logs (YYYY/MM/YYYY-MM-DD.md)
├── reports/                  # 📊 Generated reports
├── tests/                    # ✅ Pytest test suite
├── docs/                     # 📖 Documentation
└── .github/workflows/        # ⚡ GitHub Actions
```

---

## ⚡ GitHub Actions

### Daily Check (`daily_check.yml`)
- ⏰ Runs daily at 22:00 UTC
- ✅ Validates markdown files
- 📝 Opens reminder issue if today's log is missing
- 🧪 Runs test suite

### Report Generation (`generate_reports.yml`)
- 🔄 Triggers when logs are pushed to `main`
- 📊 Generates weekly and monthly reports
- 🖥️ Updates the README dashboard
- ✅ Commits only if content changed (no empty commits)

### Setup

Add your API key to GitHub Secrets:
```
Settings → Secrets and variables → Actions → New repository secret
Name: NVIDIA_API_KEY
Value: your-api-key
```

---

## 🔧 Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `NVIDIA_API_KEY` | *(required)* | NVIDIA NIM API key |
| `MODEL` | `nvidia/nemotron-3-ultra-550b-a55b` | AI model |
| `MAX_TOKENS` | `2048` | Max response tokens |
| `AI_TEMPERATURE` | `0.7` | AI creativity level |

See [Configuration Guide](docs/Configuration.md) for full details.

---

## 🧪 Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=scripts --cov=dashboard --cov=config
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/Architecture.md) | System design and data flow |
| [Installation](docs/Installation.md) | Setup instructions |
| [Configuration](docs/Configuration.md) | Environment variables and options |
| [Usage](docs/Usage.md) | Detailed usage guide |
| [API Reference](docs/API.md) | Module and class documentation |
| [FAQ](docs/FAQ.md) | Frequently asked questions |
| [Troubleshooting](docs/Troubleshooting.md) | Common issues and solutions |
| [Roadmap](docs/Roadmap.md) | Future plans and features |

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

Please ensure:
- All tests pass (`pytest tests/ -v`)
- Code follows the existing style
- New features include tests
- Documentation is updated

---

## 🗺️ Roadmap

- ✅ **v1.0** — Core features (logging, AI summaries, reports, dashboard, CLI)
- 🔜 **v1.1** — Enhanced analytics and productivity scoring
- 🔮 **v1.2** — Advanced AI features and learning recommendations
- 🚀 **v2.0** — Web dashboard and GitHub App integration

See [full roadmap](docs/Roadmap.md).

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ for developers who believe in real work, real growth, and real streaks.**

*Powered by [NVIDIA NIM](https://build.nvidia.com/) · Built with [Typer](https://typer.tiangolo.com/) & [Rich](https://rich.readthedocs.io/)*

</div>
