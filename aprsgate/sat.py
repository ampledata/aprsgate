#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python APRS Gateway Satellite Class Definitions."""

import logging
import logging.handlers
import threading
import time

import aprs
import aprsgate

import predict

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2016 Orion Labs, Inc.'


class SatBeacon(threading.Thread):

    """SatBeacon"""

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(aprsgate.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(aprsgate.LOG_LEVEL)
        _console_handler.setFormatter(aprsgate.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self, redis_conn, channels, frame, interval, tle, qth):
        threading.Thread.__init__(self)

        self.redis_conn = redis_conn
        self.channels = channels
        self.aprs_frame = aprs.Frame(frame)
        self.interval = interval
        self.tle = tle
        self.qth = qth

        self.pubsub = None
        self.daemon = True

        self._stop = threading.Event()

    def stop(self):
        """Stop the thread at the next opportunity."""
        self._stop.set()

    def stopped(self):
        """Checks if the thread is stopped."""
        return self._stop.isSet()

    def send_beacon(self):
        for channel in self.channels:
            self._logger.debug(
                'Publishing to channel=%s aprs_frame="%s"',
                channel, self.aprs_frame)
            self.redis_conn.publish(channel, self.aprs_frame)

    def run(self):
        self._logger.info('Running %s', self)
        while not self.stopped():
            passes = predict.transits(self.tle, self.qth)
            next_pass = passes.next()

            start = next_pass.start
            end = next_pass.start + next_pass.duration()
            now = time.time()

            if now >= start and now <= end:
                self.send_beacon()

            time.sleep(self.interval)
