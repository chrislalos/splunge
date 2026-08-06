import argparse

class AppendWithMulti(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        current = getattr(namespace, self.dest) or []
        current.extend(values)
        setattr(namespace, self.dest, current)

class ToScalar(argparse.Action):
	def __call__(self, parser, namespace, values, option_string=None):
		val = values[0] if values else None
		setattr(namespace, self.dest, val)


def create_parser(fnMap):
	parser = argparse.ArgumentParser(prog='splunge')
	subs = parser.add_subparsers(dest="cmd", required=True)
	#
	# init subcommand
	#
	subCmd = 'init'
	p = subs.add_parser(subCmd)
	# required
	p.add_argument('--name', nargs=1, action=ToScalar, dest='name')
	p.add_argument('--bind', nargs=1, action=ToScalar, dest='bind')
	p.add_argument('--code-folders', nargs='+', action=AppendWithMulti, dest='codeFolders')
	p.add_argument('--content-folders', nargs='+', action=AppendWithMulti, dest='contentFolders')
	p.add_argument('--template-folders', nargs='+', action=AppendWithMulti, dest='templateFolders')
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
	p.add_argument('--with-config', nargs='?', default=None, dest='withConfig')
	p.set_defaults(func=fnMap[subCmd])
	#
	# done
	#
	return parser

