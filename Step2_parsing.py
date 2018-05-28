import subprocess, shlex
from subprocess import PIPE

from typing import NamedTuple, IO, Any, List, Optional

from basic_cli_api import CommandResults, run_command, run_pipeline

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
