import io
import unittest
from splunge import util, Xgi
from splunge.handlers import BaseHandler, FileHandler, HtmlGenHandler, MarkdownHandler, PythonTemplateHandler, SourceHandler

class MiscTests(unittest.TestCase):
    def test_hello(self):
        self.assertEqual("hello", "hello")

    def test_create_abstract_handlers(self):
        xgi = Xgi.create("/")
        self.assertRaises(TypeError, BaseHandler, xgi)
        self.assertRaises(TypeError, HtmlGenHandler, xgi)

    def test_create_concrete_handlers(self):
        xgi = Xgi.create("/")
        test_for_clean(self, FileHandler, xgi)
        test_for_clean(self, MarkdownHandler, xgi)
        test_for_clean(self, PythonTemplateHandler, xgi)
        test_for_clean(self, SourceHandler, xgi)

    def test_create_cookie_value(self):
        cookie_value = util.create_cookie_value("foo", 13)
        self.assertEqual("foo=13", cookie_value)

    def test_is_io_empty0(self):
        sio = io.StringIO()
        self.assertTrue(util.is_io_empty(sio))

    def test_is_io_empty1(self):
        sio = io.StringIO("MEAT")
        self.assertFalse(util.is_io_empty(sio))

    def test_is_io_empty2(self):
        sio = io.StringIO()
        sio.write("MEAT")
        self.assertFalse(util.is_io_empty(sio))

    def test_is_io_empty3(self):
        sio = io.StringIO()
        sio.write("MEAT")
        sio.truncate(0)
        sio.flush()
        self.assertTrue(util.is_io_empty(sio))

    def test_is_io_empty4(self):
        sio = io.StringIO()
        sio.write("MEAT")
        line = sio.readline()
        self.assertFalse(util.is_io_empty(sio))


def test_for_clean(t, callable, *args, **kwargs):
    raisedEx = None
    try:
        callable(*args, **kwargs)
    except Exception as ex:
        raisedEx = ex
    t.assertIsNone(raisedEx)
