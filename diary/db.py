from contextlib import contextmanager
import sqlite3

from .core import Diary, Entry


@contextmanager
def db_cursor(address: str):
    """Convenience wrapper for DB functions.
    If the DB doesn't exist initialise it."""
    try:
        con = sqlite3.connect(f"file:{address}?mode=rw", uri=True)
    except sqlite3.OperationalError:
        with sqlite3.connect(address) as con:
            con.execute(
                """CREATE TABLE diary
                        (uuid TEXT PRIMARY KEY, username TEXT UNIQUE, name TEXT)"""
            )
            con.execute(
                """CREATE TABLE entry
                        (uuid TEXT PRIMARY KEY, diary TEXT, timestamp TEXT, text TEXT)"""
            )
            con.execute(
                """CREATE TABLE metric
                        (entry TEXT, metric TEXT, value REAL)"""
            )
    try:
        with con:
            yield con.cursor()
    finally:
        con.close()


def drop_db(adress: str):
    with db_cursor(adress) as cur:
        cur.execute("DELETE FROM diary")
        cur.execute("DELETE FROM entry")
        cur.execute("DELETE FROM metric")


def create_diary(address: str, diary: Diary, username: str) -> None:
    """Save a diary to the database"""
    with db_cursor(address) as cur:
        cur.execute(
            "INSERT INTO diary VALUES (?,?,?)", (diary.uuid, username, diary.name)
        )
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


def create_entry(address: str, diary_uuid: str, entry: Entry) -> None:
    """Create a new Entry record in the database"""
    with db_cursor(address) as cur:
        cur.execute(
            "INSERT INTO entry VALUES (?, ?, ?, ?)",
            (entry.uuid, diary_uuid, entry.timestamp, entry.text),
        )
        cur.executemany(
            "INSERT INTO metric VALUES (?, ?, ?)",
            [(entry.uuid, metric, value) for metric, value in entry.metrics.items()],
        )


def update_diary(address: str, diary: Diary) -> None:
    """Update the DB to reflect the latest Entry"""
    create_entry(address, diary.uuid, diary.entries[-1])


def load_diary(address: str, username: str) -> Diary:
    """Load a Diary from the database given a username"""
    with db_cursor(address) as cur:
        cur.execute(
            "SELECT * FROM diary WHERE username=:username", {"username": username}
        )
        rows = cur.fetchall()
        if len(rows) == 0:
            raise LookupError(f"{username} not found in db {address}")
        elif len(rows) > 1:
            sqlite3.IntegrityError(
                f"{username} found {len(rows)} times in db {address}"
            )

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
                entry = Entry(
                    timestamp=timestamp, text=text, uuid=entry_uuid, metrics={}
                )
                entries[entry_uuid] = entry
            if key:
                entry.metrics[key] = value
    return Diary(name, list(entries.values()), uuid)
