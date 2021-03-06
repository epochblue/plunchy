from os import path
from setuptools import setup

from plunchy import VERSION

long_description = open(
    path.join(
        path.dirname(__file__),
        'README.rst'
    )
).read()

entry_points = {
    'console_scripts': ['plunchy = plunchy:main']
}

setup(
    name='plunchy',
    py_modules=['plunchy'],
    entry_points=entry_points,
    version=VERSION,
    description="A simpler interface into OS X's launchctl",
    long_description=long_description,
    author='Bill Israel',
    author_email='bill.israel@gmail.com',
    url='https://github.com/epochblue/plunchy',
    keywords=['os x', 'launchctl', 'lunchy'],
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
    ],
)
