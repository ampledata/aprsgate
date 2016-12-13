#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""APRS Class Definitions"""

import logging
import logging.handlers
import threading
import time

import aprs
import aprsgate

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2016 Orion Labs, Inc.'


class GateIn(threading.Thread):

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(aprsgate.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(aprsgate.LOG_LEVEL)
        _console_handler.setFormatter(aprsgate.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self, aprsc, redis_conn, channels):
        threading.Thread.__init__(self)

        self.aprsc = aprsc
        self.redis_conn = redis_conn
        self.channels = channels
        self.pubsub = None

        self.daemon = True
        self._stop = threading.Event()

    def stop(self):
        """Stop the thread at the next opportunity."""
        self._stop.set()

    def stopped(self):
        """Checks if the thread is stopped."""
        return self._stop.isSet()

    def handle_message(self, message):
        for channel in self.channels:
            aprs_message = aprs.APRSFrame(message)
            self._logger.debug(
                'Sending to channel=%s aprs_message="%s"',
                channel, aprs_message)
            self.redis_conn.publish(channel, aprs_message)

    def run(self):
        self._logger.info('Running %s', self)
        while not self.stopped():
            self.aprsc.read(callback=self.handle_message)


class GateOut(threading.Thread):

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(aprsgate.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(aprsgate.LOG_LEVEL)
        _console_handler.setFormatter(aprsgate.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self, aprsc, redis_conn, channels):
        threading.Thread.__init__(self)

        self.aprsc = aprsc
        self.redis_conn = redis_conn
        self.channels = channels
        self.pubsub = None

        self.daemon = True
        self._stop = threading.Event()

    def stop(self):
        """Stop the thread at the next opportunity."""
        self._stop.set()

    def stopped(self):
        """Checks if the thread is stopped."""
        return self._stop.isSet()

    def handle_message(self, message):
        self._logger.debug('handling message="%s"', message)
        if message.get('type') == 'message' and message.get('data'):
            aprs_frame = message['data']
            self._logger.debug('Gating "%s"', aprs_frame)
            self.aprsc.send(aprs_frame)

    def run(self):
        self._logger.info('Running %s', self)
        self.pubsub = self.redis_conn.pubsub()
        self.pubsub.subscribe(self.channels)

        while not self.stopped():
            for message in self.pubsub.listen():
                self.handle_message(message)


class GateWorker(threading.Thread):

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(aprsgate.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(aprsgate.LOG_LEVEL)
        _console_handler.setFormatter(aprsgate.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self, redis_conn, in_channels, out_channels):
        threading.Thread.__init__(self)

        self.redis_conn = redis_conn
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.pubsub = None

        self.daemon = True
        self._stop = threading.Event()

    def stop(self):
        """Stop the thread at the next opportunity."""
        self._stop.set()

    def stopped(self):
        """Checks if the thread is stopped."""
        return self._stop.isSet()

    def handle_message(self, message):
        self._logger.debug('Handling message="%s"', message)
        if message.get('type') == 'message' and message.get('data'):
            aprs_frame = message['data']

            if not 'TCPIP*' in aprs_frame.path:
                if not 'qAR' in aprs_frame.path:
                    for channel in self.out_channels:
                        gate_id = channel.split('_')[-1]
                        aprs_frame.path.extend(['qAR', gate_id])
                        self._logger.debug(
                            'Sending to channel=%s frame="%s"',
                            channel, aprs_frame)
                        self.redis_conn.publish(channel, aprs_frame)

    def run(self):
        self._logger.info('Running %s', self)
        self.pubsub = self.redis_conn.pubsub()
        self.pubsub.subscribe(self.in_channels)

        while not self.stopped():
            for message in self.pubsub.listen():
                self.handle_message(message)


class Beacon3(threading.Thread):

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(aprsgate.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(aprsgate.LOG_LEVEL)
        _console_handler.setFormatter(aprsgate.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self, queue, frame, interval=None):
        threading.Thread.__init__(self)
        self.queue = queue
        self.frame = frame
        self.interval = interval or aprsgate.BEACON_INTERVAL

        self.daemon = True
        self._stop = threading.Event()

    def stop(self):
        """Stop the thread at the next opportunity."""
        self._stop.set()

    def stopped(self):
        """Checks if the thread is stopped."""
        return self._stop.isSet()

    def send_beacon(self):
        self._logger.info('Putting frame="%s"', self.frame)
        self.queue.enqueue(self.frame)

    def run(self):
        self._logger.info('Running %s', self)
        while not self.stopped():
            self.send_beacon()
            time.sleep(self.interval)



class Beacon(threading.Thread):

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(aprsgate.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(aprsgate.LOG_LEVEL)
        _console_handler.setFormatter(aprsgate.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self, queue, frame, interval=None):
        threading.Thread.__init__(self)
        self.queue = queue
        self.frame = frame
        self.interval = interval or aprsgate.BEACON_INTERVAL

        self.daemon = True
        self._stop = threading.Event()

    def stop(self):
        """Stop the thread at the next opportunity."""
        self._stop.set()

    def stopped(self):
        """Checks if the thread is stopped."""
        return self._stop.isSet()

    def send_beacon(self):
        self._logger.info('Putting frame="%s"', self.frame)
        self.queue.enqueue(self.frame)

    def run(self):
        self._logger.info('Running %s', self)
        while not self.stopped():
            self.send_beacon()
            time.sleep(self.interval)
