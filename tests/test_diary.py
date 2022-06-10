import unittest
import tempfile
from dataclasses import asdict
from datetime import datetime, timedelta

from diary.core import Diary, Record


class TestDiary(unittest.TestCase):
    def setUp(self):
        self.record1 = Record("2001-12-25 00:00:00-06:39", "entry1", {})
        self.record2 = Record("2002-12-25 00:00:00-06:39", "entry2", {"number": 0})
        self.diary = Diary("name", [self.record1, self.record2])

    def test_add(self):
        diary = Diary("name", [])
        now = datetime.now()
        diary.add("hello")
        self.assertEqual(len(diary.records), 1)
        record = diary.records[0]
        self.assertAlmostEqual(record.time, now, delta=timedelta(seconds=1))
        self.assertEqual(record.text, "hello")

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
