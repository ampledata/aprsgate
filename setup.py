#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup for the APRS Gate Module.

Source:: https://github.com/ampledata/aprsgate
"""

import os
import setuptools
import sys

__title__ = 'aprsgate'
__version__ = '1.0.0b1'
__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2016 Orion Labs, Inc.'


def publish():
    """Function for publishing package to pypi."""
    if sys.argv[-1] == 'publish':
        os.system('python setup.py sdist')
        os.system('twine upload dist/*')
        sys.exit()


publish()


setuptools.setup(
    name=__title__,
    version=__version__,
    description='Python APRS Gateway.',
    author='Greg Albrecht',
    author_email='oss@undef.net',
    packages=['aprsgate'],
    package_data={'': ['LICENSE']},
    package_dir={'aprsgate': 'aprsgate'},
    license=open('LICENSE').read(),
    long_description=open('README.rst').read(),
    url='https://github.com/ampledata/aprsgate',
    zip_safe=False,
    include_package_data=True,
    setup_requires=[
      'coverage >= 3.7.1',
      'httpretty >= 0.8.10',
      'nose >= 1.3.7'
    ],
    install_requires=['aprs >= 6.0.0', 'kiss >= 6.0.0'],
    entry_points={
        'console_scripts': [
            'aprsgate_tcp = aprsgate.cmd:aprsgate_tcp',
            'aprsgate_kiss_tcp = aprsgate.cmd:aprsgate_kiss_tcp',
            'aprsgate_kiss_serial = aprsgate.cmd:aprsgate_kiss_serial',
            'aprsgate_worker = aprsgate.cmd:aprsgate_worker',
            'aprsgate_beacon = aprsgate.cmd:aprsgate_beacon',
            'aprsgate_satbeacon = aprsgate.cmd:aprsgate_satbeacon'
        ]
    },
    extras_require={
        'satgate': ['pypredict'],
        '_all': ['satgate']
    },
    classifiers=[
        'Topic :: Communications :: Ham Radio',
        'Programming Language :: Python',
        'License :: OSI Approved :: Apache Software License'
    ],
    keywords=[
        'Ham Radio', 'APRS', 'KISS'
    ]
)
