html_pre = """
<!DOCTYPE html>
<html lang="en">
	<head>
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<title>{}</title>
	</head>
	<body>""".lstrip("\r\n")

html_post = """
	</body>
</html>
""".lstrip("\r\n")

# Context variable names
CTX_xgi = "current_xgi"

# specific media types for when there's a choice:
MT_html = 'text/html; charset=utf-8'

NSP_name = 'codefolders'
