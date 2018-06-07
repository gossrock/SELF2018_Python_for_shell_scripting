import asyncio
import time
import random
from typing import List, Any, Tuple


async def thing_to_run(thing:str, duration: float, give_up_number: int) -> Tuple[str,int]:
    await asyncio.sleep(0)
    start_time = round(time.time())
    number_of_calls = 0
    while True:
        time_after_start = round(time.time()) - start_time
        print(f'{time_after_start}: {thing}({duration},{give_up_number})')
        number_of_calls += 1
        if time_after_start >= give_up_number:
            return (thing, number_of_calls)
        await asyncio.sleep(duration)

async def manager(loop: asyncio.AbstractEventLoop, total_tasks: int = 10, max_simultanious: int = 3) -> None:
    await asyncio.sleep(0)
    task_list: List[asyncio.Future] = []
    tasks_created = 0
    while tasks_created < total_tasks:
        while len(task_list) < max_simultanious:
            await asyncio.sleep(0)
            tasks_created += 1
            new_task_number = tasks_created
            task_name = f'Thing {new_task_number}'
            duration = random.randint(1, 3)
            give_up_number = random.randint(3, 9)
            task = asyncio.ensure_future(thing_to_run(f'Thing {new_task_number}', duration, give_up_number), loop=loop)
            task_list.append(task)


        await task_finisher(task_list)
        await asyncio.sleep(0.1)

    while len(task_list) > 0:
        await task_finisher(task_list)
        await asyncio.sleep(0.1)

    print('done')

async def task_finisher(task_list: List[asyncio.Future]) -> None:
    for task in task_list:
        if task.done():
            await asyncio.sleep(0)
            result = task.result()
            print(f'task_finished: {result}')
            task_list.remove(task)





if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    loop.run_until_complete(manager(loop))
