import io
import unittest

from splunge import util

class MiscTests(unittest.TestCase):
    def test_hello(self):
        self.assertEqual("hello", "hello")

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