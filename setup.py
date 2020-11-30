import setuptools


setuptools.setup(name='splunge',
                 description='Relentelessly simple Python web framework.',
                 keywords='python web wsgi gunicorn django pyramid mako',
                 version='0.0.3',
                 url='https://github.com/beantaxi/splunge',
                 author='Chris Lalos',
                 author_email='chris.lalos@gmail.com',
                 install_requires=['cookies', 'gunicorn', 'jinja2', 'pygments'],
                 packages=setuptools.find_packages('src'),
                 package_dir={'': 'src'},
                 scripts=['src/runSplungeOnPort', 'src/runSplungeOnUnixSocket', 'src/www'],
                 entry_points=
                 	{'console_scripts': ['splunge = splunge.__main__:main']}
                 )
#                 packages=setuptools.find_packages(exclude=['tests']))
