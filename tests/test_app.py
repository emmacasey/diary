import unittest
from datetime import datetime, timedelta

from diary.app import app
from diary.core import Diary, Entry
from diary.db import create_diary, load_diary, drop_db


DB_ADDRESS = "tmp/testing.db"


class TestHome(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_hello_world(self):
        response = self.client.get("/")
        self.assertIn(b"<p>Hello, World!</p>", response.data)


class FromDB(unittest.TestCase):
    def setUp(self):
        app.config["DB_ADDRESS"] = DB_ADDRESS
        drop_db(DB_ADDRESS)
        self.client = app.test_client()
        self.diary = Diary(
            "diary name",
            [
                Entry("2001-01-01", "text1", {}),
                Entry("2001-01-02", "text2", {}),
                Entry("2001-01-03", "text3", {"metric": 1}),
                Entry("2001-01-04", "text1", {"metric": 10}),
                Entry("2001-01-05", "text2", {"tag": 1}),
            ],
        )
        create_diary(DB_ADDRESS, self.diary, "username")
        wrong_diary = Diary(
            "wrong name",
            [
                Entry("2001-01-01", "wrong entry", {}),
            ],
        )
        create_diary(DB_ADDRESS, wrong_diary, "wrong user")

    def tearDown(self) -> None:
        drop_db(DB_ADDRESS)


class TestRead(FromDB):
    def test_read_title(self):
        response = self.client.get("/read/username")
        self.assertIn(b"<h1>diary name</h1>", response.data)

    def test_read_entry(self):
        response = self.client.get("/read/username")
        self.assertIn(b"<em>2001-01-01</em> - text1", response.data)

    def test_read_metric(self):
        response = self.client.get("/read/username")
        self.assertIn(
            b"<strong>#metric:</strong> 1",
            response.data,
        )

    def test_read_right_user(self):
        response = self.client.get("/read/username")
        self.assertNotIn(b"<h1>wrong name</h1>", response.data)
        self.assertNotIn(b"<em>2001-01-01</em> - wrong entry", response.data)


class TestCreate(FromDB):
    def test_form(self):
        response = self.client.get("/create/")
        self.assertIn(b"<title>Create</title>", response.data)
        self.assertIn(b"Diary name", response.data)

    def test_create(self):
        response = self.client.post(
            "/create/",
            data={"name": "diary_name", "username": "new_username"},
        )
        self.assertIn(b"Redirecting", response.data)
        self.assertEqual(302, response.status_code)
        self.assertEqual("/read/new_username", response.location)
        new_diary = load_diary(DB_ADDRESS, "new_username")
        self.assertEqual(new_diary.name, "diary_name")

    def test_uniqueness(self):
        response = self.client.post(
            "/create/",
            data={"name": "diary_name", "username": "username"},
        )
        self.assertNotIn(b"<h1>diary_name</h1>", response.data)
        self.assertIn(b"username already taken", response.data)


class TestAdd(FromDB):
    def test_form(self):
        response = self.client.get("/add/username")
        self.assertIn(b"<em>2001-01-01</em> - text1", response.data)
        self.assertIn(b"<em>2001-01-02</em> - text2", response.data)
        self.assertIn(b"Dear Diary...", response.data)
        self.assertNotIn(b"text of a newly-created entry", response.data)

    def test_create(self):
        now = datetime.now()
        response = self.client.post(
            "/add/username",
            data={
                "entry_text": "text of a newly-created entry",
            },
        )
        self.assertIn(b"<em>2001-01-01</em> - text1", response.data)
        self.assertIn(b"text of a newly-created entry", response.data)
        new_diary = load_diary(DB_ADDRESS, "username")
        entry = new_diary.entries[-1]
        self.assertAlmostEqual(entry.time, now, delta=timedelta(seconds=1))
        self.assertEqual(entry.text, "text of a newly-created entry")


class TestSearch(FromDB):
    def test_form(self):
        response = self.client.get("/search/username")
        self.assertIn(b"<em>2001-01-01</em> - text1", response.data)
        self.assertIn(b"<em>2001-01-02</em> - text2", response.data)

    def test_basic_search(self):
        response = self.client.post(
            "/search/username",
            data={
                "search_term": "text1",
                "after": "",
                "before": "",
                "metric": "",
                "lt": "",
                "gt": "",
                "eq": "",
            },
        )
        self.assertIn(b"<em>2001-01-01</em> - text1", response.data)
        self.assertNotIn(b"<em>2001-01-02</em> - text2", response.data)

    def test_failing_search(self):
        response = self.client.post(
            "/search/username",
            data={
                "search_term": "no such",
                "after": "",
                "before": "",
                "metric": "",
                "lt": "",
                "gt": "",
                "eq": "",
            },
        )
        self.assertIn(b"<p>No entries found.</p>", response.data)

    def test_empty_search(self):
        response = self.client.post(
            "/search/username",
            data={
                "search_term": "",
                "after": "",
                "before": "",
                "metric": "",
                "lt": "",
                "gt": "",
                "eq": "",
            },
        )
        self.assertIn(b"<em>2001-01-01</em> - text1", response.data)
        self.assertIn(b"<em>2001-01-02</em> - text2", response.data)

    def test_after_search(self):
        response = self.client.post(
            "/search/username",
            data={
                "search_term": "",
                "after": "2001-01-02",
                "before": "",
                "metric": "",
                "lt": "",
                "gt": "",
                "eq": "",
            },
        )
        self.assertNotIn(b"<em>2001-01-01</em> - text1", response.data)
        self.assertNotIn(b"<em>2001-01-02</em> - text2", response.data)
        self.assertIn(b"<em>2001-01-03</em> - text3", response.data)

    def test_bad_date(self):
        response = self.client.post(
            "/search/username",
            data={
                "search_term": "",
                "after": "not a date",
                "before": "",
                "metric": "",
                "lt": "",
                "gt": "",
                "eq": "",
            },
        )
        self.assertIn(b"Not a valid date value.", response.data)

    def test_before_search(self):
        response = self.client.post(
            "/search/username",
            data={
                "search_term": "",
                "after": "",
                "before": "2001-01-02",
                "metric": "",
                "lt": "",
                "gt": "",
                "eq": "",
            },
        )
        self.assertIn(b"<em>2001-01-01</em> - text1", response.data)
        self.assertNotIn(b"<em>2001-01-02</em> - text2", response.data)
        self.assertNotIn(b"<em>2001-01-03</em> - text3", response.data)

    def test_between_search(self):
        response = self.client.post(
            "/search/username",
            data={
                "search_term": "",
                "after": "2001-01-02",
                "before": "2001-01-04",
                "metric": "",
                "lt": "",
                "gt": "",
                "eq": "",
            },
        )
        self.assertNotIn(b"<em>2001-01-01</em> - text1", response.data)
        self.assertNotIn(b"<em>2001-01-02</em> - text2", response.data)
        self.assertIn(b"<em>2001-01-03</em> - text3", response.data)
        self.assertNotIn(b"<em>2001-01-04</em> - text1", response.data)
        self.assertNotIn(b"<em>2001-01-05</em> - text2", response.data)

    def test_inconsitent_date_search(self):
        response = self.client.post(
            "/search/username",
            data={
                "search_term": "",
                "after": "2001-01-04",
                "before": "2001-01-02",
                "metric": "",
                "lt": "",
                "gt": "",
                "eq": "",
            },
        )
        self.assertIn(b"Inconsistent restrictions", response.data)

    def test_has_metric(self):
        response = self.client.post(
            "/search/username",
            data={
                "search_term": "",
                "after": "",
                "before": "",
                "metric": "metric",
                "lt": "",
                "gt": "",
                "eq": "",
            },
        )
        self.assertNotIn(b"<em>2001-01-02</em> - text2", response.data)
        self.assertIn(b"<em>2001-01-03</em> - text3", response.data)
        self.assertIn(b"<em>2001-01-04</em> - text1", response.data)
        self.assertNotIn(b"<em>2001-01-05</em> - text2", response.data)

    def test_metric_gt(self):
        response = self.client.post(
            "/search/username",
            data={
                "search_term": "",
                "after": "",
                "before": "",
                "metric": "metric",
                "lt": "",
                "gt": "4",
                "eq": "",
            },
        )
        self.assertNotIn(b"<em>2001-01-02</em> - text2", response.data)
        self.assertNotIn(b"<em>2001-01-03</em> - text3", response.data)
        self.assertIn(b"<em>2001-01-04</em> - text1", response.data)
        self.assertNotIn(b"<em>2001-01-05</em> - text2", response.data)

    def test_metric_lt(self):
        response = self.client.post(
            "/search/username",
            data={
                "search_term": "",
                "after": "",
                "before": "",
                "metric": "metric",
                "lt": "4",
                "gt": "",
                "eq": "",
            },
        )
        self.assertNotIn(b"<em>2001-01-02</em> - text2", response.data)
        self.assertIn(b"<em>2001-01-03</em> - text3", response.data)
        self.assertNotIn(b"<em>2001-01-04</em> - text1", response.data)
        self.assertNotIn(b"<em>2001-01-05</em> - text2", response.data)

    def test_metric_eq(self):
        response = self.client.post(
            "/search/username",
            data={
                "search_term": "",
                "after": "",
                "before": "",
                "metric": "metric",
                "lt": "",
                "gt": "",
                "eq": "10",
            },
        )
        self.assertNotIn(b"<em>2001-01-02</em> - text2", response.data)
        self.assertNotIn(b"<em>2001-01-03</em> - text3", response.data)
        self.assertIn(b"<em>2001-01-04</em> - text1", response.data)
        self.assertNotIn(b"<em>2001-01-05</em> - text2", response.data)

    def test_metric_missing(self):
        response = self.client.post(
            "/search/username",
            data={
                "search_term": "",
                "after": "",
                "before": "",
                "metric": "",
                "lt": "",
                "gt": "",
                "eq": "10",
            },
        )
        self.assertIn(b"Metric is required if restrictions are given", response.data)

    def test_metric_inconsitent(self):
        response = self.client.post(
            "/search/username",
            data={
                "search_term": "",
                "after": "",
                "before": "",
                "metric": "Metric",
                "lt": "1",
                "gt": "",
                "eq": "10",
            },
        )
        self.assertIn(b"Inconsistent restrictions", response.data)
        response = self.client.post(
            "/search/username",
            data={
                "search_term": "",
                "after": "",
                "before": "",
                "metric": "Metric",
                "lt": "1",
                "gt": "10",
                "eq": "",
            },
        )
        self.assertIn(b"Inconsistent restrictions", response.data)

    def test_combined_search(self):
        response = self.client.post(
            "/search/username",
            data={
                "search_term": "text1",
                "after": "",
                "before": "2001-01-03",
                "metric": "",
                "lt": "",
                "gt": "",
                "eq": "",
            },
        )
        self.assertIn(b"<em>2001-01-01</em> - text1", response.data)
        self.assertNotIn(b"<em>2001-01-02</em> - text2", response.data)
        self.assertNotIn(b"<em>2001-01-04</em> - text1", response.data)
