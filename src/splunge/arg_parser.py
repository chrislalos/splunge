import argparse
from . import constants

class AppendWithMulti(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        current = getattr(namespace, self.dest) or []
        current.extend(values)
        setattr(namespace, self.dest, current)


def create_parser(fnMap):
	parser = argparse.ArgumentParser(prog='splunge')
	subs = parser.add_subparsers(dest="cmd", required=True)
	#
	# init subcommand
	#
	subCmd = 'init'
	p = subs.add_parser(subCmd)
	p.add_argument('--bind', nargs=1, dest='bind')
	p.add_argument('--code-folder', nargs='+', action=AppendWithMulti, dest='codeFolders')
	p.add_argument('--content-folder', nargs='+', action=AppendWithMulti, dest='contentFolder')
	p.add_argument('--name', nargs=1, dest='name')
	p.add_argument('--template-folder', nargs='+', action=AppendWithMulti, dest='templateFolder')
	p.set_defaults(func=fnMap[subCmd])
	#
	# run subcommand
	#
	subCmd = 'run'
	p = subs.add_parser(subCmd)
	p.add_argument('--bind', nargs=1, dest='bind')
	p.add_argument('--code-folder', nargs='+', action=AppendWithMulti, dest='codeFolder')
	p.add_argument('--content-folder', nargs='+', action=AppendWithMulti, dest='contentFolder')
	p.add_argument('--name', nargs=1, dest='name')
	p.add_argument('--template-folder', nargs='+', action=AppendWithMulti, dest='templateFolder')
	p.add_argument('--with-config', nargs='?', const=constants.PATH_CfgDefault, default=constants.PATH_CfgDefault, dest='withConfig')
	p.set_defaults(func=fnMap[subCmd])
	#
	# done
	#
	return parser

