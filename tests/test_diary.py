import unittest
import tempfile
from dataclasses import asdict
from datetime import datetime, timedelta

from diary.core import Diary, Entry


class TestDiary(unittest.TestCase):
    def setUp(self):
        self.entry1 = Entry("2001-12-25 00:00:00-06:39", "entry1", {})
        self.entry2 = Entry("2002-12-25 00:00:00-06:39", "entry2", {"metric": 0})
        self.diary = Diary("name", [self.entry1, self.entry2])

    def test_add(self):
        diary = Diary("name", [])
        now = datetime.now()
        diary.add("hello")
        self.assertEqual(len(diary.entries), 1)
        entry = diary.entries[0]
        self.assertAlmostEqual(entry.time, now, delta=timedelta(seconds=1))
        self.assertEqual(entry.text, "hello")

    def test_from_dict(self):
        dump = asdict(self.diary)
        diary = Diary.from_dict(dump)
        self.assertEqual(diary, self.diary)

    def test_save_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(tmpdir + "/diary", "w") as fp:
                self.diary.save(fp)
            with open(tmpdir + "/diary", "r") as fp:
                diary = Diary.load(fp)
        self.assertEqual(diary, self.diary)


if __name__ == "__main__":
    unittest.main()
