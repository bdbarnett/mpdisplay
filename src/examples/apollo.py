import gc

gc.collect()
mem = gc.mem_free()
print(f"Free memory at start: {mem:,}")

import apollo_dsk as dsk
from time import localtime
import asyncio
from sys import implementation


show_mem = True if implementation.name == "micropython" else False

last_time = (0, 0, 0, 0, 0, 0)
async def write_time():
    global last_time
    y, mo, d, h, m, s, *_ = localtime()
    if s != last_time[5]:
        dsk.write_string(f"{h:02}:{m:02}:{s:02}", dsk.data2_pos)
        if (y, mo, d) != last_time[:3]:
            dsk.write_string(f"{y-2000:02}.{mo:02}.{d:02}", dsk.data1_pos)
        last_time = (y, mo, d, h, m, s)
        gc.collect()
        if show_mem:
            dsk.write_string(f"{mem-gc.mem_free():7}", dsk.data3_pos)

async def main():
    dsk.init_screen()

    dsk.write_string("42", dsk.prog_pos)
    dsk.write_string("01", dsk.verb_pos)
    dsk.write_string("23", dsk.noun_pos)

    while True:
        await asyncio.sleep(0)
        await write_time()
        if (key := dsk.keypad.read()) is not None:
            dsk.set_acty(True)
            dsk.set_button(key, True)

            if key < len(dsk.light_status):
                dsk.set_light(key)

            await asyncio.sleep(0.2)
            dsk.set_button(key, False)
            dsk.set_acty(False)


loop = asyncio.get_event_loop()
task = loop.create_task(main())
if hasattr(loop, "is_running") and loop.is_running():
    pass
else:
    if hasattr(loop, "run_forever"):
        loop.run_forever()
