from time import time
from requests import post
from hashlib import sha512
from getpass import getpass
from subprocess import call
from sys import argv

SERVER_URL = "http://localhost:8080"

house = argv[1]
password = getpass("House password: ")
house = (house.lower() + ".com").encode("ASCII")
while True:
    json = post(SERVER_URL + "/api/loghashrequest", data={"name": house, "password": password}).json()
    if json["type"] == "gen_success":
        h = sha512(house + json["rand"].to_bytes(8, "little") + b"DUCKS").hexdigest()
        call(["python", "program.py", password, h])
    else:
        if json["type"] == "gen_badpassword":
            print("Incorrect house password provided!")
        elif json["type"] == "gen_dnsnotregistered":
            print("That DNS name is not registered!")
        else:
            print("Unknown error.")
        print("Exitting...")
        break