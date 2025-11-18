import unittest
from werkzeug import Client
from splunge import app


class EndToEndTests(unittest.TestCase):
    def test_static_content(self):
        cli = Client(app.app)
        resp = cli.get("/www/hello.html")
        print(f'resp.iter_encoded()={resp.iter_encoded()}')
        # print(f'resp={resp}')
        print(f'resp.text={resp.text}')