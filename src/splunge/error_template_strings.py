Err404 = '''
<!DOCTYPE html>
<html lang="en">
	<head>
		<link rel="icon" type="image/png" sizes="16x16" href="/img/favicon-16x16.png">
		<link rel="icon" type="image/png" sizes="32x32" href="/img/favicon-32x32.png">
		<link rel='stylesheet' href='/style.css'>
		<title>splunge - 404</title>
		<style>
			.errorTitle {
				font-size: 3rem;
			}

			.errorTitle404 {
				font-size: 1rem;
			}

			.errorTitle404InitialLetter {
				font-size: 3rem;
			}
			
			.flexVertCenter {
				display: flex;
				flex-direction: column;
				align-items: center;
				gap: 3rem;
			}
		</style>
	</head>
	<body>
		<div class='flexVertCenter'>
			<div class='errorTitle'>
				<span class='errorTitle404InitialLetter'>4</span><span class='errorTitle404'>ile</span>
				N<span class='errorTitle404InitialLetter'>0</span><span class='errorTitle404'>t</span>
				<span class='errorTitle404InitialLetter'>4</span><span class='errorTitle404'>ound</span>
			</div>
		<div>
	</body>
</html>
'''

Err500 = '''
<!DOCTYPE html>
<html lang="en">
	<head>
		<link rel="icon" type="image/png" sizes="16x16" href="/img/favicon-16x16.png">
		<link rel="icon" type="image/png" sizes="32x32" href="/img/favicon-32x32.png">
		<link rel='stylesheet' href='/style.css'>
		<title>splunge - Internal Server Error</title>
		<style>
            .errorDetails {
                font-family: monospace;
                font-size: 1.1rem;
                line-height: 1.8rem;
                margin-top: 1rem;
                white-space: pre;
            }

            .errorSummary {
                margin-top: 1rem;
			}

            .errorTitle {
				font-size: 3rem;
                margin-top: 1rem;
			}
		</style>
	</head>
    <body>
        <div class='errorTitle'>
            Internal Server Error
        </div>
        <details>
            <summary class='errorSummary'>
            {{ message }}
            </summary>
            <div class='errorDetails'>
            {{- traceback }}
            </div>
        </details>
    </body>
</html>
'''