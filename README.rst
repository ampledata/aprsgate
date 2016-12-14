aprsgate - Python APRS Gateway
******************************


aprsgate is a Redis PubSub-backed APRS Gateway (IGate, SGate, etc.)


Installation
============
Install from pypi using pip: ``pip install aprsgate``


Usage Examples
==============

TK

Testing
=======
Run nosetests from a Makefile target::

    make test

See Also
========

* `aprs <https://github.com/ampledata/aprs>`_ Python APRS Module. Interface for APRS, APRS-IS, and APRS over KISS.
* `kiss <https://github.com/ampledata/kiss>`_ Python KISS Module. Handles interfacing-to and encoding-for various KISS interfaces.
* `dirus <https://github.com/ampledata/dirus>`_ Dirus is a daemon for managing a SDR to Dire Wolf interface. Manifests that interface as a KISS TCP port.
* `aprsgate <https://github.com/ampledata/aprsgate>`_ Python APRS Gateway. Uses Redis PubSub to run a multi-interface APRS Gateway.
* `aprstracker <https://github.com/ampledata/aprstracker>`_ TK.


Similar Projects
================

* `apex <https://github.com/Syncleus/apex>`_ by Jeffrey Phillips Freeman (WI2ARD). Next-Gen APRS Protocol. (based on this Module! :)
* `aprslib <https://github.com/rossengeorgiev/aprs-python>`_ by Rossen Georgiev. A Python APRS Library with build-in parsers for several Frame types.
* `aprx <http://thelifeofkenneth.com/aprx/>`_ by Matti & Kenneth. A C-based Digi/IGate Software for POSIX platforms.
* `dixprs <https://sites.google.com/site/dixprs/>`_ by HA5DI. A Python APRS project with KISS, digipeater, et al., support.
* `APRSDroid <http://aprsdroid.org/>`_ by GE0RG. A Java/Scala Android APRS App.
* `YAAC <http://www.ka2ddo.org/ka2ddo/YAAC.html>`_ by KA2DDO. A Java APRS Client.
* `Ham-APRS-FAP <http://search.cpan.org/dist/Ham-APRS-FAP/>`_ by aprs.fi: A Perl APRS Parser.
* `Dire Wolf <https://github.com/wb2osz/direwolf>`_ by WB2OSZ. A C-Based Soft-TNC for interfacing with sound cards. Can present as a KISS interface!


Build Status
============

Master:

.. image:: https://travis-ci.org/ampledata/aprsgate.svg?branch=master
    :target: https://travis-ci.org/ampledata/aprsgate

Develop:

.. image:: https://travis-ci.org/ampledata/aprsgate.svg?branch=develop
    :target: https://travis-ci.org/ampledata/aprsgate


Source
======
Github: https://github.com/ampledata/aprsgate

Author
======
Greg Albrecht W2GMD oss@undef.net

http://ampledata.org/

Copyright
=========
Copyright 2016 Orion Labs, Inc.

`APRS <http://www.aprs.org/>`_ is Copyright Bob Bruninga WB4APR wb4apr@amsat.org

License
=======
Apache License, Version 2.0. See LICENSE for details.
