from importlib.machinery import FileFinder
from importlib.machinery import SourceFileLoader
import importlib.util 
import os.path
from splunge import *

def loadModule (path):
	folder = os.path.dirname(path)
	print("folder=" + folder)

	filename = os.path.basename(path)
	print("filename=" + filename)

	(moduleName, dot, extension) = filename.rpartition('.')
	print("(moduleName, dot, extension)=({}, {}, {})".format(moduleName, dot, extension))

	loaderArgs = (SourceFileLoader, [dot+extension])
	finder = FileFinder(folder, loaderArgs)
	spec = finder.find_spec(moduleName)
	print("spec=" + str(spec))
	if not spec:
		raise ModuleNotFoundEx(moduleName)

	module = importlib.util.module_from_spec(spec)
	print("module=" + str(module))

	loader = spec.loader
	module.moduleSpec = spec
	module.exec = lambda: loader.exec_module(module)
	return module


# from importlib.abc import ExecutionLoader
# from importlib.machinery import SourceFileLoader
# import abc
# 
# class MagicLoader (ExecutionLoader):
# 	def __init__ (self, fullname, path):
# 		self.dlg = SourceFileLoader(fullname, path)
# 		pass
# 
# 	def get_code (self, fullname):
# 		return dlg.get_code(fullname)
# 	
# 	def get_filename (self, fullname):
# 		return dlg.get_filename(fullname)
# 
# 	def get_source (self, fullname):
# 		return dlg.get_source(fullname)
 

# ExecutionLoader.register(MagicLoader)

# if __name__ == '__main__':
	# loader = MagicLoader('fullname', 'path')
	# loader = SourceFileLoader('TestModule', 'TestModule.py')
	#for s in sorted(dir(loader)):
	#	print(s)
	#m = 
	#pass
