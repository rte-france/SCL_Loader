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

class TraceLevel:
    NOTRACE  = 0
    DETAIL   = 1
    GENERAL  = 2
    ERROR    = 3

class IEC_Console:
    def __init__(self, Niveau):
        self.Niveau   = Niveau
        self.FileId   = None

    def TraceClose(self):
        self.FileId.close()

    def Trace(self, msg, niveau ):
        if self.Niveau == 0:
            return
        if niveau >= self.Niveau:
            print(msg)
        return

class IEC_TraceFile:
    def __init__(self, Niveau, FileName):
        self.Niveau   = Niveau
        self.FileId   = None

        if FileName != '' and FileName is not None:
            self.FileName = FileName
            self.FileId   = open(FileName, "w")

    def TraceClose(self):
        self.FileId.close()

    def Trace(self, msg, niveau ):
        if niveau == 0:
            return
        if  niveau >= self.Niveau:
            if self.FileId is not None:
                txt = msg
                self.FileId.write(txt)
        return

if __name__ == '__main__':

    TR = IEC_TraceFile(TraceLevel.DETAIL,"toto.txt")
    TR.Trace("XXXXXXXXX",TraceLevel.DETAIL)
    TR.TraceClose()

    TR = IEC_TraceFile(TraceLevel.DETAIL,"SCL_files/tata.txt")
    TR.Trace("XXXXXXXXX1\n",TraceLevel.DETAIL)
    TR.Trace("XXXXXXXXX2\n",TraceLevel.DETAIL)
    TR.Trace("XXXXXXXXX3\n",TraceLevel.DETAIL)
    TR.Trace("XXXXXXXXX4\n",TraceLevel.DETAIL)
    TR.TraceClose()


    TRX = IEC_Console(TraceLevel.DETAIL)
    print("DETAIL")
    TRX.Trace(("0 TEST Niveau Detail trace NO TRACE"),TraceLevel.NOTRACE)
    TRX.Trace(("1 TEST Niveau Detail trace DETAIL "),TraceLevel.DETAIL)
    TRX.Trace(("2 TEST Niveau Detail trace GENERAL"),TraceLevel.GENERAL)
    TRX.Trace(("3 TEST Niveau Detail trace ERROR  "),TraceLevel.ERROR)

    TRX = IEC_Console(TraceLevel.GENERAL)
    print("GENERAL")
    TRX.Trace(("0 TEST Niveau Detail trace NO TRACE"),TraceLevel.NOTRACE)
    TRX.Trace(("1 TEST Niveau GENERAL trace DETAIL "),TraceLevel.DETAIL)
    TRX.Trace(("2 TEST Niveau GENERAL trace GENERAL"),TraceLevel.GENERAL)
    TRX.Trace(("3 TEST Niveau GENERAL trace ERROR  "),TraceLevel.ERROR)

    TRX = IEC_Console(TraceLevel.ERROR)
    print("ERROR")
    TRX.Trace(("0 TEST Niveau Detail trace NO TRACE"),TraceLevel.NOTRACE)
    TRX.Trace(("1 TEST Niveau ERROR trace DETAIL "),TraceLevel.DETAIL)
    TRX.Trace(("2 TEST Niveau ERROR trace GENERAL"),TraceLevel.GENERAL)
    TRX.Trace(("3 TEST Niveau ERROR trace ERROR  "),TraceLevel.ERROR)

    TRX = IEC_Console(TraceLevel.NOTRACE)
    print("NOTRACE")
    TRX.Trace(("0 TEST Niveau Detail trace NO TRACE"),TraceLevel.NOTRACE)
    TRX.Trace(("1 TEST Niveau ALARME trace DETAIL "),TraceLevel.DETAIL)
    TRX.Trace(("2 TEST Niveau ALARME trace GENERAL"),TraceLevel.GENERAL)
    TRX.Trace(("3 TEST Niveau ALARME trace ERROR  "),TraceLevel.ERROR)
