import unittest
from datetime import datetime, timedelta

from diary.core import Record


class TestRecord(unittest.TestCase):
    def test_create(self):
        now = datetime.now()
        record = Record.create("hello")
        self.assertAlmostEqual(record.time, now, delta=timedelta(seconds=1))
        self.assertEqual(record.text, "hello")

    def test_no_numbers(self):
        record = Record.create("spam, eggs, sausage and spam")
        self.assertEqual(record.numbers, {})

    def test_one_number(self):
        record = Record.create("quiet night in #mood 5")
        self.assertEqual(record.numbers, {"mood": 5})

    def test_many_numbers(self):
        record = Record.create("out for dinner #cost 18.0 #mood 5")
        self.assertEqual(record.numbers, {"cost": 18, "mood": 5})


if __name__ == "__main__":
    unittest.main()
