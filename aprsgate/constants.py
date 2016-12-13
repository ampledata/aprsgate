#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Constants for Python APRS Gateway.
"""

import logging

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2016 Orion Labs, Inc.'


LOG_LEVEL = logging.DEBUG
LOG_FORMAT = logging.Formatter(
    ('%(asctime)s aprsgate %(levelname)s %(name)s.%(funcName)s:%(lineno)d - '
     '%(message)s'))

ISS_TLE = """ISS (ZARYA)
1 25544U 98067A   16340.19707176  .00003392  00000-0  59140-4 0  9992
2 25544  51.6453 285.3071 0006023 292.9316 269.6257 15.53798216 31586
"""

QTH = (37.76, 122.4975, 56)

BEACON_INTERVAL = 600

REJECT_PATHS = set(['TCPIP', 'TCPIP*', 'NOGATE', 'RFONLY'])
