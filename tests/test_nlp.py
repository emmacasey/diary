import unittest

from diary.nlp import tokenize, strip_punc, sentiment, stats


class TestPipelines(unittest.TestCase):
    def setUp(self):
        self.para = """3 May. Bistritz.—
        Left Munich at 8:35 P. M., on 1st May, arriving at Vienna early next morning; should have arrived at 6:46, but train was an hour late."""
        self.pos = "Buda-Pesth seems a wonderful place, from the glimpse which I got of it from the train and the little I could walk through the streets."
        self.neg = "I feared to go very far from the station, as we had arrived late and would start as near the correct time as possible."

    def test_punctuation_stripper(self):
        self.assertEquals(
            strip_punc(self.para),
            """3 May Bistritz
        Left Munich at 835 P M on 1st May arriving at Vienna early next morning should have arrived at 646 but train was an hour late""",
        )

    def test_tokenizer(self):
        self.assertEquals(
            tokenize(self.para),
            [
                "3",
                "may",
                "bistritz",
                "left",
                "munich",
                "835",
                "p",
                "1st",
                "may",
                "arriv",
                "vienna",
                "earli",
                "next",
                "morn",
                "arriv",
                "646",
                "train",
                "hour",
                "late",
            ],
        )

    def test_sentiment(self):
        neutral = sentiment(self.para)
        self.assertEqual(neutral["compound"], 0)
        self.assertEqual(neutral["pos"], 0)
        self.assertEqual(neutral["neg"], 0)
        self.assertGreater(neutral["neu"], 0)

        pos = sentiment(self.pos)
        self.assertGreater(pos["compound"], 0)
        self.assertGreater(pos["pos"], 0)
        self.assertEqual(pos["neg"], 0)

        neg = sentiment(self.neg)
        self.assertLess(neg["compound"], 0)
        self.assertGreater(neg["neg"], 0)
        self.assertEqual(neg["pos"], 0)

    def test_stats(self):
        self.assertEqual(
            stats(self.para),
            {
                "compound": 0.0,
                "content_per_sent": 9.5,
                "content_words": 19,
                "letters_per_word": 124 / 35,
                "neg": 0.0,
                "neu": 1.0,
                "pos": 0.0,
                "sent_count": 2,
                "token_count": 35,
                "words_per_sent": 17.5,
            },
        )
