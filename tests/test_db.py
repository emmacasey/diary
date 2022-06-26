import unittest
import tempfile
from dataclasses import asdict
from datetime import datetime, timedelta

from diary.core import Diary, Entry
from diary.db import create_diary, load_diary


class TestDB(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.entry1 = Entry("2001-01-01", "entry1", {})
        self.entry2 = Entry("2001-01-02", "entry2", {"metric": 0, "tag": 2})
        self.entry3 = Entry("2001-01-03", "entry2", {"metric": 2, "mood": 1})
        self.diary = Diary("name", [self.entry1, self.entry2, self.entry3])

    def test_save_load(self):
        create_diary(self.diary)
        self.assertEqual(load_diary(self.diary.uuid), self.diary)


if __name__ == "__main__":
    unittest.main()
