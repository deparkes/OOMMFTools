from setuptools import setup

try:
    import m2r
    long_description = m2r.parse_from_file('README.md')
except(IOError, ImportError):
    print('Markdown not converted to rst')
    long_description = open('README.md').read()

about = {}
with open("./oommftools/_about.py") as fp:
    exec(fp.read(), about)
    
setup(
   name=about['__title__'].lower(),
   version=about['__version__']+'dev4',
   description=''.join(about['__summary__']),
   long_description=long_description,
   author=about['__author__'],
   author_email=about['__email__'],
   url=about['__uri__'],
   packages=['oommftools'],  #same as name
   install_requires=['wxpython', 'scipy', 'numpy'], #external packages as dependencies
)