#!/usr/bin/env python
from distutils.core import setup
import cryptostream

LONG_DESCRIPTION = \
"""Very basic WSGI-based protection for file downloads."""

CLASSIFIERS = [
                'Development Status :: 5 - Production/Stable',
                'Intended Audience :: Developers',
                'License :: OSI Approved :: Apache Software License',
                'Natural Language :: English',
                'Operating System :: OS Independent',
                'Programming Language :: Python',
                'Topic :: Software Development :: Libraries :: Python Modules'
              ]

KEYWORDS = 'protect download cryptography'

setup(name='cryptostream',
      version=cryptostream.VERSION,
      description='Basic WSGI-based protection for file downloads.',
      long_description=LONG_DESCRIPTION,
      author='DUO Interactive',
      author_email='support@duointeractive.com',
      maintainer='Gregory Taylor',
      maintainer_email='gtaylor@duointeractive.com',
      url='https://github.com/duointeractive/cryptostream',
      download_url='http://pypi.python.org/pypi/cryptostream/',
      packages=['cryptostream'],
      platforms=['Platform Independent'],
      classifiers=CLASSIFIERS,
      keywords=KEYWORDS,
     )
