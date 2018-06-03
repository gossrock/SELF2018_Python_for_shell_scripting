import subprocess, shlex
from subprocess import PIPE, CompletedProcess

ls = 'ls'
ls_la = 'ls -la'
ping_google_once = 'ping -c 1 google.com'
list_python_processes = "ps aux | grep 'python'"
ps_aux = 'ps aux'
grep_python = "grep 'python'"


def print_run_results(results: CompletedProcess) -> None:
    print('\nARGS')
    print(f'{results.args}')

    print('\nRETURN CODE')
    print(f'{results.returncode}')

    print('\nSTDOUT')
    print(f'{results.stdout}')

    print('\nSTDERR')
    print(f'{results.stderr}')

def print_Popen_results(command: str, returncode: int,  stdout: str, stderr: str) -> None:
    print('\nCOMMAND')
    print(command)

    print('\nRETURN CODE')
    print(f'{returncode}')

    print('\nSTDOUT')
    print(f'{stdout}')

    print('\nSTDERR')
    print(f'{stderr}')

# subprocess.run variations
def simplest_run(command: str) -> None:
    results = subprocess.run(shlex.split(command))
    print_run_results(results)

def capture_stdout_and_stderr_run(command: str) -> None:
    results = subprocess.run(shlex.split(command), stdout=PIPE, stderr=PIPE)
    print_run_results(results)

def make_strings_not_bytes_run(command: str) -> None:
    results = subprocess.run(shlex.split(command), stdout=PIPE, stderr=PIPE, encoding='utf-8')
    print_run_results(results)

def execute_with_bash_run(command: str) -> None:
    results = subprocess.run(command, stdout=PIPE, stderr=PIPE, encoding='utf-8', shell=True, executable='/bin/bash')
    print_run_results(results)

# subprocess.Popen variations
def pipe_without_using_bash(command1: str, command2: str) -> None:
    process1 = subprocess.Popen(shlex.split(command1), stdout=PIPE, stderr=PIPE)
    process2 = subprocess.Popen(shlex.split(command2), stdin=process1.stdout, stdout=PIPE, stderr=PIPE, encoding='utf-8')
    return_code = process2.wait()
    stdout, stderr = process2.communicate()
    print_Popen_results(f'{command1} | {command2}', return_code, stdout, stderr)

def pipe_without_using_bash2(command1: str, command2: str) -> None:
    process1 = subprocess.Popen(shlex.split(command1), stdin=None, stdout=PIPE, stderr=PIPE, encoding='utf-8')
    p1_stdout, p1_stderr = process1.communicate(None)
    p1_return_code = process1.wait()

    process2 = subprocess.Popen(shlex.split(command2), stdin=PIPE, stdout=PIPE, stderr=PIPE, encoding='utf-8')
    p2_stdout, p2_stderr = process2.communicate(p1_stdout)
    p2_return_code = process2.wait()

    print_Popen_results(f'{command1} | {command2}', p2_return_code, p2_stdout, p2_stderr)



if __name__ == '__main__':
    #simplest_run(ls)
    #capture_stdout_and_stderr_run(ls_la)
    #make_strings_not_bytes_run(ping_google_once)
    #make_strings_not_bytes_run(list_python_processes) # fails to run properly
    #execute_with_bash_run(list_python_processes)
    #pipe_without_using_bash(ps_aux, grep_python)
    pipe_without_using_bash2(ps_aux, grep_python)
