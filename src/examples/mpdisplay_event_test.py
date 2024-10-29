from board_config import broker
from pydevices import Events
import asyncio


async def main():
    while True:
        e = broker.poll()
        if e:
            print(e)
            if e == Events.QUIT:
                break
        await asyncio.sleep(0.001)

loop = asyncio.get_event_loop()
loop.create_task(main())
if hasattr(loop, "run_forever"):
    loop.run_forever()
