import os.path
from .Response import Response
from . import util
from .HttpEnricher import enrich_module


class FileHandler:
	def handleRequest (self, wsgi):
		done = False
		try:
			f = util.open_by_path(wsgi)
			util.respond_with_file(wsgi. resp, f)
			done = True
		except FileNotFoundError:
			# We want this to be handled at a higher level
			pass
		return done


class PythonModuleHandler:
	def handle_request (self, wsgi):
		# Get local path, append .py to the path, & confirm the file exists
		localPath = util.get_local_path(wsgi)
		module_path = f'{localPath}.py'
		if not os.path.exists(module_path):
			raise Exception(f'module path not found: {module_path}')
		# Load the module
		module = util.load_module(module_path)
		if not module:
			raise Exception(f'module not found: {module_path}')
		# Enrich the module
		enrich_module(module, wsgi)
		# Execute the module
		module_state = util.exec_module(module)
		resp = Response()
		# Does stdout exist? If so, use it for output
		if not util.is_io_empty(module_state.stdout):
			s = module_state.stdout.getvalue()
			resp.iter = [s]
		else:
			# Get output args
			args = util.get_module_args(module)
			# Does _ exist? If so use it as a template
			if '_' in args:
				sTemplate = args.pop('_')
				s = util.render_string(sTemplate, args)
				resp.add_line(s)
			else:
				# Does a .pyp exist? If so, create a template handler and transfer control to it
				templatePath = f'{localPath}.pyp'
				if os.path.exists(templatePath):
					handler = PythonTemplateHandler()
					return handler.handle_request(wsgi, args)
				else:
					# Render the content as a nice table
					for key, val in args.items():
						line = '{}={}'.format(key, val)
						resp.add_line(line) 
			return (resp, True)
	

class PythonTemplateHandler:
	def __init__ (self, *, encoding='latin-1'):
		self.encoding = encoding

	def handle_request (self, wsgi, args={}):
		# Get local path, append .pyp to the path, & confirm the file exists
		localPath = util.get_local_path(wsgi)
		templatePath = f'{localPath}.pyp'
		# Load the template & render it w wsgi args
		if not os.path.exists(templatePath):
			raise Exception(f'template path not found: {templatePath}')
		wsgi_args = util.create_wsgi_args(wsgi)
		args.update(wsgi_args)
		content = util.render_template(templatePath, args)
		# encodedContent = content.encode(self.encoding)
		# Initialize the response + return
		resp = Response()
		resp.headers.set('Content-Type', 'text/html')
		resp.add_line(content)
		return (resp, True)