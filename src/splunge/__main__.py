from argparse import ArgumentParser
from pprint import pprint
import os
import sys
import subprocess

def runBehindNginx (args):
	for arg in args:
		print(args)


def runLocally (args):
	print("*** running locally ***")
	pyPath = sys.executable
	pyFolder = os.path.dirname(pyPath)
	gunicornPath = os.path.join(pyFolder, 'gunicorn')
	print("gunicornPath={}".gunicornPath)
	if args.port:
		cmd = "{} -b localhost:{} splunge.App:Application".format(gunicornPath, args.port)
	else:
		cmd = "{} -b localhost splunge.App:Application".format(gunicornPath, args.port)
	print(cmd)
	subprocess.run(cmd)


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

