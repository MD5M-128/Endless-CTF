import fake_socket as socket
from sys import argv

password = argv[1]
payload = argv[2]
domain = "watkins.com"
serve = "sender"

s = socket.socket()

if s.dns_lookup(serve + "." + domain)["type"] == "dns_notfound":
    print("Logging in to DNS...")
    response = s.dns_login(serve, domain, password)
    if response["type"] != "dns_login":
        print("DNS Login error")
        # TODO: Find out why, then try again
        exit(0)

print("Looking up receiver server...")
endpoint = s.dns_lookup("receiver.watkins.com")
if endpoint["type"] != "dns_result":
    print("DNS Lookup error.")
    # TODO: Find out why, then try again
    exit(0)

ip = endpoint["ip"]
print("Sending...")
s.sendto(payload, (ip, 65535))

# And it's as easy as that.
# No. It really isn't