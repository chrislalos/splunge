import io
import os
from .. import loggin, util
from ..Response import Response
from ..Xgi import Xgi
from .HtmlGenHandler import HtmlGenHandler


class PythonTemplateHandler(HtmlGenHandler):
	def open_content(self):
		loggin.debug(f'{self.__class__.__name__}.open_content()')
		return self.xgi.open_template()

	def gen_html(self, f, context: dict=None):
		loggin.debug(f'{self.__class__.__name__}.gen_html()')
		html = util.render_filelike(f, context)
		f.close()
		return html
