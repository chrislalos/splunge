import argparse
from dataclasses import dataclass
import sys
from . import wsg_fn, Xgi
from .arg_parser import create_parser
PATH_CfgDefault = "./.splunge.cfg.py"


# create an a
def createConfigObjs(args):
    pass


def init(args, configPath=None):
    print("Welcome")
    # If --name not set, prompt for name (ex: current folder basename)
    # If --bind not set, prompt for bind (ex: 0.0.0.0:13001, unix://var/run/$name.sock)
    # If --content-folder not set, prompt for one or more --content-folder, blank line to end)
    # If --code-folder not set, prompt for one or more --code-folder, blank line to end)
    # If --template-folder not set, prompt for one or more --template-folder, blank line to end)
    # Write config file as splunge.cfg.py
    cfg = None
    if configFile:
        spec = importlib.util.spec_from_file_location('__config__', configPath)
        cfgModule = importlib.module_from_spec(spec)
        spec.loader.exec_module(cfgModule)
        cfg = vars(cfgModule)
    appInfo = initAppInfo(args, cfg)



def run(args):
    (cfg, guniCfg) = createConfig(args)

    pass


def main():
    parser = create_parser()
    args = parser.parse_args(sys.argv[1:])
    args.func(args)


if __name__ == '__main__':
    main()
