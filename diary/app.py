from flask import Flask, render_template
from diary.core import Diary

app = Flask(__name__)


@app.route("/")
def hello_world():
    return render_template("index.html")


@app.route("/read")
def read():
    with open("tmp/test.diary", "r") as f:
        diary = Diary.load(f)
    return render_template("read.html", diary=diary)


if __name__ == "__main__":
    app.run()
