from .core import Diary, Record


def strict_search(diary: Diary, search_term: str) -> list[Record]:
    return [record for record in diary.records if search_term in record.text]
