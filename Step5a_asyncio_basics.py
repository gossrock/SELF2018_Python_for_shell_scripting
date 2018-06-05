import asyncio
import time


async def thing_to_run(thing:str, duration: float) -> None:
    start_time = round(time.time())
    await asyncio.sleep(0)
    while True:
        time_after_start = round(time.time()) - start_time
        print(f'{time_after_start}: {thing}')
        await asyncio.sleep(duration)





if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(thing_to_run('Larry', 2))
    asyncio.ensure_future(thing_to_run('Moe', 3))
    asyncio.ensure_future(thing_to_run('Curly', 5))
    loop.run_forever()
