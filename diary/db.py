import sqlite3
from functools import wraps

from .core import Diary, Entry


def with_db(func):
    """Convenience wrapper for DB functions.
    If the DB doesn't exist initialise it."""

    @wraps(func)
    def wrapped_func(*args, **kwargs):
        try:
            con = sqlite3.connect("file:tmp/main.db?mode=rw", uri=True)
        except sqlite3.OperationalError:
            with sqlite3.connect("tmp/main.db") as con:
                cur = con.cursor()
                cur.execute(
                    """CREATE TABLE diary
                        (uuid TEXT PRIMARY KEY, name TEXT)"""
                )
                cur.execute(
                    """CREATE TABLE entry
                        (uuid TEXT PRIMARY KEY, diary TEXT, timestamp TEXT, text TEXT)"""
                )
                cur.execute(
                    """CREATE TABLE metric
                        (entry TEXT, metric TEXT, value REAL)"""
                )
        try:
            with con:
                result = func(con.cursor(), *args, **kwargs)
        finally:
            con.close()
        return result

    return wrapped_func


@with_db
def create_diary(cur, diary: Diary) -> None:
    """Save a diary to the database"""
    cur.execute("INSERT INTO diary VALUES (?,?)", (diary.uuid, diary.name))
    cur.executemany(
        "INSERT INTO entry VALUES (?, ?, ?, ?)",
        [
            (entry.uuid, diary.uuid, entry.timestamp, entry.text)
            for entry in diary.entries
        ],
    )
    cur.executemany(
        "INSERT INTO metric VALUES (?, ?, ?)",
        [
            (entry.uuid, metric, value)
            for entry in diary.entries
            for metric, value in entry.metrics.items()
        ],
    )


@with_db
def create_entry(cur, diary_uuid: str, entry: Entry) -> None:
    """Create a new Entry record in the database"""
    cur.execute(
        "INSERT INTO entry VALUES (?, ?, ?, ?)",
        (entry.uuid, diary_uuid, entry.timestamp, entry.text),
    )
    cur.executemany(
        "INSERT INTO metric VALUES (?, ?, ?)",
        [(entry.uuid, metric, value) for metric, value in entry.metrics.items()],
    )


def update_diary(diary: Diary) -> None:
    """Update the DB to reflect the latest Entry"""
    create_entry(diary.uuid, diary.entries[-1])


@with_db
def load_diary(cur, uuid: str) -> Diary:
    """Load a Diary from the database given a uuid"""
    cur.execute("SELECT * FROM diary WHERE uuid=:uuid", {"uuid": uuid})
    _, name = cur.fetchone()

    entries: dict[str, Entry] = {}
    for row in cur.execute(
        "SELECT * FROM entry LEFT JOIN metric ON entry.uuid=metric.entry WHERE diary=? ORDER BY timestamp",
        (uuid,),
    ):
        print(row)
        entry_uuid, _, timestamp, text, _, key, value = row
        try:
            entry = entries[entry_uuid]
        except:
            entry = Entry(timestamp=timestamp, text=text, uuid=entry_uuid, metrics={})
            entries[entry_uuid] = entry
        if key:
            entry.metrics[key] = value
    return Diary(name, list(entries.values()), uuid)
