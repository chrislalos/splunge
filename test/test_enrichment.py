import contextlib
import importlib
from io import StringIO
import os
import pytest
from werkzeug.test import EnvironBuilder
from splunge.HttpEnricher import HttpEnricher, create_enrichment_object, enrich_module
from splunge import module_runner, util
from splunge import CodeFolderLoader, ModuleExecutionResponse, Xgi

@pytest.fixture(scope='module', autouse=True)
def _setup():
	old = os.getcwd()
	os.chdir('/www')
	ldr = CodeFolderLoader(['/www/hello'])
	ldr.install()
	yield
	os.chdir(old)
	ldr.uninstall()

def test_enrich_module():
	moduleName = 'codefolder.foo'
	module = importlib.import_module(moduleName)
	assert module is not None
	assert not hasattr(module, 'http')
	xgi = Xgi.create(path, method="GET")
	enrich_module(module, xgi)
	assert hasattr(module, 'http')
	http = getattr(module, "http")
	assert http is not None
	assert isinstance(http, HttpEnricher)
	contentLength = 13
	http.contentLength = contentLength
	assert contentLength == int(http.contentLength)
	assert 1 == len(http.headers.items())
	headerValue = int(http.headers['Content-Length'])
	assert headerValue is not None
	assert contentLength == headerValue
	
def test_execute_module_foo():
	path = './www/hello/foo.py'
	module = util.load_module_by_path(path)
	xgi = Xgi.create(path, method="GET")
	enrich_module(module, xgi)
	moduleState = ModuleExecutionResponse.exec_module(module)
	assert moduleState is not None
	assert 2 == len(moduleState.context)
	assert isinstance(moduleState.context[0], dict)
	assert moduleState.context[1] is None
	assert moduleState.stdout is not None
	assert util.is_io_empty(moduleState.stdout)

def x_test_get_module_attrs():
	path = './www/hello/foo.py'
	module = util.load_module_by_path(path)
	xgi = Xgi.create(path, method="GET")
	enrich_module(module, xgi)
	module.__spec__.loader.exec_module(module)
	attrNames = util.get_attr_names(module)


def test_module_args_get():
	http = create_enricher("/hello/foo", "bar=13&bum=thirteen")
	assert http.args is not None
	assert str(13) == http.args['bar']
	assert 'thirteen' == http.args['bum']

def test_module_args_post():
	http = create_enricher("/hello/foo", {'bar': 13, 'bum': 'thirteen'})
	assert http.args is not None
	assert str(13) == str(http.args['bar'])
	assert 'thirteen' == http.args['bum']

def test_module_args_post_binary():
	path = "/hello/foo"
	b=b'0123456789'
	contentType='application/octet-stream'
	xgi = Xgi.create(path, method="POST", data=b, content_type=contentType)
	assert contentType == xgi['CONTENT_TYPE']
	assert str(len(b)) == xgi['CONTENT_LENGTH']
	http = HttpEnricher(xgi)
	assert 0 == len(http.args)

def test_module_local_path():
	path = "/www/hello/foo"
	xgi = Xgi.create(path)
	localPath = xgi.get_local_path()
	currDir = os.getcwd()
	targetPath = os.path.abspath(f"{currDir}/{path}")
	assert targetPath == localPath
	modulePath = f'{localPath}.py'
	assert os.path.isfile(modulePath)
	module = util.load_module('foo', modulePath, 'mycode')
	assert module is not None
	module = util.enrich_module(module, xgi)
	assert path == module.http.path
	module_runner.exec_module(module, xgi)

def test_module_pypinfo():
	path = "/hello/foo"
	xgi = Xgi.create(path)
	http = HttpEnricher(xgi)
	stdout = StringIO()
	with contextlib.redirect_stdout(stdout):
		http.pypinfo()
	assert not util.is_io_empty(stdout)

def test_module_set_content_length():
	path = "/hello/foo"
	xgi = Xgi.create(path)
	http = HttpEnricher(xgi)
	contentLength = 13
	http.contentLength = contentLength
	assert 13 == int(http.contentLength)
	assert 1 == len(http.headers.items())
	headerValue = int(http.headers['Content-Length'])
	assert headerValue is not None
	assert contentLength == headerValue


def test_module_set_content_type():
	path = "/hello/foo"
	xgi = Xgi.create(path)
	http = HttpEnricher(xgi)
	url = "http://example.com/newurl"
	contentType = "text/plain"
	http.contentType = contentType
	assert contentType == http.contentType
	assert 1 == len(http.headers.items())
	headerValue = http.headers['Content-Type']
	assert headerValue is not None
	assert contentType == headerValue


def test_module_validate_method():
	path = "/hello/foo"
	xgi = Xgi.create(path)
	http = HttpEnricher(xgi)
	method = "get"
	methods = ["pOSt", "gET"]
	assert http.validate_method(method, methods)


def create_enricher (path, queryString=None):
	queryString="bar=13&bum=thirteen"
	xgi = Xgi.create(path, query_string=queryString)
	http = HttpEnricher(xgi)
	return http
