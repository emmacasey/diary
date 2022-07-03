import base64
import sqlite3
from datetime import datetime
from io import BytesIO

from flask import Flask, redirect, render_template, request, url_for
from matplotlib.figure import Figure
from wtforms import DateField, FloatField, Form, StringField, TextAreaField
from wtforms.validators import Optional

from diary.core import Diary
from diary.db import create_diary, load_diary, update_diary
from diary.nlp import stats
from diary.search import date_filter, metric_filter, strict_search

app = Flask(__name__)

app.config["DB_ADDRESS"] = "tmp/main.db"


@app.route("/")
def hello_world():
    """Hello world"""

    return render_template("index.html")


@app.route("/read/<username>")
def read(username):
    """Read entries from the diary associated with a user in the database"""

    diary = load_diary(app.config["DB_ADDRESS"], username)
    return render_template("read.html", diary=diary)


def plot_to_base64(X, Y) -> str:
    fig = Figure()
    ax = fig.subplots()
    ax.plot(X, Y)
    buf = BytesIO()
    fig.savefig(buf, format="png")
    return base64.b64encode(buf.getbuffer()).decode("ascii")


@app.route("/graphs")
def demo_graph():
    """Make graphs of metrics and stats from the diary saved at tests/dracula.diary"""
    with open("tests/dracula.diary", "r") as f:
        diary = Diary.load(f)
    metrics: dict[str, tuple[list[datetime], list[float]]] = {}
    for entry in diary.entries:
        entry_stats = stats(entry.text) | entry.metrics
        for metric, value in entry_stats.items():
            try:
                metrics[metric][0].append(entry.time)
                metrics[metric][1].append(value)
            except KeyError:
                metrics[metric] = ([entry.time], [value])

    graphs: dict[str, str] = {}
    for metric, (X, Y) in metrics.items():
        graphs[metric] = plot_to_base64(X, Y)

    return render_template("graphs.html", diary=diary, graphs=graphs)


class CreateForm(Form):
    """A wtform to create diary entries, without validation."""

    name = StringField("Diary name")
    username = StringField("username")


@app.route("/create/", methods=["GET", "POST"])
def create():
    """Create a new diary associated with a user in the database and then save it"""
    form = CreateForm(request.form)
    if request.method == "POST" and form.validate():
        diary = Diary(form.name.data, [])
        try:
            create_diary(app.config["DB_ADDRESS"], diary, form.username.data)
            return redirect(url_for("read", username=form.username.data))
        except sqlite3.IntegrityError:
            form.username.errors.append("username already taken")
    return render_template("create.html", form=form)


class AddForm(Form):
    """A wtform to create diary entries, without validation."""

    entry_text = TextAreaField("Dear Diary...")


@app.route("/add/<username>", methods=["GET", "POST"])
def add(username):
    """Add a new entry in the diary associated with a user in the database and then save it"""

    diary = load_diary(app.config["DB_ADDRESS"], username)
    form = AddForm(request.form)
    if request.method == "POST" and form.validate():
        diary.add(form.entry_text.data)
        update_diary(app.config["DB_ADDRESS"], diary)
        return render_template("add.html", form=form, diary=diary)
    return render_template("add.html", form=form, diary=diary)


class SearchForm(Form):
    """A wtform to search diary entries, with simple validation."""

    search_term = StringField("Search Term")
    before = DateField("Before", validators=[Optional()])
    after = DateField("After", validators=[Optional()])
    metric = StringField("Metric")
    gt = FloatField("Greater Than", validators=[Optional()])
    lt = FloatField("Less Than", validators=[Optional()])
    eq = FloatField("Equals", validators=[Optional()])

    def validate(self):
        if not super().validate():
            return False

        if self.before.data and self.after.data and self.after.data > self.before.data:
            self.after.errors.append("Inconsistent restrictions")
            self.before.errors.append("Inconsistent restrictions")
            return False

        if self.gt.data or self.lt.data or self.eq.data:
            if not self.metric.data:
                self.metric.errors.append(
                    "Metric is required if restrictions are given"
                )
                return False
            if self.gt.data and self.lt.data and self.gt.data > self.lt.data:
                self.gt.errors.append("Inconsistent restrictions")
                self.lt.errors.append("Inconsistent restrictions")
                return False
            if self.eq.data and (self.gt.data or self.lt.data):
                self.eq.errors.append("Inconsistent restrictions")
                return False
        return True


@app.route("/search/<username>", methods=["GET", "POST"])
def search(username):
    """Search over the entries from the diary associated with a user in the database
    Including some limited validation to ensure requirements are consistent."""

    diary = load_diary(app.config["DB_ADDRESS"], username)
    form = SearchForm(request.form)
    if request.method == "POST" and form.validate():
        entries = strict_search(diary, form.search_term.data)
        try:
            after = form.after.data.isoformat()
        except AttributeError:
            after = None
        try:
            before = form.before.data.isoformat()
        except AttributeError:
            before = None
        entries = date_filter(entries, after=after, before=before)
        if form.metric.data:
            entries = metric_filter(
                entries,
                metric=form.metric.data,
                lt=form.lt.data,
                gt=form.gt.data,
                eq=form.eq.data,
            )
        return render_template("search.html", form=form, entries=entries)
    return render_template("search.html", form=form, entries=diary.entries)


if __name__ == "__main__":
    app.run()
