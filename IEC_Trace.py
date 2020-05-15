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

##
# \b Trace: class to handle trace to the console and/or to file
# @brief
# This class defines a set of methods to trace information to the console or to file, according to a Level.
# This is mainly for debugging purpose.
# 
class Trace:
    ##
    # \b Console: output traces to the Python console
    # @brief
    # Tracing to the Python Console.
    # 
    class Console:
        ## \b Description
        #
        # Constructor for Console
        #
        # @param    _Level  :  Session Level value
        # @var     Level    :  Keep the level of Trace
        # @var     FileId   :  File id once opened
        def __init__(self, _Level):     ## Constructor for Console
            self.Level   = _Level       ## Level   :  Keep the level of Trace
            self.FileId   = None        ## FileId  :  File id once opened
        ##
        # Closing the channel
        def TraceClose(self):
            self.FileId.close()

        ##
        # Actual trace output according to the activated level.
        def Trace(self, msg, msgLevel ):
            if self.Level == 0:
                return
            if msgLevel >= self.Level:
                print(msg)
            return

    ## \b Description
    # \b TraceFile: output traces to a file
    # @brief
    # Tracing to a defined file.
    #
    class File:
        ##
        # Constructor for file based traces.
        #
        # @param  _Level    : Session Level value
        # @param  _FileName : File to be used as an output
        # @var    Level     : Keep the level of Trace
        # @var    FileId    : ID of the trace file
        def __init__(self, _Level, _FileName):  ## Constructor for file logging
            self.Level   = _Level   ## Level   :  Keep the level of Trace
            self.FileId   = None    ## FileId  :  File id once opened
    
            if _FileName != '' and _FileName is not None:
                self.FileName =_FileName
                self.FileId   = open(_FileName, "w")
        ##
        # Closing the file
        def Close(self):
            self.FileId.close()
    
        ##
        # Actual trace output according to the activated level.
        def Trace(self, msg, msgLevel ):
            if msgLevel == 0:
                return
            if  msgLevel >= self.Level:
                if self.FileId is not None:
                    txt = msg
                    self.FileId.write(txt)
            return
##
# \b IEC_Trace: unitary test for Tracing
if __name__ == '__main__':

    TR = Trace.File(Trace.Level.DETAIL,"toto.txt")
    TR.Trace("XXXXXXXXX",Trace.Level.DETAIL)
    TR.Trace.Close()

    TR = Trace.File(Trace.Level.DETAIL,"SCL_files/tata.txt")
    TR.Trace("XXXXXXXXX1\n",Trace.Level.DETAIL)
    TR.Trace("XXXXXXXXX2\n",Trace.Level.DETAIL)
    TR.Trace("XXXXXXXXX3\n",Trace.Level.DETAIL)
    TR.Trace("XXXXXXXXX4\n",Trace.Level.DETAIL)
    TR.Trace.Close()


    TRX = Trace.Console(Trace.Level.DETAIL)
    print("DETAIL")
    TRX.Trace(("0 TEST Level Detail trace NO TRACE"),Trace.Level.NOTRACE)
    TRX.Trace(("1 TEST Level Detail trace DETAIL "),Trace.Level.DETAIL)
    TRX.Trace(("2 TEST Level Detail trace GENERAL"),Trace.Level.GENERAL)
    TRX.Trace(("3 TEST Level Detail trace ERROR  "),Trace.Level.ERROR)

    TRX = Trace.Console(Trace.Level.GENERAL)
    print("GENERAL")
    TRX.Trace(("0 TEST Level Detail trace NO TRACE"),Trace.Level.NOTRACE)
    TRX.Trace(("1 TEST Level GENERAL trace DETAIL "),Trace.Level.DETAIL)
    TRX.Trace(("2 TEST Level GENERAL trace GENERAL"),Trace.Level.GENERAL)
    TRX.Trace(("3 TEST Level GENERAL trace ERROR  "),Trace.Level.ERROR)

    TRX = Trace.Console(Trace.Level.ERROR)
    print("ERROR")
    TRX.Trace(("0 TEST Level Detail trace NO TRACE"),Trace.Level.NOTRACE)
    TRX.Trace(("1 TEST Level ERROR trace DETAIL "),Trace.Level.DETAIL)
    TRX.Trace(("2 TEST Level ERROR trace GENERAL"),Trace.Level.GENERAL)
    TRX.Trace(("3 TEST Level ERROR trace ERROR  "),Trace.Level.ERROR)

    TRX = Trace.Console(Trace.Level.NOTRACE)
    print("NOTRACE")
    TRX.Trace(("0 TEST Level Detail trace NO TRACE"),Trace.Level.NOTRACE)
    TRX.Trace(("1 TEST Level ALARME trace DETAIL "),Trace.Level.DETAIL)
    TRX.Trace(("2 TEST Level ALARME trace GENERAL"),Trace.Level.GENERAL)
    TRX.Trace(("3 TEST Level ALARME trace ERROR  "),Trace.Level.ERROR)
