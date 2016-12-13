#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python APRS Gateway Functions."""

import aprsgate

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2016 Orion Labs, Inc.'
__license__ = 'All rights reserved. Do not redistribute.'


def reject_frame(aprs_frame):
    if aprsgate.REJECT_PATHS.intersection(aprs_frame.path):
        print 'Rejecting Path "%s"', aprs_frame.path
        return True
    elif aprs_frame.text.startswith('}'):
        print 'Rejecting Internet "%s"', aprs_frame.text
        return True

    for frame_path in aprs_frame.path:
        if frame_path.startswith('q'):
            print 'Rejecting q "%s"', frame_path
            return True

    return False
