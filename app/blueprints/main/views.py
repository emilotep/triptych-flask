from flask import Blueprint, render_template, url_for, request
main = Blueprint("main", __name__)

@main.route('/')
def index():
    title = "Triptych"
    return render_template("main/index.html", title = title)
