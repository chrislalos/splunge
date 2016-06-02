class InvalidMethodEx(Exception):
	def __init__ (self, badMethod, validMethods):
		self.badMethod = badMethod
		self.validMethods = validMethods

	def __str__ (self):
		sValidMethods = ', '.join(self.validMethods)
		s = "Invalid HTTP method: %s. Must be one of [%s]" % (self.badMethod, sValidMethods)
		return s

	def getAllowHeaderValue (self):
		s = "Allow: {}".format(', '.join(self.validMethods))
		return s


class GeneralClientEx(Exception):
	def __init__ (self, msg):
		self.msg = msg

	def __str__ (self):
		s = "Client error: %s" % self.msg
		return s

	def getWarningHeaderValue (self):
		s = "299 %s" % self.msg
		return s


class ModuleNotFoundEx (Exception):
	def __init__ (self, moduleName):
		self.moduleName = moduleName

	def __str__ (self):
		s = "Module '{}' not found".format(self.moduleName)
		return s


	
