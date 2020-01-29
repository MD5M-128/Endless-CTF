import time
import json
import asyncio
import websockets

async def network(ws, path):
    async for msg in ws:
        try:
            json_msg = json.loads(msg)
        except:
            print("Invalid JSON received.")
            return
        
        print(f"< {msg}")

        new_packet = {
            "time": int(time.time()),
            "content": json_msg["content"],
            "fromIp": ws.remote_address[0],
            "toIp": json_msg["ip"],
            "fromPort": ws.remote_address[1],
            "toPort": json_msg["port"]
        }

        str_pack = json.dumps(new_packet)
        await ws.send(str_pack)
        print(f"> {str_pack}")

start_server = websockets.serve(network, "0.0.0.0", 8765)

print("Starting websockets now...")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()