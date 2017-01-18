from setuptools import setup, find_packages

setup(
    name='OOMMFTools',
    version='1.0',
    packages=find_packages(),
    install_requires=[
          'numpy',
          'scipy'
      ],
      dependency_links=['https://wxpython.org/'],
)