import readline
import rlcompleter
import sys

from splunge import cli, util
import boxylady as boxy

def main():
	readline.parse_and_bind('tab: complete')
	print("cli + util helpers loaded. Try: cli.<TAB>, util.<TAB>")
	print(sys.argv)
	args = " ".join(sys.argv[1:])
	print(args)
	exec(args, globals(), locals())
	

if __name__ == '__main__':
	main()
