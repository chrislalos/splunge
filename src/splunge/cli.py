import argparse
import sys
from . import wsg_fn

PATH_CfgDefault = "./.splunge.cfg.py"


class AppendWithMulti(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        current = getattr(namespace, self.dest) or []
        current.extend(values)
        setattr(namespace, self.dest, current)


class AppFactory(BaseApplication):
    def _init(self, cfg, guniCfg):
        self.cfg, guniCfg
        self.guniCfg = guniCfg

    def load(self):
        return wsgi_fn

    def load_config(self):
        return self.guniCfg


class Config:
    def __init__(self, *,
                 name,
                 bind,
                 contentFolders=[],
                 codeFolders=[],
                 templateFolders=[]):
        self.name = name
        self.contentFolders = contentFolders
        self.codeFolders = codeFolders
        self.templateFolders = templateFolders
        self.gunicornConfig = dict()


def create_parser():
    parser = argparse.ArgumentParser(prog='splunge')
    subs = parser.add_subparsers(dest="cmd", required=True)
    #
    # init subcommand
    #
    p = subs.add_parser('init')
    p.add_argument('--bind', nargs=1, dest='bind')
    p.add_argument('--code-folder', nargs='+', action=AppendWithMulti, dest='codeFolder')
    p.add_argument('--content-folder', nargs='+', action=AppendWithMulti, dest='contentFolder')
    p.add_argument('--name', nargs=1, dest='name')
    p.add_argument('--template-folder', nargs='+', action=AppendWithMulti, dest='templateFolder')
    p.set_defaults(func=init)
    #
    # run subcommand
    #
    p = subs.add_parser('run')
    p.add_argument('--bind', nargs=1, dest='bind')
    p.add_argument('--code-folder', nargs='+', action=AppendWithMulti, dest='codeFolder')
    p.add_argument('--content-folder', nargs='+', action=AppendWithMulti, dest='contentFolder')
    p.add_argument('--name', nargs=1, dest='name')
    p.add_argument('--template-folder', nargs='+', action=AppendWithMulti, dest='templateFolder')
    p.add_argument('--with-config', nargs='?', const=PATH_CfgDefault, default=PATH_CfgDefault, dest='withConfig')
    p.set_defaults(func=run)
    #
    # done
    #
    return parser



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
