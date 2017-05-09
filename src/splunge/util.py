import contextlib
from http.cookies import SimpleCookie
from importlib.machinery import FileFinder
from importlib.machinery import SourceFileLoader
import importlib.util
import inspect
import io
import jinja2
import os.path
import sys
from splunge import mimetypes
from splunge.ExecModuleState import ExecModuleState

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


def createCookie (name, value, *, comment=None, domain=None, expires=None, httpOnly=True,
	               maxAge=None, path='/', secure=False, version=1):
	cookieJar = SimpleCookie()
	cookieJar[name] = value
	cookie = cookieJar[name]
	if comment: cookie['comment'] = comment
	if domain: cookie['domain'] = domain
	if expires: cookie['expires'] = expires
	if httpOnly: cookie['httponly'] = httpOnly
	if maxAge: cookie['max-age'] = maxAge
	if path: cookie['path'] = path
	if secure: cookie['secure'] = secure
	if version: cookie['version'] = version
	return cookie


def createHttpObject (req):
	http = type('', (), {})()                      # Creates an anonymous class and instantiates it
	http.env = req.env
	http.method = req.method
	http.path = req.path
	http.args = req.args
	return http


def createModule (req, resp):
	# create the module path and load the module using machinery
	modulePath = '{}.py'.format(req.localPath)
	moduleSpec = loadModuleSpec(modulePath)
	module = importlib.util.module_from_spec(moduleSpec)
	# create the extras and add them
	moduleExtras = createModuleExtras(req, resp)
	module.__dict__.update(moduleExtras.__dict__)
	return module


def createModuleExtras (req, resp):
	def addCookie (name, value, **kwargs): 
		cookiejar = SimpleCookie()
		cookiejar[name] = value
		cookie = cookiejar[name]
		cookie.update(kwargs)
		headerName = 'Set-Cookie'
		headerValue = cookie.OutputString()
		print('*** Adding cookie: {}: {}'.format(headerName, headerValue))
		resp.setHeader(headerName, headerValue)
	
	def pypinfo (env):
		for key, value in sorted(env.items()):
			print('{}={}'.format(key, value))
		return None

	moduleExtras = type('ModuleExtras', (), {})()
	moduleExtras.http = createHttpObject(req)
	moduleExtras.response = resp
	moduleExtras.addCookie =      lambda name, value: addCookie(name, value)
	moduleExtras.pypinfo =        lambda: pypinfo(req.env)
	# moduleExtras.pypinfo =        lambda: None
	moduleExtras.validateMethod = lambda validMethods: validateMethod(req.method, validMethods)
	moduleExtras.redirect =       lambda url: { resp.redirect(url) }
	moduleExtras.setContentType = lambda contentType: resp.setContentType(contentType)
	moduleExtras.setHeader =      lambda name, value: resp.setHeader(name, value)
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
	attrsBefore = set(dir(module))
	newStdout = io.StringIO()
	with contextlib.redirect_stdout(newStdout):
		module.__spec__.loader.exec_module(module)
	moduleState = ExecModuleState()
	print('*** dir(moduleState)')
	print(dir(moduleState))
	moduleState.args = getModuleArgs(module, attrsBefore)
	moduleState.shortcut = getattr(module, '_', None) 
	if not isIoEmpty(newStdout):
		print('*** newStdout is not empty')
		moduleState.stdout = newStdout
#	else:
#		moduleState.stdout = None
	return moduleState

# def execModule (module):
# 	attrs1 = set(dir(module))
# 	f = io.StringIO()
# 	with contextlib.redirect_stdout(f):
# 		module.exec()
# 	attrs2 = set(dir(module))
# 	newAttrs = [el for el in attrs2 if el not in attrs1 and el != '__builtins__']
# 	args = {'http': module.http}
# 	for attr in newAttrs:
# 		val = getattr(module, attr)
# 		# We don't want to include functions or classes
# 		if not callable(val): # and not inspect.isclass(val)
# 			args[attr] = getattr(module, attr)
# 	return args



def execModuleSpec (moduleSpec, moduleExtras):
	module = importlib.util.module_from_spec(moduleSpec)
	moduleState = execModule(module)
	return moduleState
	
	
def getMimeType (path):
	defaultMimeType = 'application/octet-steam'
	(_, ext) = os.path.splitext(path)
	if not ext:
		mimeType = defaultMimeType
	else:
		mimeType = mimetypes.map.get(ext, defaultMimeType)
	return mimeType


def getModuleArgs (module, attrsBefore):
	args = {}
	attrs2 = set(dir(module))
	newAttrs = [el for el in attrs2 if el not in attrsBefore and el not in ['__builtins__', 'http']]
	for attr in newAttrs:
		val = getattr(module, attr)
		# We don't want to include functions or classes
		if not callable(val) and not inspect.isclass(val):
			args[attr] = val
	return args


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


# Check if an IO is empty, by moving to the end and confirming it is zero. 
# (This saves the cursor position before checking, and restores it afterwards)
def isIoEmpty (anIo):
	cur = anIo.tell()
	end = anIo.seek(0, io.SEEK_END)
	isEmpty = (end == 0)
	anIo.seek(cur, io.SEEK_SET)
	return isEmpty


# Shorthand for invoking jinja on a template string
def renderString (s, args):
	jenv = jinja2.Environment()
	jtemplate = jenv.from_string(s)
	s = jtemplate.render(args)
	return s


# Shorthand for invoking jinja on a template path
def renderTemplate (templatePath, args):
#	print("*** {}".format(os.getcwd()), file=sys.stderr)
	cwd = os.getcwd()
	jloader = jinja2.FileSystemLoader(cwd, followlinks=True)
	jenv = jinja2.Environment(loader=jloader)
	templateName = os.path.relpath(templatePath, cwd)
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

