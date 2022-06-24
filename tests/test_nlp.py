import unittest

from diary.nlp import tokenize


class TestPipelines(unittest.TestCase):
    def test_tokenizer(self):
        self.assertEquals(
            [
                "may",
                "bistritz",
                "left",
                "munich",
                "may",
                "arriv",
                "vienna",
                "earli",
                "next",
                "morn",
                "arriv",
                "train",
                "hour",
                "late",
            ],
            tokenize(
                "3 May. Bistritz.—Left Munich at 8:35 P. M., on 1st May, arriving at Vienna early next morning; should have arrived at 6:46, but train was an hour late."
            ),
        )
