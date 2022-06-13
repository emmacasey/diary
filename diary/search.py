from typing import Optional

from .core import Diary, Record


def strict_search(diary: Diary, search_term: str) -> list[Record]:
    """For a given diary return a list of records where the search term is a substring
    of the record's text."""
    return [record for record in diary.records if search_term in record.text]


def date_filter(
    records: list[Record], *, before: Optional[str] = None, after: Optional[str] = None
) -> list[Record]:
    """Filter a list of records to only those before and after given timestamps,
    both terms are optional, and both should be iso strings."""
    return [
        record
        for record in records
        if (before is None or record.timestamp < before)
        and (after is None or record.timestamp > after)
    ]


def metric_filter(
    records: list[Record],
    metric: str,
    *,
    gt: Optional[float] = None,
    lt: Optional[float] = None,
    eq: Optional[float] = None,
) -> list[Record]:
    """ "Filter a list of records to only those with a given metric, and of those
    only those greater than, less than, and equal to the given (optional) values."""
    return [
        record
        for record in records
        if metric in record.metrics
        and (lt is None or record.metrics[metric] < lt)
        and (gt is None or record.metrics[metric] > gt)
        and (eq is None or record.metrics[metric] == eq)
    ]
