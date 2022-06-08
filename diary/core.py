from dataclasses import dataclass
from datetime import datetime


@dataclass
class Record:
    """Individual diary entry record"""

    time: datetime
    text: str


@dataclass
class Diary:
    """Diary object"""

    name: str
    records: list[Record]
