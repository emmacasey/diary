import unittest

from diary.core import Diary, Record
from diary.search import strict_search, date_filter, metric_filter

record1 = Record("2001-12-25", "spam", {})
record2 = Record("2002-12-25", "spam eggs", {"metric": 0})
record3 = Record("2003-12-25", "eggs beans sausage spam", {"tag": 1})
record4 = Record("2004-12-25", "beans spam egg spam", {"metric": 10})
all_records = [
    record1,
    record2,
    record3,
    record4,
]
diary = Diary("name", all_records)


class TestStrictSeach(unittest.TestCase):
    def test_full_word(self):
        self.assertEqual(
            strict_search(diary, "spam"),
            [record1, record2, record3, record4],
        )

    def test_partial_word(self):
        self.assertEqual(strict_search(diary, "egg"), [record2, record3, record4])

    def test_phrase(self):
        self.assertEqual(strict_search(diary, "spam egg"), [record2, record4])


class TestDateFilter(unittest.TestCase):
    def test_before(self):
        self.assertEqual(
            date_filter(all_records, before="2002-12-25"),
            [record1],
        )

    def test_after(self):
        self.assertEqual(
            date_filter(all_records, after="2002-12-25"),
            [record3, record4],
        )


class TestMetricFilter(unittest.TestCase):
    def test_has_metric(self):
        self.assertEqual(metric_filter(all_records, "metric"), [record2, record4])

    def test_lt(self):
        self.assertEqual(metric_filter(all_records, "metric", lt=5), [record2])

    def test_gt(self):
        self.assertEqual(metric_filter(all_records, "metric", gt=5), [record4])

    def test_eq(self):
        self.assertEqual(metric_filter(all_records, "metric", eq=10), [record4])


if __name__ == "__main__":
    unittest.main()
