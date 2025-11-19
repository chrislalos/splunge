import io
import os
import textwrap
import unittest
from markdown_it import MarkdownIt
from werkzeug.test import create_environ
from splunge import app, constants, util, MarkdownHandler, Response

class MarkdownTests(unittest.TestCase):
	def test_hello(self):
		localPath = 'www/hello.md'
		urlPath = f'/{localPath}'
		# Create a wsgi + then create a handler for it
		wsgi = create_environ(urlPath)
		handler = app.create_handler(wsgi)
		self.assertIsNotNone(handler)
		self.assertIsInstance(handler, MarkdownHandler)
		# Execute the handler
		(resp, isDone) = handler.handle_request(wsgi)
		self.assertIsNotNone(resp)
		self.assertIs(type(resp), Response)
		self.assertTrue(isDone)
		self.assertIsInstance(resp.iter, list)
		self.assertEqual(1, len(resp.iter))	
		self.assertIsNotNone(resp.iter[0])
		content = resp.iter[0]
		# Create expected output & test
		content_expected = load_markdown_content(localPath)
		self.assertEqual(content_expected, content)

		
def load_markdown_content(path):
	title = os.path.basename(path)
	pre = constants.html_pre
	post = constants.html_post
	with open(path, 'r') as f:
		frag = MarkdownIt().render(f.read())
		content = util.html_fragment_to_doc(frag, title=title, pre=pre, post=post)	
	return f'{content}\r\n'.encode('latin-1')
	
