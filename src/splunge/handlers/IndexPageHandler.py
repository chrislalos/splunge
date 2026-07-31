import mimetypes
import os
from .. import constants
from ..loggin import debug
from ..Response import Response
from .BaseHandler import BaseHandler

class IndexPageHandler(BaseHandler):
	fallbackIndexPage = 'index.html'
	indexPageMap = {
		"/index.py": "/index", 
		"/index.pyp": "/index",
		"/index.html": None,
		"/index.htm": None
	}

	def handle_request(self) -> Response:
		for indexPage, indexUrl in self.indexPageMap.items():
			indexPagePath = f'{os.getcwd()}{indexPage}'
			exists = os.path.exists(indexPagePath)
			debug(f'absPath={indexPagePath:60} exists={exists}')
			if exists:
				if indexUrl:
					return Response.create_redirect(303, f'Redirecting to {indexUrl}', indexUrl)
				return self._serve_file(indexPagePath)
		return self._serve_file(f'{os.getcwd()}/{self.fallbackIndexPage}')

	def _serve_file(self, path):
		mimeType, _ = mimetypes.guess_type(path)
		if not mimeType or mimeType == 'text/html':
			mimeType = constants.MT_html
		with open(path, 'rb') as f:
			return Response.create_from_file(f, mimeType)


