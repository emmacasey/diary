import sqlite3

from .core import Diary, Entry


def with_db(func):
    def wrapped_func(*args, **kwargs):
        try:
            con = sqlite3.connect("file:tmp/main.db?mode=rw", uri=True)
        except sqlite3.OperationalError:
            with sqlite3.connect("tmp/main.db") as con:
                cur = con.cursor()
                cur.execute(
                    """CREATE TABLE diary
                        (uuid text, name text)"""
                )
                cur.execute(
                    """CREATE TABLE entry
                        (uuid text, diary text, timestamp text, text text)"""
                )
                cur.execute(
                    """CREATE TABLE metric
                        (entry text, metric text, value real)"""
                )
        with con:
            result = func(con.cursor(), *args, **kwargs)
        con.close()
        return result

    return wrapped_func


@with_db
def create_diary(cur, diary: Diary) -> None:
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
    cur.execute(
        "INSERT INTO entry VALUES (?, ?, ?, ?)",
        (entry.uuid, diary_uuid, entry.timestamp, entry.text),
    )
    cur.executemany(
        "INSERT INTO metric VALUES (?, ?, ?)",
        [(entry.uuid, metric, value) for metric, value in entry.metrics.items()],
    )


@with_db
def load_diary(cur, uuid: str) -> Diary:
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
