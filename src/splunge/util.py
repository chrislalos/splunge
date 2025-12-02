import contextlib
from http.cookies import SimpleCookie
import importlib
import io
import os
import re
import sys
import textwrap
from typing import NamedTuple, TYPE_CHECKING
if TYPE_CHECKING:
	from _typeshed.wsgi import WSGIEnvironment
import urllib
from importlib.machinery import FileFinder, SourceFileLoader
import jinja2
import werkzeug

from . import constants, loggin
from .mimetypes import mimemap


def create_cookie_value(name, value, **kwargs):
	d = {name: value}
	d.update(kwargs)
	cookie = SimpleCookie(d)
	morsel = cookie[name]
	cookieValue = morsel.OutputString()
	return cookieValue


def create_get_args (wsgi):
	''' Return a dictionary of query string args. '''
	qs = wsgi['QUERY_STRING']
	if not qs:
		return {}
	args = parse_query_string(qs)
	return args
				

# http://wsgi.tutorial.codepoint.net/parsing-the-request-post
def create_post_args (wsgi):
	''' Return a dictionary of post data args. '''
	# Make sure non-empty post data exists
	postData = read_post_data(wsgi)
	contentType = wsgi['CONTENT_TYPE']
	if not postData or contentType != 'application/x-www-form-urlencoded':
		return {}
	# Assume post data is a query string and parse it
	if type(postData) == bytes:
		postData = postData.decode('utf-8')
	args = parse_query_string(postData)
	return args


def create_wsgi_args(wsgi):
	''' Return args (if any) based on http method. '''
	method = wsgi['REQUEST_METHOD'].lower()
	if method == 'get':
		return create_get_args(wsgi)
	if method == 'post':
		return create_post_args(wsgi)
	return {}


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
# 	print('*** Adding cookie: {}: {}'.format(headerName, headerValue))
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


def get_file_name(wsgi):
	return os.path.basename(get_path(wsgi))


def get_folder(path):
	(folder, _) = os.path.split(path)
	return folder


def get_local_path(wsgi):
	''' Return the local path of the resources specified by the wsgi '''
	path = get_path(wsgi)
	return os.path.abspath(os.getcwd() + path)


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


def get_module_folder(wsgi):
	path = get_module_path(wsgi)
	(folder, _) = os.path.split(path)
	return folder


def get_module_path(wsgi):
	# Get local path, append .py to the path, & confirm the path exists
	localPath = get_local_path(wsgi)
	modulePath = f'{localPath}.py'
	return modulePath


def get_path (wsgi):
	''' Return the wsgi's path. '''
	return wsgi['PATH_INFO'].strip()


def get_path_extension (wsgi):
	''' Return the file extension for the wsgi. '''
	path = get_path(wsgi)
	(_, ext) = os.path.splitext(path)
	return ext


def get_template_path(wsgi):
	# Does a .pyp exist? If so, create a template handler and transfer control to it
	localPath = get_local_path(wsgi)
	templatePath = f'{localPath}.pyp'
	return templatePath


def html_fragment_to_doc(frag, *, title='', pre=constants.html_pre, post=constants.html_post):
	sio = io.StringIO()
	print(textwrap.dedent(pre.format(title)), file=sio)
	fragLines = frag.split('\n')
	for line in fragLines:
		print(f'\t\t{line}', file=sio)
	print(textwrap.dedent(post), file=sio)
	sio.seek(0)
	return sio.read()


def is_index_page(wsgi):
	path = wsgi['PATH_INFO'].strip()
	print(f'path={path}')
	flag = False
	if not path or path == '/':
		flag = True
	return flag


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


def load_module(wsgi: "WSGIEnvironment"):
	# Get local path, append .py to the path, & confirm the path exists
	modulePath = get_module_path(wsgi)
	loggin.info(f'modulePath={modulePath}')
	if not os.path.exists(modulePath):
		raise Exception(f'module path not found: {modulePath}')
	# Load the module
	module = load_module_by_path(modulePath)
	return module


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


def open_by_path (wsgi):
	localPath = get_local_path(wsgi)
	f = open(localPath, 'rb')
	return f
	

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


def pypinfo (wsgi):
	for key, value in sorted(wsgi.items()):
		print('{}={}'.format(key, value))
	return None


def read_post_data(wsgi):
	# PEP 3333 says CONTENT_LENGTH may be omitted
	contentLength = wsgi.get('CONTENT_LENGTH')
	if not contentLength:
		return None
	contentLength = int(contentLength)
	post_input = wsgi.get('wsgi.input')
	if not post_input:
		return None
	d = post_input.read(contentLength)
	return d


def render_string(sTemplate, context):
	jenv = jinja2.Environment()
	jtemplate = jenv.from_string(sTemplate)
	s = jtemplate.render(context)
	return s

# Shorthand for invoking jinja on a template path
def render_template (templatePath, args={}):
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


def respond_with_file(wsgi, resp, f):
	_32K = 32768
	if 'wsgi.file_wrapper' in wsgi:
		resp.iter = wsgi['wsgi.file_wrapper'](f, _32K)
	else:
		with f:
			resp.iter = [f.read()]
		


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
