import subprocess, shlex
from subprocess import PIPE

from typing import NamedTuple, IO, Any, List, Optional

from basic_cli_api import CommandResults, run_command, run_pipeline
#### Parse Tools ###################################################
def colapse_spaces(text: str) -> str:
    while '  ' in text: # while 'double space' in text
        text = text.replace('  ', ' ') # replace('double-space', 'single-space')
    return text


########## PS parse #############################


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

def find_and_kill() -> None:
    search_criteria = input('WHAT TYPE OF PROCESS TO SEARCH FOR? ')
    results = run_pipeline(['ps aux', f'grep {search_criteria} '])
    parsed_results: List[PSLineData] = parse_ps_data(results.stdout)

    print('================')
    for num, parsed_line_data in enumerate(parsed_results):
        print(f'{num}) {parsed_line_data}')
    to_kill = int(input('WHO DO YOU WANT TO KILL?'))
    run_command(f'kill {parsed_results[to_kill].pid}')

##########################################
########## Parse Ping ####################
class PingData(NamedTuple):
    original_host: str
    host_ip: str
    single_pings: List['SinglePingData']
    packets_transmitted: int
    packets_received: int
    percent_packet_loss: float
    time: int
    rtt_min: float
    rtt_avg: float
    rtt_max: float
    rtt_mdev: float
    error_message: str

def parse_ping_data(ping_stdout: str, ping_stderr: str) -> PingData:
    original_host: str = None
    host_ip: str = None
    single_pings: List['SinglePingData'] = []
    packets_transmitted: int = None
    packets_received: int = None
    percent_packet_loss: float = None
    time: int = None
    rtt_min: float = None
    rtt_avg: float = None
    rtt_max: float = None
    rtt_mdev: float = None
    error_message: str = None

    ping_lines = ping_stdout.split('\n')
    for line in ping_lines:
        line_data = line.split(' ')
        if 'bytes from' in line:
            single_pings.append(parse_single_ping_data(line))
        elif 'PING' in line:
            original_host = line_data[1]
            host_ip = line_data[2][1:-2]
        elif 'packets transmitted' in line:
            packets_transmitted = int(line_data[0])
            packets_recieved = int(line_data[3])
            print(line_data[5][:-1])
            percent_packet_loss = float(line_data[5][:-1])
            time = int(line_data[9][:-3])
        elif 'rtt' in line:
            rtt_stat_data = line_data[3].split('/')
            rtt_min = float(rtt_stat_data[0])
            rtt_avg = float(rtt_stat_data[1])
            rtt_max = float(rtt_stat_data[2])
            rtt_mdev = float(rtt_stat_data[3])

    ping_error_lines = ping_stderr.split('\n')
    print(ping_error_lines)
    for line in ping_error_lines:
        ping_error_line_data = line.split(' ')
        if 'ping:' in line:
            original_host = ping_error_line_data[1][:-1]
            error_message = " ".join(ping_error_line_data[2:])
        elif 'connect' in line:
            error_message = ' '.join(ping_error_line_data[1:])


    return PingData(original_host, host_ip,
                    single_pings,
                    packets_transmitted, packets_received, percent_packet_loss, time,
                    rtt_min, rtt_avg, rtt_max, rtt_mdev,
                    error_message)




class SinglePingData(NamedTuple):
    ip_address: str
    reverse_dns: str
    round_trip_time: int

    def __str__(self) -> str:
        return f'Ping({self.ip_address}, {self.reverse_dns}, {self.round_trip_time})'

def parse_single_ping_data(ping_output: str) -> SinglePingData:
    line_data = ping_output.split(' ')
    ip = None
    reverse_dns = None
    round_trip_time = None

    #print(line_data)
    if '(' in line_data[4]:
        ip = line_data[4][1:-2]
        reverse_dns = line_data[3]
    else:
        ip = line_data[3]
    round_trip_time = line_data[-2].split('=')[1]

    return SinglePingData(ip, reverse_dns, round_trip_time)



def is_it_up(host: str) -> None:
    results = run_command(f'ping -c 2 {host}')
    print(results)
    print(parse_ping_data(results.stdout, results.stderr))







###########################################
if __name__ == '__main__':
    #find_and_kill()
    #is_it_up('10.10.1.1')
    #is_it_up('google.com')
    #is_it_up('teach.mapnwea.org')

    is_it_up('10.10.1.3')
    #is_it_up('copier6')
