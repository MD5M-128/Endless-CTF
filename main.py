from Crypto.Random import random
from hashlib import sha512
from flask import *
import threading
import asyncio
import bcrypt
import json
import time

app = Flask(__name__)

with open("dnsrecords.json", "r") as f: DNS_CRED = json.load(f)
try:
    with open("comprecords.json", "r") as f: COMP_DATA = json.load(f)
except:
    with open("comprecords.json", "w+") as f:
        COMP_DATA = {k: {"points": 0} for k in DNS_CRED.keys()}
        json.dump(COMP_DATA, f)

class ThreadSyncer(threading.local):
    def __init__(self):
        self.comp_hash = hash(json.dumps(COMP_DATA))

FLAGS = {}
KILLPROG = False
THREAD_LOCAL = ThreadSyncer()

def steve(): # Jobs
    last_save = time.time()
    while True:
        t = time.time()
        for f in list(FLAGS):
            if t - FLAGS[f]["time"] > 10:
                FLAGS.pop(f)
        if t - last_save > 30:
            last_save = t
            print(COMP_DATA)
            with open("comprecords.json", "w+") as f: json.dump(COMP_DATA, f)
        if KILLPROG:
            break

def scoreboard_eventsource():
    while True:
        if THREAD_LOCAL.comp_hash != (h := hash(json.dumps(COMP_DATA))):
            THREAD_LOCAL.comp_hash = h
            send_data = [{"name": entry, "points": COMP_DATA[entry]["points"]} for entry in COMP_DATA]
            yield "data: " + json.dumps(send_data) + "\n\n"

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/network/")
def network():
    return render_template("network.html")

@app.route("/dns/")
def dns():
    return render_template("dns.html")

@app.route("/scoreboard/")
def scoreboard():
    return render_template("scoreboard.html")

@app.route("/api/loghashrequest", methods=["POST"])
def api_loghashrequest():
    name = request.form["name"]
    password = request.form["password"]
    if name in DNS_CRED:
        if bcrypt.checkpw(password.encode("UTF8"), DNS_CRED[name]["password"].encode("UTF8")):
            num = random.randint(0, 2**64 - 1)
            response = {
                "type": "gen_success",
                "rand": num
            }
            h = sha512(name.encode("ASCII") + num.to_bytes(8, "little") + b"DUCKS").hexdigest()
            FLAGS[h] = {
                "name": name,
                "rand": num,
                "time": time.time()
            }
            return jsonify(response)
        else:
            return jsonify({"type": "gen_badpassword"})
    else:
        return jsonify({"type": "gen_dnsnotregistered"})

@app.route("/api/submithash", methods=["POST"])
def api_submithash():
    h = request.form["hash"]
    name = request.form["name"]
    password = request.form["password"]
    if name in DNS_CRED:
        if bcrypt.checkpw(password.encode("UTF8"), DNS_CRED[name]["password"].encode("UTF8")):
            if h in FLAGS:
                if FLAGS[h]["name"] != name:
                    COMP_DATA[name]["points"] += 50
                    return jsonify({"type": "points", "count": 50})
                else:
                    COMP_DATA[name]["points"] += 10
                    return jsonify({"type": "points", "count": 10})
                FLAGS.pop(h)
            else:
                return jsonify({"type": "flag_invalid"})
        else:
            return jsonify({"type": "gen_badpassword"})
    else:
        return jsonify({"type": "gen_dnsnotregistered"})

@app.route("/streams/scoreboard", methods=["GET", "POST"])
def streams_scoreboard():
    return Response(scoreboard_eventsource(), mimetype="text/event-stream")

jobs = threading.Thread(target=steve, daemon=True)
jobs.start()
app.run("0.0.0.0", 8080, threaded=True)