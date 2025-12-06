from markdown_it import MarkdownIt
import unittest
from splunge import util
from werkzeug.test import create_environ
from splunge import Xgi

class UtilTests(unittest.TestCase):
    def test_html_fragment_to_doc(self):
        md = MarkdownIt()
        markdown = "### Content</p>\n<p>Hello!</p>\n"
        frag = md.render(markdown)
        doc = util.html_fragment_to_doc(frag)

    def test_is_index_page_empty_string(self):
        xgi = Xgi.create('')
        flag = xgi.is_index_page()
        self.assertTrue(flag)
    
    def test_is_index_page_slash(self):
        xgi = Xgi.create('/')
        flag = xgi.is_index_page()
        self.assertTrue(flag)
