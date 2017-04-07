from argparse import ArgumentParser
from pprint import pprint
import os
import sys
import subprocess


APP = 'splunge.App:Application'


def createAddress (args):
	if args.port:
		addr = 'localhost:{}'.format(args.port)
	else:
		addr = 'localhost'
	return addr


def createGunicornPath ():
	pyPath = sys.executable
	pyFolder = os.path.dirname(pyPath)
	gunicornPath = os.path.join(pyFolder, 'gunicorn')
	return gunicornPath


def runBehindNginx (args):
	for arg in args:
		print(args)


def runLocally (args):
	print("*** running locally ***")
	gunicornPath = createGunicornPath()
	addr = createAddress(args)
	cmdArgs = [gunicornPath, "-b", addr, APP]
	pprint(cmdArgs)
	subprocess.run(cmdArgs)


def parseArgs (argv):
	parser = ArgumentParser(add_help=False)
	parser.add_argument('-h', '--host', required=False)
	parser.add_argument('-p', '--port', required=False)
	args = parser.parse_args(argv)
	return args


def main ():
	args = parseArgs(sys.argv[1:])
	pprint(args)
	if args.host:
		runBehindNginx(args)
	else:
		runLocally(args)

if __name__ == '__main__':
	main()
