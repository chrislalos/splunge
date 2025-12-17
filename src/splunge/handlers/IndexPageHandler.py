import os
from ..Response import Response
from ..Xgi import loggin
from .BaseHandler import BaseHandler

class IndexPageHandler(BaseHandler):
	fallbackIndexPage = 'index.html'
	indexPageMap = {
		"/index.py": "/index", 
		"/index.pyp": "/index",
		"/index.html": None,
		"/index.htm": None
	}
	''' Handle index page requests by redirection to /index.html. '''

	def handle_request(self) -> Response:
		# @note it might be better to iterate over multiple options and use the one that exists
		for indexPage, indexUrl in self.indexPageMap.items():
			indexPagePath = f'{os.getcwd()}{indexPage}'
			exists = os.path.exists(indexPagePath)
			loggin.debug(f'absPath={indexPagePath:60} exists={exists}')
			if exists:
				location = indexUrl or indexPage
				break
		# if the location isn't found, redirect to index.html which will 404. gotta do somethin!
		if not location:
			location = self.fallbackIndexPage
		statusCode = 303
		statusMessage = f'Redirecting to {location}'
		resp = Response.create_redirect(statusCode, statusMessage, location)
		return resp


