import time
import json
import asyncio
import threading
import websockets

class socket:
    def __init__(self, ws_addr=("localhost", 8765)):
        def _do_handler(ws_addr):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.handler(ws_addr))
            loop.close()
        self._kill = False
        self._handle_thread = threading.Thread(target=_do_handler, args=[ws_addr])
        self._handle_thread.start()
        self.ip = "127.0.1.1"
        self.port = 1
        self._to_send = []
    
    def __del__(self):
        self._kill = True
    
    def sendto(self, message, addr):
        msg = {
            "fromIp": self.ip,
            "fromPort": self.port,
            "ip": addr[0],
            "port": addr[1],
            "content": message
        }
        self._to_send.append(msg)

    async def _sendto(self, message, addr):
        msg = {
            "fromIp": self.ip,
            "fromPort": self.port,
            "ip": addr[0],
            "port": addr[1],
            "content": message
        }
        await self.ws.send(json.dumps(msg))
    
    async def handler(self, addr):
        uri = "ws://" + addr[0] + ":" + str(addr[1])
        async with websockets.connect(uri) as websocket:
            while True:
                if self._kill: break
                if len(self._to_send) > 0:
                    print(self._to_send[0])
                    await websocket.send(self._to_send[0])
                    self._to_send.pop(0)
            """
            #<<<<self.ws = await websockets.connect(uri)
            self.ws = websocket
            #consumer_task = asyncio.ensure_future(
            #    self.consumer_handler(websocket))
            producer_task = asyncio.ensure_future(
                self.producer_handler(websocket))
            done, pending = await asyncio.wait(
                #[consumer_task, producer_task],
                [producer_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            for task in pending:
                task.cancel()
            """
    
    async def consumer_handler(self, ws):
        while True:
            pass
    async def producer_handler(self, ws):
        while True:
            if len(self._to_send) > 0:
                await ws.send(self._to_send[0])
                self._to_send.pop(0)