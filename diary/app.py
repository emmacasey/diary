from flask import Flask, render_template, request
from wtforms import Form, StringField
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


class SearchForm(Form):
    search_term = StringField("Search Term")
    before = StringField("Before", widget=DateInput())
    after = StringField("After", widget=DateInput())


@app.route("/search", methods=["GET", "POST"])
def search():
    with open("tmp/test.diary", "r") as f:
        diary = Diary.load(f)
    form = SearchForm(request.form)
    if request.method == "POST" and form.validate():
        records = strict_search(diary, form.search_term.data)
        records = date_filter(records, after=form.after.data, before=form.before.data)
        return render_template("search.html", form=form, records=records)
    return render_template("search.html", form=form, records=diary.records)


if __name__ == "__main__":
    app.run()
