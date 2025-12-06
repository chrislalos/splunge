import io
import os
import textwrap
import unittest
from markdown_it import MarkdownIt
from werkzeug.test import create_environ
from splunge import app, constants, util, MarkdownHandler, Response
from splunge.Xgi import Xgi

class MarkdownTests(unittest.TestCase):
	def test_hello(self):
		# setup paths
		localPath = 'www/hello.md'
		urlPath = f'/{localPath}'
		# create a handler for the path + execute it
		content = handle_request(self, urlPath)
		# Create expected output & test
		content_expected = load_markdown_content(localPath)
		self.assertEqual(content_expected, content)

		

def create_markdown_handler(testcase, path):
	# Create a wsgi + then create a handler for it
	xwsgi = create_xgi(path)
	handler = app.create_handler(xwsgi)
	testcase.assertIsNotNone(handler)
	testcase.assertIsInstance(handler, MarkdownHandler)
	return handler


def handle_request(testcase, path):
	handler = create_markdown_handler(testcase, path)
	wsgi = create_environ(path)
	xgi = Xgi(wsgi)
	(resp, isDone) = handler.handle_request(xgi)
	testcase.assertIsNotNone(resp)
	testcase.assertIs(type(resp), Response)
	testcase.assertTrue(isDone)
	testcase.assertIsInstance(resp.iter, list)
	testcase.assertEqual(1, len(resp.iter))	
	testcase.assertIsNotNone(resp.iter[0])
	return resp.iter[0]


def load_markdown_content(path):
	''' Load the expected markdown content for the path.
		
	This is a concatenation of ...
		- stock html_pre
		- html conversion of the rstripped markdown loaded from the path
		- stock html_post
	The converted html's <title> tag is set to the path's filename.
	'''
	title = os.path.basename(path)
	pre = constants.html_pre
	post = constants.html_post
	with open(path, 'r') as f:
		frag = MarkdownIt().render(f.read())
		content = util.html_fragment_to_doc(frag.rstrip(), title=title, pre=pre, post=post)	
	return f'{content}'.encode('utf-8')


def create_xgi(path):
	wsgi = create_environ(path)
	xgi = Xgi(wsgi)
	return xgi
