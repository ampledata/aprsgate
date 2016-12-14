#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python APRS Gateway Class Definitions."""

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

    """
    Accepts APRS Fames from an APRS Connection and Publishes them to
    the Channels.
    """

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
            aprs_frame = aprs.Frame(message)
            self._logger.debug(
                'Publishing to channel=%s aprs_frame="%s"',
                channel, aprs_frame)
            self.redis_conn.publish(channel, aprs_frame)

    def run(self):
        self._logger.info('Running %s', self)
        while not self.stopped():
            self.aprsc.receive(callback=self.handle_message)


class GateOut(threading.Thread):

    """
    Accepts APRS Fames from an PubSub and transmits them.
    """

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
        self._logger.debug('Handling message="%s"', message)
        if message.get('type') == 'message' and message.get('data'):
            message_data = message['data']
            aprs_frame = aprs.Frame(message_data)

            # Use the ',I' construct for APRS-IS:
            if self.aprsc.use_i_construct:
                aprs_frame.path.append('I')

            self._logger.info('Sending aprs_frame="%s"', aprs_frame)
            self.aprsc.send(aprs_frame)

    def run(self):
        self._logger.info('Running %s', self)
        self.pubsub = self.redis_conn.pubsub()
        self._logger.info(
            'Subscribing to channels="%s"', self.channels)
        self.pubsub.subscribe(self.channels)

        while not self.stopped():
            for message in self.pubsub.listen():
                self.handle_message(message)


class GateWorker(threading.Thread):

    """worker"""

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
            message_data = message['data']
            aprs_frame = aprs.Frame(message_data)

            if aprsgate.reject_frame(aprs_frame):
                return

            for channel in self.out_channels:
                gate_dir, gate_id, gate_tag = channel.split('_')

                # Don't re-gate my own frames. (anti-loop)
                for frame_path in aprs_frame.path:
                    if gate_id in str(frame_path):
                        return

                aprs_frame.path.append(aprs.Callsign(gate_id))

                self._logger.debug(
                    'Sending to channel=%s frame="%s"',
                    channel, aprs_frame)

                self.redis_conn.publish(channel, aprs_frame)

    def run(self):
        self._logger.info('Running %s', self)
        self.pubsub = self.redis_conn.pubsub()
        self._logger.info(
            'Subscribing to in_channels="%s"', self.in_channels)
        self._logger.info(
            'Publishing to out_channels="%s"', self.out_channels)
        self.pubsub.subscribe(self.in_channels)

        while not self.stopped():
            for message in self.pubsub.listen():
                self.handle_message(message)


class GateBeacon(threading.Thread):

    """Beacon"""

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(aprsgate.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(aprsgate.LOG_LEVEL)
        _console_handler.setFormatter(aprsgate.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self, redis_conn, channels, frame, interval):
        threading.Thread.__init__(self)

        self.redis_conn = redis_conn
        self.channels = channels
        self.aprs_frame = aprs.Frame(frame)
        self.interval = interval

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
            self.send_beacon()
            time.sleep(self.interval)
