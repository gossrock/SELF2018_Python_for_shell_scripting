import argparse


def SetupParser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='echo things')
    parser.add_argument('-l', '--loud', action='store_true', help='tells it to echo loudly')
    parser.add_argument('dont_echo', nargs=1, help='the first argument gets ignored')
    parser.add_argument("echo", nargs='+', help='things to echo')
    return parser



if __name__ == '__main__':
    parser = SetupParser()
    args = parser.parse_args()
    print(args)
    for thing in args.echo:
        if args.loud:
            print(thing.upper())
        else:
            print(thing)
