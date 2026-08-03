import os

from .BaseHandler import BaseHandler
from .FileHandler import FileHandler
from .HtmlGenHandler import HtmlGenHandler
from .IndexPageHandler import IndexPageHandler
from .MarkdownHandler import MarkdownHandler
from .PythonModuleHandler import PythonModuleHandler
from .PythonTemplateHandler import PythonTemplateHandler
from .SourceHandler import SourceHandler
from ..Xgi import Xgi
from .. import loggin

lookupTable = {
	'.a': ('application/octet-stream', FileHandler),
	'.ai': ('application/postscript', FileHandler),
	'.aif': ('audio/x-aiff', FileHandler),
	'.aifc': ('audio/x-aiff', FileHandler),
	'.aiff': ('audio/x-aiff', FileHandler),
	'.au': ('audio/basic', FileHandler),
	'.avi': ('video/x-msvideo', FileHandler),
	'.bat': ('text/plain', FileHandler),
	'.bcpio': ('application/x-bcpio', FileHandler),
	'.bin': ('application/octet-stream', FileHandler),
	'.bmp': ('image/x-ms-bmp', FileHandler),
	'.c': ('text/plain', FileHandler),
	'.cdf': ('application/x-cdf', FileHandler),
	'.cpio': ('application/x-cpio', FileHandler),
	'.csh': ('application/x-csh', FileHandler),
	'.css': ('text/css', FileHandler),
	'.csv': ('text/csv', FileHandler),
	'.dll': ('application/octet-stream', FileHandler),
	'.doc': ('application/msword', FileHandler),
	'.dot': ('application/msword', FileHandler),
	'.dvi': ('application/x-dvi', FileHandler),
	'.eml': ('message/rfc822', FileHandler),
	'.eps': ('application/postscript', FileHandler),
	'.etx': ('text/x-setext', FileHandler),
	'.exe': ('application/octet-stream', FileHandler),
	'.gif': ('image/gif', FileHandler),
	'.gtar': ('application/x-gtar', FileHandler),
	'.h': ('text/plain', FileHandler),
	'.hdf': ('application/x-hdf', FileHandler),
	'.htm': ('text/html', FileHandler),
	'.html': ('text/html', FileHandler),
	'.ico': ('image/vnd.microsoft.icon', FileHandler),
	'.ief': ('image/ief', FileHandler),
	'.jpe': ('image/jpeg', FileHandler),
	'.jpeg': ('image/jpeg', FileHandler),
	'.jpg': ('image/jpeg', FileHandler),
	'.js': ('application/javascript', FileHandler),
	'.ksh': ('text/plain', FileHandler),
	'.latex': ('application/x-latex', FileHandler),
	'.m1v': ('video/mpeg', FileHandler),
	'.m3u': ('application/vnd.apple.mpegurl', FileHandler),
	'.m3u8': ('application/vnd.apple.mpegurl', FileHandler),
	'.man': ('application/x-troff-man', FileHandler),
	'.md': ('text/markdown', MarkdownHandler),
	'.mid': ('audio/midi', FileHandler),
	'.midi': ('audio/midi', FileHandler),
	'.me': ('application/x-troff-me', FileHandler),
	'.mht': ('message/rfc822', FileHandler),
	'.mhtml': ('message/rfc822', FileHandler),
	'.mif': ('application/x-mif', FileHandler),
	'.mov': ('video/quicktime', FileHandler),
	'.movie': ('video/x-sgi-movie', FileHandler),
	'.mp2': ('audio/mpeg', FileHandler),
	'.mp3': ('audio/mpeg', FileHandler),
	'.mp4': ('video/mp4', FileHandler),
	'.mpa': ('video/mpeg', FileHandler),
	'.mpe': ('video/mpeg', FileHandler),
	'.mpeg': ('video/mpeg', FileHandler),
	'.mpg': ('video/mpeg', FileHandler),
	'.ms': ('application/x-troff-ms', FileHandler),
	'.nc': ('application/x-netcdf', FileHandler),
	'.nws': ('message/rfc822', FileHandler),
	'.o': ('application/octet-stream', FileHandler),
	'.obj': ('application/octet-stream', FileHandler),
	'.oda': ('application/oda', FileHandler),
	'.p12': ('application/x-pkcs12', FileHandler),
	'.p7c': ('application/pkcs7-mime', FileHandler),
	'.pbm': ('image/x-portable-bitmap', FileHandler),
	'.pdf': ('application/pdf', FileHandler),
	'.pfx': ('application/x-pkcs12', FileHandler),
	'.pgm': ('image/x-portable-graymap', FileHandler),
	'.pct': ('image/pict', FileHandler),
	'.pic': ('image/pict', FileHandler),
	'.pict': ('image/pict', FileHandler),
	'.pl': ('text/plain', FileHandler),
	'.png': ('image/png', FileHandler),
	'.pnm': ('image/x-portable-anymap', FileHandler),
	'.pot': ('application/vnd.ms-powerpoint', FileHandler),
	'.ppa': ('application/vnd.ms-powerpoint', FileHandler),
	'.ppm': ('image/x-portable-pixmap', FileHandler),
	'.pps': ('application/vnd.ms-powerpoint', FileHandler),
	'.ppt': ('application/vnd.ms-powerpoint', FileHandler),
	'.ps': ('application/postscript', FileHandler),
	'.pwz': ('application/vnd.ms-powerpoint', FileHandler),
	'.py': ('application/x-python-code', SourceHandler),
	'.pyc': ('application/x-python-code', FileHandler),
	'.pyp': ('application/x-splunge-template', SourceHandler),
	'.pyo': ('application/x-python-code', FileHandler),
	'.qt': ('video/quicktime', FileHandler),
	'.ra': ('audio/x-pn-realaudio', FileHandler),
	'.ram': ('application/x-pn-realaudio', FileHandler),
	'.ras': ('image/x-cmu-raster', FileHandler),
	'.rdf': ('application/xml', FileHandler),
	'.rgb': ('image/x-rgb', FileHandler),
	'.roff': ('application/x-troff', FileHandler),
	'.rtf': ('application/rtf', FileHandler),
	'.rtx': ('text/richtext', FileHandler),
	'.sgm': ('text/x-sgml', FileHandler),
	'.sgml': ('text/x-sgml', FileHandler),
	'.sh': ('application/x-sh', FileHandler),
	'.shar': ('application/x-shar', FileHandler),
	'.snd': ('audio/basic', FileHandler),
	'.so': ('application/octet-stream', FileHandler),
	'.src': ('application/x-wais-source', FileHandler),
	'.sv4cpio': ('application/x-sv4cpio', FileHandler),
	'.sv4crc': ('application/x-sv4crc', FileHandler),
	'.svg': ('image/svg+xml', FileHandler),
	'.swf': ('application/x-shockwave-flash', FileHandler),
	'.t': ('application/x-troff', FileHandler),
	'.tar': ('application/x-tar', FileHandler),
	'.tcl': ('application/x-tcl', FileHandler),
	'.tex': ('application/x-tex', FileHandler),
	'.texi': ('application/x-texinfo', FileHandler),
	'.texinfo': ('application/x-texinfo', FileHandler),
	'.tif': ('image/tiff', FileHandler),
	'.tiff': ('image/tiff', FileHandler),
	'.tr': ('application/x-troff', FileHandler),
	'.tsv': ('text/tab-separated-values', FileHandler),
	'.txt': ('text/plain', FileHandler),
	'.ustar': ('application/x-ustar', FileHandler),
	'.vcf': ('text/x-vcard', FileHandler),
	'.wav': ('audio/x-wav', FileHandler),
	'.webm': ('video/webm', FileHandler),
	'.wiz': ('application/msword', FileHandler),
	'.wsdl': ('application/xml', FileHandler),
	'.xbm': ('image/x-xbitmap', FileHandler),
	'.xlb': ('application/vnd.ms-excel', FileHandler),
	'.xls': ('application/excel', FileHandler),
	'.xml': ('text/xml', FileHandler),
	'.xpdl': ('application/xml', FileHandler),
	'.xpm': ('image/x-xpixmap', FileHandler),
	'.xsl': ('application/xml', FileHandler),
	'.xul': ('text/xul', FileHandler),
	'.xwd': ('image/x-xwindowdump', FileHandler),
	'.zip': ('application/zip', FileHandler),
	'.zzz': ('ZZZzzzzzzz', None),
}

def create(xgi: Xgi, *, code_folder: str=None) -> BaseHandler:
	""" Return the appropriate handler for the wsgi. """
	if not code_folder:
		code_folder = os.getcwd()
	handler = None
	if xgi.is_index_page():
		handler =  IndexPageHandler(xgi)
	elif xgi.is_python_module():
		handler = PythonModuleHandler(xgi)
	elif xgi.is_python_markup(code_folder):
		handler =  PythonTemplateHandler(xgi)
	elif is_mime_type(xgi):
		handler = create_mime_handler(xgi)
	else:
		handler = FileHandler(xgi)
	if handler:
		loggin.debug(f'handler found: {type(handler).__name__}')
	else:
		loggin.warning('no handler found')
	return handler


def create_mime_handler(xgi):
	""" Return the appropriate MIME handler for the xgi. """
	# Get MIME type from path extension
	ext  = xgi.get_path_extension()
	if not ext in lookupTable:
		return None
	(_, handlerType) = lookupTable[ext]
	handler = handlerType(xgi)
	return handler

	
def handle_404(xgi, start_response):
	status = "404 Resource Not Found"
	try:
		loggin.debug("inside handle_404()")
		templatePath = f'/err/404.pyp'
		loggin.debug(f'templatePath={templatePath}')
		# Load the template & render it w wsgi args
		args = {"path": xgi['PATH_INFO']}
		content = util.render_template(templatePath, args).encode()
		contentLength = len(content)
		headers = Headers()
		headers.contentLength = contentLength
		headers.contentType = constants.MT_html
		loggin.debug("headers")
		loggin.debug(headers)
		loggin.debug("starting response")
		start_response(status, headers.asTuples())
		return [content]
	except Exception as ex:
		loggin.error(ex)
		content = util.render_string(error_template_strings.Err404, args).encode('utf-8')
		contentLength = len(content)
		headers = Headers()
		headers.contentLength = contentLength
		headers.contentType = "text/html"
		start_response(status, headers.asTuples())
		return [content]


def handle_error(ex, xgi, start_response):
	status = "513 uhoh"
	try:
		loggin.error(ex, exc_info=True)
		# Create a traceback from the ex + create a context from the message+traceback
		ss = traceback.extract_tb(ex.__traceback__)
		s = "".join([html.escape(line).lstrip() for line in ss.format()])
		args = {
			"message": str(ex),
			"traceback": s
		}
		# Load + render the template, and encode as HTML
		templatePath = '/err/500.pyp'
		content = util.render_template(templatePath, args).encode('utf-8')
		# Create headers
		contentLength = len(content)
		headers = Headers()
		headers.contentLength = contentLength
		headers.contentType = constants.MT_html
		# Deliver the response
		start_response(status, headers.asTuples())
		return [content]
	except Exception as ex:
		# loggin.error(ex, exc_info=True)
		content = util.render_string(error_template_strings.Err500, args).encode('utf-8')
		contentLength = len(content)
		headers = Headers()
		headers.contentLength = contentLength
		headers.contentType = "text/html"
		start_response(status, headers.asTuples())
		return [content]


def is_mime_type(xgi):
	''' Check if the wsgi has a recognized MIME type. '''
	mimeType = lookup_mime_type(xgi)
	return not not mimeType 


def lookup_mime_type(xgi) -> str:
	''' Check if the wsgi has a recognized MIME type. '''
	ext = xgi.get_path_extension()
	loggin.debug(f'ext={ext}')
	if not ext in lookupTable:
		loggin.debug("ext not found in lookup table")
		return None
	(mimeType, _) = lookupTable[ext]
	loggin.debug(f'mimeType={mimeType}')
	return mimeType
	
