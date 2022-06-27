from datetime import datetime
import base64
from io import BytesIO


from matplotlib.figure import Figure
from flask import Flask, render_template, request
from wtforms import Form, StringField, TextAreaField, DateField, FloatField
from wtforms.validators import Optional

from diary.core import Diary
from diary.search import strict_search, date_filter, metric_filter
from diary.nlp import stats

app = Flask(__name__)


@app.route("/")
def hello_world():
    """Hello world"""
    return render_template("index.html")


@app.route("/read")
def demo_read():
    """Read entries from the diary saved at tests/test.diary"""
    with open("tests/test.diary", "r") as f:
        diary = Diary.load(f)
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

    entry_text = TextAreaField("Dear Diary...")


@app.route("/create", methods=["GET", "POST"])
def create():
    """Create entries in the diary saved at tests/test.diary and then save it"""
    with open("tests/test.diary", "r") as f:
        diary = Diary.load(f)
    form = CreateForm(request.form)
    if request.method == "POST" and form.validate():
        diary.add(form.entry_text.data)
        with open("tests/test.diary", "w") as f:
            diary.save(f)
        return render_template("create.html", form=form, diary=diary)
    return render_template("create.html", form=form, diary=diary)


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


@app.route("/search", methods=["GET", "POST"])
def search():
    """Search over the entries from the diary saved at tests/test.diary
    Including some limited validation to ensure requirements are consistent."""
    with open("tests/test.diary", "r") as f:
        diary = Diary.load(f)
    form = SearchForm(request.form)
    print(form.data)
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
