import subprocess, shlex
from subprocess import PIPE

from typing import NamedTuple, IO, Any, List, Optional

######### COMAND LINE API ##############
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

##############################################

########## PS parse #############################
def colapse_spaces(text: str) -> str:
    while '  ' in text: # while 'double space' in text
        text = text.replace('  ', ' ') # replace('double-space', 'single-space')
    return text

class PSLineData(NamedTuple):
    pid: str
    command: str
    def __str__(self) -> str:
        return f"COMMAND: '{self.command}'"


def parse_ps_data(ps_output: str) -> List[PSLineData]:
    parsed_results: List[PSLineData] = []
    for line in ps_output.split('\n'):
        if "USER" not in line and line is not '':
            parsed_results.append( parse_ps_line_data(line))
    return parsed_results


def parse_ps_line_data(ps_line: str) -> PSLineData:
    line_data = colapse_spaces(ps_line).split(' ')
    pid = line_data[1]
    command = ' '.join(line_data[10:])
    return PSLineData(pid, command)


##########################################

if __name__ == '__main__':
    search_criteria = input('WHAT TYPE OF PROCESS TO SEARCH FOR? ')
    results = run_pipeline(['ps aux', f'grep {search_criteria} '])
    parsed_results: List[PSLineData] = parse_ps_data(results.stdout)

    print('================')
    for num, parsed_line_data in enumerate(parsed_results):
        print(f'{num}) {parsed_line_data}')
    to_kill = int(input('WHO DO YOU WANT TO KILL?'))
    run_command(f'kill {parsed_results[to_kill].pid}')
