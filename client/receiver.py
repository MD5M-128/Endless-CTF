import fake_socket as socket
from sys import argv

import submitter

password = argv[2]
domain = argv[1]
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
    if data:
        print(data["content"])
        print(submitter.submit(domain, password, data["content"]))

# And it's as easy as that.
# No. It really isn't