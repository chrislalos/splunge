import importlib.machinery
import importlib.util
import os
import sys


class CodeFolderLoader:
    def __init__(self, codeFolders, *, nspName='codefolder'):
        self.codeFolders = [os.path.abspath(cf) for cf in codeFolders]
        self.nspName = nspName
        self.nspPrefix = nspName + '.'

    def install(self):
        spec = importlib.machinery.ModuleSpec(self.nspName, None, is_package=True)
        spec.submodule_search_locations = []
        sys.modules[self.nspName] = importlib.util.module_from_spec(spec)
        sys.meta_path.insert(0, self)

    def uninstall(self):
        sys.meta_path.remove(self)
        sys.modules.pop(self.nspName, None)

    def find_spec(self, fullname, path, target=None):
        if not fullname.startswith(self.nspPrefix):
            return None
        relative = fullname[len(self.nspPrefix):]
        parts = relative.replace('.', '/')
        mod_file = parts + '.py'
        for cf in self.codeFolders:
            full = os.path.join(cf, mod_file)
            if os.path.isfile(full):
                return importlib.util.spec_from_file_location(fullname, full)
        for cf in self.codeFolders:
            full = os.path.join(cf, parts)
            if os.path.isdir(full):
                spec = importlib.machinery.ModuleSpec(fullname, None, is_package=True)
                spec.submodule_search_locations = [full]
                return spec
        return None
