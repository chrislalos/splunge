import glob
import logging
import os
import readline

def path_completer(text, state):
	with open('./completer_debug.log', 'a') as f:
		try:
			f.write(f'text={text} state={state}\n')
			if state == 0:
				base = os.path.expanduser(text) if text.startswith('~') else text
				if os.path.isdir(base):
					if base.endswith('/'):
						pattern = base + '*'
					else:
						pattern = base + '/*'
				else:
					pattern = base + '*'
				raw_matches = sorted(glob.glob(pattern))
				home = os.path.expanduser('~')
				path_completer.matches = []
				for m in raw_matches:
					display = m.replace(home, '~', 1) if text.startswith('~') else m
					if os.path.isdir(m):
						display += '/'
					path_completer.matches.append(display)
				f.write(f'base={base!r} pattern={pattern!r} matches={path_completer.matches}\n')
			try:
				return path_completer.matches[state]
			except IndexError:
				return None
		except Exception:
			import traceback
			traceback.print_exc(file=f)

def main():
	logging.basicConfig(filename='completer.log', level=logging.INFO)
	readline.set_completer_delims(readline.get_completer_delims().replace('/', ''))
	readline.set_completer(path_completer)
	readline.parse_and_bind('tab: complete')
	line = input("hello ")

if __name__ == '__main__':
	main()

