import unittest
import unittest
from diary.app import app
from diary.core import Diary, Record


class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.diary = Diary(
            "diary name",
            [
                Record("2001-01-01", "text1", {}),
                Record("2001-01-01", "text2", {}),
                Record("2001-01-01", "text3", {"metric": 1}),
            ],
        )
        with open("tmp/test.diary", "w") as f:
            self.diary.save(f)

    def test_hello_world(self):
        response = self.client.get("/")
        self.assertIn(b"<p>Hello, World!</p>", response.data)

    def test_read(self):
        response = self.client.get("/read")
        self.assertIn(b"<h1>diary name</h1>", response.data)
        self.assertIn(b"<em>2001-01-01</em> - text1", response.data)
        self.assertIn(
            b"<strong>#metric:</strong> 1",
            response.data,
        )
