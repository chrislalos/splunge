from pprint import pprint
import unittest
from splunge import Headers

def create_headers (name=None, value=None, *, d=None):
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


class HeadersTests(unittest.TestCase):
	def test_notIn (self):
		headers = Headers()
		self.assertTrue('bogusHeader' not in headers)


	def test_addSingleValue (self):
		name = 'Content-length'
		value = 'text/html'
		headers = create_headers(name, value)
		self.assertTrue(name in headers)
		self.assertEqual(value, headers[name])


	def test_addSingleValueI(self):
		name = 'Content-length'
		value = 'text/html'
		headers = create_headers(name, value)
		tuplesControl = [(name, value)]
		nameLower = name.lower()
		self.assertTrue(nameLower in headers)
		self.assertEqual(value, headers[nameLower])
		nameUpper = name.upper()
		self.assertTrue(nameUpper in headers)
		self.assertEqual(value, headers[nameUpper])
		self.assertEqual(tuplesControl, headers.asTuples())


	def test_addMultiValues (self):
		name = 'MultiValue'
		value1 = 'a'
		value2 = 'bee'
		value3 = 'sea'
		values = [value1, value2, value3]
		tuplesControl = [(name, value) for value in values]
		headers = create_headers(name, values)
		self.assertEqual(values, headers[name])
		self.assertEqual(tuplesControl, headers.asTuples())


	def test_addMultiValuesI (self):
		name = 'MultiValue'
		nameLower = name.lower()
		nameUpper = name.upper()
		values = ['a', 'bee', 'sea', 'Dee', 'EEEE!!!!']
		tuplesControl = [(name, value) for value in sorted(values)]
		headers = create_headers()
		for value in values[0:3]:
			headers.add(name, value)
		headers.add(nameLower, values[3])
		headers.add(nameUpper, values[4])
		self.assertEqual(len(values), len(headers[name]))
		self.assertEqual(len(values), len(headers[nameLower]))
		self.assertEqual(len(values), len(headers[nameUpper]))
		self.assertEqual(values, headers[name])
		self.assertEqual(values, headers[nameLower])
		self.assertEqual(values, headers[nameUpper])
		pprint('tuplesControl')
		pprint(tuplesControl)
		pprint('headers.asTuples()')
		pprint(headers.asTuples())
		self.assertEqual(tuplesControl, headers.asTuples())


	def test_overwriteHeader(self):
		headers = create_headers()
		name = 'name'
		value1 = 'value1'
		value2 = 'value2'
		headers.set(name, value1)
		self.assertEqual(value1, headers[name])
		headers.set(name, value2)
		self.assertTrue(len(headers) == 1)
		self.assertEqual(value2, headers[name])


	def test_contentLength(self):
		headers = create_headers()
		name = 'Content-length'
		value = 13
		headers.contentLength = value
		self.assertEqual(str(value), headers[name])
		self.assertEqual(str(value), headers.contentLength)


	def test_contentType(self):
		headers = create_headers()
		name = 'Content-type'
		value = 'text/html'
		headers.contentType = value
		self.assertEqual(value, headers.contentType)
		self.assertEqual(value, headers[name])


	def testDelete(self):
		name = 'Content-type'
		value = 'text/html'
		headers = create_headers(name, value)
		self.assertEqual(1, len(headers))
		headers.pop(name)
		self.assertEqual(0, len(headers))
		self.assertTrue(name not in headers)
		self.assertTrue(not headers[name])


	def testDeleteI(self):
		name = 'Content-type'
		value = 'text/html'
		headers = create_headers(name, value)
		self.assertEqual(1, len(headers))
		nameLower = name.lower()
		headers.pop(nameLower)
		self.assertEqual(0, len(headers))
		self.assertTrue(nameLower not in headers)
		self.assertTrue(not headers[nameLower])


	def testDeleteMany(self):
		name = 'Set-Cookie'
		value1 = 'likes=cheese'
		value2 = 'hates=life'
		headers = create_headers()
		headers.add(name, value1)
		headers.add(name, value2)
		# tuples = headers.asTuples(name)
		# self.assertEqual(2, len(tuples))
		# jar = Cookies()
		# for t in tuples:
		# 	(_, cookieString) = t
		# 	jar.parse_response(cookieString)
		# self.assertTrue('likes' in jar)
		# self.assertEqual('cheese', jar['likes'].value)
		# self.assertTrue('hates' in jar)
		# self.assertEqual('life', jar['hates'].value)
		headers.deleteAll(name)
		tuples = headers.asTuples(name)
		self.assertEqual(0, len(tuples))


	def test_nonExistentHeader(self):
		headers = Headers()
		self.assertTrue('bogusHeader' not in headers)
		self.assertTrue(not headers['bogusHeader'])


	def test_numericKeyAndValue(self):
		headers = Headers()
		name = 1
		sName = str(name)
		value = 100
		sValue = str(value)
		headers.add(name, value)
		self.assertEqual(headers[name], sValue)
		self.assertEqual(headers[sName], sValue)


	def test_numericKeyMissing(self):
		headers = Headers()
		self.assertTrue(not headers[1])


	def test_tuples1(self):
		headers = Headers()
		name = 'Content-length'
		value = 'text/html'
		tuplesControl = [(name, value)]
		headers.add(name, value)
		tuples = headers.asTuples()
		self.assertEqual(tuples, tuplesControl)


	def test_tuples2(self):
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
		self.assertEqual(tuples, tuplesControl)
