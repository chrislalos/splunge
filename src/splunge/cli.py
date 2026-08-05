from dataclasses import dataclass
import os.path
import readline
import sys
from . import arg_parser
from . import Xgi
from .app import Config


def completer (text, state):
	with open('completer.log', 'a') as f:
		try:
			print('meat')
			dir, prefix = os.path.split(text)
			if not dir:
				dir = '.'
			matches = [f for f in os.listdir(dir) if f.startswith(prefix)]
			s = f'completer(): text={text:<20s} state={state:<4d} dir={dir:<20} prefix={prefix:<20}\n'
			f.write(s)
			return matches[state]
		except ex:
			import traceback
			with open('completer.err.log', 'a') as ferr:
				traceback.print_exc(file=ferr)
				print(ex)
			return None


# create an a
def createConfigObjs(args):
    pass


def getConfigValue(prompt, default=None, multi=False, autoComplete=False):
	print("hi")
	if autoComplete:
		readline.set_completer_delims(readline.get_completer_delims().replace('/', ''))
		readline.set_completer(completer)
		readline.parse_and_bind("tab: complete")
	prompt = f"{prompt}: "
	val = input(prompt)
	return val



def init(args, configPath=None):
    # If --name not set, prompt for name (ex: current folder basename)
    # If --bind not set, prompt for bind (ex: 0.0.0.0:13001, unix://var/run/$name.sock)
    # If --content-folder not set, prompt for one or more --content-folder, blank line to end)
    # If --code-folder not set, prompt for one or more --code-folder, blank line to end)
    # If --template-folder not set, prompt for one or more --template-folder, blank line to end)
    # Write config file as splunge.cfg.py
	print("Welcome")
	# initialize readline
	if not args.name:
		name = getConfigValue("name")
	if not args.codeFolders:
		codeFolder = getConfigValue("codeFolder", autoComplete=True)
	contentFolders = []
	guniCfg = {}
	templateFolders = []

	cfg = Config(name=name, codeFolders=codeFolders, contentFolders=contentFolders, guniCfg=guniCfg, templateFolders=templateFolders)
	cfg.pprint()
#     cfg = None
#     if args.configFile:
#         spec = importlib.util.spec_from_file_location('__config__', configPath)
#         cfgModule = importlib.module_from_spec(spec)
#         spec.loader.exec_module(cfgModule)
#         cfg = vars(cfgModule)
#     appInfo = initAppInfo(args, cfg)


def run(args):
    (cfg, guniCfg) = createConfig(args)

    pass


def main():
	fnMap = {
		"init": init,
		"run": run,
	}
	parser = arg_parser.create_parser(fnMap)
	args = parser.parse_args(sys.argv[1:])
	args.func(args)


if __name__ == '__main__':
    main()
