from subprocess import call
from requests import post

SERVER_URL = "http://localhost:8080"

def submit(name, password, flag):
    return post(SERVER_URL + "/api/submithash", data={"name": name, "password": password, "hash": flag}).json()