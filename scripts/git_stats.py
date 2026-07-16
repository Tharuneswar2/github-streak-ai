"""Git repository statistics collector.

Uses GitPython to extract commit history, file changes, LOC metrics,
and activity patterns from the local repository.
"""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from config.settings import Settings, get_settings

logger = logging.getLogger(__name__)


class GitStatsError(Exception):
    """Base exception for git statistics errors."""


class RepositoryNotFoundError(GitStatsError):
    """Raised when no git repository is found at the specified path."""


@dataclass
class CommitInfo:
    """Summary of a single git commit."""

    sha: str
    message: str
    author: str
    date: datetime
    files_changed: int = 0


@dataclass
class RepoStatistics:
    """Aggregate repository statistics."""

    total_commits: int = 0
    total_files: int = 0
    total_loc: int = 0
    active_days: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    top_authors: list[tuple[str, int]] = field(default_factory=list)
    recent_commits: list[CommitInfo] = field(default_factory=list)
    files_by_type: dict[str, int] = field(default_factory=dict)


class GitStatsCollector:
    """Collects statistics from the local Git repository using GitPython."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._repo_path = self._settings.project_root
        self._repo = self._initialize_repo()

    def _initialize_repo(self) -> Any:
        try:
            import git
            repo = git.Repo(str(self._repo_path), search_parent_directories=True)
            return repo
        except ImportError:
            raise GitStatsError("GitPython is required. Install: pip install gitpython")
        except Exception as exc:
            raise RepositoryNotFoundError(
                f"No git repository found at {self._repo_path}. Run: git init"
            ) from exc

    def get_commit_count(self) -> int:
        try:
            return int(self._repo.git.rev_list("--count", "HEAD"))
        except Exception:
            return 0

    def get_files_changed(self, commit_count: int = 1) -> int:
        try:
            output = self._repo.git.diff("--name-only", f"HEAD~{commit_count}", "HEAD")
            return len(output.strip().splitlines()) if output.strip() else 0
        except Exception:
            return 0

    def get_loc_stats(self) -> int:
        total_loc = 0
        try:
            tracked_files = self._repo.git.ls_files().splitlines()
            text_ext = {
                ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".md",
                ".yml", ".yaml", ".json", ".toml", ".sh", ".rs", ".go", ".java",
            }
            for fp in tracked_files:
                full = Path(self._repo.working_dir) / fp
                if full.suffix.lower() in text_ext and full.exists():
                    try:
                        total_loc += len(full.read_text(encoding="utf-8", errors="ignore").splitlines())
                    except OSError:
                        continue
        except Exception as exc:
            logger.warning("Error counting LOC: %s", exc)
        return total_loc

    def get_active_days(self) -> list[date]:
        try:
            output = self._repo.git.log("--format=%ai", "--all")
            if not output.strip():
                return []
            dates: set[date] = set()
            for line in output.strip().splitlines():
                try:
                    dates.add(datetime.fromisoformat(line.strip()).date())
                except ValueError:
                    continue
            return sorted(dates)
        except Exception:
            return []

    def get_streak_count(self) -> int:
        active_days = self.get_active_days()
        if not active_days:
            return 0
        today = date.today()
        check_date = today
        if today not in active_days:
            yesterday = today - timedelta(days=1)
            if yesterday not in active_days:
                return 0
            check_date = yesterday
        active_set = set(active_days)
        streak = 0
        while check_date in active_set:
            streak += 1
            check_date -= timedelta(days=1)
        return streak

    def get_longest_streak(self) -> int:
        active_days = self.get_active_days()
        if not active_days:
            return 0
        longest = current = 1
        for i in range(1, len(active_days)):
            if active_days[i] - active_days[i - 1] == timedelta(days=1):
                current += 1
                longest = max(longest, current)
            else:
                current = 1
        return longest

    def get_recent_activity(self, count: int = 10) -> list[CommitInfo]:
        commits: list[CommitInfo] = []
        try:
            for commit in list(self._repo.iter_commits("HEAD", max_count=count)):
                commits.append(CommitInfo(
                    sha=commit.hexsha[:8],
                    message=commit.message.strip().splitlines()[0],
                    author=str(commit.author),
                    date=commit.committed_datetime,
                    files_changed=len(commit.stats.files),
                ))
        except Exception as exc:
            logger.warning("Error reading recent commits: %s", exc)
        return commits

    def get_top_authors(self, limit: int = 5) -> list[tuple[str, int]]:
        try:
            output = self._repo.git.shortlog("-sn", "--all")
            authors: list[tuple[str, int]] = []
            for line in output.strip().splitlines()[:limit]:
                parts = line.strip().split("\t", 1)
                if len(parts) == 2:
                    authors.append((parts[1].strip(), int(parts[0].strip())))
            return authors
        except Exception:
            return []

    def get_files_by_type(self) -> dict[str, int]:
        try:
            tracked = self._repo.git.ls_files().splitlines()
            counter: Counter[str] = Counter()
            for fp in tracked:
                counter[Path(fp).suffix.lower() or "(none)"] += 1
            return dict(counter.most_common(20))
        except Exception:
            return {}

    def get_full_stats(self) -> RepoStatistics:
        active_days = self.get_active_days()
        try:
            total_files = len(self._repo.git.ls_files().splitlines())
        except Exception:
            total_files = 0
        return RepoStatistics(
            total_commits=self.get_commit_count(),
            total_files=total_files,
            total_loc=self.get_loc_stats(),
            active_days=len(active_days),
            current_streak=self.get_streak_count(),
            longest_streak=self.get_longest_streak(),
            top_authors=self.get_top_authors(),
            recent_commits=self.get_recent_activity(),
            files_by_type=self.get_files_by_type(),
        )

    def get_stats_dict(self) -> dict[str, Any]:
        stats = self.get_full_stats()
        return {
            "total_commits": stats.total_commits,
            "total_files": stats.total_files,
            "total_loc": stats.total_loc,
            "active_days": stats.active_days,
            "current_streak": stats.current_streak,
            "longest_streak": stats.longest_streak,
            "top_authors": stats.top_authors,
            "files_by_type": stats.files_by_type,
            "recent_commits": [
                {"sha": c.sha, "message": c.message, "author": c.author,
                 "date": c.date.strftime("%Y-%m-%d %H:%M"), "files_changed": c.files_changed}
                for c in stats.recent_commits
            ],
        }
