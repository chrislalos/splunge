import argparse
import sys


def init_arg_parser():
    parser = argparse.ArgumentParser(
        prog='splunge',
        epilog=''
    )
    subs = parser.add_subparsers(dest="cmd", required=True)
    
    # init subcommand
    p = subs.add_parser('init')
    p.set_defaults(func=init)

    # done
    args = parser.parse_args(sys.argv[1:])
    return args


def init(args):
    print("init!")


def main():
    args = init_arg_parser()
    args.func(args)


if __name__ == '__main__':
    main()
