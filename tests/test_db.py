import sqlite3
import unittest

from diary.core import Diary, Entry
from diary.db import create_diary, load_diary, create_entry


class TestDB(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.entry1 = Entry("2001-01-01", "entry1", {})
        self.entry2 = Entry("2001-01-02", "entry2", {"metric": 0, "tag": 2})
        self.entry3 = Entry("2001-01-03", "entry3", {"metric": 2, "mood": 1})
        self.entry4 = Entry("2001-01-04", "entry4", {"metric": 5, "goal": 10})
        self.diary = Diary("name", [self.entry1, self.entry2, self.entry3])

    def test_save_load(self):
        create_diary(self.diary)
        self.assertEqual(load_diary(self.diary.uuid), self.diary)

    def test_create_entry(self):
        create_diary(self.diary)
        create_entry(self.diary.uuid, self.entry4)
        diary = load_diary(self.diary.uuid)
        self.assertEquals(len(diary.entries), 4)
        self.assertEqual(diary.entries[-1], self.entry4)

    def test_uniqueness(self):
        create_diary(self.diary)
        with self.assertRaises(sqlite3.DatabaseError):
            create_diary(self.diary)
        with self.assertRaises(sqlite3.DatabaseError):
            create_entry(self.diary.uuid, self.entry1)


if __name__ == "__main__":
    unittest.main()
