import json
import os.path
from pprint import pprint
import splunge.util

moduleExtras = {'1': 1, '2': '2', '3': 'three',
             	 'list': [1, 2, 3, 4, 5],
            	 'f': (lambda x: x*10)
             	}

testEnv = { "REQUEST_METHOD": "TEST",
            "SCRIPT_NAME": "TEST",
            "PATH_INFO": "TEST",
            "QUERY_STRING": "TEST",
            "CONTENT_TYPE": "TEST",
            "SERVER_NAME": "TEST",
            "SERVER_POST": "TEST",
            "SERVER_PROTOCOL": "TEST",
            "wsgi.version": "test",
            "wsgi.url_scheme": "test",
            "wsgi.input": None,
            "wsgi.multithread": False,
            "wsgi.multiprocess": False,
            "wsgi.run_once": True
          }

def test_start_response (env, headers, exc_info=None):
	write = lambda:None
	return write


def testModuleFile (file):
	path = os.path.abspath(file)
#	print('path={}'.format(path))
	moduleSpec = splunge.util.load_module_spec(path)
#	pprint(moduleSpec)
	splunge.util.execModuleSpec(moduleSpec, None)
#	pprint(moduleSpec)
#	print("moduleSpec.gotoTemplate={}".format(moduleSpec.gotoTemplate))
#	print("moduleSpec.hasShortcut={}".format(moduleSpec.hasShortcut))
#	print("moduleSpec.hasStdout={}".format(moduleSpec.hasStdout))
#	print("moduleSpec.stdout.len()={}".format(len(moduleSpec.stdout.getvalue())))
#	if moduleSpec.args:
#		print("moduleSpec.args")
#		print("---------------")
		# j = json.dumps(moduleSpec.args)
		# pprint(j)
#		pprint(moduleSpec.args)
#	print()
	if moduleSpec.hasStdout:
		print(moduleSpec.stdout.getvalue())
#	print()


def testModuleExtras (file):
	path = os.path.abspath(file)
#	print('path={}'.format(path))
	moduleSpec = splunge.util.load_module_spec(path)
#	pprint(moduleSpec)
	splunge.util.execModuleSpec(moduleSpec, moduleExtras)
#	pprint(moduleSpec)
#	print("moduleSpec.gotoTemplate={}".format(moduleSpec.gotoTemplate))
#	print("moduleSpec.hasShortcut={}".format(moduleSpec.hasShortcut))
#	print("moduleSpec.hasStdout={}".format(moduleSpec.hasStdout))
#	print("moduleSpec.stdout.len()={}".format(len(moduleSpec.stdout.getvalue())))
#	if moduleSpec.args:
#		print("moduleSpec.args")
#		print("---------------")
		# j = json.dumps(moduleSpec.args)
		# pprint(j)
#		pprint(moduleSpec.args)
#	print()
	if moduleSpec.hasStdout:
		print(moduleSpec.stdout.getvalue())
#	print()


def testTemplate (file, args):
	path = os.path.abspath(file)
	s = splunge.util.renderTemplate(path, args)
#	print(s)
