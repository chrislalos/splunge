path='/tmp/smiley.jpg'
setHeader('Content-Disposition', 'attachment; filename="sMiLeY.png"')
setHeader('Content-Type', 'application/octet-stream')
f = open(path, 'rb')
content = f.read()
response.iter = [content]
setHeader('Content-Length', str(len(content)))
