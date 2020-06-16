#
# Copyright (c) 2019-2020, RTE (https://www.rte-france.com)
# See AUTHORS.txt
#
# This Source Code Form is subject to the terms of the Apache License, version 2.0.
# If a copy of the Apache License, version 2.0 was not distributed with this file,
# you can obtain one at http://www.apache.org/licenses/LICENSE-2.0.
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of [R#SPACE], [IEC61850 Digital Control System testing.
#

from importlib import import_module
from IEC61850_XML_Class import Communication
from IEC_Trace import Trace as TR
from IEC_Trace import Level as TL

##  Those 4 time stamsp shall allow to evaluate:
#   - the network transit delay tArrivalEth-tGoose
#   - the transit delay between kernel drive to the application container: tArrivalApp - tArrivalEth
# Beware GooseTimeStamp has a specific time reference.
class GooseTiming:
#    from libiec61850 import ACSI

    def __init__(self):
        self.tGoose      = 0    # The Goose Time as in GooseMessage.T (may differ form the '.t' timestamp(s) embedded in the DataSet.
        self.GooseTimeStamp = 0 # Le time stamp de la detection de uchangement d'état (quand stNum =0)
        self.tArrivalEth = 0    # Driver Ethernet receiver at Ethernet driver side
        self.tArrivalApp = 0    # Actual time when reaching the application


## \b ACSI:  key parameters to establish a client server ACSI Association.
#
# This class is holding all data needed to establish a ACSI association.
#
# @param _IedName
# @param _IedIP         The IP Adress to used for this IED/AccessPoint
# @param _APName        The AccessPoint Name, linkg to ConnectedAP in communication.
# @param _SrvTo         The Server Time Out
# @param _SrvDexc       The Server description
#
class ACSI:
    def __init__(self, _IedName, _IedIP, _APName, _SrvTo, _SrvDesc, _iedAdrMMS):
        self.IedName  = _IedName
        self.IedIP    = _IedIP
        self.APName   = _APName
        self.SrvTo    = _SrvTo
        self.SrvDesc  = _SrvDesc
        self.mmsBase  = _IedName + '/' + _APName
        self.iedAdrMMS= _iedAdrMMS

## \b TEST:  a set of abstraction interface to handle IEC61850 rtesting at system level, IED level an ddummy / lop-back testing
#
# This class is holding 3 classes, which instanciate the same set of method:
#
#   __init__
#   Associate           : Create the MMS association between the client and the server
#   ReadDataPoint       : Read a MMS data point, actually a call to the ACSI service GatDataValue
#   WriteDataPoint      : Read a MMS data point, actually a call to the ACSI service GatDataValue

# Service fonctions (see below) the set of the next functions will allow to create 'loop-back' testing when writing the test
# code in a non connected mode:
#
#   CheckValueEqual     : Check that a MMS data point  is equal to a certain value. Work only for final data point (t, q, stVal...)
#   CheckValueInf       : Check that a MMS data point  is Inferior to to a certain value.
#   CheckValueSup       : Check that a MMS data point  is Inferior to to a certain value.
class TEST:

    def CreateDictionary(tMMS, IedName, APName, Mode):

        Variable={}
        for i in range(0, len(tMMS)):
            IecDA = tMMS[i]

            fc          = IecDA.fc
            BasicType   = IecDA.BasicType
            EnumType    = IecDA.EnumType
            TypeValue   = IecDA.TypeValue
            ValKind     = IecDA.ValKind
            IntAdr      = IecDA.IntAdr
            mmsAdr      = IecDA.mmsAdr
            u_mmsAdr    = IecDA.u_mmsAdr

            if Mode=="MMS":
                VAR_ID = IedName + '/' + APName + '/' +  IecDA.mmsAdr
            else:
                VAR_ID = IedName + '/' + APName + '/' + IecDA.u_mmsAdr

            Variable[VAR_ID] = {"mmsAdr": mmsAdr, "IntAdr:": IntAdr, "ValKind": ValKind,
                              "fc": fc, "BasicType": BasicType, "EnumType": EnumType,
                              "TypeValue": TypeValue, "u_mmsAdr": u_mmsAdr}
        return Variable

    ## \b IEDTesting:
    #
    # This class is place holder for the usage of libiec61850
    #
    #
    class IEDTesting:
        # @constructor:
        # @param _ACSI         An instance of the key ACSI parameters to create a connection from the testing tools (client) to a server.
        # @param _ipAdrTools   The IP Address to an external tools
        # @param _desc         A description
        def __init__(self, _ACSI, _ipAdrTools, _desc):
            self.ACSI       = _ACSI
            self.ipAdrTools = _ipAdrTools
            self.desc       = _desc
            self.TR         = TR.Trace.Console()

        def Associate( self, _ACSI_Associate):
            self.IedName    = _ACSI_Associate.IedName

            client = self.ACSI.getACSI(self.ACSI.IedName + '/' + self.ACSIApName)
            if client is not None:
                return (client.associate(self.ipAdr))
            return client

        def ReadDataPoint(self, MmsAdrPath):
            # Calling ACSI ReadDataValue from OpenSource Lib


        def WriteDataPoint(self, MmsAdrPath, value):
            # Appel du service ACSI WriteDataValue

        def CheckValueEqual(self, MmsAdrPath, TestValue):
            return (self.ReadDataPoint(MmsAdrPath) == TestValue)

        def CheckValueInf(self, MmsAdrPath, TestValue):
            return (self.ReadDataPoint(MmsAdrPath) < TestValue)

        def CheckValueSup(self, MmsAdrPath, TestValue):
            return (self.ReadDataPoint(MmsAdrPath) > TestValue)

        def WaitGoose(self, DataSetId, GooseID, Do, Da,  Delays, timeOut):
            return

        def WaitReport(self, DataSetId, GooseID, timeOut):
            return


    ##
    # \b System services  specific instance for system testing
    #
    # @para  ACSI   an instance of the ACSI class
    # @param IEC_Connection  the relevant instance of  Communication.SubNetwork.ConnectedAP.PhysConn
    class SystemTestingActual:
        def __init__(self, _ACSI, _ipAdrTools, _desc):
            self.ACSI       = _ACSI
            self.ipAdrTools = _ipAdrTools
            self.desc       = _desc
            self.TR         = TR.Trace.Console()

            UTEST     = import_module("utest")
            self.IEC  = getattr(UTEST,"IECToolKit")

            VSUTIL   = import_module("VsUtils")
#            self.VS  = getattr(VSUTIL,"variables")

            self.VS      = TEST.CreateDictionary(self.ACSI.iedAdrMMS,self.ACSI.IedName,self.ACSI.APName,"")
            self.VS_MMS  = TEST.CreateDictionary(self.ACSI.iedAdrMMS,self.ACSI.IedName,self.ACSI.APName,"MMS")


        def Associate(self):
            # TODO

            return True

# The address
        # ReadDataPoint for a U-TEST adress: '/' based, FC at DA level
        def ReadDataPoint(self, U_MmsAdr):

            # Get the MMS Adress at U-TEST format:

            X = self.VS[U_MmsAdr]
            MmsAdr = self.ACSI.mmsBase + '/' + X.get('mmsAdr')     # Todo conver MmsAdrPath

            Value = self.VS_MMS[MmsAdr]                                 ## ==> Read 'VS'
            Val = Value.get("TypeValue")
            if Val is None:
                Val="_None_"
            return (Value)

        def WriteDataPoint(self, MmsAdrPath, value):

            VsName = self.ACSI.mmsBase + MmsAdrPath

            Error  = self.mgr.writeDataValues(VsName, value)
            return (Error)

        def CheckValueEqual(self, MmsAdrPath, TestValue ):
            return(self.ReadDataPoint(MmsAdrPath) == TestValue)

        def CheckValueInf(self, MmsAdrPath, TestValue):
            return(self.ReadDataPoint(MmsAdrPath) < TestValue)

        def CheckValueSup(self, MmsAdrPath, TestValue):
            return(self.ReadDataPoint(MmsAdrPath) > TestValue)

        def WaitGoose(self, DataSetId, GooseID, Do, Da,  Delays, timeOut):

            return

        def WaitReport(self, DataSetId, GooseID, timeOut):
            return


            ##
            # \b System services  specific instance for system testing
            #
            # @para  _ipAdrTools     the ip adress of the testing tools
            # @param IEC_Connection  the relevant instance of  Communication.SubNetwork.ConnectedAP.PhysConn
    class Dummy:
        def __init__(self, _ACSI, _ipAdrTools, _desc):
            self.ACSI       = _ACSI
            self.ipAdrTools = _ipAdrTools
            self.desc       = _desc
            self.TR         = TR.Trace.Console()

            ## Create a 'VS' like dictionary based on u_mmsAdr
            self.VS = {}

        def Associate(self):
            clientID = self.ACSI.IedName + '/' + self.ACSI.APName
            self.TR(("Assocation with: " + clientID),TL.DETAIL)
            return clientID

        def ReadDataPoint(self, MmsAdrPath):
            VsName = self.ACSI.mmsBase + MmsAdrPath  # Todo conver MmsAdrPath

            #            self.mgr.getDataValues(VsName)   ## ==> Update 'VS'
            #        # TODO manage time-out
            Value = self.VS[VsName]  ## ==> Read 'VS'
            return (Value)

        def WriteDataPoint(self, MmsAdrPath, value):
            VsName = self.ACSI.mmsBase + MmsAdrPath
            Error = self.mgr.writeDataValues(VsName, value)
            return (Error)

        def CheckValueEqual(self, MmsAdrPath, TestValue):
            return (self.ReadDataPoint(MmsAdrPath) == TestValue)

        def CheckValueInf(self, MmsAdrPath, TestValue):
            return (self.ReadDataPoint(MmsAdrPath) < TestValue)

        def CheckValueSup(self, MmsAdrPath, TestValue):
            return (self.ReadDataPoint(MmsAdrPath) > TestValue)

        def WaitGoose(self, DataSetId, GooseID, Do, Da, Delays, timeOut):
            return

        def WaitReport(self, DataSetId, GooseID, timeOut):
            return

        ##
    # \b Dummy Services  'a loop back' instance of ACSI services /
    #
    # @para  _ipAdrTools    Unused (dummy service)
    # @param IEC_Connection  the relevant instance of  Communication.SubNetwork.ConnectedAP.PhysConn

    class Dummy2:
        def __init__(self, _ACSI, _ipAdrTools, _desc):
            self.ACSI       = _ACSI
            self.ipAdrTools = _ipAdrTools
            self.desc       = _desc
            self.TR         = TR.Trace.Console()


        def Associate(self):
            # TODO ?
            self.TR(("Association with:", self.ACSI.IedName+'/'+self.ACSI.APName),TL.GENERAL)
            return ("dummy")

        def ReadDataPoint(self, MmsAdrPath):
            ## Lecture du data model LOCAL (loop-back mode)

            Adresse  =  'self.DM.' + MmsAdrPath.IntAdr
            self.TR.Trace(("xxx:"+Adresse + ':' + Adresse), TL.DETAIL)

            try:
                Test  = eval(Adresse)  # Verify existence of some initialisation data
                Value = eval(AdrValue)

                return Value

            except Exception as inst:  # No data, an exception is expected hera
                A = type(inst)
                return None


        def WriteDataPoint(self, MmsAdrPath , value):
            AdrValue =  'self.DM.' + MmsAdrPath.IntAdr + ".value"
            eval(AdrValue=value)

        def CheckValueEqual(self, MmsAdrPath, TestValue):
            return (self.ReadDataPoint(MmsAdrPath) == TestValue)

        def CheckValueInf(self, MmsAdrPath, TestValue):
            return (self.ReadDataPoint(MmsAdrPath) < TestValue)

        def CheckValueSup(self, MmsAdrPath, TestValue):
            return (self.ReadDataPoint(MmsAdrPath) > TestValue)

            ## Ecriture du Data Model Local

class API_Test:
    def __init__(self, _desc):
        self.desc = _desc

    def getAPI_TXT(self,mode):
        if mode=="IED":
            return (TEST.IEDTesting)
        if mode=="SYSTEM":
            return (TEST.SystemTestingActual)
        if mode=="DUMMY":
            return (TEST.Dummy)

##
# \b MAIN call the unitary test 'Test_ParcoursDataModel'
if __name__ == '__main__':

    ied = API_Test("test iedIED")
    IED = ied.getAPI_TXT("DUMMY")
    X = IED('A','B','C')

    X.Associate('IedName','ApName',"IpAdr")


