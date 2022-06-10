from dataclasses import dataclass, asdict
from datetime import datetime
from typing import TextIO
import json
import re


@dataclass
class Record:
    """Individual diary entry record.
    To instantiate pass the text to .create(), this will auto-populate the current date
    and will detect numbers written in the form `#keyword 10.0`."""

    timestamp: str
    text: str
    numbers: dict[str, float]

    @classmethod
    def create(cls, text: str) -> "Record":
        numbers = {
            name: float(num) for name, num in re.findall(r"#(\w+) (\d+\.?\d*)", text)
        }
        return cls(datetime.now().isoformat(), text, numbers)

    def __str__(self) -> str:
        return f"{self.timestamp} - {self.text}"

    @property
    def time(self) -> datetime:
        return datetime.fromisoformat(self.timestamp)


@dataclass
class Diary:
    """Diary object."""

    name: str
    records: list[Record]

    def add(self, text: str) -> None:
        self.records.append(Record.create(text))

    def __str__(self) -> str:
        return f"{self.name} with {len(self.records)} entries"

    @classmethod
    def from_dict(cls, dump: dict) -> "Diary":
        """The inverse of dataclasses.asdict"""
        records = [Record(**record_dict) for record_dict in dump["records"]]
        return Diary(dump["name"], records)

    def save(self, file: TextIO) -> None:
        json.dump(asdict(self), file, indent=4)

    @classmethod
    def load(cls, file: TextIO) -> "Diary":
        dump = json.load(file)
        return Diary.from_dict(dump)
