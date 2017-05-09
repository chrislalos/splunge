from http.cookies import SimpleCookie

# pypinfo()
_ = "checking cookies - Does this reload?"

setContentType('text/html')
if 'HTTP_COOKIE' not in http.env:
	print('No Cookie')
	addCookie('likes', 'cheese')
else:
	print('YES cookie!')
	cookiejar = SimpleCookie(http.env['HTTP_COOKIE'])
	cookie = cookiejar['likes']
	print('{}={}'.format('likes', cookie.value))

