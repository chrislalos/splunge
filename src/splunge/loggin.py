import logging
import os
import pathlib
import sys

def critical(msg, *args, **kwargs):
	logger.critical(msg, *args, **kwargs)


def debug(msg, *args, **kwargs):
	logger.debug(msg, *args, **kwargs)


def error(msg, *args, **kwargs):
	logger.error(msg, *args, **kwargs)


def exception(msg, *args, exc_info=True, **kwargs):
	logger.exception(msg, *args, exc_info=True, **kwargs)


def fatal(msg, *args, **kwargs):
	logger.fatal(msg, *args, **kwargs)


def info(msg, *args, **kwargs):
	logger.info(msg, *args, **kwargs)


def log(level, msg, *args, **kwargs):
	logger.log(level, msg, *args, **kwargs)


def warn(msg, *args, **kwargs):
	logger.warn(msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
	logger.warning(msg, *args, **kwargs)



def init():
	print("init'ing logger ...", file=sys.stderr)
	splungeLogFile = os.getenv("SPLUNGE_LOGFILE")
	testing = os.getenv("TESTING")
	print(f'testing={testing}', file=sys.stderr)
	f: logging.Formatter = None
	h: logging.FileHandler = None
	if splungeLogFile:
		f = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
		logPath = pathlib.Path(splungeLogFile)
		h = logging.FileHandler(logPath)
		print(f'writing log to {os.path.abspath(splungeLogFile)}', file=sys.stderr)
	elif testing == '1' or testing.lower == 'y':
		f = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
		logPath = pathlib.Path(os.path.join(os.getcwd(), 'splunge_test.log'))
		h = logging.FileHandler(logPath)
		print(f'writing log to {os.path.abspath(logPath)}', file=sys.stderr)
	else:
		h = logging.StreamHandler(sys.stderr)
		print(f'arg is stream: writing log to sys.stderr', file=sys.stderr)
	h.setFormatter(f)
	logger = logging.getLogger("splunge")
	logger.setLevel(logging.DEBUG)
	logger.addHandler(h)
	return logger

logger = init()