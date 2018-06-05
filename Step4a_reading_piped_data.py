import sys
import select
from typing import List, TextIO, NamedTuple, Tuple

class ReadySelected(NamedTuple):
    ready_reads: List[TextIO]
    ready_writes: List[TextIO]
    ready_exceptional: List[TextIO]

def my_select(read_list: List[TextIO]=[],
              write_list: List[TextIO]=[],
              exceptional_condition_list: List[TextIO]=[],
              time_out: int = 0) -> ReadySelected:
    return ReadySelected(*select.select(read_list, write_list, exceptional_condition_list, time_out))

def stringify_stdin() -> str:
    stdin = ''
    while sys.stdin in my_select(read_list=[sys.stdin]).ready_reads:
        line = sys.stdin.readline()
        if line:
            stdin += line
        else: # an empty line means stdin has been closed
            break
    return stdin

def list_stdin() -> None:
    for number, line in enumerate(STDIN.rstrip('\n').split('\n')):
        line = line.rstrip('\n')
        print(f'{number}) {line}')


if __name__ == '__main__':
    STDIN = stringify_stdin()
    list_stdin()
