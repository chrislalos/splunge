from .. import loggin
from ..Response import Response
from .BaseHandler import BaseHandler


class FileHandler(BaseHandler):
	@classmethod
	def respond_with_file(cls, f, mimeType, fileWrapper) -> Response:
		resp = None
		if fileWrapper:
			resp = Response.create_from_file_wrapper(f, fileWrapper, mimeType)
		else:
			resp = Response.create_from_file(f, mimeType)
		return resp

	def get_output_as_filelike(self, context: dict=None):
		loggin.debug(f'{self.__class__.__name__}.get_output_as_filelike')
		return self.xgi.open_by_path()

	def get_mime_type(self):
		from . import lookup_mime_type
		mimeType = lookup_mime_type(self.xgi)
		return mimeType
	
	def handle_request (self, context: dict=None) -> Response:
		f = self.get_output_as_filelike(context)
		mimeType = self.get_mime_type()
		resp = self.respond_with_file(f, mimeType, self.xgi.fileWrapper)
		return resp
