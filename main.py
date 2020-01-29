from flask import *

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/network/")
def network():
    return render_template("network.html")

app.run("0.0.0.0", 8080)