from flask import Flask, render_template, request
from wtforms import Form, StringField, TextAreaField, DateField, FloatField
from wtforms.validators import Optional
from diary.core import Diary
from diary.search import strict_search, date_filter, metric_filter

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
        if form.metric.data:
            records = metric_filter(
                records,
                metric=form.metric.data,
                lt=form.lt.data,
                gt=form.gt.data,
                eq=form.eq.data,
            )
        return render_template("search.html", form=form, records=records)
    return render_template("search.html", form=form, records=diary.records)


if __name__ == "__main__":
    app.run()
