def isDefault (path):
	flag = (path == '/')
	return flag


def isFavicon (path):
	flag = (path.lower() == '/favicon.ico')
	return flag


def isPythonFile (path):
	flag = (path.endswith('.py'))
	return flag


def isTemplateFile (path):
	flag = (path.endswith('.pyp'))
	return flag
