from run_commands import run, CommandResults

if __name__ == '__main__':
    print(run('ls'))
    print(run('ls -la'))
    print(run('ping -c 1 google.com'))
    print(run('ps aux | grep "python"'))
