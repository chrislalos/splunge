from ..Response import Response
from ..Xgi import Xgi
from .BaseHandler import BaseHandler

class IndexPageHandler(BaseHandler):
	index_page_list = ["/index.html"]
	''' Handle index page requests by redirection to /index.html. '''

	def handle_request(self) -> Response:
		# @note it might be better to iterate over multiple options and use the one that exists
		location = self.index_page_list[0]
		statusCode = 303
		statusMessage = f'Redirecting to {location}'
		resp = Response.create_redirect(statusCode, statusMessage, location)
		return resp


