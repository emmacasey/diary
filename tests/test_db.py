import sqlite3
import unittest


from diary.core import Diary, Entry
from diary.db import create_diary, load_diary, create_entry, drop_db

DB_ADDRESS = "tmp/testing.db"


class TestDB(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.entry1 = Entry("2001-01-01", "entry1", {})
        self.entry2 = Entry("2001-01-02", "entry2", {"metric": 0, "tag": 2})
        self.entry3 = Entry("2001-01-03", "entry3", {"metric": 2, "mood": 1})
        self.entry4 = Entry("2001-01-04", "entry4", {"metric": 5, "goal": 10})
        self.diary = Diary("name", [self.entry1, self.entry2, self.entry3])

    def tearDown(self) -> None:
        drop_db(DB_ADDRESS)

    def test_save_load(self):
        create_diary(DB_ADDRESS, self.diary, "username")
        self.assertEqual(load_diary(DB_ADDRESS, "username"), self.diary)

    def test_create_entry(self):
        create_diary(DB_ADDRESS, self.diary, "username")
        create_entry(DB_ADDRESS, self.diary.uuid, self.entry4)
        diary = load_diary(DB_ADDRESS, "username")
        self.assertEquals(len(diary.entries), 4)
        self.assertEqual(diary.entries[-1], self.entry4)

    def test_uniqueness(self):
        create_diary(DB_ADDRESS, self.diary, "username")
        with self.assertRaises(sqlite3.DatabaseError):
            create_diary(DB_ADDRESS, self.diary, "username")
        new_diary = Diary("name2", [self.entry4])
        with self.assertRaises(sqlite3.DatabaseError):
            create_diary(DB_ADDRESS, new_diary, "username")
        with self.assertRaises(sqlite3.DatabaseError):
            create_entry(DB_ADDRESS, self.diary.uuid, self.entry1)


if __name__ == "__main__":
    unittest.main()
