"""Shared race-result persistence interface.

This module defines the canonical race-result persistence contract used by
both database backends in the Momentum codebase.
"""

from abc import ABC, abstractmethod
from typing import Optional, Sequence

from database.models import RaceResult


class RaceResultPersistence(ABC):
    """Canonical persistence contract for race result batches."""

    @abstractmethod
    def save_race_results(self, race_result_batch: Sequence[RaceResult]) -> None:
        """Persist a batch of race results in one operation."""

    def save_race_result(self, result: RaceResult) -> Optional[int]:
        """Compatibility wrapper that delegates to the canonical batch API."""
        self.save_race_results([result])
        return getattr(result, "id", None)

    def create_race_result(self, result: RaceResult) -> Optional[int]:
        """Compatibility wrapper preserved for legacy callers."""
        return self.save_race_result(result)
