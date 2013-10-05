from distutils.core import setup
import os

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

setup(
    name='gears-libsass',
    version='0.0.1',
    author='Alex Good',
    author_email='alex@makerlabs.co.uk',
    py_modules=['gears_libsass'],
    description='Gears compiler for sass using python-libsass',
    long_description=read('README'),
    install_requires=[
        'libsass>=0.3.0'
    ],
    test_suite='tests',
    dependency_links=[
        "git+https://github.com/dahlia/libsass-python@ef62f743f9010495b71afb4fe79dca3beb3b709f#egg=libsass-0.3.0",
    ]
)
