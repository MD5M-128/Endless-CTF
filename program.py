import fake_socket as socket
from sys import argv

password = argv[1]
payload = argv[2]
domain = "waktins.com"
serve = "sender"

s = socket.socket()

response = s.dns_login(serve, domain, password)
if response["type"] != "dns_login":
    # TODO: Find out why, then try again
    exit(0)

endpoint = s.dns_lookup("receiver.watkins.com")
if response["type"] != "dns_result":
    # TODO: Find out why, then try again
    exit(0)

ip = endpoint["ip"] # SERIOUS: Make fake_socket return string IP addresses in all cases
s.sendto(payload, ip)

# And it's as easy as that.
# No. It really isn't