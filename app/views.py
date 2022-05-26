from flask import render_template
from artifacts_api import artifacts_api

@artifacts_api.route("/")
def index():
    return render_template("index.html")

