from distutils.core import setup

version ='0.1.0'
setup(
    name = 'plunchy',
    py_modules = ['plunchy'],
    scripts = ['bin/plunchy'],
    version = version,
    description = "A simpler interface into OS X's launchctl",
    author = 'Bill Israel',
    author_email = 'bill.israel@gmail.com',
    url = 'https://github.com/epochblue/plunchy',
    keywords = ['os x', 'launchctl'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
    ],
)
