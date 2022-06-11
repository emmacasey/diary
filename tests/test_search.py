import unittest
import tempfile
from dataclasses import asdict
from datetime import datetime, timedelta

from black import assert_equivalent

from diary.core import Diary, Record
from diary.search import strict_search


class TestSeach(unittest.TestCase):
    def setUp(self):
        self.record1 = Record("2001-12-25", "spam", {})
        self.record2 = Record("2002-12-25", "spam eggs", {"number": 0})
        self.record3 = Record("2003-12-25", "eggs beans sausage spam", {"tag": 1})
        self.record4 = Record("2004-12-25", "beans spam egg spam", {"number": 10})
        self.diary = Diary(
            "name",
            [
                self.record1,
                self.record2,
                self.record3,
                self.record4,
            ],
        )

    def test_strict_search(self):
        self.assertEqual(
            strict_search(self.diary, "spam"),
            [self.record1, self.record2, self.record3, self.record4],
        )
        self.assertEqual(
            strict_search(self.diary, "egg"), [self.record2, self.record3, self.record4]
        )


if __name__ == "__main__":
    unittest.main()
