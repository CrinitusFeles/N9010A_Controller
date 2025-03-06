
import asyncio
from n9010a_controller.n9010a_api import N9010A_API
from python_tcp.aio.client import SocketClient

def on_received(data):
    print(data)

async def main():
    client = SocketClient('10.2.63.45', 5025)
    await client.connect()
    client.received.subscribe(on_received)
    cmd = N9010A_API.get_center_freq()
    await client.send(cmd)
    await asyncio.sleep(2)
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
