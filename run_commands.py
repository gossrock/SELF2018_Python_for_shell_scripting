import subprocess, asyncio
from subprocess import PIPE
from asyncio.subprocess import PIPE as aPIPE
import shlex
from typing import NamedTuple, Optional, List

class CommandResults(NamedTuple):
    command: Optional[str]
    return_code: Optional[int]
    stdout: Optional[str]
    stderr: Optional[str]

    def __str__(self) -> str:
        output = 'COMMAND\n'
        output += f'{self.command}\n'

        output += '\nRETURN CODE\n'
        output += f'{self.return_code}\n'

        output += '\nSTDOUT\n'
        output += f'{self.stdout}\n'

        output += '\nSTDERR\n'
        output += f'{self.stderr}\n'

        return output

BLANK_RESULTS = CommandResults(None, None, None, None)

##### STANDARD / SYNCRONOUS #####

def run(command: str, stdin: Optional[str] = None, encoding: str = 'utf-8') -> CommandResults:
    command = command.strip()
    if '|' in command:
        return _run_pipeline(command.split('|')) # Probobly not the best aproach
    else:
        process = subprocess.Popen(shlex.split(command), stdin=PIPE, stdout=PIPE, stderr=PIPE, encoding=encoding)
        stdout, stderr = process.communicate(stdin)
        return_code = process.wait()
        return CommandResults(command, return_code, stdout, stderr)

def _run_pipeline(commands: List[str], stdin: Optional[str] = None, encoding: str = 'utf-8') -> CommandResults:
    command_results = BLANK_RESULTS
    for command in commands:
        command_results = run(command, stdin=stdin, encoding=encoding)
        stdin = command_results.stdout
    return command_results

##### ASYNCRONOUS (RESULTS AFTER) #####

async def async_run(command: str, stdin: Optional[str] = None, encoding: str = 'utf-8') -> CommandResults:
    command = command.strip()
    if '|' in command:
        return await _async_run_pipeline(command.split('|'))
    else:
        process = await asyncio.create_subprocess_exec(*shlex.split(command),stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        if stdin is not None:
            stdout_bytes, stderr_bytes = await process.communicate(stdin.encode(encoding))
        else:
            stdout_bytes, stderr_bytes = await process.communicate()
        stdout = stdout_bytes.decode(encoding)
        stderr = stderr_bytes.decode(encoding)
        return_code = await process.wait()
        return CommandResults(command, return_code, stdout, stderr)

async def _async_run_pipeline(commands: List[str], stdin:Optional[str] = None, encoding: str = 'utf-8') -> CommandResults:
    command_results = BLANK_RESULTS
    for command in commands:
        command_results = await async_run(command, stdin=stdin, encoding=encoding)
        stdin = command_results.stdout
    return command_results



##### ASYNCRONOUS (RESULTS DURING) #####
class AsyncCommandRunner:
    loop: asyncio.events.AbstractEventLoop
    command: str
    sub_commands: Optional[List[str]]
    started: bool = False
    ended: bool = False
    stdin: Optional[str]
    encoding: str
    process: asyncio.subprocess.Process
    stdout: str
    stderr: str
    return_code: int

    def __init__(self, loop:asyncio.AbstractEventLoop, command: str, stdin: Optional[str] = None, encoding: str = 'utf-8') -> None:
        self.loop = loop
        self.command = command.strip()
        if '|' in self.command:
            self.sub_commands = self.command.split('|')
        else:
            self.sub_commands = None
        self.stdin = stdin
        self.encoding = encoding
        self.stdout = ''
        self.stderr = ''
        return_code = 0
        results: CommandResults = BLANK_RESULTS


    async def go(self) -> CommandResults:
        self.started = False
        self.ended = False
        stdin = self.stdin
        previous_commands_results = None
        if self.sub_commands is not None and len(self.sub_commands)>1:
            previous_commands_results = await _async_run_pipeline(self.sub_commands[:-1], stdin=stdin, encoding=self.encoding)
            stdin = previous_commands_results.stdout

        command = self.command
        if self.sub_commands is not None:
            command = self.sub_commands[-1:][0]

        self.started = True
        self.process = await asyncio.create_subprocess_exec(*shlex.split(command),stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        self.returncode = await self.process.wait()

        if self.stdin is not None:
            stdout_bytes, stderr_bytes = await self.process.communicate(self.stdin.encode(self.encoding))
        else:
            stdout_bytes, stderr_bytes = await self.process.communicate()
        self.ended = True
        self.stdout += stdout_bytes.decode(self.encoding)
        self.stderr += stderr_bytes.decode(self.encoding)
        self.results =  CommandResults(self.command, self.return_code, self.stdout, self.stderr)
        return self.results

    async def readline(self) -> Optional[str]:
        next_line_bytes = None
        if self.process.stdout is not None:
            next_line_bytes = await self.process.stdout.readline()
            next_line = next_line_bytes.decode(self.encoding)
            self.stdout += next_line
        return next_line
