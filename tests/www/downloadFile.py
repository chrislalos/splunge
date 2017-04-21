path='/tmp/smiley.jpg'
addHeader('Content-Disposition', 'attachment; filename="sMiLeY.png"')
addHeader('Content-Type', 'application/octet-stream')
f = open(path, 'rb')
response.body = f.read()
addHeader('Content-Length', str(len(response.body)))
