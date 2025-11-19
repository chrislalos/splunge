import setuptools


setuptools.setup(name='splunge',
                 entry_points={},
                 install_requires=[
                     'gunicorn',
                     'jinja2',
                     'markdown_it_py',
                     'pygments'
                 ],
                 scripts=['scripts/www'],
                 version='0.1.0',
                 )
#                 packages=setuptools.find_packages(exclude=['tests']))
