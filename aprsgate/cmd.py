#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python APRS Gateway Commands."""

import argparse
import time

import aprs
import redis

import aprsgate

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2016 Orion Labs, Inc.'
__license__ = 'All rights reserved. Do not redistribute.'


def start_aprsgate(aprsc, callsign, redis_server, tag):
    gate_in_channels = ['_'.join(['GateIn', callsign, tag])]
    gate_out_channels = ['_'.join(['GateOut', callsign, tag])]

    redis_conn = redis.StrictRedis(redis_server)

    thread_pool = []

    thread_pool.append(
        aprsgate.GateIn(aprsc, redis_conn, gate_in_channels))

    thread_pool.append(
        aprsgate.GateOut(aprsc, redis_conn, gate_out_channels))

    try:
        aprsc.start()

        [th.start() for th in thread_pool]

        while [th.is_alive() for th in thread_pool]:
            time.sleep(0.01)

    except KeyboardInterrupt:
        [th.stop() for th in thread_pool]
    finally:
        [th.stop() for th in thread_pool]


def aprsgate_tcp():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-c', '--callsign', help='callsign', required=True
    )
    parser.add_argument(
        '-r', '--redis_server', help='Redis Server', required=True
    )
    parser.add_argument(
        '-t', '--tag', help='Gate Tag', required=False, default='IGATE'
    )

    parser.add_argument(
        '-p', '--passcode', help='passcode', required=True
    )
    parser.add_argument(
        '-f', '--aprs_filter', help='Filter', required=False,
        default='p/RS0ISS u/ARISS/RS0ISS'
    )

    opts = parser.parse_args()

    aprsc = aprs.TCPAPRS(
        opts.callsign,
        opts.passcode,
        aprs_filter=opts.aprs_filter
    )

    start_aprsgate(aprsc, opts.callsign, opts.redis_server, opts.tag)


def aprsgate_kiss_serial():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-c', '--callsign', help='callsign', required=True
    )
    parser.add_argument(
        '-r', '--redis_server', help='Redis Server', required=True
    )
    parser.add_argument(
        '-t', '--tag', help='Gate Tag', required=False, default='IGATE'
    )

    parser.add_argument(
        '-s', '--serial_port', help='Serial Port', required=True
    )
    parser.add_argument(
        '-S', '--speed', help='speed', required=False, default=19200
    )

    opts = parser.parse_args()

    aprsc = aprs.APRSSerialKISS(opts.serial_port, opts.speed)
    start_aprsgate(aprsc, opts.callsign, opts.redis_server, opts.tag)


def aprsgate_kiss_tcp():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-c', '--callsign', help='callsign', required=True
    )
    parser.add_argument(
        '-r', '--redis_server', help='Redis Server', required=True
    )
    parser.add_argument(
        '-t', '--tag', help='Gate Tag', required=False, default='IGATE'
    )

    parser.add_argument(
        '-H', '--host', help='Host', required=True
    )
    parser.add_argument(
        '-P', '--port', help='TCP Port', required=False, default=8001
    )

    opts = parser.parse_args()

    aprsc = aprs.APRSTCPKISS(
        opts.host,
        opts.port
    )

    start_aprsgate(aprsc, opts.callsign, opts.redis_server, opts.tag)


def aprsgate_worker():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-c', '--callsign', help='callsign', required=True
    )
    parser.add_argument(
        '-r', '--redis_server', help='Redis Server', required=True
    )
    parser.add_argument(
        '-t', '--tag', help='Gate Tag', required=False, default='IGATE'
    )

    opts = parser.parse_args()

    gate_in_channels = ['_'.join(['GateIn', opts.callsign, opts.tag])]
    gate_out_channels = ['_'.join(['GateOut', opts.callsign, opts.tag])]

    redis_conn = redis.StrictRedis(opts.redis_server)

    worker = aprsgate.GateWorker(
        redis_conn,
        in_channels=gate_in_channels,
        out_channels=gate_out_channels
    )

    try:
        worker.start()

        while worker.is_alive():
            time.sleep(0.01)

    except KeyboardInterrupt:
        worker.stop()
    finally:
        worker.stop()


def aprsgate_beacon():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-c', '--callsign', help='callsign', required=True
    )
    parser.add_argument(
        '-r', '--redis_server', help='Redis Server', required=True
    )
    parser.add_argument(
        '-t', '--tag', help='Gate Tag', required=False, default='IGATE'
    )

    parser.add_argument(
        '-f', '--frame', help='Frame', required=True
    )
    parser.add_argument(
        '-i', '--interval', help='Interval', required=False, default=60
    )

    opts = parser.parse_args()

    gate_out_channels = ['_'.join(['GateOut', opts.callsign, opts.tag])]

    redis_conn = redis.StrictRedis(opts.redis_server)

    beacon = aprsgate.GateBeacon(
        redis_conn,
        channels=gate_out_channels,
        frame=opts.frame,
        interval=opts.interval
    )

    try:
        beacon.start()

        while beacon.is_alive():
            time.sleep(0.01)

    except KeyboardInterrupt:
        beacon.stop()
    finally:
        beacon.stop()
