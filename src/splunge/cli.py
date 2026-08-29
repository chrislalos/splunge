import logging
import os
import sys

from . import arg_parser, path_completer
from .app import Config, createGunicornConfig, create_run_config
from .util import get_config_value, prompt_save_file


# create an Config object
def createConfig(args):
	pass


def init(args, configPath=None):
	try:
		print("Welcome")
		while True:
			cfg = _create_user_app_config(
				name=args.name,
				accessLog=args.accessLog,
				bind=args.bind,
				codeFolders=args.codeFolders,
				contentFolders=args.contentFolders,
				errorLog=args.errorLog,
				logFolder=args.logFolder,
				templateFolders=args.templateFolders,
			)
			if cfg is not None:
				break
			retry = get_config_value("Try again", default="y")
			if not (retry and retry.lower().startswith('y')):
				print("Config creation aborted.")
				return
		print(cfg)
		path = prompt_save_file("Save config", default=f"./{cfg.name}.toml")
		if path:
		    _save_app_config(cfg, path)
		    print(f"Config saved to {path}")
		else:
		    print("Config not saved.")
	except (EOFError, KeyboardInterrupt):
		print()
		sys.exit(0)


#     cfg = None
#     if args.configFile:
#         spec = importlib.util.spec_from_file_location('__config__', configPath)
#         cfgModule = importlib.module_from_spec(spec)
#         spec.loader.exec_module(cfgModule)
#         cfg = vars(cfgModule)
#     appInfo = initAppInfo(args, cfg)


def run(args):
	config_path = args.withConfig or _resolve_config()
	if not config_path:
		print("No config file found. Run 'splunge init' first.", file=sys.stderr)
		sys.exit(1)
	app_cfg = _load_app_config(config_path)
	_mark_as_app_config(config_path)
	run_cfg = create_run_config(
		app_cfg,
		bind=args.bind,
		codeFolders=args.codeFolders,
		contentFolders=args.contentFolders,
		templateFolders=args.templateFolders,
		logFolder=args.logFolder,
		accessLog=args.accessLog,
		errorLog=args.errorLog,
		reload=args.reload,
		debug=args.debug,
	)


def setup_logging():
	# add handler to log to completer_debug.log
	handler = logging.FileHandler("completer_debug.log", mode="a")
	handler.setLevel(logging.DEBUG)
	completerLogger = path_completer.get_completer_logger()
	completerLogger.addHandler(handler)
	completerLogger.setLevel(logging.DEBUG)


def _create_user_app_config(name=None,
							accessLog=None,
							bind=None,
							codeFolders=None,
                            contentFolders=None,
							errorLog=None,
							logFolder=None,
							templateFolders=None):
	'''Prompt the user for values to create a basic app config.
	name            required, scalar, default=$dirname
	bind            required, scalar, example='0.0.0.0:13000, unix:/var/run/$name.sock'
	codeFolders     optional, multi
	contentFolders  optional, multi
	templateFolders optional, multi'''
	try:
		if not name:
			name = get_config_value("Name", default=os.path.basename(os.getcwd()), required=True)
		if not bind:
			defaultTcp = '0.0.0.0:13000'
			defaultUnix = f'unix:/run/{name}.sock'
			default = defaultTcp
			example = f'{defaultUnix},{defaultUnix}'
			bind = get_config_value("bind", default=default, logFolderexample=example, required=True)
		if not codeFolders:
			codeFolders = get_config_value("code folder(s)", autoComplete=True, multi=True)
		if not contentFolders:
			contentFolders = get_config_value("content folder(s)", autoComplete=True, multi=True)
		if not templateFolders:
			templateFolders = get_config_value("template folder(s)", autoComplete=True, multi=True)
		if not logFolder:
			logFolder = get_config_value("Log folder", default="/log", autoComplete=True)
		if not accessLog:
			default = os.path.join(logFolder, "access.log")
			accessLog = get_config_value("Access log path", default=default, autoComplete=True)
		if not errorLog:
			default = os.path.join(logFolder, "error.log")
			errorLog = get_config_value("Error log path", default=default, autoComplete=True)
		guniCfg = createGunicornConfig(accessLog=accessLog, bind=bind, errorLog=errorLog)
		return Config(
			name=name,
			codeFolders=codeFolders,
			contentFolders=contentFolders,
			guniCfg=guniCfg,
			logFolder=logFolder,
			templateFolders=templateFolders,
		)
	except (KeyboardInterrupt, EOFError):
		print()
		return None

def _get_app_config_paths():
	"""Get paths of all app configs in this folder, non-recursive.
	An app config file is any file marked with the splunge.app.cfg xattr."""
	from .util import find_xattr_configs
	return find_xattr_configs(os.getcwd())


def _get_default_config_path():
	"""Get the default config file for this app folder if it exists."""
	path = f"./{os.path.basename(os.getcwd())}.toml"
	return path


def _get_user_app_config_path():
	"""Prompt the user to enter an app config path. They must enter a file
	that exists."""
	path = get_config_value("Config file path", autoComplete=True, required=True)
	if path and os.path.isfile(path):
		return path
	return None


def _load_app_config(path):
	"""Load the app config at this path."""
	import toml
	d = toml.load(path)
	return Config(**d)


def _load_default_config():
	"""Load the default config file for this app folder if it exists."""
	path = _get_default_config_path()
	if not path:
		return None
	return _load_app_config(path)


def _mark_as_app_config(path):
	"""Mark a config file with the splunge.app.cfg xattr."""
	from .util import set_config_xattr
	set_config_xattr(path)


def _save_app_config(cfg, path):
	'''Save the app config to the specified path.'''
	cfg.to_file(path)
	_mark_as_app_config(path)


def _save_default_app_config(cfg, dirPath=None):
	'''Save the app config to the default app config name for the specified
	dir. dirPath must be an existing folder.'''
	if dirPath:
		path = os.path.join(dirPath, f"{cfg.name}.toml")
	else:
		path = _get_default_config_path()
	_save_app_config(cfg, path)


def _unmark_as_app_config(path):
	'''Remove the splunge.app.cfg xattr if present.'''
	from .util import remove_config_xattr
	remove_config_xattr(path)


def _resolve_config():
	path = _get_default_config_path()
	if path:
		return path
	xattrs = _get_app_config_paths()
	if len(xattrs) == 1:
		return xattrs[0]
	if len(xattrs) > 1:
		print("Multiple config files found:")
		for i, p in enumerate(xattrs, 1):
			print(f"  {i}: {p}")
		while True:
			choice = input(f"Choose (1-{len(xattrs)}, or blank to skip): ")
			if choice == '':
				return None
			try:
				return xattrs[int(choice) - 1]
			except (ValueError, IndexError):
				pass
	return None


def main():
	fnMap = {
		"init": init,
		"run": run,
	}
	setup_logging()
	parser = arg_parser.create_parser(fnMap)
	args = parser.parse_args(sys.argv[1:])
	args.func(args)


if __name__ == "__main__":
	main()
