import setuptools


setuptools.setup(name='splunge',
                 entry_points={},
                 install_requires=[
                     'gunicorn',
                     'jinja2',
                     'markdown_it_py',
                     'pygments',
                     'werkzeug',
                 ],
                 scripts=['scripts/www'],
                 package_dir={'': 'src'},
                 packages=setuptools.find_packages(where='src'),
                 version='0.1.1',
                 )
