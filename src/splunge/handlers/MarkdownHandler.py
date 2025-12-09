import io
from markdown_it import MarkdownIt
from .. import util
from ..Headers import Headers
from ..Response import Response
from ..Xgi import Xgi
from .HtmlGenHandler import HtmlGenHandler


class MarkdownHandler(HtmlGenHandler):
	def gen_html(self, f, context: dict=None):
		with f:	
			content = f.read().decode('utf-8')
		md = MarkdownIt()
		frag = md.render(content).rstrip()
		title = self.xgi.get_file_name()
		html = util.html_fragment_to_doc(frag, title=title)
		return html
