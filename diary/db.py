import sqlite3
from functools import wraps

from .core import Diary, Entry

DB_ADDRESS = "tmp/main.db"


def drop_db(adress: str):
    with sqlite3.connect(adress) as con:
        cur = con.cursor()
        cur.execute("DELETE FROM diary")
        cur.execute("DELETE FROM entry")
        cur.execute("DELETE FROM metric")


def with_db(func):
    """Convenience wrapper for DB functions.
    If the DB doesn't exist initialise it."""

    @wraps(func)
    def wrapped_func(*args, **kwargs):
        try:
            con = sqlite3.connect(f"file:{DB_ADDRESS}?mode=rw", uri=True)
        except sqlite3.OperationalError:
            with sqlite3.connect(DB_ADDRESS) as con:
                cur = con.cursor()
                cur.execute(
                    """CREATE TABLE diary
                        (uuid TEXT PRIMARY KEY, username TEXT UNIQUE, name TEXT)"""
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
def create_diary(cur, diary: Diary, username: str) -> None:
    """Save a diary to the database"""
    cur.execute("INSERT INTO diary VALUES (?,?,?)", (diary.uuid, username, diary.name))
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
def load_diary(cur, username: str) -> Diary:
    """Load a Diary from the database given a username"""
    cur.execute("SELECT * FROM diary WHERE username=:username", {"username": username})
    rows = cur.fetchall()
    if len(rows) == 0:
        raise LookupError
    elif len(rows) > 1:
        sqlite3.IntegrityError

    uuid, _, name = rows[0]
    entries: dict[str, Entry] = {}
    for row in cur.execute(
        "SELECT * FROM entry LEFT JOIN metric ON entry.uuid=metric.entry WHERE diary=? ORDER BY timestamp",
        (uuid,),
    ):
        entry_uuid, _, timestamp, text, _, key, value = row
        try:
            entry = entries[entry_uuid]
        except KeyError:
            entry = Entry(timestamp=timestamp, text=text, uuid=entry_uuid, metrics={})
            entries[entry_uuid] = entry
        if key:
            entry.metrics[key] = value
    return Diary(name, list(entries.values()), uuid)
