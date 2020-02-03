import fake_socket as socket
from subprocess import call
from sys import argv

password = argv[1]
domain = "watkins.com"
serve = "receiver"

s = socket.socket()

if s.dns_lookup(serve + "." + domain)["type"] == "dns_notfound":
    print("Logging in to DNS...")
    response = s.dns_login(serve, domain, password)
    if response["type"] != "dns_login":
        print("DNS Login error")
        # TODO: Find out why, then try again
        exit(0)

while True:
    data = s.recv()
    if data: print(data["content"])

# And it's as easy as that.
# No. It really isn't