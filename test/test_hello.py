import os
import pytest


@pytest.fixture(autouse=True)
def chdir_www():
    old = os.getcwd()
    os.chdir('www')
    yield
    os.chdir(old)


def test_hello():
    print("hello")
    assert 2+2 == 4

def test_hello_splunge():
    import splunge

def test_hello_splunge_too():
    from splunge import Xgi, handlers
    xgi = Xgi.create('/')
    handler = handlers.create(xgi)
    assert handler is not None

def test_hello_splunge_also():
    import os
    from splunge import Xgi, handlers
    from splunge.handlers import IndexPageHandler, PythonModuleHandler
    from splunge.handlers import PythonTemplateHandler, SourceHandler
    from splunge.handlers import MarkdownHandler, FileHandler

    cf = os.getcwd()

    # No files needed — extension or URL alone suffices
    assert isinstance(handlers.create(Xgi.create('/'), code_folder=cf), IndexPageHandler)
    assert isinstance(handlers.create(Xgi.create('/hello.html'), code_folder=cf), FileHandler)
    assert isinstance(handlers.create(Xgi.create('/hello.md'), code_folder=cf), MarkdownHandler)
    assert isinstance(handlers.create(Xgi.create('/hello.py'), code_folder=cf), SourceHandler)
    assert isinstance(handlers.create(Xgi.create('/hello.pyp'), code_folder=cf), SourceHandler)
    assert isinstance(handlers.create(Xgi.create('/nope'), code_folder=cf), FileHandler)

    # Files must exist — specific to PythonModuleHandler / PythonTemplateHandler
    assert isinstance(handlers.create(Xgi.create('/hello/foo'), code_folder=cf), PythonModuleHandler)
    assert isinstance(handlers.create(Xgi.create('/hello/bar'), code_folder=cf), PythonTemplateHandler)

