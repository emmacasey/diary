import unittest
from datetime import datetime, timedelta

from diary.core import Diary


class TestDiary(unittest.TestCase):
    def test_add(self):
        diary = Diary("name", [])
        now = datetime.now()
        diary.add("hello")
        self.assertEqual(len(diary.records), 1)
        record = diary.records[0]
        self.assertAlmostEqual(record.time, now, delta=timedelta(seconds=1))
        self.assertEqual(record.text, "hello")


if __name__ == "__main__":
    unittest.main()
