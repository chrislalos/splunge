from dataclasses import dataclass
import os
from typing import TYPE_CHECKING
from werkzeug.test import EnvironBuilder
if TYPE_CHECKING:
	from _typeshed.wsgi import WSGIEnvironment
from . import loggin
from . import util
from .mimetypes import mimemap
@dataclass
class Xgi:
	wsgi: "WSGIEnvironment"
	postData = None

	@classmethod
	def create(cls, path='/', base_url=None, query_string=None, method='GET', input_stream=None, content_type=None, content_length=None, errors_stream=None, multithread=False, multiprocess=False, run_once=False, headers=None, data=None, environ_base=None, environ_overrides=None):
		params = locals()
		params.pop('cls')
		wsgi = EnvironBuilder(**params).get_environ()
		xgi = Xgi(wsgi)
		return xgi


	@property
	def contentType(self):
		val = None
		if 'CONTENT_TYPE' in self.wsgi:
			val = self.wsgi['CONTENT_TYPE']
		return val

	@property
	def fileWrapper(self): return getattr(self.wsgi, "file_wrapper", None)

	def __getattr__ (self, name):
		return getattr(self.wsgi, name)

	def __getitem__ (self, key):
		return self.wsgi[key]

	def create_args(self):
		''' Return args (if any) based on http method. '''
		method = self['REQUEST_METHOD'].lower()
		if method == 'get':
			return self.create_get_args()
		elif method == 'post':
			return self.create_post_args()
		return {}

	def create_get_args (self):
		''' Return a dictionary of query string args. '''
		qs = self['QUERY_STRING']
		if not qs:
			return {}
		args = util.parse_query_string(qs)
		return args
					
	# http://wsgi.tutorial.codepoint.net/parsing-the-request-post
	def create_post_args (self):
		''' Return a dictionary of post data args. '''
		# Make sure non-empty post data exists
		postData = self.read_post_data()
		if not postData or self.contentType != 'application/x-www-form-urlencoded':
			return {}
		# Assume post data is a query string and parse it
		loggin.debug(f'type(postData)={type(postData)}')
		if type(postData) == bytes:
			postData = postData.decode('utf-8')
		loggin.debug(f'postData={postData}')
		args = util.parse_query_string(postData)
		return args

	def get_file_name(self):
		return os.path.basename(self.get_path())

	def get_local_path(self):
		''' Return the local path of the resources specified by the wsgi '''
		path = self.get_path().removeprefix("/")
		return os.path.abspath(os.path.join(os.getcwd(), path))

	def get_module_folder(self):
		path = self.get_module_path()
		(folder, _) = os.path.split(path)
		return folder

	def get_module_path(self, code_folder):
		# Get local path, append .py to the path, & confirm the path exists
		path = self.get_path().removeprefix("/")
		modulePath = f'{os.path.join(code_folder, path)}.py'
		return modulePath

	def get_path (self) -> str:
		''' Return the wsgi's path. '''
		return self['PATH_INFO'].strip()

	def get_path_extension (self):
		''' Return the file extension for the wsgi. '''
		path = self.get_path()
		(_, ext) = os.path.splitext(path)
		return ext

	def get_template_path(self, code_folder):
		# Does a .pyp exist? If so, create a template handler and transfer control to it
		module_path = self.get_module_path(code_folder)
		module_path_no_ext, _ = os.path.splitext(module_path)
		templatePath = f'{module_path_no_ext}.pyp'
		return templatePath

	def is_index_page(self):
		path = self['PATH_INFO'].strip()
		flag = False
		if not path or path == '/':
			flag = True
		return flag

	def is_python_markup(self, code_folder):
		''' Check if a request respresents python markup / jinja template.
		
		A request represents a python markup iff
			- Its path has no extension
			- Appending .pyp to the path yields a file that exists in the local
			filesystem
		'''
		ext = self.get_path_extension()
		template_path = self.get_template_path(code_folder)
		template_path_no_ext, _ = os.path.splitext(template_path)
		print(f'ext={ext} template_path={template_path} template_path_no_ext={template_path_no_ext}')
		# Is the path a non-existent file *and* does it lack an extension? (e.g. http://foo.com/app/user)  
		if not ext and not os.path.isfile(template_path_no_ext):
			if os.path.isfile(template_path):
				return True
		return False


	def is_python_module(self, code_folder):
		''' Check if a request respresents a python module.
		
		A request represents a python module iff
			- Its path has no extension
			- Appending .py to the path yields a file that exists in the local
			filesystem
		'''
		ext = self.get_path_extension()
		module_path = self.get_module_path(code_folder)
		module_path_no_ext, _ = os.path.splitext(module_path)
		print(f'ext={ext} module_path={module_path} module_path_no_ext={module_path_no_ext}')
		# Is the path a non-existent FILE and does it lack an extension? (e.g. http://foo.com/app/user)  
		if not ext and not os.path.isfile(module_path_no_ext):
			# If it exists as a file with a .py ext, use PythonHandler
			if os.path.isfile(module_path):
				return True
		return False

	def has_template_path(self, code_folder):
		# Does a .pyp exist? If so, create a template handler and transfer control to it
		templatePath = self.get_template_path(code_folder)
		return os.path.exists(templatePath)

	def load_module(self):
		# Get local path, append .py to the path, & confirm the path exists
		modulePath = self.get_module_path()
		loggin.info(f'modulePath={modulePath}')
		if not os.path.exists(modulePath):
			raise Exception(f'module path not found: {modulePath}')
		# Load the module
		module = util.load_module_by_path(modulePath)
		return module

	def open_by_path (self):
		localPath = self.get_local_path()
		f = open(localPath, 'rb')
		return f
		
	def open_template (self, code_folder):
		localTemplatePath = self.get_template_path(code_folder)
		f = open(localTemplatePath, 'rb')
		return f
		
	def read_post_data(self):
		if not self.postData:
			contentLength = self.get('CONTENT_LENGTH')
			# PEP 3333 says CONTENT_LENGTH may be omitted
			if not contentLength:
				return None
			contentLength = int(contentLength)
			post_input = self.get('wsgi.input')
			if not post_input:
				return None
			self.postData = post_input.read(contentLength)
		return self.postData
