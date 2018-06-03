import subprocess
from subprocess import PIPE
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

def run(command: str, stdin: Optional[str] = None, encoding: str = 'utf-8') -> CommandResults:
    command = command.strip()
    if '|' in command:
        return _run_pipeline(command.split('|'))
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


if __name__ == '__main__':
    print(run('ls'))
    print(run('ls -la'))
    print(run('ping -c 1 google.com'))
    print(run('ps aux | grep "python"'))
