import asyncio
from run_commands import CommandResults, async_run
from typing import List

async def run_manager(tasks: List[asyncio.futures.Future]) -> None:
    while len(tasks) > 0:
        await asyncio.sleep(0.1)
        print(len(tasks))
        for task in tasks:
            if task.done():
                print(task.result())
                tasks.remove(task)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    reveal_type(loop)
    task1 = asyncio.ensure_future(async_run('ping -c 4 localhost'))
    task2 = asyncio.ensure_future(async_run('ping -c 2 127.0.0.1'))
    task3 = asyncio.ensure_future(async_run('ping -c 1 9.9.9.9'))
    task4 = asyncio.ensure_future(async_run('ps aux | grep python'))
    loop.run_until_complete(run_manager([task1, task2, task3, task4]))
