from markdown_it import MarkdownIt
import unittest
from splunge import util


class UtilTests(unittest.TestCase):
    def test_html_fragment_to_doc(self):
        md = MarkdownIt()
        markdown = "### Content</p>\n<p>Hello!</p>\n"
        frag = md.render(markdown)
        print(f'frag={frag}')
        doc = util.html_fragment_to_doc(frag)
        print(f'doc={doc}')