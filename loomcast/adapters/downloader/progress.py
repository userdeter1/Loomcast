from __future__ import annotations

from types import TracebackType
from typing import Any

from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TaskID,
    TextColumn,
    TransferSpeedColumn,
)
from typing_extensions import Self


class ProgressReporter:
    """Base callback object for model download progress tracking."""

    def on_progress(
        self, status: str, completed: int | None = None, total: int | None = None
    ) -> None:
        """Receive a progress update callback.

        Args:
            status: Status description text (e.g. 'downloading sha256:...', 'verifying').
            completed: Total bytes completed so far, if available.
            total: Total expected bytes, if available.
        """

    def create_sub_reporter(self, prefix: str) -> ProgressReporter:
        """Create a child progress reporter for concurrent task isolation."""
        return self


class NullProgressReporter(ProgressReporter):
    """Silent progress reporter that ignores all progress events."""

    def on_progress(
        self, status: str, completed: int | None = None, total: int | None = None
    ) -> None:
        pass


class SubProgressReporter(ProgressReporter):
    """Child progress reporter bound to a dedicated task in a parent RichProgressReporter."""

    def __init__(self, parent: RichProgressReporter, prefix: str):
        self.parent = parent
        self.prefix = prefix
        self._task_id: TaskID | None = None

    def on_progress(
        self, status: str, completed: int | None = None, total: int | None = None
    ) -> None:
        self.parent.start()
        desc = f"[{self.prefix}] {status}" if self.prefix else status
        if self._task_id is None:
            self._task_id = self.parent._progress.add_task(
                description=desc,
                total=total,
                completed=completed or 0,
            )
        else:
            kwargs: dict[str, Any] = {"description": desc}
            if total is not None:
                kwargs["total"] = total
            if completed is not None:
                kwargs["completed"] = completed
            self.parent._progress.update(self._task_id, **kwargs)


class RichProgressReporter(ProgressReporter):
    """Terminal visual progress reporter powered by rich.progress."""

    def __init__(self, console: Console | None = None):
        self.console = console
        self._progress: Progress | None = None
        self._task_id: TaskID | None = None

    def start(self) -> None:
        """Start the Rich Progress display if not already running."""
        if self._progress is None:
            self._progress = Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                DownloadColumn(),
                TransferSpeedColumn(),
                console=self.console,
            )
            self._progress.start()

    def stop(self) -> None:
        """Stop and clean up the Rich Progress display."""
        if self._progress is not None:
            self._progress.stop()
            self._progress = None
            self._task_id = None

    def create_sub_reporter(self, prefix: str) -> ProgressReporter:
        """Create a child progress reporter dedicated to a specific task prefix."""
        return SubProgressReporter(self, prefix=prefix)

    def __enter__(self) -> Self:
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.stop()

    def on_progress(
        self, status: str, completed: int | None = None, total: int | None = None
    ) -> None:
        """Update progress bar display with status and byte metrics."""
        if self._progress is None:
            self.start()

        if self._task_id is None:
            self._task_id = self._progress.add_task(
                description=status,
                total=total,
                completed=completed or 0,
            )
        else:
            kwargs: dict[str, Any] = {"description": status}
            if total is not None:
                kwargs["total"] = total
            if completed is not None:
                kwargs["completed"] = completed
            self._progress.update(self._task_id, **kwargs)
