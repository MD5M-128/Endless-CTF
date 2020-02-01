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

class InvalidIPError(Exception):
    pass

class socket:
    def __init__(self, ws_addr=("localhost", 8765)):
        self._kill = False
        self.ip = ipv4_to_num("127.0.1.1")
        self.port = 1
        self._to_send = []
        self._to_recv = []
        self._bound_to = ("0.0.0.0", -1)
        SOCKETS.add(self)

        def on_message(ws, message):
            try:
                msg = json.loads(message)
                if (msg["ip"] == self._bound_to[0] or self._bound_to[0] == "0.0.0.0") and (msg["port"] == self._bound_to[1] or self._bound_to[1] == -1):
                    if valid_ip_num(msg["ip"]):
                        self._to_recv.append()
                    else:
                        print("Bound IP invalid!")
            except json.decoder.JSONDecodeError:
                print("Invalid JSON data sent!")

        def on_error(ws, error):
            raise error

        def on_close(ws):
            self._kill = True
            del self

        def on_open(ws):
            while True:
                if self._kill: break
                if len(self._to_send) > 0:
                    ws.send(json.dumps(self._to_send[0]))
                    self._to_send.pop(0)
            ws.close()
            

        #websocket.enableTrace(True)
        ws = websocket.WebSocketApp("ws://" + ws_addr[0] + ":" + str(ws_addr[1]) + "/",
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)
        ws.on_open = on_open
        self._handle_thread = threading.Thread(target=ws.run_forever, args=[], daemon=True)
        self._handle_thread.start()
    
    def __del__(self):
        #print("Dead!")
        self._kill = True
    
    def sendto(self, message, addr):
        msg = {
            "type": "packet",
            "fromIp": self.ip,
            "fromPort": self.port,
            "ip": ipv4_to_num(addr[0]),
            "port": addr[1],
            "content": message
        }
        self._to_send.append(msg)
    
    def close(self):
        self._kill = True

    def dns_login(self, name, password):
        msg = {
            "type": "dns_login",
            "name": name,
            "password": password
        }
        self._to_send.append(msg)
    def dns_logout(self, name, password):
        msg = {
            "type": "dns_logout",
            "name": name,
            "password": password
        }
        self._to_send.append(msg)