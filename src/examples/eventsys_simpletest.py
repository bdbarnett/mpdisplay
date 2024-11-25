from board_config import broker
import asyncio


async def main():
    while True:
        e = broker.poll()
        if e:
            print(e)
            if e == broker.Events.QUIT:
                break
        await asyncio.sleep(0.001)


loop = asyncio.get_event_loop()
main_task = loop.create_task(main())  # noqa: RUF006
if hasattr(loop, "run_forever"):
    loop.run_forever()
