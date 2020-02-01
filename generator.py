from time import time
from hashlib import sha512
from getpass import getpass
from os import system
from sys import argv

house = argv[1]
password = getpass("H")
if house in ["carnley", "challen", "moyes", "watkins"]:
    house = house.encode("ASCII")
    h = sha512(house + int(time() - 8).to_bytes(8, "little") + b"DUCKS" + int(time()).to_bytes(8, "big")).hexdigest()
    system("python sender.py " + h)