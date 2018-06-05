#from typing import NamedTuple, List, Dict
from typing import Dict, List
import asyncio
import shlex
import statistics
import shutil
import argparse

DATABASE: Dict[str, List[float]] = {}

def add_host_to_database(host:str) -> None:
    DATABASE[host] = []

def add_to_database(host:str, round_trip_time: float) -> None:
    if host not in DATABASE.keys():
        add_host_to_database(host)
    DATABASE[host].append(round_trip_time)


async def ping(host: str) -> None:
    await asyncio.sleep(0)
    add_host_to_database(host)
    process = await asyncio.create_subprocess_exec(*shlex.split(f'ping {host}'), stdout=asyncio.subprocess.PIPE)
    while True:
        if process.stdout is not None:
            output_bytes = await process.stdout.readline()
            output = output_bytes.decode('utf-8')
            if 'bytes from' in output:
                round_trip_time = float(output.strip().split(' ')[-2].split('=')[1])
                #print(round_trip_time)
                add_to_database(host, round_trip_time)
                #print(DATABASE)
        await asyncio.sleep(0.1)


async def display_data() -> None:
    print('waiting for data ...')
    await asyncio.sleep(3)
    max_len_url = 0
    print('\033[F'+' '*80, end='')
    while True:
        print(f'\r', end='')
        for host in DATABASE.keys():
            if len(host) > max_len_url:
                max_len_url = len(host)
            if len(DATABASE.keys()) > 0:
                data = DATABASE[host]
                sent = len(data)

                mean = 0.0
                Min = 0.0
                Max = 0.0
                if len(data) is not 0:
                    mean = round(statistics.mean(data), 3)
                    Min = min(data)
                    Max = max(data)

                stdev = 0.0
                if len(data)>=2:
                    stdev = round(statistics.stdev(data), 3)
                url_extra_spaces = ' '*(max_len_url - len(host))
                most_recent_ping = -1.0
                if len(DATABASE[host]) > 0:
                    most_recent_ping = DATABASE[host][-1]
                output = f'{host}{url_extra_spaces}:  {most_recent_ping}\t({sent}\t{mean}/{stdev}\t{Min}/{Max})'

                print(output)

        await asyncio.sleep(1)
        terminal_size = shutil.get_terminal_size((80, 20))
        for _ in DATABASE.keys():
            print('\033[F'+' '*terminal_size.columns, end='')



def ParseCLIArgs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='ping multiple host simultaniously.')
    parser.add_argument("hosts", nargs='+', help='hosts to ping')
    return parser.parse_args()




if __name__ == '__main__':
    args = ParseCLIArgs()

    loop = asyncio.get_event_loop()

    for host in args.hosts:
        asyncio.ensure_future(ping(host))

    asyncio.ensure_future(display_data())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('\nbye')
