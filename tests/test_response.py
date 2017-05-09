import os.path
import pickle
import tempfile
from cookies import Cookie, Cookies
import pytest
from splunge import util
from splunge.Response import Response
### Headers

def test_initialHeaders ():
	resp = Response()
	assert resp.headers is not None
	assert len(resp.headers()) == 0

# Add header
def test_addHeader ():
	resp = Response()
	name = 'name'
	value = 'value'
	resp.addHeader(name, value)
	assert resp.hasHeader(name)
	assert value == resp.header(name)


# Clear headers, get headers
def test_clearHeaders ():
	resp = Response()
	resp.addHeader('name1', 'value1')
	resp.addHeader('name2', 'value2')
	resp.addHeader('name3', 'value3')
	assert 3 == len(resp.headers())
	resp.clearHeaders()
	assert 0 == len(resp.headers())

# Single header value
def test_singleValue ():
	resp = Response()
	name = 'name'
	value = 'value'
	resp.addHeader(name, value)
	valueAfter = resp.header(name)
	assert value == valueAfter

# Single header value fails after multiple assignment
def test_singleValueFail ():
	resp = Response()
	name = 'name'
	value = 'value'
	value2 = 'value2'
	resp.addHeader(name, value)
	resp.addHeader(name, value2)
	with pytest.raises(Exception):
		resp.header(name)
	
# Multivalue
def test_multiValue ():
	resp = Response()
	name = 'name'
	value1 = 'value1'
	value2 = 'value2'
	resp.addHeader(name, value1)
	resp.addHeader(name, value2)
	values = resp.headers(name)
	assert 2 == len(values)
	assert [value1, value2] == values


# Multivalue
def test_multiValueCoercion ():
	resp = Response()
	name = 'name'
	value1 = 'value1'
	resp.addHeader(name, value1)
	values = resp.headers(name)
	assert isinstance(values, list)
	assert 1 == len(values)
	assert [value1] == values


### Redirects

# Redirect, get headers
def test_redirect ():
	resp = Response()
	url = 'test.html'
	resp.redirect(url)
	urlAfter = resp.header('Location')
	assert 303 == resp.statusCode
	assert url == urlAfter

# Redirect twice, get headers
def test_redirectTwice ():
	resp = Response()
	url = 'test.html'
	url2 = 'test2.html'
	resp.redirect(url)
	urlAfter = resp.header('Location')
	assert 303 == resp.statusCode
	assert url == urlAfter
	resp.redirect(url2)
	urlAfter2 = resp.header('Location')
	assert 303 == resp.statusCode
	assert url2 == urlAfter2


### Status

# Set status, check status
def test_setStatus ():
	resp = Response()
	statusCode = 999
	statusMessage = 'Really Fake Status'
	resp.status = (statusCode, statusMessage)
	assert statusCode == resp.statusCode
	assert statusMessage == resp.statusMessage

# Set status twiceeck status
def test_setStatusTwice ():
	resp = Response()
	statusCode = 999
	statusMessage = 'Really Fake Status'
	resp.status = (statusCode, statusMessage)
	assert statusCode == resp.statusCode
	assert statusMessage == resp.statusMessage
	statusCode2 = 998
	statusMessage2 = 'Really Fake Status2'
	resp.status = (statusCode2, statusMessage2)
	assert statusCode2 == resp.statusCode
	assert statusMessage2 == resp.statusMessage

# Do nothing, check status
def test_initialStatus ():
	resp = Response()
	assert 200 == resp.statusCode
	assert 'OK' == resp.statusMessage


### Iter / Content
def lineToBytes (line, encoding='latin-1'):
	lineBytes = '{}\r\n'.format(line).encode(encoding)
	return lineBytes


# Add line, check iter
def test_addLine ():
	resp = Response()
	line = 'Hello'
	resp.addLine(line)
	iter = resp.iter
	assert iter is not None
	assert 1 == len(iter)
	lineBytes = lineToBytes(line)
	lineBytesAfter = iter[0]
	assert lineBytes == lineBytesAfter


# Addlines, check iter
def test_addLines ():
	resp = Response()
	line1 = 'Hello'
	line2 = 'I must'
	line3 = 'Be Going'
	lines = [line1, line2, line3]
	resp.addLines(lines)
	lineByteses = [lineToBytes(line) for line in lines]
	resp = Response()
	resp.addLines(lines)
	assert resp.iter is not None
	assert len(lines) == len(resp.iter)
	for i, lineBytes in enumerate(resp.iter):
		assert lineByteses[i] == lineBytes

# Add bytes, check iter
def test_addBytes ():
	resp = Response()
	LENGTH = 1000
	data = b'0'*LENGTH
	resp.add(data)
	assert resp.iter is not None
	assert 1 == len(resp.iter)
	assert LENGTH == len(resp.iter[0])
	assert data == resp.iter[0]

# Add dict, check iter
def test_addDict ():
	resp = Response()
	d = {'a': 1, 'b': '2', 'c': 'three'}
	resp.add(d)
	dBytes = pickle.dumps(d)
	assert resp.iter is not None
	assert 1 == len(resp.iter)
	assert len(dBytes) == len(resp.iter[0])
	assert dBytes == resp.iter[0]
	

### File downloads
def test_fileDownload ():
	resp = Response()
	LENGTH = 1000
	data = b'0'*LENGTH
	try:
		tmp = tempfile.NamedTemporaryFile()
		tmpPath = tmp.name
		tmp.write(data)
		tmp.seek(0)
		resp.addDownload(tmpPath)
	finally:
		tmp.close()
	#
	mimeType = util.getMimeType(tmpPath)
	assert mimeType == resp._headers.contentType
	assert LENGTH == int(resp._headers.contentLength)
	assert 1 == len(resp.iter)
	assert LENGTH == len(resp.iter[0])
	assert data == resp.iter[0]

### Cookies

def _testCookie (header, name, value):
	cookie = Cookie.from_string(header)
	assert name == cookie.name
	assert value == cookie.value


def _testCookies (headers, args):
	jar = Cookies()
	for header in headers:
		jar.parse_response(header)
	for (name, value) in args:
		cookie = jar[name]
		assert cookie is not None
		assert value == cookie.value


# Add a cookie, test headers
def test_setCookie ():
	resp = Response()
	name = 'likes'
	value = 'cheese'
	#
	resp.setCookie(name, value)
	#
	cookieHeader = resp.header('Set-Cookie')
	assert cookieHeader is not None
	_testCookie(cookieHeader, name, value)


# Add a cookie, test headers
def test_setCookies ():
	resp = Response()
	data = [('likes', 'cheese'), ('hates', 'face'), ('notSure', 'beer')]
	for (name, value) in data:
		resp.setCookie(name, value)
	#
	cookieHeaders = resp.headers('Set-Cookie')
	assert isinstance(cookieHeaders, list)
	assert len(data) == len(cookieHeaders)
	_testCookies(cookieHeaders, data)


#
def test_setCookieTwice ():
	resp = Response()
	name = 'likes'
	value = 'cheese'
	value2 = 'cats'
	resp.setCookie(name, value)
	resp.setCookie(name, value2)
	#
	cookieHeaders = resp.headers('Set-Cookie')
	assert isinstance(cookieHeaders, list)
	assert 1 == len(cookieHeaders)
	args= [(name, value2)]
	_testCookies(cookieHeaders, args)


