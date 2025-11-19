import io
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
		# Create expected output
		sio = io.StringIO()
		title = util.get_file_name(wsgi)
		print(textwrap.dedent(constants.html_pre).format(title), file=sio)
		with open(localPath, 'r') as f:
			s = MarkdownIt().render(f.read())
			lines = s.split('\n')
			for line in lines:
				print(f'\t\t{line}', file=sio)
			print(textwrap.dedent(constants.html_post), file=sio)
			print('\r\n', end='', file=sio)
		sio.seek(0)
		content_expected = sio.read().encode('utf-8')
		print(f'content_expected\n{content_expected}\n')
		print(f'content\n{content}\n')
		# Test
		self.assertEqual(content_expected, content)

		
		
