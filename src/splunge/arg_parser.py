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
	p.set_defaults(func=fnMap[subCmd])
	p.add_argument('--template-folders', nargs='+', action=AppendWithMulti, dest='templateFolders')
	p.add_argument('--name', nargs=1, action=ToScalar, dest='name')
	p.add_argument('--bind', nargs=1, action=ToScalar, dest='bind')
	p.add_argument('--code-folders', nargs='+', action=AppendWithMulti, dest='codeFolders')
	p.add_argument('--content-folders', nargs='+', action=AppendWithMulti, dest='contentFolders')
	p.add_argument('--log-folder', nargs=1, action=ToScalar, dest='logFolder')
	p.add_argument('--access-log', nargs='?', default=None, dest='accessLog')
	p.add_argument('--error-log', nargs='?', default=None, dest='errorLog')	
	
	#
	# run subcommand
	#
	subCmd = 'run'
	p = subs.add_parser(subCmd)
	p.set_defaults(func=fnMap[subCmd])
	p.add_argument('--bind', nargs=1, action=ToScalar, dest='bind')
	p.add_argument('--code-folders', nargs='+', action=AppendWithMulti, dest='codeFolders')
	p.add_argument('--content-folders', nargs='+', action=AppendWithMulti, dest='contentFolders')
	p.add_argument('--template-folders', nargs='+', action=AppendWithMulti, dest='templateFolders')
	p.add_argument('--log-folder', nargs=1, action=ToScalar, dest='logFolder')
	p.add_argument('--access-log', nargs='?', default=None, dest='accessLog')
	p.add_argument('--error-log', nargs='?', default=None, dest='errorLog')
	p.add_argument('--reload', action='store_true', dest='reload')
	p.add_argument('--debug', action='store_true', dest='debug')
	p.add_argument('--with-config', nargs='?', default=None, dest='withConfig')
	#
	# done
	#
	return parser

