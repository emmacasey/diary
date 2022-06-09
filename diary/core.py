from dataclasses import dataclass
from datetime import datetime


@dataclass
class Record:
    """Individual diary entry record."""

    time: datetime
    text: str

    @classmethod
    def create(cls, text: str) -> "Record":
        return cls(datetime.now(), text)


@dataclass
class Diary:
    """Diary object."""

    name: str
    records: list[Record]

    def add(self, text: str) -> None:
        self.records.append(Record.create(text))
