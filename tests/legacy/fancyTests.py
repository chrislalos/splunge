import os
import unittest
import util
import splunge

def createEnvForFile (filename):
	env = { "REQUEST_METHOD": "get",
           "SCRIPT_NAME": "/",
           "PATH_INFO": filename,
           "QUERY_STRING": None,
           "SERVER_NAME": "localhost",
           "SERVER_PORT": "8123",
           "SERVER_PROTOCOL": "HTTP/1.1",
           "wsgi.version": (1, 0),
           "wsgi.url_scheme": "http",
           "wsgi.input": None,
           "wsgi.multithread": False,
           "wsgi.multiprocess": False,
           "wsgi.run_once": True
         }
	return env        



testStatus = ""
testWriteData = []
testHeaders = []
def createStartResponse ():
	def write (data):
		testWriteData.append(data)
	def start_response (status, headers, exc_info=None):
		testStatus = status
		testHeaders = headers
		return write
	return start_response




# This assumes you are loading a file in the root folder of where splunge is running
@unittest.skip("(I am a humble base class)")
class BaseTests:
	class TestFile (unittest.TestCase):
		def setUp (self):
			if not hasattr(self, 'isSetup') or not self.isSetup:
				self.isSetup = True
				cwd = os.getcwd()
				try:
					os.chdir('www')
					path = os.path.abspath(self.__class__.FILENAME)
					# print("path={}".format(path))
					# save the size
					self.fileContentSize = os.path.getsize(path)
					# Load the file
					with open(path, 'rb') as f:
						self.fileContent = f.read()
					# Get the filename
					(_, filename) = os.path.split(path)
					# Create an env using the filename
					env = createEnvForFile(filename)
					# Get the start response which I need to create
					start_response = createStartResponse()
					# Instantiate the splunge app object using the env and start response
					app = splunge.App.Application(env, start_response)
					# One it's created, iterate over it and do something with the output.
					#self.wsgiContent = b''
					# for chunk in app:
					#	self.wsgiContent += chunk
					# Compare that output with the file.
					# self.wsgiContentSize = len(self.wsgiContent)
					pass
				finally:
					os.chdir(cwd)

		def testContent (self): pass
			# self.assertEqual(self.fileContent, self.wsgiContent)

		def testContentSize (self): pass
			# self.assertEqual(self.fileContentSize, self.wsgiContentSize)


# This assume you are loading a file in the root folder of where splunge is running
class TestHtml (BaseTests.TestFile):
	FILENAME = 'static.html'	

# This assume you are loading a file in the root folder of where splunge is running
class TestJpg (BaseTests.TestFile):
	FILENAME = 'topo-weako.jpg'

# def suite():
# 	suite = unittest.TestSuite()
#	suite.addTest(TestHtml())
#	suite.addTest(TestJpg())
	
if __name__ == '__main__':
	unittest.main()
