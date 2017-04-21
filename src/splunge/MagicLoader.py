# The Python import machinery consists of finders and loaders.
# The finder finds the module.
# The loader loads the module.
#
# When you do 'import yourModule' in your code, the import machinery is invoked,
# and it loads *and executes* yourModule. We don't want the module executed, because
# we want to load the module up with handy stuff before executing. This is what lets
# an author of a splunge web app get away with not doing imports simply to write vanilla
# web app code. It's already loaded.
#
# So anyway, we want to load the module and not execute it, which is why we can't import
# the module, even programatically because import = load + execute. But we can study the
# code behind import, and see how it loads the module, and steal that code. Which is what
# the code below does: the little bit of code below was the result of studying the import
# code. That's why the code is weird; it's weird because the import machinery is weird.
#
# This became possible in Python 3 (or maybe a later 2.x - I can't recall), when 
# the core import code got moved from C to Python.


from importlib.machinery import FileFinder
from importlib.machinery import SourceFileLoader
import importlib.util 
import os.path

def loadModule (path):
	# Simple filename / path stuff
	(folder, filename) = os.path.split(path)
	print("folder=" + folder)
	print("filename=" + filename)
	(moduleName, dot, extension) = filename.rpartition('.')
	print("(moduleName, dot, extension)=({}, {}, {})".format(moduleName, dot, extension))
	# Enter the weirdness: pass a (loader class, file extension) tuple, wrapped in a list, to
	# the c'tor of importlib's FileFinder. Use the file finder to 'find' a module spec (which
	# is sort of metainfo on a module), then use import machinery to turn the spec into a 
	# module.
	loaderArgs = (SourceFileLoader, [dot+extension])
	finder = FileFinder(folder, loaderArgs)
	spec = finder.find_spec(moduleName)
	print("spec=" + str(spec))
	if not spec:
		raise ModuleNotFoundEx(moduleName)
	module = importlib.util.module_from_spec(spec)
	print("module=" + str(module))
	# And now a final weird trick: In python loaders are responsible for execution as well,
	# which seems like an unnecessary coupling. They get away with it because import = load+execute
	# and so decoupling load and execution is not a priority for Python. But it is for splunge.
	# So as a bit of syntactic sugar we add an 'exec' function to the module, which is just a lambda
	# that calls exec_module() on the loader.
	# @todo Think about the implications, of clobbering exec() if exec() happened to exist in the module.
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
