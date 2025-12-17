import unittest
from splunge import Xgi

class Tests(unittest.TestCase):
    def test_create_args(self):
        path = "/www/meat/bar?name=meat"
        xgi = Xgi.create(path)
        # get args
        getArgs = xgi.create_get_args()
        self.assertIsNotNone(getArgs)
        self.assertEqual(1, len(getArgs))
        self.assertTrue('name' in getArgs)
        self.assertEqual("meat", getArgs['name'])
        # post args
        postArgs = xgi.create_post_args()
        self.assertIsNotNone(postArgs)
        # args
        self.assertEqual(0, len(postArgs))
        args = xgi.create_args()
        self.assertIsNotNone(args)
        self.assertEqual(1, len(args))
        self.assertTrue('name' in args)
        self.assertEqual("meat", args['name'])