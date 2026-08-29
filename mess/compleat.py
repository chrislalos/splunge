import logging

from splunge.path_completer import get_completer_logger, set_completer

'''
compleat.py - harness for a path completer

When prompting the user for input for a filename or path, autocomplete is a
must. path_completer handles relative and absolute paths, and translates ~
to the user's home folder. It uses python's `readline` library instead of
trying to figure any of that stuff out for itself.
'''


def setup_logging():
	# add handler to log to completer_debug.log
	handler = logging.FileHandler('completer_debug.log', mode='a')
	handler.setLevel(logging.DEBUG)
	completerLogger = get_completer_logger()
	completerLogger.addHandler(handler)
	completerLogger.setLevel(logging.DEBUG)


def main():
	setup_logging()
	with set_completer():
		line = input("hello ")
		print(line)

if __name__ == '__main__':
	main()

