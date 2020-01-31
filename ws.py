import time
import json
import asyncio
import websockets

import logging
logger = logging.getLogger('websockets')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

CONNECTED = set()

async def network(ws, path):
    CONNECTED.add(ws)
    print(ws.remote_address[0] + ":" + str(ws.remote_address[1]) + " connected.")
    try:
        async for msg in ws:
            print("Message received from " + ws.remote_address[0] + ":" + str(ws.remote_address[1]))
            try:
                json_msg = json.loads(msg)
            except:
                print("Invalid JSON received.")
                return
            
            print(f"< {msg}")

            if "type" in json_msg:
                if json_msg["type"] == "packet":
                    new_packet = {
                        "time": int(time.time()),
                        "content": json_msg["content"],
                        "fromIp": ws.remote_address[0],
                        "toIp": json_msg["ip"],
                        "fromPort": ws.remote_address[1],
                        "toPort": json_msg["port"]
                    }

                    str_pack = json.dumps(new_packet)
                    await asyncio.wait([ws.send(str_pack) for ws in CONNECTED])

    finally:
        print(ws.remote_address[0] + ":" + str(ws.remote_address[1]) + " disconnected.")
        CONNECTED.remove(ws)

start_server = websockets.serve(network, "0.0.0.0", 8765)

print("Starting websockets now...")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()