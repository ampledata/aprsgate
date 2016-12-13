#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python APRS Gateway Commands."""

import argparse
import logging
import logging.handlers
import Queue
import time

import aprs
import aprsgate
import aprsgate.sat

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2016 Orion Labs, Inc.'
__license__ = 'All rights reserved. Do not redistribute.'


def setup_logging(log_level=None):
    """
    Sets up logging.

    :param log_level: Log level to setup.
    :type param: `logger` level.
    :returns: logger instance
    :rtype: instance
    """
    log_level = log_level or aprsgate.LOG_LEVEL

    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(aprsgate.LOG_FORMAT)
    logger.addHandler(console_handler)
    logger.propagate = False

    return logger


def sat_gate():
    """Tracker Command Line interface for APRS."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--debug', help='Enable debug logging', action='store_true'
    )
    parser.add_argument(
        '-c', '--callsign', help='callsign', required=True
    )
    parser.add_argument(
        '-p', '--passcode', help='passcode', required=True
    )
    parser.add_argument(
        '-P', '--port', help='port', default=8001
    )
    parser.add_argument(
        '-S', '--speed', help='speed', required=True
    )
    parser.add_argument(
        '-i', '--interval', help='interval', default=60
    )
    parser.add_argument(
        '-u', '--ssid', help='ssid', default='6'
    )
    parser.add_argument(
        '-T', '--tle', help='TLE', default=aprsgate.ISS_TLE
    )
    parser.add_argument(
        '-Q', '--qth', help='QTH', default=aprsgate.QTH
    )

    opts = parser.parse_args()

    if opts.debug:
        log_level = logging.DEBUG
    else:
        log_level = None

    logger = setup_logging(log_level)

    aprs_serial_int = aprs.APRSSerialKISS(port=opts.port, speed=opts.speed)
    aprs_tcp_int = aprs.TCPAPRS(opts.callsign, opts.passcode)

    queue1 = Queue.Queue()
    queue2 = Queue.Queue()

    beacon_frame = 'SUNSET>BEACON:>W2GMD Experimental Python APRS Gateway.'
    sat_frame = 'SUNSET>CQ,ARISS:!3745.60N/12229.85W`W2GMD Experimental Python APRS Gateway CM87ss'

    sat_beacon1 = aprsgate.sat.SatBeacon(
        queue1, tle=opts.tle, qth=opts.qth, frame=sat_frame)
    gate_out1 = aprsgate.GateOut(queue1, aprs_serial_int)

    gate_in2 = aprsgate.GateIn(queue2, aprs_serial_int)
    beacon2 = aprsgate.Beacon(queue2, beacon_frame)
    gate_out2 = aprsgate.GateOut(queue2, aprs_tcp_int)

    try:
        sat_beacon1.start()
        gate_out1.start()

        gate_in2.start()
        beacon2.start()
        gate_out2.start()

        queue1.join()
        queue2.join()

        while (sat_beacon1.is_alive() and gate_out1.is_alive() and
               gate_in2.is_alive() and beacon2.is_alive() and
               gate_out2.is_alive()):
            time.sleep(0.01)

    except KeyboardInterrupt:
        sat_beacon1.stop()
        gate_out1.stop()

        gate_in2.stop()
        beacon2.stop()
        gate_out2.stop()

    finally:
        sat_beacon1.stop()
        gate_out1.stop()

        gate_in2.stop()
        beacon2.stop()
        gate_out2.stop()
