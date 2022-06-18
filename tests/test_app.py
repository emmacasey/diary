import unittest
import unittest
from diary.app import app
from diary.core import Diary, Record


class TestHome(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_hello_world(self):
        response = self.client.get("/")
        self.assertIn(b"<p>Hello, World!</p>", response.data)


class FromSaveFile(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.diary = Diary(
            "diary name",
            [
                Record("2001-01-01", "text1", {}),
                Record("2001-01-02", "text2", {}),
                Record("2001-01-03", "text3", {"metric": 1}),
                Record("2001-01-04", "text1", {"metric": 10}),
                Record("2001-01-05", "text2", {"tag": 1}),
            ],
        )
        with open("tmp/test.diary", "w") as f:
            self.diary.save(f)


class TestRead(FromSaveFile):
    def test_read_title(self):
        response = self.client.get("/read")
        self.assertIn(b"<h1>diary name</h1>", response.data)

    def test_read_record(self):
        response = self.client.get("/read")
        self.assertIn(b"<em>2001-01-01</em> - text1", response.data)

    def test_read_metric(self):
        response = self.client.get("/read")
        self.assertIn(
            b"<strong>#metric:</strong> 1",
            response.data,
        )


class TestSearch(FromSaveFile):
    def test_form(self):
        response = self.client.get("/search")
        self.assertIn(b"<em>2001-01-01</em> - text1", response.data)
        self.assertIn(b"<em>2001-01-02</em> - text2", response.data)

    def test_basic_search(self):
        response = self.client.post(
            "/search",
            data={
                "search_term": "text1",
            },
        )
        self.assertIn(b"<em>2001-01-01</em> - text1", response.data)
        self.assertNotIn(b"<em>2001-01-02</em> - text2", response.data)

    def test_empty_search(self):
        response = self.client.post(
            "/search",
            data={
                "search_term": "no such",
            },
        )
        self.assertIn(b"<p>No entries found.</p>", response.data)
