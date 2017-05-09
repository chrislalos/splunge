from collections import UserDict

# Supported operations:
#   Return None on missing key instead of KeyError
#   Multivalues are supported
#   It is easy to get all the header values as tuples
#   Getting an individual key works as expected; sometimes this returns a list as appropriate
#   Commonly used headers (eg Content-length) can be retrieved as properties 

class Headers (UserDict):
	def __contains__ (self, key):
		if not self.data:
			return False
		key = str(key).lower()
		lowerKeys = [k.lower() for k in self.data]
		return key in lowerKeys

	
	def __getattr__ (self, name):
		if name == 'contentLength':
			return self['content-length']
		if name == 'contentType':
			return self['content-type']
		else:
			return super().__getattribute__(name)

	
	def __setattr__ (self, name, value):
		if name == 'contentLength':
			self.set('content-length', value)
		elif name == 'contentType':
			self.set('content-type', value)
		else:
			super().__setattr__(name, value)


	def __delitem__ (self, key):
		key = key.lower()
		for k in self.data:
			if k.lower() == key:
				self.data.pop(k)
				break


	def __getitem__ (self, key):
		if not key:
			return None
		key = str(key).lower()
		lowerMap = {k.lower(): self.data[k] for k in self.data}
		if not key in lowerMap:
			return None
		return lowerMap[key]

	
	def __missing__ (self, key): 
		return None

	
	def __setitem__ (self, key, value):
		key = str(key)

		if not isinstance(value, (str, list)):
			value = str(value)
		super().__setitem__(key, value)
	

	def add (self, key, value):
		if key not in self:
			self[key] = value
		else:
			oldValue = self[key]
			if isinstance(oldValue, list):
				self[key].append(value)
			else:
				a = [oldValue, value]
				self[key] = a


	def asTuples (self):
		tuples = []
		for k,v in sorted(self.items()):
			if not isinstance(v, list):
				tuples.append((k, v))
			else:
				theseTuples = [(k, v2) for v2 in sorted(v)]
				tuples.extend(theseTuples)
		return sorted(tuples)
	
	
	def set (self, key, value):
		self[key] = value



