from attr import Attribute
from flask import Flask, render_template, request
from wtforms import Form, StringField, TextAreaField, DateField
from wtforms.validators import Optional
from wtforms.widgets import DateInput
from diary.core import Diary
from diary.search import strict_search, date_filter

app = Flask(__name__)


@app.route("/")
def hello_world():
    return render_template("index.html")


@app.route("/read")
def demo_read():
    with open("tmp/test.diary", "r") as f:
        diary = Diary.load(f)
    return render_template("read.html", diary=diary)


class CreateForm(Form):
    entry_text = TextAreaField("Dear Diary...")


@app.route("/create", methods=["GET", "POST"])
def create():
    with open("tmp/test.diary", "r") as f:
        diary = Diary.load(f)
    form = CreateForm(request.form)
    if request.method == "POST" and form.validate():
        diary.add(form.entry_text.data)
        with open("tmp/test.diary", "w") as f:
            diary.save(f)
        return render_template("create.html", form=form, diary=diary)
    return render_template("create.html", form=form, diary=diary)


class SearchForm(Form):
    search_term = StringField("Search Term")
    before = DateField("Before", validators=[Optional()])
    after = DateField("After", validators=[Optional()])


@app.route("/search", methods=["GET", "POST"])
def search():
    with open("tmp/test.diary", "r") as f:
        diary = Diary.load(f)
    form = SearchForm(request.form)
    print(form.data)
    if request.method == "POST" and form.validate():
        records = strict_search(diary, form.search_term.data)
        try:
            after = form.after.data.isoformat()
        except AttributeError:
            after = None
        try:
            before = form.before.data.isoformat()
        except AttributeError:
            before = None
        records = date_filter(records, after=after, before=before)
        return render_template("search.html", form=form, records=records)
    return render_template("search.html", form=form, records=diary.records)


if __name__ == "__main__":
    app.run()
