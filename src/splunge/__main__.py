import argparse
import sys

def runBehindNginx (args):
	for arg in args:
		print(arg)


def runLocally (args):
	print("*** running locally ***")


def parseArgs ():
	pass


if __name__ == '__main__':
	# print("Usage: splunge [hostname]")
	args = parseArgs()
	if len(sys.argv) > 1:
		runBehindNginx(sys.argv[1:])
	else:
		runLocally(sys.argv[1:])
