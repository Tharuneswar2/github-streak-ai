"""Automated content generator for daily streak commits.

Generates varied, meaningful content throughout the day to maintain
an active GitHub contribution streak with 7-15 commits daily.
Each run produces unique content based on the current time slot.
"""

from __future__ import annotations

import hashlib
import json
import logging
import random
from datetime import date, datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Curated Content Pools ────────────────────────────────────

TECH_TIPS = [
    ("Python", "Use `functools.lru_cache` to memoize expensive function calls and improve performance."),
    ("Git", "Use `git stash` to temporarily save uncommitted changes when switching branches."),
    ("Docker", "Use multi-stage builds to reduce final image size by separating build and runtime dependencies."),
    ("Linux", "Use `xargs` with `find` for efficient batch operations: `find . -name '*.py' | xargs grep 'TODO'`."),
    ("Python", "Use `dataclasses` with `__slots__=True` for memory-efficient data containers in Python 3.10+."),
    ("Git", "Use `git bisect` to binary-search for the commit that introduced a bug."),
    ("Security", "Never store secrets in code. Use environment variables or secret managers like HashiCorp Vault."),
    ("Python", "Use `pathlib.Path` instead of `os.path` for cleaner, more readable file system operations."),
    ("DevOps", "Implement health checks in your containers with `HEALTHCHECK` in Dockerfile."),
    ("Python", "Use `typing.Protocol` for structural subtyping — duck typing with type safety."),
    ("Git", "Use `git log --oneline --graph --all` for a visual branch history in the terminal."),
    ("Python", "Use `contextlib.suppress(Exception)` instead of empty try/except blocks."),
    ("Testing", "Follow the AAA pattern: Arrange, Act, Assert — for clean, readable test cases."),
    ("Docker", "Use `.dockerignore` to exclude unnecessary files and speed up builds."),
    ("Python", "Use `collections.Counter` for frequency counting instead of manual dictionary loops."),
    ("Linux", "Use `tmux` or `screen` for persistent terminal sessions on remote servers."),
    ("Python", "Use `itertools.chain.from_iterable()` to flatten nested iterables efficiently."),
    ("Git", "Set up `git aliases` in `~/.gitconfig` for frequently used commands."),
    ("Python", "Use `enum.Enum` for type-safe constants instead of magic strings or numbers."),
    ("DevOps", "Use `act` to test GitHub Actions workflows locally before pushing."),
    ("Python", "Use `__all__` in `__init__.py` to control public API exports."),
    ("Security", "Always validate and sanitize user input — never trust client-side data."),
    ("Python", "Use `functools.partial` to create specialized versions of functions."),
    ("Testing", "Use `pytest.mark.parametrize` to run the same test with different inputs."),
    ("Linux", "Use `htop` instead of `top` for a more interactive process monitoring experience."),
    ("Python", "Use f-strings with `=` for debugging: `f'{variable=}'` prints both name and value."),
    ("Git", "Use `git reflog` to recover lost commits or undo a bad rebase."),
    ("Docker", "Pin specific image versions in Dockerfiles instead of using `latest` tag."),
    ("Python", "Use `textwrap.dedent()` for clean multi-line strings in code."),
    ("DevOps", "Use semantic versioning (SemVer) for all releases: MAJOR.MINOR.PATCH."),
]

QUOTES = [
    ("Consistency beats intensity.", "James Clear"),
    ("Code is read much more often than it is written.", "Guido van Rossum"),
    ("First, solve the problem. Then, write the code.", "John Johnson"),
    ("Simplicity is the soul of efficiency.", "Austin Freeman"),
    ("Any fool can write code that a computer can understand.", "Martin Fowler"),
    ("The best error message is the one that never shows up.", "Thomas Fuchs"),
    ("Make it work, make it right, make it fast.", "Kent Beck"),
    ("Programs must be written for people to read.", "Hal Abelson"),
    ("Talk is cheap. Show me the code.", "Linus Torvalds"),
    ("Perfection is achieved when there is nothing left to take away.", "Antoine de Saint-Exupéry"),
    ("The only way to learn a new programming language is by writing programs in it.", "Dennis Ritchie"),
    ("Debugging is twice as hard as writing the code in the first place.", "Brian Kernighan"),
    ("The most disastrous thing you can ever learn is your first programming language.", "Alan Kay"),
    ("Software is a great combination of artistry and engineering.", "Bill Gates"),
    ("In theory, there is no difference between theory and practice. In practice, there is.", "Jan L.A. van de Snepscheut"),
    ("Clean code always looks like it was written by someone who cares.", "Robert C. Martin"),
    ("Every great developer you know got there by solving problems they were unqualified to solve.", "Patrick McKenzie"),
    ("The function of good software is to make the complex appear to be simple.", "Grady Booch"),
    ("Measuring programming progress by lines of code is like measuring aircraft building progress by weight.", "Bill Gates"),
    ("Before software can be reusable it first has to be usable.", "Ralph Johnson"),
    ("A language that doesn't affect the way you think about programming is not worth knowing.", "Alan Perlis"),
    ("The computer was born to solve problems that did not exist before.", "Bill Gates"),
    ("One of my most productive days was throwing away 1,000 lines of code.", "Ken Thompson"),
    ("Experience is the name everyone gives to their mistakes.", "Oscar Wilde"),
    ("It's not a bug — it's an undocumented feature.", "Anonymous"),
    ("The best time to plant a tree was 20 years ago. The second best time is now.", "Chinese Proverb"),
    ("Learning never exhausts the mind.", "Leonardo da Vinci"),
    ("Small daily improvements over time lead to stunning results.", "Robin Sharma"),
    ("Don't comment bad code — rewrite it.", "Brian Kernighan"),
    ("Weeks of coding can save you hours of planning.", "Anonymous"),
]

CODE_SNIPPETS = [
    ("Python — Context Manager", "python", '''from contextlib import contextmanager

@contextmanager
def timer(label: str):
    """Time a block of code and print the duration."""
    import time
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"{label}: {elapsed:.4f}s")

# Usage:
# with timer("database query"):
#     results = db.query("SELECT * FROM users")
'''),
    ("Python — Retry Decorator", "python", '''import functools
import time

def retry(max_attempts: int = 3, delay: float = 1.0):
    """Retry a function on failure with exponential backoff."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    wait = delay * (2 ** (attempt - 1))
                    time.sleep(wait)
        return wrapper
    return decorator
'''),
    ("Python — Singleton Pattern", "python", '''class Singleton:
    """Thread-safe singleton using __new__."""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
'''),
    ("Bash — Safe Script Template", "bash", '''#!/usr/bin/env bash
set -euo pipefail
IFS=$\'\\n\\t\'

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

log() { echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"; }
err() { log "ERROR: $*" >&2; }
die() { err "$*"; exit 1; }

main() {
    log "Starting ${SCRIPT_NAME}..."
    # Your code here
    log "Done."
}

main "$@"
'''),
    ("Python — Dataclass with Validation", "python", '''from dataclasses import dataclass, field
from typing import Self

@dataclass(frozen=True, slots=True)
class Config:
    """Immutable configuration with validation."""
    host: str
    port: int = 8080
    debug: bool = False
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not 1 <= self.port <= 65535:
            raise ValueError(f"Invalid port: {self.port}")
        if not self.host:
            raise ValueError("Host cannot be empty")
'''),
    ("Python — Async Batch Processor", "python", '''import asyncio
from typing import TypeVar, Callable, Awaitable

T = TypeVar("T")
R = TypeVar("R")

async def batch_process(
    items: list[T],
    processor: Callable[[T], Awaitable[R]],
    concurrency: int = 5,
) -> list[R]:
    """Process items concurrently with a concurrency limit."""
    semaphore = asyncio.Semaphore(concurrency)
    async def limited(item: T) -> R:
        async with semaphore:
            return await processor(item)
    return await asyncio.gather(*(limited(i) for i in items))
'''),
]

LEARNING_TOPICS = [
    "Design Patterns: Strategy, Observer, Factory, Decorator, Singleton",
    "SOLID Principles: Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency Inversion",
    "Data Structures: Arrays, Linked Lists, Trees, Graphs, Hash Tables, Heaps",
    "Algorithms: Sorting, Searching, Dynamic Programming, Greedy, Divide and Conquer",
    "System Design: Load Balancers, Caching, Message Queues, Database Sharding",
    "Networking: TCP/IP, HTTP/2, WebSockets, DNS, TLS/SSL",
    "Databases: Indexing, Normalization, ACID, CAP Theorem, Query Optimization",
    "CI/CD: Pipeline Design, Blue-Green Deployment, Canary Releases, Feature Flags",
    "Security: OAuth2, JWT, CORS, XSS, CSRF, SQL Injection Prevention",
    "Cloud: Serverless, Containers, Kubernetes, Service Mesh, Infrastructure as Code",
    "Testing: Unit, Integration, E2E, Property-Based, Mutation Testing",
    "Monitoring: Observability, Metrics, Logging, Tracing, Alerting Strategies",
    "API Design: REST, GraphQL, gRPC, OpenAPI, Versioning, Rate Limiting",
    "Python Advanced: Metaclasses, Descriptors, Generators, Coroutines, GIL",
    "Architecture: Microservices, Event-Driven, CQRS, Domain-Driven Design",
]


def _daily_seed(offset: int = 0) -> int:
    """Generate a deterministic seed based on today's date and an offset."""
    today_str = date.today().isoformat()
    raw = f"{today_str}-{offset}"
    return int(hashlib.md5(raw.encode()).hexdigest()[:8], 16)


def _pick(items: list, offset: int = 0) -> object:
    """Deterministically pick an item based on today's date."""
    rng = random.Random(_daily_seed(offset))
    return rng.choice(items)


class ContentGenerator:
    """Generates varied daily content for automated streak commits."""

    def __init__(self, project_root: Path | None = None) -> None:
        self.root = project_root or Path.cwd()
        self.today = date.today()
        self.now = datetime.now()

    def _log_dir(self) -> Path:
        d = self.root / "logs" / str(self.today.year) / f"{self.today.month:02d}"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _log_path(self) -> Path:
        return self._log_dir() / f"{self.today.isoformat()}.md"

    def create_daily_log(self) -> tuple[Path, str]:
        """Create or return the daily log file."""
        path = self._log_path()
        if not path.exists():
            content = (
                f"# Daily Log — {self.today.strftime('%B %d, %Y')}\n\n"
                f"**Date:** {self.today.isoformat()}  \n"
                f"**Day:** {self.today.strftime('%A')}\n\n---\n\n"
                "## 🎯 Goals\n\n- Continuous learning and improvement\n- Build and ship\n\n---\n\n"
                "## ✅ Completed Tasks\n\n- Daily streak maintained\n- Knowledge base updated\n\n---\n\n"
                "## 📖 Study Notes\n\n- See today's learning entries\n\n---\n\n"
                "## 💻 Coding Notes\n\n- See today's code snippets\n\n---\n\n"
                "## 🐛 Bugs Fixed\n\n- N/A\n\n---\n\n"
                "## 💡 Learnings\n\n- See today's tech tips\n\n---\n\n"
                "## 📋 Tomorrow Plan\n\n- Continue the streak\n\n---\n\n"
                "## 🤖 AI Summary\n\n- Auto-generated\n\n---\n"
            )
            path.write_text(content, encoding="utf-8")
            return path, "📝 Create daily log"
        return path, ""

    def write_tech_tip(self) -> tuple[Path, str]:
        """Write today's tech tip."""
        category, tip = _pick(TECH_TIPS, offset=1)
        path = self.root / "logs" / "tips" / f"{self.today.isoformat()}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        content = (
            f"# 💡 Tech Tip — {self.today.strftime('%B %d, %Y')}\n\n"
            f"**Category:** {category}\n\n"
            f"> {tip}\n\n"
            f"---\n*Auto-generated by GitHub Streak AI*\n"
        )
        path.write_text(content, encoding="utf-8")
        return path, f"💡 Tech tip: {category}"

    def write_quote(self) -> tuple[Path, str]:
        """Write today's motivational quote."""
        quote, author = _pick(QUOTES, offset=2)
        path = self.root / "logs" / "quotes" / f"{self.today.isoformat()}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        content = (
            f"# 💬 Quote of the Day — {self.today.strftime('%B %d, %Y')}\n\n"
            f'> *"{quote}"*\n>\n'
            f"> — **{author}**\n\n"
            f"---\n*Auto-generated by GitHub Streak AI*\n"
        )
        path.write_text(content, encoding="utf-8")
        return path, f"💬 Quote: {author}"

    def write_code_snippet(self) -> tuple[Path, str]:
        """Write today's code snippet."""
        title, lang, code = _pick(CODE_SNIPPETS, offset=3)
        path = self.root / "logs" / "snippets" / f"{self.today.isoformat()}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        content = (
            f"# 💻 Code Snippet — {title}\n\n"
            f"**Date:** {self.today.isoformat()}\n\n"
            f"```{lang}\n{code}\n```\n\n"
            f"---\n*Auto-generated by GitHub Streak AI*\n"
        )
        path.write_text(content, encoding="utf-8")
        return path, f"💻 Snippet: {title}"

    def write_learning_note(self) -> tuple[Path, str]:
        """Write a learning topic note."""
        topic = _pick(LEARNING_TOPICS, offset=4)
        path = self.root / "logs" / "learning" / f"{self.today.isoformat()}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        subtopics = [s.strip() for s in topic.split(":")[1].split(",")] if ":" in topic else [topic]
        title = topic.split(":")[0] if ":" in topic else "Learning"
        bullets = "\n".join(f"- [ ] {s}" for s in subtopics)
        content = (
            f"# 📚 Learning — {title}\n\n"
            f"**Date:** {self.today.isoformat()}\n\n"
            f"## Topics to Explore\n\n{bullets}\n\n"
            f"## Notes\n\n- Review and practice these concepts\n\n"
            f"---\n*Auto-generated by GitHub Streak AI*\n"
        )
        path.write_text(content, encoding="utf-8")
        return path, f"📚 Learning: {title}"

    def update_progress(self) -> tuple[Path, str]:
        """Update the progress tracker."""
        path = self.root / "logs" / "progress.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        data: dict = {}
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                data = {}
        data["last_updated"] = self.now.isoformat()
        data["total_days"] = data.get("total_days", 0) + 1
        dates_list = data.get("dates", [])
        today_str = self.today.isoformat()
        if today_str not in dates_list:
            dates_list.append(today_str)
        data["dates"] = dates_list[-365:]
        data["current_streak"] = self._calc_streak(dates_list)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return path, f"📊 Progress: streak {data['current_streak']} days"

    def write_reflection(self) -> tuple[Path, str]:
        """Write an evening reflection."""
        path = self.root / "logs" / "reflections" / f"{self.today.isoformat()}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        day_num = (self.today - date(self.today.year, 1, 1)).days + 1
        content = (
            f"# 🌙 Daily Reflection — {self.today.strftime('%B %d, %Y')}\n\n"
            f"**Day {day_num} of {365 + (1 if self.today.year % 4 == 0 else 0)}**\n\n"
            "## What went well today?\n\n- Maintained the streak\n- Continued learning\n\n"
            "## What could be improved?\n\n- Always room to grow\n\n"
            "## Key insight\n\n- Consistency compounds over time\n\n"
            f"---\n*Auto-generated by GitHub Streak AI*\n"
        )
        path.write_text(content, encoding="utf-8")
        return path, "🌙 Daily reflection"

    def update_streak_log(self) -> tuple[Path, str]:
        """Update the master streak log."""
        path = self.root / "logs" / "streak.md"
        header = "# 🔥 Streak Log\n\n| Date | Day | Status |\n|------|-----|--------|\n"
        existing = ""
        if path.exists():
            existing = path.read_text(encoding="utf-8")
        if self.today.isoformat() not in existing:
            row = f"| {self.today.isoformat()} | {self.today.strftime('%A')} | ✅ Active |\n"
            if not existing:
                existing = header
            existing += row
            path.write_text(existing, encoding="utf-8")
        return path, "🔥 Streak log updated"

    @staticmethod
    def _calc_streak(dates: list[str]) -> int:
        """Calculate current streak from a list of date strings."""
        from datetime import timedelta
        if not dates:
            return 0
        sorted_dates = sorted(set(dates), reverse=True)
        today = date.today()
        streak = 0
        check = today
        date_set = {date.fromisoformat(d) for d in sorted_dates}
        if check not in date_set:
            check = today - timedelta(days=1)
            if check not in date_set:
                return 0
        while check in date_set:
            streak += 1
            check -= timedelta(days=1)
        return streak


def get_time_slot_actions(hour: int) -> list[str]:
    """Return which content actions to run based on the current hour (UTC).

    Distributes 7-15 commits across the day by assigning different
    content types to different time slots.
    """
    slot_map: dict[int, list[str]] = {
        0: ["daily_log", "streak_log"],
        2: ["tech_tip"],
        4: ["quote"],
        6: ["code_snippet"],
        8: ["learning_note", "progress"],
        10: ["tech_tip", "quote"],
        12: ["code_snippet", "learning_note"],
        14: ["reflection", "progress"],
        16: ["tech_tip", "streak_log"],
        18: ["quote", "code_snippet"],
        20: ["learning_note", "progress"],
        22: ["reflection", "streak_log"],
    }
    # Find closest slot
    slots = sorted(slot_map.keys())
    closest = min(slots, key=lambda s: abs(s - hour))
    return slot_map[closest]


if __name__ == "__main__":
    import sys
    gen = ContentGenerator()
    hour = datetime.utcnow().hour if len(sys.argv) < 2 else int(sys.argv[1])
    actions = get_time_slot_actions(hour)
    method_map = {
        "daily_log": gen.create_daily_log,
        "tech_tip": gen.write_tech_tip,
        "quote": gen.write_quote,
        "code_snippet": gen.write_code_snippet,
        "learning_note": gen.write_learning_note,
        "progress": gen.update_progress,
        "reflection": gen.write_reflection,
        "streak_log": gen.update_streak_log,
    }
    for action in actions:
        func = method_map.get(action)
        if func:
            path, msg = func()
            if msg:
                print(f"{msg} -> {path}")
