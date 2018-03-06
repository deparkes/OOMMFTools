from setuptools import setup

about = {}
with open("./oommftools/_about.py") as fp:
    exec(fp.read(), about)

with open("README.md", 'r') as f:
    long_description = f.read()
    
setup(
   name=about['__title__'].lower(),
   version=about['__version__'],
   description=about['__summary__'],
   long_description=long_description,
   author=about['__author__'],
   author_email=about['__email__'],
   packages=['oommftools'],  #same as name
   install_requires=['wxpython', 'scipy', 'numpy'], #external packages as dependencies
)