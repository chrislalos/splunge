import logging
import os


PATH = "./splunge.log"

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
	print("Calling logger.info()...")
	logger.info(msg, *args, **kwargs)


def log(level, msg, *args, **kwargs):
	logger.log(level, msg, *args, **kwargs)


def warn(msg, *args, **kwargs):
	logger.warn(msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
	logger.warning(msg, *args, **kwargs)



def initLogger():
	print("init'ing logger ...")
	f = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	h = logging.FileHandler(PATH)
	h.setFormatter(f)
	logger = logging.getLogger("splunge")
	logger.setLevel(logging.DEBUG)
	logger.addHandler(h)
	print(f'writing log to {os.getcwd()}/{PATH}')
	return logger

logger = initLogger()