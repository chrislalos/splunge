class PathString (str):
	def __new__ (cls, s):
		print(type(super()))
		self = super().__new__(cls, s)
		if s is None:
			self.parts = []
		else:
			self.parts = s[1:].split('/')
		return self

	def __getitem__ (self, index):
		return self.parts[index]
			
