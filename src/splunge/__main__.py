import argparse
import sys

def runBehindNginx (args):
	for arg in args:
		print(args)


def runLocally (args):
	print("*** running locally ***")


def parseArgs (argv):
	pass


def main (argv):
	args = parseArgs(argv)
	if args.host:
		runBehindNginx(args)
	else:
		runLocally(args)

if __name__ == '__main__':
	main(sys.argv[1:])

