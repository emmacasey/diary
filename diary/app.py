from flask import Flask, render_template, request
from wtforms import Form, StringField, TextAreaField, DateField, FloatField
from wtforms.validators import Optional
from diary.core import Diary
from diary.db import create_diary, load_diary, update_diary
from diary.search import strict_search, date_filter, metric_filter

app = Flask(__name__)


@app.route("/")
def hello_world():
    """Hello world"""

    return render_template("index.html")


@app.route("/read/<username>")
def read(username):
    """Read entries from the diary associated with a user in the database"""

    diary = load_diary(username)
    return render_template("read.html", diary=diary)


class AddForm(Form):
    """A wtform to create diary entries, without validation."""

    entry_text = TextAreaField("Dear Diary...")


@app.route("/add/<username>", methods=["GET", "POST"])
def add(username):
    """Add a new entry in the diary associated with a user in the database and then save it"""

    diary = load_diary(username)
    form = AddForm(request.form)
    if request.method == "POST" and form.validate():
        diary.add(form.entry_text.data)
        update_diary(diary)
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

    diary = load_diary(username)
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
