import argparse


class AppendWithMulti(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        current = getattr(namespace, self.dest) or []
        current.extend(values)
        setattr(namespace, self.dest, current)


def create_parser():
    parser = argparse.ArgumentParser(prog='splunge')
    subs = parser.add_subparsers(dest="cmd", required=True)
    #
    # init subcommand
    #
    p = subs.add_parser('init')
    p.add_argument('--bind', nargs=1, dest='bind')
    p.add_argument('--code-folder', nargs='+', action=AppendWithMulti, dest='codeFolder')
    p.add_argument('--content-folder', nargs='+', action=AppendWithMulti, dest='contentFolder')
    p.add_argument('--name', nargs=1, dest='name')
    p.add_argument('--template-folder', nargs='+', action=AppendWithMulti, dest='templateFolder')
    p.set_defaults(func=init)
    #
    # run subcommand
    #
    p = subs.add_parser('run')
    p.add_argument('--bind', nargs=1, dest='bind')
    p.add_argument('--code-folder', nargs='+', action=AppendWithMulti, dest='codeFolder')
    p.add_argument('--content-folder', nargs='+', action=AppendWithMulti, dest='contentFolder')
    p.add_argument('--name', nargs=1, dest='name')
    p.add_argument('--template-folder', nargs='+', action=AppendWithMulti, dest='templateFolder')
    p.add_argument('--with-config', nargs='?', const=PATH_CfgDefault, default=PATH_CfgDefault, dest='withConfig')
    p.set_defaults(func=run)
    #
    # done
    #
    return parser




