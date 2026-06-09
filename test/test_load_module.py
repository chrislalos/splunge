import importlib.util
import os.path
import sys
import unittest
from splunge import util

CODE_FOLDER = "/Users/chris/src/splunge/test/code"

class Tests(unittest.TestCase):
	''' hacky nonsense

	Explicitly set the code folder (this will actually be an envvar)
	Get the parent folder and the basename
	Explicitly add the parent folder to sys.path
	Do an import of the basename - this should succeed because we just added the parent to sys.path
	Create a module name setting the package to the basename
	Get the absolute path of a module
	Call importlib.util.spec_from_file_location(f'{basename.modulePath}', absPath)

	This works because we have dynamically imported a module and given it a dotted name,
	and the package portion is reachable because we added its parent to sys.path and
	then imported it with import_module.

	importlib.import_module() is the only way I've found to load a namespace package
	'''

	def test_load_by_path(self):
		home = os.getenv('HOME')
		expectedCodeFolder = f"{home}/src/splunge/test/code"
		expectedFilename = "rel.py"
		expectedPath = os.path.join(expectedCodeFolder, "rel.py")
		
		(codeFolder, filename) = os.path.split(expectedPath)
		self.assertEqual(expectedCodeFolder, codeFolder)
		self.assertEqual(expectedFilename, filename)

		(root, ext) = os.path.splitext(filename)
		self.assertEqual("rel", root)
		self.assertEqual(".py", ext)
		
		# sys.path.append(codeFolder)
		nsp_name = "mycode"
		# ns = util.create_namespace_package(nsp_name, codeFolder)
		# self.assertIn(nsp_name, sys.modules)
		# util.add_code_folder(nsp_name, codeFolder)
		
		# module_name = f'{nsp_name}.{root}'

		# spec = importlib.util.spec_from_file_location(module_name, expectedPath)
		# mod = importlib.util.module_from_spec(spec)
		# self.assertIsNotNone(spec)
		# self.assertIsNotNone(mod)

		mod = util.load_module(root, codeFolder, nsp_name)
		print(f'mod.__name__={mod.__name__}')
		mod.__spec__.loader.exec_module(mod)
		

	def test_load_by_path2(self):
		codeFolder = os.path.abspath('./www')
		nsp_name = 'mycode'
		moduleName = "meat.foo"
		mod = util.load_module(moduleName, codeFolder, nsp_name)
		print(f'mod.__name__={mod.__name__}')
		mod.__spec__.loader.exec_module(mod)

		# util.add_code_folder(nsp_name, codeFolderPath)
		# spec = importlib.util.spec_from_file_location('mycode.meat.foo', './www/meat/foo.py')
		# mod = importlib.util.module_from_spec(spec)
		# mod.__spec__.loader.exec_module(mod)		

	def test_new_rel(self):
		cwd = os.getcwd()
		codeFolderPath = f'{os.getcwd()}/test/code'
		try:
			self.assertTrue(os.path.exists(codeFolderPath))
			nsp = util.create_namespace_package("codeFolder", codeFolderPath)
			self.assertIsNotNone(nsp)
			# This won't actually work for handling web pages because it imports
			# loads and executes the module. The whole point of splunge is to 
			# load a module but delay execution until after enrichment. But this 
			# is a nice test to confirm that the import works
			import codeFolder.rel # pyright: ignore[reportMissingImports]
		finally:
			os.chdir(cwd)

	def test_no_exec(self):
		pass

	def test_package_name_0(self):
		spec = load_spec_w_python('', 'modules.rel')
		self.assertIsNotNone(spec)

	def test_relative_import(self):
		sys.path.insert(0, "/Users/chris/src/splunge/test")
		relPath = 'modules/rel.py'
		spec = load_spec_w_python(relPath, 'modules.rel')
		self.assertIsNotNone(spec)
		# print(f'spec={spec}')
		mod = importlib.util.module_from_spec(spec)
		self.assertIsNotNone(mod)
		# print(f'mod.relbro.s={mod.relbro.s}')
		# print(f'mod.__package__={mod.__package__}')
		mod.__loader__.exec_module(mod)
		# print(f'mod.relbro.s={mod.relbro.s}')
		# print(f'mod.__package__={mod.__package__}')
		# print(f'mod.relbro.__package__={mod.relbro.__package__}')

	def test_relative_import_clean(self):
		print()
		(packgeName, mod) = import_folder_as_package(CODE_FOLDER)
		urlPath = '/admin/home'
		### convert the url path to a module name and the path to an absolute path
		moduleName = get_module_name_from_url_path(urlPath)
		print(f'moduleName={moduleName}')
		path = get_absolute_module_path(urlPath)
		print(f'path={path}')
		self.assertTrue(os.path.exists(path))
		# # Add codeFolder to sys.path, and load and execute the module
		spec = load_spec_w_python(path, moduleName)
		self.assertIsNotNone(spec)
		mod = importlib.util.module_from_spec(spec)
		print(f'mod.__package__={mod.__package__}')
		self.assertIsNotNone(mod)
		mod.__loader__.exec_module(mod)

	def test_relative_import_clean_2(self):
		## mimic the existence of a code folder and a url path referring to a module
		print()
		(packageName, mod) = import_folder_as_package(CODE_FOLDER)
		### convert the url path to a module name and the path to an absolute path
		urlPath = '/rel'
		moduleName = get_module_name_from_url_path(urlPath)
		print(f'moduleName={moduleName}')
		path = get_absolute_module_path(urlPath)
		print(f'path={path}')
		self.assertTrue(os.path.exists(path))
		# # Add codeFolder to sys.path, and load and execute the module
		spec = load_spec_w_python(path, moduleName)
		print(f'spec.parent={spec.parent}')
		self.assertIsNotNone(spec)
		mod = importlib.util.module_from_spec(spec)
		print(f'mod.__package__={mod.__package__}')
		self.assertIsNotNone(mod)
		mod.__loader__.exec_module(mod)

	
	def test_relative_import_new(self):
		''' A New Hope?
		I've gone to a lot of trouble to coerce Python to ultimately set the __package__ attribute on a loaded
		module such that relative imports from the module. But maybe I can just load the module and then set
		__package__ on the module to something findable? Or is would this just be a weird way to set __package__,
		that wouldn't change the requirement of loading the code folder as a package and giving it a name that
		one way or the other ends up as a dynamically loaded module's __package__ variable.
		
		It might be more idiomatic to give the module a name corresponding to its location, and a __package__ that
		refers to the package from which to do relative imports, seeing as that's the whole point of package. So
		maybe this isn't a huge change but it might be slightly preferable to munging the module name.
		'''
		print()
		# Get the code folder into sys.modules as a package
		# Load module dynamically, naming it after its file name
		# Assign __package__
		# Execute the module

	
	def test_relative_import_so(self):
		sys.path.insert(0, "/Users/chris/src/splunge/test/modules")
		relPath = 'modules/rel.py'
		spec = load_spec_w_python(relPath, 'kids.rel')
		self.assertIsNotNone(spec)
		# print(f'spec={spec}')
		mod = importlib.util.module_from_spec(spec)
		print(f'mod.__package__={mod.__package__}')
		self.assertIsNotNone(mod)
		mod.__loader__.exec_module(mod)
		# print(f'mod.relbro.s={mod.relbro.s}')
		# print(f'mod.__package__={mod.__package__}')
		# print(f'mod.relbro.__package__={mod.relbro.__package__}')

	def test_one_off(self):
		home = os.getenv('HOME')

		codeFolder = f"{home}/src/splunge/test/code"
		sys.path.append(codeFolder)
		ns = util.create_namespace_package('mycode', codeFolder)

		path = f"{codeFolder}/rel.py"
		spec = importlib.util.spec_from_file_location('mycode.rel', path)
		mod = importlib.util.module_from_spec(spec)
		
		spec.loader.exec_module(mod)
		# print(f'mod.__package__={mod.__package__}')
		# print(f'sys.modules["code"]={sys.modules["mycode"]}')
		# sys.path.append(os.path.dirname(os.path.dirname(path)))


	def test_spec_loaders(self):
		relPath = 'modules/foo.py'
		print(f'len(sys.modules)={len(sys.modules)}')
		spec1 = load_spec_w_splunge(relPath)
		print(f'len(sys.modules)={len(sys.modules)}')
		spec2 = load_spec_w_python(relPath, 'foo')
		print(f'len(sys.modules)={len(sys.modules)}')
		# print(f'spec1={spec1}')
		# print(f'spec1.loader={spec1.loader}')
		# print(f'spec2={spec2}')
		# print(f'spec2.loader={spec2.loader}')
		mod1 = importlib.util.module_from_spec(spec1)
		print(f'len(sys.modules)={len(sys.modules)}')
		mod2 = importlib.util.module_from_spec(spec2)
		print(f'len(sys.modules)={len(sys.modules)}')
		# print(f'mod1={mod1}')
		# print(f'mod2={mod2}')
		# print(f'dir(mod1)={dir(mod1)}')
		# print(f'dir(mod2)={dir(mod2)}')
		# print(f'mod1.__package__={mod1.__package__}')
		# print(f'mod2.__package__={mod2.__package__}')

	def test_spec_loaders_rel(self):
		relPath = 'modules/rel.py'
		spec1 = load_spec_w_splunge(relPath)
		spec2 = load_spec_w_python(relPath, 'modules.rel')
		print(f'spec1={spec1}')
		print(f'spec1.loader={spec1.loader}')
		print(f'spec2={spec2}')
		print(f'spec2.loader={spec2.loader}')
		mod1 = importlib.util.module_from_spec(spec1)
		mod2 = importlib.util.module_from_spec(spec2)

		# specModules = load_spec_w_splunge('./modules')
		# self.assertIsNotNone(specModules)
		# modModules = importlib.util.module_from_spec(specModules)
		# sys.modules['modules'] = modModules

		sys.modules['modules.rel'] = mod2
		print(f'mod1={mod1}')
		print(f'mod2={mod2}')
		print(f'dir(mod1)={dir(mod1)}')
		print(f'dir(mod2)={dir(mod2)}')
		print(f'mod1.__package__={mod1.__package__}')
		print(f'mod2.__package__={mod2.__package__}')
		mod2.__spec__.loader.exec_module(mod2)

	def test_spec_loaders_sub(self):
		relPath = 'modules/sub/bum.py'
		spec1 = load_spec_w_splunge(relPath)
		spec2 = load_spec_w_python(relPath, 'sub.bum')
		print(f'spec1={spec1}')
		print(f'spec1.loader={spec1.loader}')
		print(f'spec2={spec2}')
		print(f'spec2.loader={spec2.loader}')
		mod1 = importlib.util.module_from_spec(spec1)
		mod2 = importlib.util.module_from_spec(spec2)
		sys.modules['sub.bum'] = mod2
		print(f'mod1={mod1}')
		print(f'mod2={mod2}')
		print(f'dir(mod1)={dir(mod1)}')
		print(f'dir(mod2)={dir(mod2)}')
		print(f'mod1.__package__={mod1.__package__}')
		print(f'mod2.__package__={mod2.__package__}')
		mod2.__spec__.loader.exec_module(mod2)
	def print_package(self):
		print([el for el in dir(sys.modules[__name__]) if isinstance(el, str) and el.startswith('__') and el.endswith('__')])
		print(f"__file__={sys.modules[__name__].__file__}")
		print(f"__package__={sys.modules[__name__].__package__}")
		print(f"dirname={get_folder()}")


def exec_module(t, moduleName, path):
	sys.path.insert(0, "/Users/chris/src/splunge/test")
	spec = load_spec_w_python(path, moduleName)
	t.assertIsNotNone(spec)
	mod = importlib.util.module_from_spec(spec)
	t.assertIsNotNone(mod)
	mod.__loader__.exec_module(mod)


def get_folder ():
	path = sys.modules[__name__].__file__
	folder = os.path.dirname(path)
	return folder


def load_spec_w_python(path, name):
	print(f'os.path.exists(path)={os.path.exists(path)}')
	spec = importlib.util.spec_from_file_location(name, path)
	return spec


def load_spec_w_splunge(relPath):
	path = os.path.abspath(f"{get_folder()}/{relPath}")
	print(f'os.path.exists(path)={os.path.exists(path)}')
	spec = util.load_module_spec(path)
	return spec


def get_absolute_module_path(urlPath):
	codeFolder = os.path.abspath(CODE_FOLDER)
	path = f'{codeFolder}/{urlPath}.py'
	return path


def get_module_name_from_url_path(urlPath):
	''' admin/foo => {packageName}.admin.foo
	# Drop the .py, split on '/', rejoin on '.' '''
	packageName = os.path.basename(CODE_FOLDER)
	urlPath = urlPath.lstrip('/')
	moduleName = '.'.join(urlPath.split('/'))
	return f'{packageName}.{moduleName}'


def import_folder_as_package(path):
	parentFolder = os.path.dirname(path)
	packageName = os.path.basename(path)
	# sys.path.insert(0, parentFolder)
	# mod = importlib.import_module(packageName)
	print(f'packageName={packageName} path={path}')
	spec = importlib.machinery.PathFinder.find_spec(packageName, path)
	mod = importlib.util.module_from_spec(spec)
	return (packageName, mod)
