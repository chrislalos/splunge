import os
import os.path
import pytest
from werkzeug.test import create_environ
from splunge import app, constants
from splunge import handlers, util, CodeFolderLoader, FileHandler, IndexPageHandler, MarkdownHandler, PythonModuleHandler, PythonTemplateHandler, Response, SourceHandler, Xgi

@pytest.fixture(scope='module', autouse=True)
def _setup():
	old = os.getcwd()
	os.chdir('/www')
	ldr = CodeFolderLoader(['/www/hello'])
	ldr.install()
	yield
	os.chdir(old)
	ldr.uninstall()

def test_index_page():
    # Create a xgi, then create + execute a handler for it
    oldCwd = os.getcwd()
    try:
        os.chdir('./sample-site')
        (handler, resp) = create_and_test_handler("/", IndexPageHandler)
        # Test the response
        check_response_ok_html(resp)
    finally:
        os.chdir(oldCwd)

def test_markdown():
    # Create a xgi, then create + execute a handler for it
    (handler, resp) = create_and_test_handler("/hello.md", MarkdownHandler)
    # Test the response
    check_response_ok_html(resp)

def test_module():
    # Create a xgi, then create + execute a handler for it
    (handler, resp) = create_and_test_handler("/foo", PythonModuleHandler)
    # Test the response
    check_response_ok_html(resp)
    
def test_module_in_folder():
    # Create a xgi, then create + execute a handler for it
	(handler, resp) = create_and_test_handler("/sub/bum", PythonModuleHandler)
    # Test the response
	check_response_ok_html(resp)
    
def test_module_plus_markup():
    # Create a xgi, then create + execute a handler for it
    (handler, resp) = create_and_test_handler("/foo3", PythonModuleHandler)
    # Test the response
    check_response_ok_html(resp)
    
def test_module_with_redirect():
    # Create a xgi, then create + execute a handler for it
    (handler, resp) = create_and_test_handler("/redirect_0_from", PythonModuleHandler)
    # Test the response
    check_response_redirect(resp, 'redirect_0_to.html')

def test_module_with_relative_import():
    pass

def test_module_with_under():
    # Create a xgi, then create + execute a handler for it
    (handler, resp) = create_and_test_handler("/hello/foo2", PythonModuleHandler)
    # Test the response
    check_response_ok_html(resp)

def test_python_source():
    # Create a xgi, then create + execute a handler for it
    (handler, resp) = create_and_test_handler('/hello/foo.py', SourceHandler)
    # Test the response
    check_response_ok_html(resp)

def test_static_content_html():
    # Create a xgi, then create + execute a handler for it
    (handler, resp) = create_and_test_handler('/hello.html', FileHandler)
    # Test the response
    check_response_ok(resp, "text/html")

def test_static_content_png():
    # Create a xgi, then create + execute a handler for it
    (handler, resp) = create_and_test_handler('/img/sun.png', FileHandler)
    # Test the response
    check_response_ok(resp, "image/png")

def test_template():
    # Create a xgi, then create + execute a handler for it
    (handler, resp) = create_and_test_handler("/bar?name=meat", PythonTemplateHandler)
    # Test the response
    check_response_ok_html(resp)

def check_response(resp, statusCode, contentType, location=None):
	assert resp.exc_info is None
	assert statusCode == resp.statusCode
	assert contentType == resp.contentType
	assert location == resp.location


def check_response_ok(resp, contentType):
	check_response(resp, 200, contentType, None)
	assert int(resp.contentLength) > 0


def check_response_ok_html(resp):
	check_response_ok(resp, "text/html; charset=utf-8")


def check_response_redirect(resp, location):
	check_response(resp, 303, None, location)
	assert int(resp.contentLength) == 0


def create_xgi(path):
	wsgi = create_environ(path)
	xgi = Xgi(wsgi)
	return xgi


def create_and_test_handler(path, handlerType):
	xgi = Xgi.create(path)
	handler = handlers.create(xgi)
	assert handler is not None
	assert isinstance(handler, handlerType)
	resp = handler.handle_request()
	assert resp is not None
	return (handler, resp)

