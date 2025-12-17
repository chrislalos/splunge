def lookup_mime_type(xgi) -> str:
	''' Check if the wsgi has a recognized MIME type. '''
	ext = xgi.get_path_extension()
	loggin.debug(f'ext={ext}')
	if not ext in lookupTable:
		loggin.debug("ext not found in lookup table")
		return None
	mimeType = lookupTable[ext]
	loggin.debug(f'mimeType={mimeType}')
	return mimeType
	
