from dataclasses import dataclass, asdict
from datetime import datetime
from typing import TextIO
import json
import re


@dataclass
class Entry:
    """Individual diary entry.
    To instantiate pass the text to .create(), this will auto-populate the current date
    and will detect metrics written in the form `#keyword 10.0`.
    Timestamp is a string in iso format to allow stringwise comparison.
    """

    timestamp: str
    text: str
    metrics: dict[str, float]

    @classmethod
    def create(cls, text: str) -> "Entry":
        metrics = {
            metric: float(value)
            for metric, value in re.findall(r"#(\w+) (\d+\.?\d*)", text)
        }
        return cls(datetime.now().isoformat(), text, metrics)

    def __str__(self) -> str:
        return f"{self.timestamp} - {self.text}"

    @property
    def time(self) -> datetime:
        return datetime.fromisoformat(self.timestamp)


@dataclass
class Diary:
    """Diary object.
    Can be converted to/from json format with dataclasses.asdict and cls.from_dict.
    Can be saved to/loaded from a text file with self.save and cls.load.
    """

    name: str
    entries: list[Entry]

    def add(self, text: str) -> None:
        self.entries.append(Entry.create(text))

    def __str__(self) -> str:
        return f"{self.name} with {len(self.entries)} entries"

    @classmethod
    def from_dict(cls, dump: dict) -> "Diary":
        """The inverse of dataclasses.asdict"""
        entries = [Entry(**entry_dict) for entry_dict in dump["entries"]]
        return Diary(dump["name"], entries)

    def save(self, file: TextIO) -> None:
        json.dump(asdict(self), file, indent=4)

    @classmethod
    def load(cls, file: TextIO) -> "Diary":
        dump = json.load(file)
        return Diary.from_dict(dump)
