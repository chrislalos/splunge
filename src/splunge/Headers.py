from collections import UserDict

# Supported operations:
#   Return None on missing key instead of KeyError
#   Multivalues are supported
#   It is easy to get all the header values as tuples
#   Getting an individual key works as expected; sometimes this returns a list as appropriate
#   Commonly used headers (eg Content-length) can be retrieved as properties 

class Headers (UserDict):
	HN_ContentLength = "Content-Length"
	HN_ContentType = "Content-Type"
	HN_Location = "Location"

	@classmethod
	def create (cls, base_headers: "Headers") -> "Headers":
		headers = Headers()
		headers.update(base_headers)
		return headers

	# Content-Length
	@property
	def contentLength(self): return self[self.HN_ContentLength]
	@contentLength.deleter
	def contentLength(self):
		if hasattr(self, self.HN_ContentLength): delattr(self, self.HN_ContentLength)
	@contentLength.setter
	def contentLength(self, val): self[self.HN_ContentLength] = val
	
	# Content-Type
	@property
	def contentType(self): return self[self.HN_ContentType]
	@contentType.deleter
	def contentType(self):
		print("Calling deleter")
		if hasattr(self, self.HN_ContentType): delattr(self, self.HN_ContentType)
	@contentType.setter
	def contentType(self, val): self[self.HN_ContentType] = val
	
	# Location
	@property
	def location(self): return self[self.HN_Location]
	@location.deleter
	def location(self):
		if hasattr(self, self.HN_Location): delattr(self, self.HN_Location)
	@location.setter
	def location(self, val): self[self.HN_Location] = val
	
	
	def __contains__ (self, key):
		if not self.data:
			return False
		key = str(key).lower()
		lowerKeys = [k.lower() for k in self.data]
		return key in lowerKeys

	def __delattr__ (self, key):
		if key == 'contentLength':
			key = self.Headers.HN_ContentLength
		elif key == 'contentType':
			key = Headers.HN_ContentType
		key = key.lower()
		print(f'deleting {key}')
		if hasattr(self, key):
			delattr(self, key)

	def __getattr__ (self, name):
		if name == 'contentLength':
			return self[Headers.HN_ContentLength.lower()]
		if name == 'contentType':
			return self[Headers.HN_ContentType.lower()]
		else:
			return super().__getattribute__(name.lower())

	
	def __setattr__ (self, name, value):
		if name == 'contentLength':
			self.set(Headers.HN_ContentLength.lower(), value)
		elif name == 'contentType':
			self.set(Headers.HN_ContentType.lower(), value)
		else:
			super().__setattr__(name.lower(), value)


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
		super().__setitem__(key.lower(), value)
	

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


	def asTuples (self, key=None):
		if key:
			values = self[key]
			if not values:
				tuples = []
			else:
				tuples = [(key, value) for value in values]
		else:
			tuples = []
			for k,v in sorted(self.items()):
				if not isinstance(v, list):
					tuples.append((k, v))
				else:
					theseTuples = [(k, v2) for v2 in sorted(v)]
					tuples.extend(theseTuples)
		return sorted(tuples)
	
	
	def deleteAll (self, name):
		self.pop(name)


	def get(self, key):
		return self[key]


	def set (self, key, value):
		self[key] = value
