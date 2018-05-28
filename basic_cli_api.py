import subprocess
from subprocess import PIPE
import shlex
from typing import NamedTuple, Optional, List

class CommandResults(NamedTuple):
    command: str
    return_code: int
    stdout: str
    stderr: str

def run_command(command: str, stdin: Optional[str] = None, encoding: str = 'utf-8') -> CommandResults:
    if stdin == None:
        process = subprocess.Popen(shlex.split(command), stdout=PIPE, stderr=PIPE, encoding=encoding)
        stdout, stderr = process.communicate()
    else:
        process = subprocess.Popen(shlex.split(command), stdin=PIPE, stdout=PIPE, stderr=PIPE, encoding=encoding)
        stdout, stderr = process.communicate(stdin)
    return_code = process.wait()
    return CommandResults(command, return_code, stdout, stderr)

def run_pipeline(commands: List[str], encoding: str = 'utf-8') -> CommandResults:
    command_results = run_command(commands[0], encoding=encoding)
    for command in commands[1:]:
        command_results = run_command(command, stdin=command_results.stdout, encoding=encoding)
    return command_results
