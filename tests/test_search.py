import unittest

from diary.core import Diary, Entry
from diary.search import strict_search, date_filter, metric_filter

entry1 = Entry("2001-12-25", "spam", {})
entry2 = Entry("2002-12-25", "spam eggs", {"metric": 0})
entry3 = Entry("2003-12-25", "eggs beans sausage spam", {"tag": 1})
entry4 = Entry("2004-12-25", "beans spam egg spam", {"metric": 10})
all_entries = [
    entry1,
    entry2,
    entry3,
    entry4,
]
diary = Diary("name", all_entries)


class TestStrictSeach(unittest.TestCase):
    def test_full_word(self):
        self.assertEqual(
            strict_search(diary, "spam"),
            [entry1, entry2, entry3, entry4],
        )

    def test_partial_word(self):
        self.assertEqual(strict_search(diary, "egg"), [entry2, entry3, entry4])

    def test_phrase(self):
        self.assertEqual(strict_search(diary, "spam egg"), [entry2, entry4])


class TestDateFilter(unittest.TestCase):
    def test_before(self):
        self.assertEqual(
            date_filter(all_entries, before="2002-12-25"),
            [entry1],
        )

    def test_after(self):
        self.assertEqual(
            date_filter(all_entries, after="2002-12-25"),
            [entry3, entry4],
        )


class TestMetricFilter(unittest.TestCase):
    def test_has_metric(self):
        self.assertEqual(metric_filter(all_entries, "metric"), [entry2, entry4])

    def test_lt(self):
        self.assertEqual(metric_filter(all_entries, "metric", lt=5), [entry2])

    def test_gt(self):
        self.assertEqual(metric_filter(all_entries, "metric", gt=5), [entry4])

    def test_eq(self):
        self.assertEqual(metric_filter(all_entries, "metric", eq=10), [entry4])


if __name__ == "__main__":
    unittest.main()
