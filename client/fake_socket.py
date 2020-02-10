import sys
import time
import json
import atexit
import asyncio
import threading
import websocket

SOCKETS = set()

def _exit_handler():
    for i in SOCKETS: i.__del__()

atexit.register(_exit_handler)

def ipv4_to_num(ip):
    s = 0
    p = 3
    if len(splt := ip.split(".")) == 4:
        for i in splt:
            if 0 <= (n := int(i)) <= 255:
                s += n * 256 ** p
                p -= 1
            else:
                raise InvalidIPError("Each part of an IPv4 address must be between 0 and 255.")
    else:
        raise InvalidIPError("An IPv4 address may only have 4 parts")
    return s
def num_to_ipv4(num):
    parts = []
    for i in range(3, -1, -1):
        parts.append(str(num >> (i * 8) & 255))
    return ".".join(parts)
def valid_ip_ipv4(ip):
    try:
        ipv4_to_num(ip)
        return True
    except InvalidIPError:
        return False
def valid_ip_num(num):
    try:
        ipv4_to_num(num_to_ipv4(num))
        return True
    except InvalidIPError:
        return False


if len(sys.argv) > 3:
    IP = sys.argv[3]
else:
    house = sys.argv[1]
    if house == "carnley.com": IP = "10.0.0.7"
    elif house == "challen.com": IP = "10.1.0.7"
    elif house == "moyes.com": IP = "10.2.0.7"
    elif house == "watkins.com": IP = "10.3.0.7"
#IP = ipv4_to_num(IP)


class InvalidIPError(Exception):
    pass

class socket:
    def __init__(self, ws_addr=("localhost", 8765)):
        self._kill = False
        self.ip = IP
        self.port = 1
        self._to_send = []
        self._to_recv = []
        self._dns_queue = []
        self._bound_to = (ipv4_to_num(self.ip), -1)
        SOCKETS.add(self)

        def on_message(ws, message):
            try:
                msg = json.loads(message)
                #print("Arrived here")
                if msg["type"] == "packet":
                    #print("And here")
                    if (msg["ip"] == self._bound_to[0] or self._bound_to[0] == 0) and (msg["port"] == self._bound_to[1] or self._bound_to[1] == -1):
                        #print("Even here!")
                        if valid_ip_num(msg["ip"]):
                            #print("We'll carry on, we'll carry on...")
                            self._to_recv.append(msg)                       # Can we just ask how I forgot to put an argument here?
                        else:
                            print("Bound IP invalid!")
                elif msg["type"].startswith("dns_"):
                    self._dns_queue.append(msg)
            except json.decoder.JSONDecodeError:
                print("Invalid JSON data sent!")
            except Exception as e:
                self._last_error = e
                raise e                 # Doesn't usually work

        def on_error(ws, error):
            raise error

        def on_close(ws):
            self._kill = True
            del self

        def on_open(ws):
            def run():
                while True:
                    if self._kill: break
                    if len(self._to_send) > 0:
                        ws.send(json.dumps(self._to_send[0]))
                        self._to_send.pop(0)
                ws.close()
            self._second_thread = threading.Thread(target=run, args=[], daemon=True)
            self._second_thread.start()
            

        #websocket.enableTrace(True)
        ws = websocket.WebSocketApp("ws://" + ws_addr[0] + ":" + str(ws_addr[1]) + "/",
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)
        ws.on_open = on_open
        self._handle_thread = threading.Thread(target=ws.run_forever, args=[], daemon=True)
        self._handle_thread.start()
    
    #def raiser(self):
    #    raise self._last_error

    def __del__(self):
        #print("Dead!")
        self._kill = True
    
    def sendto(self, message, addr):
        msg = {
            "type": "packet",
            "fromIp": ipv4_to_num(self.ip),
            "fromPort": self.port,
            "ip": ipv4_to_num(addr[0]),
            "port": addr[1],
            "content": message
        }
        self._to_send.append(msg)
    
    def recv(self):
        return self._to_recv.pop(0) if self._to_recv else None
    
    def close(self):
        self._kill = True

    def dns_login(self, server, domain, password):
        msg = {
            "type": "dns_login",
            "server": server,
            "domain": domain,
            "password": password,
            "ip": ipv4_to_num(self.ip)
        }
        dnss = len(self._dns_queue)
        self._to_send.append(msg)
        while True:
            if len(self._dns_queue) > dnss:
                for i in self._dns_queue:
                    if i["type"] == "dns_login" or i["type"] == "dns_notregistered" or i["type"] == "dns_badpassword":
                        self._dns_queue.remove(i)
                        if i["type"] == "dns_login":
                            i["ip"] = num_to_ipv4(i["ip"])
                        return i
    def dns_logout(self, server, domain, password):
        msg = {
            "type": "dns_logout",
            "server": server,
            "domain": domain,
            "password": password
        }
        dnss = len(self._dns_queue)
        self._to_send.append(msg)
        while True:
            if len(self._dns_queue) > dnss:
                for i in self._dns_queue:
                    if i["type"] == "dns_logout" or i["type"] == "dns_notloggedin" or i["type"] == "dns_badpassword":
                        self._dns_queue.remove(i)
                        return i
    def dns_lookup(self, name):
        msg = {
            "type": "dns_lookup",
            "name": name
        }
        dnss = len(self._dns_queue)
        self._to_send.append(msg)
        while True:
            if len(self._dns_queue) > dnss:
                for i in self._dns_queue:
                    if i["type"] == "dns_result" or i["type"] == "dns_notfound":
                        self._dns_queue.remove(i)
                        if i["type"] == "dns_result":
                            i["ip"] = num_to_ipv4(i["ip"])
                        return i
    def dns_all(self):
        msg = {
            "type": "dns_all"
        }
        dnss = len(self._dns_queue)
        self._to_send.append(msg)
        while True:
            if len(self._dns_queue) > dnss:
                for i in self._dns_queue:
                    if i["type"] == "dns_all":
                        self._dns_queue.remove(i)
                        for j in i["entries"]:
                            j["ip"] = num_to_ipv4(j["ip"])
                        return i["entries"]
    
    def wait_for_send(self):
        while self._to_send: pass