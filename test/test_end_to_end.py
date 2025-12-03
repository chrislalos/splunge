import os
import unittest
from werkzeug import Client
from splunge import app


class EndToEndTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cwd = os.getcwd()
        print()
        print(f"changing folder to ./www; saving cwd as {cls.cwd}")
        os.chdir('./www')

    @classmethod
    def tearDownClass(cls):
        print()
        if hasattr(cls, "cwd"):
            print(f"changing folder back to {cls.cwd}")
        else:
            print("tearDownClass() called but cls.cwd isn't set. Strange.")
        os.chdir(cls.cwd)

    def test_404(self):
        url = "/xxx/yyy/zzz"
        cli = Client(app.app)
        resp = cli.get(url)
        statusCode, sep, statusMessage = resp.status.partition(' ')
        self.assertEqual(str(404), statusCode)
        if statusMessage:
            self.assertNotEqual('OK', statusMessage.upper())
        print(f'resp.text={resp.text}')


    def test_hello_html(self):
        test_get(self, "/hello.html")

    def test_meat_foo(self):
        test_get(self, "/meat/foo")
    
    def test_meat_foo3(self):
        test_get(self, "/meat/foo3?luckyNumber=13")


def test_get(t: unittest.TestCase, url: str, *, contentType=None):
    cli = Client(app.app)
    resp = cli.get(url)
    statusCode, sep, statusMessage = resp.status.partition(' ')
    t.assertEqual(str(200), statusCode)
    if statusMessage:
        t.assertEqual('OK', statusMessage.upper())
    print(f'resp.text={resp.text}')
    if contentType:
        t.assertEqual(contentType, resp.content_type)
