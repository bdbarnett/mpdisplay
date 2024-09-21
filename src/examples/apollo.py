import gc
try:
    # For CircuitPython and MicroPython
    from gc import mem_free
except ImportError:
    # For CPython
    from psutil import virtual_memory
    def mem_free():
        return virtual_memory().free

gc.collect()
mem = mem_free()
print(f"Free memory at start: {mem:,}")

import apollo_dsk as dsk  # noqa: E402
import time  # noqa: E402
import asyncio  # noqa: E402


last_time = (0, 0, 0, 0, 0, 0)
async def write_time():
    global last_time
    y, mo, d, h, m, s, *_ = time.localtime()
    if s != last_time[5]:
        dsk.write_string(f"{h:02}:{m:02}:{s:02}", dsk.data2_pos)
        if (y, mo, d) != last_time[:3]:
            dsk.write_string(f"{y-2000:02}.{mo:02}.{d:02}", dsk.data1_pos)
        last_time = (y, mo, d, h, m, s)
        gc.collect()
        dsk.write_string(f"{mem-mem_free():7}", dsk.data3_pos)

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
