from http.cookies import SimpleCookie
import importlib
import io
import os
import re
import textwrap
from typing import NamedTuple, TYPE_CHECKING
if TYPE_CHECKING:
	from _typeshed.wsgi import WSGIEnvironment
import urllib
from importlib.machinery import FileFinder, SourceFileLoader
import jinja2

from . import constants, loggin


def context_to_bytes(context: dict) -> bytes:
	f = io.StringIO()
	# Render the content as a nice table
	for key, val in context.items():
		line = '{}={}'.format(key, val)
		print(line, file=f)
	buf = f.getvalue().encode('utf-8')
	return buf


def create_cookie_value(name, value, **kwargs):
	d = {name: value}
	d.update(kwargs)
	cookie = SimpleCookie(d)
	morsel = cookie[name]
	cookieValue = morsel.OutputString()
	return cookieValue


# def exec_module(module):
# 	""" Execute an enriched module & return a ModuleExecutionResponse.

# 	"""
# 	# Redirect stdout to a new StringIO and execute module
# 	moduleStdout = io.StringIO()
# 	with contextlib.redirect_stdout(moduleStdout):
# 		module.__spec__.loader.exec_module(module)
# 	# Create the module state
# 	moduleContext = get_module_context(module)
# 	moduleResponse = module.http.resp
# 	moduleState = ModuleExecutionResponse(context=moduleContext, stdout=moduleStdout, response=moduleResponse)
# 	return moduleState


# def addCookie (name, value, **kwargs): 
# 	cookiejar = SimpleCookie()
# 	cookiejar[name] = value
# 	cookie = cookiejar[name]
# 	cookie.update(kwargs)
# 	headerName = 'Set-Cookie'
# 	headerValue = cookie.OutputString()
# 	resp.setHeader(headerName, headerValue)



def get_attr_names(module, attrNamesBefore=None):
	''' Return all a module's attribute names.

	Filter out 'special' attributes
	  - all callables
	  - all user-defined types
	  - all __internal__ attributes, eg `__name__`
	'''
	rx = re.compile('__.*__')
	attrNames= [el for el in set(dir(module))
			    if not callable(getattr(module, el, None))
				and not isinstance(el, type)
				and not rx.match(el)]
	return attrNames


def get_module_attrs(module):
	attrNames = get_attr_names(module)
	attrs = {name: getattr(module, name, None) for name in attrNames}
	return attrs


def get_module_context (module):
	''' Return the args set during module execution

	    If the special _ attribute has been set, use that
		If _ is not set, then use all attributes set during module execution
	'''
	args = get_module_attrs(module)
	args.pop('http', None)
	sTemplate = None
	if '_' in args:
		sTemplate = args.pop('_')
	return (args, sTemplate)
	# @note - this function needs to check for the existence of '_'
	# args = {}
	# # Create a set of the module's attrs post-execution, and filter
	# attrs2 = set(dir(module))
	# newAttrs = [el for el in attrs2 if el not in attrsBefore and el not in ['__builtins__', 'http']]
	# for attr in newAttrs:
	# 	val = getattr(module, attr)
	# 	# We don't want to include functions or classes
	# 	if not callable(val) and not inspect.isclass(val):
	# 		args[attr] = val


def get_folder(path):
	(folder, _) = os.path.split(path)
	return folder

def html_fragment_to_doc(frag, *, title='', pre=constants.html_pre, post=constants.html_post):
	sio = io.StringIO()
	print(textwrap.dedent(pre.format(title)), file=sio)
	fragLines = frag.split('\n')
	for line in fragLines:
		print(f'\t\t{line}', file=sio)
	print(textwrap.dedent(post), file=sio)
	sio.seek(0)
	return sio.read()


# Check if an IO is empty, by moving to the end and confirming it is zero. 
# (This saves the cursor position before checking, and restores it afterwards)
def is_io_empty (anIo):
	''' Check if an io (eg StringIO) is empty or not. '''
	if not anIo:
		return True
	cur = anIo.tell()
	end = anIo.seek(0, io.SEEK_END)
	isEmpty = (end == 0)
	anIo.seek(cur, io.SEEK_SET)
	return isEmpty


def load_module_by_path (path):
	''' Load a python module by path using importlib machinery. '''
	# create the module path and load the module using machinery
	moduleSpec = load_module_spec(path)
	if not moduleSpec:
		raise Exception(f'No module spec found for path={path}')
	module = importlib.util.module_from_spec(moduleSpec)
	return module


def load_module_spec (path):
	''' Return a ModuleSpec for the specified path using importlib machinery.
	
	The importlib machinery's process is a little weird.
	  - Instantiate a loader class, eg importlib.machinery.SourceFileLoader
	  - Instantiate a FileFinder from a path, the loader object, and a file extension (.py)
	  - Use the FileFinder to lookup the spec.

	It's strange to take a path, break it into a local folder and an extension,
	create a FileFinder for the specific path and extension, and then immediately
	use that FileFinder to return a ModuleSpec. Seems like the importlib.machinery
	could do all that given a path. But it can't. That's what this function is for.
	'''
	splitPath = split_module_path(path)
	folder, moduleName, ext = splitPath.folder, splitPath.moduleName, splitPath.ext	
	loaderArgs = (SourceFileLoader, [ext])
	finder = FileFinder(folder, loaderArgs)
	spec = finder.find_spec(moduleName)
	return spec


def parse_query_string(qs):
	if not qs:
		return {}
	args_raw = urllib.parse.parse_qs(qs)
	args = {}
	# Convert single-items lists into simple values
	for key, v in args_raw.items():
		if v:
			if len(v) == 1:
				value = v[0]
			else:
				value = v
			args[key] = value
	return args


def render_filelike(f, context={}):
	with f:
		s = f.read().decode('utf-8')
	return render_string(s, context)

def render_string(sTemplate, context={}):
	jenv = jinja2.Environment()
	loggin.debug(f'sTemplate={sTemplate}')
	jtemplate = jenv.from_string(sTemplate)
	if not context:
		context = {}
	s = jtemplate.render(context)
	return s

# Shorthand for invoking jinja on a template path
def render_template (templatePath, context={}):
#	print("*** {}".format(os.getcwd()), file=sys.stderr)
	cwd = os.getcwd()
	jloader = jinja2.FileSystemLoader(cwd, followlinks=True)
	jenv = jinja2.Environment(loader=jloader)
	templateName = os.path.relpath(templatePath, cwd)
	jtemplate = jenv.get_template(templateName)
	if not context:
		context = {}
	s = jtemplate.render(context)
	return s 


def split_module_path(path):
	''' Return a named tuple of the path split into a folder, module name, and extension.
	
	@note this does not validate that the path represents a module.
	'''
	
	(folder, filename) = os.path.split(path)
	(moduleName, ext) = os.path.splitext(filename)
	SplitPath = NamedTuple('splitPath', [('folder', str),
				                         ('moduleName', str),
				                         ('ext', str)])
	return SplitPath(folder, moduleName, ext)


def validate_method (method, methods):
	''' Check if a method exists in a collection of methods.

	If the arg under test is None, return False.
	If the 'collection of methods' is just a single string, fake it.
	This function is case insensitive.
	'''
	if not method or not methods:
		return False
	if isinstance(methods, str):
		methods = [ methods ]
	if not method.lower() in [s.lower() for s in methods]:
		return False
	return True
