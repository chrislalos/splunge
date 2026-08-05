import glob
import logging
import os
import readline
from contextlib import contextmanager


def get_completer_logger():
	completerLogger = logging.getLogger('completer')
	return completerLogger


@contextmanager
def set_completer():
	prev = readline.get_completer()
	readline.set_completer_delims(readline.get_completer_delims().replace('/', ''))
	readline.parse_and_bind('tab: complete')
	readline.set_completer(completer)
	try:
		yield completer
	finally:
		readline.set_completer(prev)


def completer(text, state):
	logger = get_completer_logger()
	try:
		logger.debug('text=%r state=%d', text, state)
		if state == 0:
			base = os.path.expanduser(os.path.expandvars(text))
			if os.path.isdir(base):
				if base.endswith('/'):
					pattern = base + '*'
				else:
					pattern = base + '/*'
			else:
				pattern = base + '*'
			raw_matches = sorted(glob.glob(pattern))
			home = os.path.expanduser('~')
			completer.matches = []
			for m in raw_matches:
				display = m.replace(home, '~', 1) if text.startswith('~') else m
				if os.path.isdir(m):
					display += '/'
				completer.matches.append(display)
			logger.debug('base=%r pattern=%r matches=%r', base, pattern, completer.matches)
		try:
			return completer.matches[state]
		except IndexError:
			return None
	except Exception:
		logger.exception('path_completer failed')

