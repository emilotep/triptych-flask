from flask import Blueprint, render_template, url_for, request
import os
main = Blueprint("main", __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "GET":
        title = "Triptych"
        return render_template("main/index.html", title = title)

    elif request.method == "POST":
        title = "Triptych"
        os.system("python3 /opt/scripts/ansible/avd_dc1/avd_sync.py")
        return render_template("main/index.html", title = title)
