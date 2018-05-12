import sys
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
   version=about['__version__'],
   description=''.join(about['__summary__']),
   long_description=long_description,
   author=about['__author__'],
   maintainer=about['__maintainer__'],
   license='GPLv2',
   author_email=about['__email__'],
   url=about['__uri__'],
   packages=['oommftools'],  #same as name
   install_requires=['scipy', 'numpy'] + (
        ["wxpython"] if not sys.platform.startswith("linux") else []
        ), #external packages as dependencies
    classifiers=[
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Programming Language :: Python :: 2.7',
    'Intended Audience :: Science/Research',
    'Topic :: Scientific/Engineering :: Physics',
    'Topic :: Scientific/Engineering :: Visualization',
    'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)'
    ],
)
