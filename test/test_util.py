from markdown_it import MarkdownIt
import unittest
from splunge import util
from werkzeug.test import create_environ


class UtilTests(unittest.TestCase):
    def test_html_fragment_to_doc(self):
        md = MarkdownIt()
        markdown = "### Content</p>\n<p>Hello!</p>\n"
        frag = md.render(markdown)
        print(f'frag={frag}')
        doc = util.html_fragment_to_doc(frag)
        print(f'doc={doc}')

    def test_is_index_page_empty_string(self):
        wsgi = create_environ('')
        flag = util.is_index_page(wsgi)
        self.assertTrue(flag)
    
    def test_is_index_page_slash(self):
        wsgi = create_environ('/')
        flag = util.is_index_page(wsgi)
        self.assertTrue(flag)
