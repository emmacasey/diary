import unittest
from datetime import datetime

from diary.core import Record


class TestRecord(unittest.TestCase):
    def test_init(self):
        now = datetime.now()
        record = Record(now, "hello")
        self.assertEqual(record.time, now)
        self.assertEqual(record.text, "hello")


if __name__ == "__main__":
    unittest.main()
