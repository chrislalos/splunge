# splunge
Splunge is the world's easiest Python Web framework. Simpler than Django ... simpler than Pyramid ... even simpler than Flask.

Splunge isn't really even a framework. You just write Python code, do calculations, assign results to variables, and print() them -- or don't -- and `splunge` takes care of making the data available over HTTP, as a simple Web page.

Need something fancier? `splunge` uses Jinja templates, the most popular Python Web-template language and the most commonly used with more traditional frameworks. Presenting content with splunge is quite similar to presenting content with larger frameworks.

`splunge` is not (currently!) designed for next-gen Web experiences or database-driven applications. But if you process large amounts of data, you want to make it available on the Web, and you want to spend zero time learning Python Web frameworks, then splunge is for you.

## Features

`splunge` was born from the desire to make a few uses cases very simple

- Do some calculations, save the values to a few variables, display them
- Do some calculations, only show the final results, skipping immediately variable
- Take an existing Python script, which outputs results via `print()`, and turn it into a Web page
- Display a Python script's source code in the browser
- Support simple templating through Jinja, without forcing `render_template()` or any template-specific coding
- DO NOT force the developer to define routes. The route for `hello.py` is `/hello`, and the route for its source code is `/hello.py`.


## Under the Hood

`splunge` is a base-bones implementation of the WSGI specification, according to [PEP 444](https://www.python.org/dev/peps/pep-0444/). It uses [gunicorn](https://gunicorn.org/) to handle incoming connections, which made writing `splunge` a lot easier.

`splunge` uses Python's built-in module import machinery to custom-load Python scripts as modules. This is how splunge 'enriches' Python scripts to be more HTTP-aware saving the author from tedious imports.

`splunge` also uses jinja for templating, Pygments for syntax highlighting, and various other 3rd party modules for other features. The size of the splunge codebase is fairly small.

## Getting Started

The easiest way to get started with `splunge`, is to clone the repo, install `splunge` from your local folder using `pip`, and then start up the splunge web server.

1. `git clone https://github.com/beantaxi/splunge`
1. `cd splunge`
1.  `python -m venv `*`your-path-to-a-venv-folder`*
1.  `pip install splunge`
1. `cd sample-site`
1. `www`

This will run splunge inside the sample web site - the sample web site will be online!

Some URLs to visit (or curl)
- http://localhost:1313/index.html
- http://localhost:1313/set-underscore
- http://localhost:1313/some-values
- http://localhost:1313/write-to-stdout
- http://localhost:1313/simple-template
- http://localhost:1313/masters-of-models

#### Todo

HTTPS support
DataFrames as HTML tables
