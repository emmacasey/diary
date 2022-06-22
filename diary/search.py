from typing import Optional

from .core import Diary, Entry


def strict_search(diary: Diary, search_term: str) -> list[Entry]:
    """For a given diary return a list of entries where the search term is a substring
    of the entry's text."""
    return [entry for entry in diary.entries if search_term in entry.text]


def date_filter(
    entries: list[Entry], *, before: Optional[str] = None, after: Optional[str] = None
) -> list[Entry]:
    """Filter a list of entries to only those before and after given timestamps,
    both terms are optional, and both should be iso strings."""
    return [
        entry
        for entry in entries
        if (not before or entry.timestamp < before)
        and (not after or entry.timestamp > after)
    ]


def metric_filter(
    entries: list[Entry],
    metric: str,
    *,
    gt: Optional[float] = None,
    lt: Optional[float] = None,
    eq: Optional[float] = None,
) -> list[Entry]:
    """Filter a list of entries to only those with a given metric, and of those
    only those greater than, less than, and equal to the given (optional) values."""
    return [
        entry
        for entry in entries
        if metric in entry.metrics
        and (lt is None or entry.metrics[metric] < lt)
        and (gt is None or entry.metrics[metric] > gt)
        and (eq is None or entry.metrics[metric] == eq)
    ]
