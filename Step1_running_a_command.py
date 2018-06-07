import subprocess, shlex
from subprocess import PIPE, CompletedProcess

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

#simplest_run('ls')

def capture_stdout_and_stderr_run(command: str) -> None:
    results = subprocess.run(shlex.split(command), stdout=PIPE, stderr=PIPE)
    print_run_results(results)

#capture_stdout_and_stderr_run('ls -la')

def make_strings_not_bytes_run(command: str) -> None:
    results = subprocess.run(shlex.split(command), stdout=PIPE, stderr=PIPE, encoding='utf-8')
    print_run_results(results)

#make_strings_not_bytes_run('ping -c 1 google.com')
#make_strings_not_bytes_run("ps aux | grep 'python'") # fails to run properly

def execute_with_bash_run(command: str) -> None:
    results = subprocess.run(command, stdout=PIPE, stderr=PIPE, encoding='utf-8', shell=True, executable='/bin/bash')
    print_run_results(results)

#execute_with_bash_run("ps aux | grep 'python'")

# subprocess.Popen variations
def pipe_without_using_bash(command1: str, command2: str) -> None:
    process1 = subprocess.Popen(shlex.split(command1), stdout=PIPE, stderr=PIPE)
    process2 = subprocess.Popen(shlex.split(command2), stdin=process1.stdout, stdout=PIPE, stderr=PIPE, encoding='utf-8')
    return_code = process2.wait()
    stdout, stderr = process2.communicate()
    print_Popen_results(f'{command1} | {command2}', return_code, stdout, stderr)

#pipe_without_using_bash('ps aux', "grep 'python'")

def pipe_without_using_bash2(command1: str, command2: str) -> None:
    process1 = subprocess.Popen(shlex.split(command1), stdin=None, stdout=PIPE, stderr=PIPE, encoding='utf-8')
    p1_stdout, p1_stderr = process1.communicate(None)
    p1_return_code = process1.wait()

    process2 = subprocess.Popen(shlex.split(command2), stdin=PIPE, stdout=PIPE, stderr=PIPE, encoding='utf-8')
    p2_stdout, p2_stderr = process2.communicate(p1_stdout)
    p2_return_code = process2.wait()

    print_Popen_results(f'{command1} | {command2}', p2_return_code, p2_stdout, p2_stderr)

#pipe_without_using_bash2('ps aux', "grep 'python'")
