import setuptools


setuptools.setup(name='splunge',
                 description='Relentelessly simple Python web framework.',
                 keywords='python web wsgi gunicorn django pyramid mako',
                 version='0.0.1',
                 url='https://github.com/beantaxi/splunge',
                 author='Chris Lalos',
                 author_email='chris.lalos@gmail.com',
                 install_requires=['gunicorn', 'jinja2'],
                 packages=setuptools.find_packages('src'),
                 package_dir={'': 'src'}),
                 entry_points=
                 	{'console_scripts': ['splunge = splunge']}
#                 packages=setuptools.find_packages(exclude=['tests']))
