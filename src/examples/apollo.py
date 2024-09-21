
import apollo_dsk as dsk
from time import localtime
import asyncio


async def main():
    
    last_time = (0, 0, 0, 0, 0, 0)
    def write_time():
        nonlocal last_time
        y, mo, d, h, m, s, *_ = localtime()
        if (y, mo, d) != last_time[:3]:
            dsk.write_string(f"{y-2000:02}.{mo:02}.{d:02}", dsk.data1_pos)
        if (h, m, s) != last_time[3:]:
            dsk.write_string(f"{h:02}:{m:02}:{s:02}", dsk.data2_pos)
            last_time = (y, mo, d, h, m, s)

    dsk.init_screen()

    dsk.write_string("PR", dsk.prog_pos)
    dsk.write_string("OS", dsk.verb_pos)
    dsk.write_string("NO", dsk.noun_pos)

    dsk.write_string("-987,654", dsk.data3_pos)

    while True:
        await asyncio.sleep(0)
        write_time()
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
