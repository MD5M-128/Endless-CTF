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

class socket:
    def __init__(self, ws_addr=("localhost", 8765)):
        self._kill = False
        self.ip = "127.0.1.1"
        self.port = 1
        self._to_send = []
        SOCKETS.add(self)

        def on_message(ws, message):
            print(message)

        def on_error(ws, error):
            print(error)

        def on_close(ws):
            print("### closed ###")

        def on_open(ws):
            def run(*args):
                while True:
                    if self._kill: break
                    if len(self._to_send) > 0:
                        print(self._to_send[0])
                        ws.send(json.dumps(self._to_send[0]))
                        self._to_send.pop(0)
                ws.close()
                print("thread terminating...")
            run()
            

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
            "ip": addr[0],
            "port": addr[1],
            "content": message
        }
        self._to_send.append(msg)