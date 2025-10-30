import util

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



testStatus
testWriteData = []
testHeaders = []
def createStartResponse ():
	def write (data):
		testWriteData.append(data)
	def start_response (status, headers, exc_info):
		testStatus = status
		testHeaders = headers
		return write
	return start_response




# This assume you are loading a file in the root folder of where splunge is running
def testFile (path):
	# save the size
	nContent = os.path.getsize(path)
	# Load the file
	with open(path, 'rb') as f:
		content = f.read()
	# Get the filename
	(_, filename) = os.path.split(path)
	# Create an env using the filename
	env = createEnvForFile(filename)
	# Get the start response which I need to create
	start_response = createStartResponse()
	# Instantiate the splunge app object using the env and start response
	app = splunge.App.Application(env, start_response)
	# One it's created, iterate over it and do something with the output.
	resp = []
	for chunk in app:
		resp.append(chunk)
	# Compare that output with the file.
	print("{} {}".format(nContent, len(resp))


path = os.path.abspath('static.html')
print("path={}".format(path))
testFile(path)
