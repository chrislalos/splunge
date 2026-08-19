import readline
import rlcompleter

from splunge import cli, util
import boxylady as boxy

def main():
	readline.parse_and_bind('tab: complete')
	print("cli + util helpers loaded. Try: cli.<TAB>, util.<TAB>")
	print("")


if __name__ == '__main__':
	main()
