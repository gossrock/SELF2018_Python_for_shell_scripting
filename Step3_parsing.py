import subprocess, shlex
from subprocess import PIPE

from typing import NamedTuple, IO, Any, List, Optional

from run_commands import CommandResults, run
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
        return f"'{self.command}'"

def parse_ps_data(ps_output: str) -> List[PSLineData]:
    parsed_results: List[PSLineData] = []
    for line in ps_output.split('\n'):
        if line is not ''  and line[0:3] is not "USER":
            parsed_results.append( parse_ps_line_data(line))
    return parsed_results

def parse_ps_line_data(ps_line: str) -> PSLineData:
    # prez      4649  0.3  0.0  36868  9152 pts/2    S+   12:44   0:00 python3 ./infinate_loop_to_kill.py
    line_data = colapse_spaces(ps_line).split(' ')
    pid = line_data[1] # second item in list is the process id
    command = ' '.join(line_data[10:]) # the command starts on item index 10 and following
    return PSLineData(pid, command)

def find_and_kill() -> None:
    search_criteria = input('WHAT TYPE OF PROCESS SHOULD I SEARCH FOR? ')
    results = run(f'ps aux | grep {search_criteria}')
    parsed_results: List[PSLineData] = []
    if results.stdout is not None:
        parsed_results = parse_ps_data(results.stdout)

    print('================')
    if len(parsed_results) > 0:
        for num, parsed_line_data in enumerate(parsed_results):
            print(f'{num}) {parsed_line_data}')
        to_kill = int(input('WHO DO YOU WANT TO KILL? '))
        run(f'kill {parsed_results[to_kill].pid}')
    else:
        print('No Results')

#find_and_kill()

##########################################

########## Parse Ping ####################
class PingData(NamedTuple):
    original_host: Optional[str]
    host_ip: Optional[str]
    single_pings: Optional[List['SinglePingData']]
    packets_transmitted: Optional[int]
    packets_received: Optional[int]
    percent_packet_loss: Optional[float]
    time: Optional[float]
    rtt_min: Optional[float]
    rtt_avg: Optional[float]
    rtt_max: Optional[float]
    rtt_mdev: Optional[float]
    error_message: Optional[str]

def parse_ping_data(ping_stdout: Optional[str], ping_stderr: Optional[str]) -> PingData:
    original_host = None
    host_ip = None
    single_pings = []
    packets_transmitted = None
    packets_received = None
    percent_packet_loss = None
    time = None
    rtt_min = None
    rtt_avg = None
    rtt_max = None
    rtt_mdev = None
    error_message = None

    if ping_stdout is not None:
        ping_lines = ping_stdout.split('\n')
        for line in ping_lines:
            line_data = line.split(' ')
            if 'bytes from' in line:
                # Each ICMP request-response produces a line like this:
                # 64 bytes from localhost (127.0.0.1): icmp_seq=1 ttl=64 time=0.022 ms
                single_pings.append(parse_single_ping_data(line))
            elif 'PING' in line:
                # the first line (when running normally) of ping looks like:
                # PING localhost (127.0.0.1) 56(84) bytes of data.
                original_host = line_data[1]
                host_ip = line_data[2][1:-2]
            elif 'packets transmitted' in line:
                # the first useful line of statistics looks like this:
                # 2 packets transmitted, 2 received, 0% packet loss, time 1024ms
                packets_transmitted = int(line_data[0])
                packets_received = int(line_data[3])
                #print(line_data[5][:-1])
                percent_packet_loss = float(line_data[5][:-1])
                time = int(line_data[9][:-3])
            elif 'rtt' in line:
                # the second line of useful statistics looks like this:
                # rtt min/avg/max/mdev = 0.022/0.051/0.080/0.029 ms
                rtt_stat_data = line_data[3].split('/')
                rtt_min = float(rtt_stat_data[0])
                rtt_avg = float(rtt_stat_data[1])
                rtt_max = float(rtt_stat_data[2])
                rtt_mdev = float(rtt_stat_data[3])

    if ping_stderr is not None:
        ping_error_lines = ping_stderr.split('\n')
        #print(ping_error_lines)
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
    ip_address: Optional[str]
    reverse_dns: Optional[str]
    round_trip_time: Optional[float]

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
    round_trip_time = float(line_data[-2].split('=')[1])

    return SinglePingData(ip, reverse_dns, round_trip_time)



def is_it_up(host: str) -> None:
    results = run(f'ping -c 5 {host}')
    #print(results)
    data = parse_ping_data(results.stdout, results.stderr)
    #print(data)
    if results.return_code == 0:
        output = f'{data.original_host} is UP ({data.packets_received}/{data.packets_transmitted}'
        output += f' | average rtt: {data.rtt_avg})'
        print(output)
    else:
        output = f'{data.original_host}: {data.error_message}'
        print(output)


is_it_up('localhost')
is_it_up('google.com')
is_it_up('udeidhuiduidh')
is_it_up('192.0.2.1')
