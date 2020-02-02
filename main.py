from Crypto.Random import random
from flask import *
import bcrypt
import json

app = Flask(__name__)

with open("dnsrecords.json", "r") as f: dns_cred = json.loads(f.read())

flags = {}

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/network/")
def network():
    return render_template("network.html")

@app.route("/dns/")
def dns():
    return render_template("dns.html")

@app.route("/api/loghashrequest", methods=["POST"])
def api_loghashrequest():
    name = request.form["name"]
    password = request.form["password"]
    if name in dns_cred:
        if bcrypt.checkpw(password.encode("UTF8"), dns_cred[name]["password"].encode("UTF8")):
            num = random.randint(0, 2**64 - 1)
            response = {
                "type": "gen_success",
                "rand": num
            }
            flags[num] = name
            return jsonify(response)
        else:
            return jsonify({"type": "gen_badpassword"})
    else:
        return jsonify({"type": "gen_dnsnotregistered"})

app.run("0.0.0.0", 8080)