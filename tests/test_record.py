import unittest
from datetime import datetime, timedelta

from diary.core import Record


class TestRecord(unittest.TestCase):
    def test_create(self):
        now = datetime.now()
        record = Record.create("hello")
        self.assertAlmostEqual(record.time, now, delta=timedelta(seconds=1))
        self.assertEqual(record.text, "hello")


if __name__ == "__main__":
    unittest.main()
