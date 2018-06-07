import asyncio
from run_commands import CommandResults, AsyncCommandRunner
from typing import List




async def manager(hosts_to_ping: List[str], loop: asyncio.AbstractEventLoop) -> None:
    runners: List[AsyncCommandRunner] = []
    for host in hosts_to_ping:
        runner = AsyncCommandRunner(loop, f'ping -c 10 {host}')
        runner.go()
        runners.append(runner)




if __name__ == '__main__':
    loop = asyncio.get_event_loop()
