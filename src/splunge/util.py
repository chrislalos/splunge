import contextlib
from importlib.machinery import FileFinder
from importlib.machinery import SourceFileLoader
import importlib.util
import io
import jinja2
import os.path
import sys


def argsToTuple (*args, length):
#	print('*** args: {}'.format(args), file=sys.stderr)
#	print('len(args)={}'.format(len(args)), file=sys.stderr)
	if len(args) == length:
		t = tuple(args)
	elif len(args) == 1 and isinstance(args[0], (list, tuple)) and len(args[0]) == length:
		t = tuple(args[0])
	else:
		raise Exception('Arguments must either be {} value(s) or a list or tuple {} element(s) long'.format(length, length))
	return t



def createHttpObject (req):
		http = type('', (), {})()                      # Creates an anonymous class and instantiates it
		http.env = req.env
		http.method = req.method
		http.path = req.path
		http.args = req.args
		return http


def createModuleExtras (req, resp):
	moduleExtras = type('ModuleExtras', (), {})
	moduleExtras.http = createHttpObject(req)
	moduleExtras.response = resp
	moduleExtras.addHeader =      lambda name, value: resp.addHeader(name, value)
	moduleExtras.validateMethod = lambda validMethods: validateMethod(req.method, validMethods)
	moduleExtras.redirect =       lambda url: { response.redirect(url) }
	moduleExtras.setContentType = lambda contentType: response.setContentType(contentType)
	return moduleExtras
		# import exceptions




######################################################################################
#
# Splunge's enhanced exec module function.
#
# This function tries to do as little as possible, so it delegates the actual module
# execution to the modules own exec() method, as it should.
# 
# The only difference, is that this function captures the dir() of the module before
# and after. This lets the function detect which attributes have been added by module
# execution, which it assumes are of interest to the user. If no .pyp template file is
# defined, then the response body consists of name/value pairs of all these attributes.
#
# There are two ways that a module, once executed, can indicate that processing should
# halt.
#
# One is by writing to stdout, which is a quick and cheap way of writing a response.
# The other is by setting _ to either binary content, a data structure, or a template string.
def execModule (module):
	attrs1 = set(dir(module))
	f = io.StringIO()
	with contextlib.redirect_stdout(f):
		module.exec()
	attrs2 = set(dir(module))
	newAttrs = [el for el in attrs2 if el not in attrs1 and el != '__builtins__']
	args = {'http': module.http}
	for attr in newAttrs:
		val = getattr(module, attr)
		# We don't want to include functions or classes
		if not callable(val): # and not inspect.isclass(val)
			args[attr] = getattr(module, attr)
	return args


def execModuleSpec (moduleSpec, moduleExtras):
	module = importlib.util.module_from_spec(moduleSpec)
	if moduleExtras:
		module.__dict__.update(moduleExtras.__dict__)
	attrs1 = set(dir(module))
	f = io.StringIO()
	with contextlib.redirect_stdout(f):
		moduleSpec.loader.exec_module(module)
	bHasShortcut = hasattr(module, '_') 
	bHasStdout = hasStdout(f)
	bGotoTemplate = not (bHasShortcut or bHasStdout)
	setattr(moduleSpec, 'gotoTemplate', bGotoTemplate)
	setattr(moduleSpec, 'hasShortcut', bHasShortcut)
	setattr(moduleSpec, 'hasStdout', bHasStdout)
	setattr(moduleSpec, 'stdout', f)
	args = {}
	if hasattr(module, 'http'):
		args['http'] = module.http
	attrs2 = set(dir(module))
	newAttrs = [el for el in attrs2 if el not in attrs1 and el != '__builtins__']
	for attr in newAttrs:
		val = getattr(module, attr)
		# We don't want to include functions or classes
		if not callable(val): # and not inspect.isclass(val)
			args[attr] = getattr(module, attr)
	setattr(moduleSpec, 'args', args)
	
	
def loadModuleSpec (path):
	# Simple filename / path stuff
	(folder, filename) = os.path.split(path)
	print("folder=" + folder, file=sys.stderr)
	print("filename=" + filename, file=sys.stderr)
	(moduleName, ext) = os.path.splitext(filename)
	print("moduleName={}".format(moduleName, file=sys.stderr))
	# Enter the weirdness: pass a (loader class, file extension) tuple, wrapped in a list, to
	# the c'tor of importlib's FileFinder. Use the file finder to 'find' a module spec (which
	# is sort of metainfo on a module), then use import machinery to turn the spec into a 
	# module.
	loaderArgs = (SourceFileLoader, [ext])
	finder = FileFinder(folder, loaderArgs)
	spec = finder.find_spec(moduleName)
	return spec


def hasStdout (stringIO):
	markCur = stringIO.tell()
	stringIO.seek(0, io.SEEK_END)
	markEnd = stringIO.tell()
#	print("markEnd={}".format(markEnd))
	flag = (markEnd > 0)
	stringIO.seek(markCur, io.SEEK_SET)
	return flag


# Shorthand for invoking jinja on a template string
def renderString (s, args):
	jenv = jinja2.Environment()
	jtemplate = jenv.from_string(s)
	s = jtemplate.render(args)
	return s


# Shorthand for invoking jinja on a template path
def renderTemplate (templatePath, args):
#	print("*** {}".format(os.getcwd()), file=sys.stderr)
	jloader = jinja2.FileSystemLoader(os.getcwd(), followlinks=True)
	jenv = jinja2.Environment(loader=jloader)
	templateName = os.path.basename(templatePath)
	jtemplate = jenv.get_template(templateName)
	if not args:
		args = {}
	s = jtemplate.render(args)
	return s 


def validateMethod (method, methods):
	if isinstance(methods, str):
		methods = [ methods ]
	if not method in [s.upper() for s in methods]:
		raise InvalidMethodEx(method, methods)

