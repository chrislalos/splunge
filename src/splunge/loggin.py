import logging as stdlib_logging

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
	logger = stdlib_logging.getLogger("splunge")
	logger.setLevel(stdlib_logging.DEBUG)
	h = stdlib_logging.FileHandler(PATH)
	logger.addHandler(h)
	return logger

logger = initLogger()