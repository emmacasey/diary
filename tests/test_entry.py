import unittest
from datetime import datetime, timedelta

from diary.core import Entry


class TestEntry(unittest.TestCase):
    def test_create(self):
        now = datetime.now()
        entry = Entry.create("hello")
        self.assertAlmostEqual(entry.time, now, delta=timedelta(seconds=1))
        self.assertEqual(entry.text, "hello")

    def test_no_metrics(self):
        entry = Entry.create("spam, eggs, sausage and spam")
        self.assertEqual(entry.metrics, {})

    def test_one_metric(self):
        entry = Entry.create("quiet night in #mood 5")
        self.assertEqual(entry.metrics, {"mood": 5})

    def test_many_metrics(self):
        entry = Entry.create("out for dinner #cost 18.0 #mood 5")
        self.assertEqual(entry.metrics, {"cost": 18, "mood": 5})


if __name__ == "__main__":
    unittest.main()
