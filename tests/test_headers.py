from pprint import pprint
from splunge.Headers import Headers

def setup (name=None, value=None, *, d=None):
	headers = Headers()
	if name:
		if isinstance(value, list):
			for v in value:
				headers.add(name, v)
		else:
			headers[name] = value
	if d:
		headers.update(d)
	return headers
	

def test_notIn ():
	headers = Headers()
	assert 'bogusHeader' not in headers


def test_addSingleValue ():
	name = 'Content-length'
	value = 'text/html'
	headers = setup(name, value)
	assert name in headers
	assert value == headers[name]


def test_addSingleValueI ():
	name = 'Content-length'
	value = 'text/html'
	headers = setup(name, value)
	tuplesControl = [(name, value)]
	nameLower = name.lower()
	assert nameLower in headers
	assert value == headers[nameLower]
	nameUpper = name.upper()
	assert nameUpper in headers
	assert value == headers[nameUpper]
	assert tuplesControl == headers.asTuples()


def test_addMultiValues ():
	name = 'MultiValue'
	value1 = 'a'
	value2 = 'bee'
	value3 = 'sea'
	values = [value1, value2, value3]
	tuplesControl = [(name, value) for value in values]
	headers = setup(name, values)
	assert values == headers[name]
	assert tuplesControl == headers.asTuples()


def test_addMultiValuesI ():
	name = 'MultiValue'
	nameLower = name.lower()
	nameUpper = name.upper()
	values = ['a', 'bee', 'sea', 'Dee', 'EEEE!!!!']
	tuplesControl = [(name, value) for value in sorted(values)]
	headers = setup()
	for value in values[0:3]:
		headers.add(name, value)
	headers.add(nameLower, values[3])
	headers.add(nameUpper, values[4])
	assert len(values) == len(headers[name])
	assert len(values) == len(headers[nameLower])
	assert len(values) == len(headers[nameUpper])
	assert values == headers[name]
	assert values == headers[nameLower]
	assert values == headers[nameUpper]
	pprint('tuplesControl')
	pprint(tuplesControl)
	pprint('headers.asTuples()')
	pprint(headers.asTuples())
	assert tuplesControl == headers.asTuples()


def test_overwriteHeader ():
	headers = setup()
	name = 'name'
	value1 = 'value1'
	value2 = 'value2'
	headers.set(name, value1)
	assert value1 == headers[name]
	headers.set(name, value2)
	assert len(headers) == 1
	assert value2 == headers[name]


def test_contentLength ():
	headers = setup()
	name = 'Content-length'
	value = 13
	headers.contentLength = value
	assert str(value) == headers[name]
	assert str(value) == headers.contentLength


def test_contentType ():
	headers = setup()
	name = 'Content-type'
	value = 'text/html'
	headers.contentType = value
	assert value == headers.contentType
	assert value == headers[name]


def testDelete ():
	name = 'Content-type'
	value = 'text/html'
	headers = setup(name, value)
	assert 1 == len(headers)
	headers.pop(name)
	assert 0 == len(headers)
	assert name not in headers
	assert not headers[name]


def testDeleteI ():
	name = 'Content-type'
	value = 'text/html'
	headers = setup(name, value)
	assert 1 == len(headers)
	nameLower = name.lower()
	headers.pop(nameLower)
	assert 0 == len(headers)
	assert nameLower not in headers
	assert not headers[nameLower]


def test_nonExistentHeader ():
	headers = Headers()
	assert 'bogusHeader' not in headers
	assert not headers['bogusHeader']


def test_numericKeyAndValue ():
	headers = Headers()
	name = 1
	sName = str(name)
	value = 100
	sValue = str(value)
	headers.add(name, value)
	assert headers[name] == sValue
	assert headers[sName] == sValue


def test_numericKeyMissing ():
	headers = Headers()
	assert not headers[1]


def test_tuples1 ():
 	headers = Headers()
 	name = 'Content-length'
 	value = 'text/html'
 	tuplesControl = [(name, value)]
 	headers.add(name, value)
 	tuples = headers.asTuples()
 	assert tuples == tuplesControl


def test_tuples2 ():
	headers = Headers()
	name = 'MultiValue'
	value1 = 'a'
	value2 = 'bee'
	value3 = 'sea'
	tuplesControl = [(name, value1), (name, value2), (name, value3)]
	headers.add(name, value1)
	headers.add(name, value2)
	headers.add(name, value3)
	tuples = headers.asTuples()
	assert tuples == tuplesControl

	

