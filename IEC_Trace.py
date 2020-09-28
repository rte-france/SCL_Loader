#
# Copyright (c) 2019-2020, RTE (https://www.rte-france.com)
# See AUTHORS.txt
#
# This Source Code Form is subject to the terms of the Apache License, version 2.0.
# If a copy of the Apache License, version 2.0 was not distributed with this file,
# you can obtain one at http://www.apache.org/licenses/LICENSE-2.0.
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of [R#SPACE], [IEC61850 Digital Contronl System testing.
#

##
# \b TraceLevel: Defines 4 levels of traces
#
#  Defines 4 levels of traces from 0: NO_TRACE, DETAIL, GENERAL and ERROR.
#  The initialisation of the Trace System give the value of the level activated.
#  The call to the trace function inserted in the code, are preset to a certain level (most often "DETAIL").
# @param NOTRACE  No trace are emitted.
# @param DETAIL   Detailed traces are emitted.
# @param GENERAL  On the general traces are emitted (usual mode)
# @param ERROR    Only the ERROR traces are emitted.
class Level:
    ## NOTRACE  No trace are emitted.
    NOTRACE = 0
    ## DETAIL   Detailed traces are emitted
    DETAIL  = 1
    ## GENERAL  On the general traces are emitted (usual mode)
    GENERAL = 2
    ## ERROR    Only the ERROR traces are emitted.
    ERROR   = 3

import logging

##
# \b Trace: class to handle trace to the console and/or to file
# @brief
# This class defines a set of methods to trace information to the console or to file, according to a Level.
# This is mainly for debugging purpose.
# 
class Trace:
    ## \b Description
    #
    # Constructor for Console
    #
    # @param    _Level  :  Session Level value
    # @var     Level    :  Keep the level of Trace
    # @var     FileId   :  File id once opened
    def __init__(self, _Level, File=None):   ## Constructor for Console
        self.Level    = _Level

        if _Level == Level.DETAIL:
            self.Level = logging.DEBUG
        elif _Level == Level.ERROR:
            self.Level = logging.ERROR
        elif _Level == Level.GENERAL:
            self.Level == logging.INFO
        elif _Level == Level.NOTRACE:
            self.Level == logging.NOTSET

        if File is not None:
            logging.basicConfig(filename=File,level=self.Level)
        else:
            logging.basicConfig(level=self.Level)

    # Actual trace output according to the activated level.
    def Trace(self, msg, msgLevel ):
        if msgLevel is Level.NOTRACE:
            return
        if self.Level == Level.DETAIL:
            logging.debug(msg)
        if self.Level == Level.ERROR:
            logging.error(msg)
        if self.Level == Level.GENERAL:
            logging.info(msg)

        return

##
# \b IEC_Trace: unitary test for Tracing
if __name__ == '__main__':

    TR = Trace(Level.DETAIL,"toto.txt")
    TR.Trace("XXXXXXXXX",Level.DETAIL)

    TR.Trace("XXXXXXXXX1\n",Level.DETAIL)
    TR.Trace("XXXXXXXXX2\n",Level.DETAIL)
    TR.Trace("XXXXXXXXX3\n",Level.DETAIL)
    TR.Trace("XXXXXXXXX4\n",Level.DETAIL)

