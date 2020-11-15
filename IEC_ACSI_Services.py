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
import time


from IEC_Trace import Trace
from IEC_Trace import Level as TL
from IEC_FileListe import FileListe
from IEC_ParcoursDataModel import globalDataModel
from IEC_FileListe import FileListe as FL
#import ACSI_Services as IED_ACSI

#dummy implementation...
class ACSI_Services:
    def __init__(self, _desc):
        self.desc = _desc

    def Associate(self, iedName, apName):
        print("Associaton with"+iedName+apName)


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
# @param _IedName       The IED name..
# @param _IedIP         The IP Adress to used for this IED/AccessPoint/Server
# @param _APName        The AccessPoint Name, linkg to ConnectedAP in communication.
# @param _SrvTo         The Server Time Out
# @param _DataModel     The hiearchical data model from the SCL / including DOI / DAI / SDI value
# @param _iedAdrMMS     The table of MMS address for the IED.
#
class ACSI:
    def __init__(self, _IedName, _IedIP, _APName, _SrvTo, _DataModel, _iedAdrMMS):
        self.IedName    = _IedName
        self.IedIP      = _IedIP
        self.APName     = _APName
        self.SrvTo      = _SrvTo
        self.DataModel  = _DataModel
        self.mmsBase    = _IedName + '/' + _APName
        self.iedAdrMMS  = _iedAdrMMS

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

    def CreateDictionary(tMMS, IedName, APName):

        t0 = time.time()
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

            Variable[IecDA.mmsAdr] = {"mmsAdr": mmsAdr, "IntAdr": IntAdr, "ValKind": ValKind,
                                      "fc": fc, "BasicType": BasicType, "EnumType": EnumType,
                                     "TypeValue": TypeValue, "u_mmsAdr": u_mmsAdr}

            Variable[IecDA.u_mmsAdr] = {"mmsAdr": mmsAdr, "IntAdr": IntAdr, "ValKind": ValKind,
                                        "fc": fc, "BasicType": BasicType, "EnumType": EnumType,
                                       "TypeValue": TypeValue, "u_mmsAdr": u_mmsAdr}
        t1 = time.time()
        deltaT = t1 - t0
        print("Time to create dictionaries" + str(deltaT) + " for: "  + str(len(tMMS))+ " datapoints.\n")

        return Variable

    ## \b IEDTesting:
    #
    # This class is place holder for the usage of libiec61850
    #
    #
    class IED:
        # @constructor:
        # @param _ACSI         An instance of the key ACSI parameters to create a connection from the testing tools (client) to a server.
        # @param _ipAdrTools   The IP Address to an external tools
        # @param _desc         A description
        def __init__(self, _ACSI, _ipAdrTools, _desc):
            self.ACSI       = _ACSI
            self.ipAdrTools = _ipAdrTools
            self.desc       = _desc
            self.VS         = TEST.CreateDictionary(self.ACSI.iedAdrMMS,self.ACSI.IedName,self.ACSI.APName)
            self.srvACSI    = ACSI_Services(_desc)

        def Associate( self):
            print("ACSI Assocation")
            client = self.srvACSI.Associate(self.ACSI.IedName,self.ACSI.APName)
#            if client is not None:
#                return (client.associate(self.ipAdr))
            return client

        def ReadDataPoint(self, MmsAdrPath):
##          Need to actually call the IED level library

            DataPoint = self.VS[MmsAdrPath]
            IntrAdr = DataPoint.get("IntAdr")

            print("Value"+Value)

        def WriteDataPoint(self, MmsAdrPath, value):
##          Need to actually call the IED level library
            return value

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
    class System:
        def __init__(self, _ACSI, _ipAdrTools, _desc):  # _ACSI will be None in System Case.
            self.ACSI       = _ACSI
            self.ipAdrTools = _ipAdrTools
            self.desc       = _desc
            self.T          = Trace(TL.GENERAL)

            UTEST     = import_module("utest")
            self.IEC  = getattr(UTEST,"IECToolKit")

            self.uTest  = self.IEC("Test dummy sytem)")
            self.mgr    = self.uTest.Manager(_ipAdrTools)

## ACTUAL CODE REQUIRED:
##            VSUTIL   = import_module("VsUtils")
##            self.VS  = getattr(VSUTIL,"variables")

        def Associate(self, ACSI):
# Testing   self.ACSI = ACSI
            self.VS   = TEST.CreateDictionary(self.ACSI.iedAdrMMS,self.ACSI.IedName,self.ACSI.APName)


            return True

        def ReadDataPoint(self, MmsAdr):


            DataPoint = self.VS[MmsAdr]

## To access to dictionary data:
#          IntrAdr = DataPoint.get("IndAddr")

            Value = DataPoint.get("TypeValue")
            if Value is None:
                Value="_None_"
            return (Value)

        def WriteDataPoint(self, MmsAdrPath, value):

            VsName = self.ACSI.mmsBase + MmsAdrPath

            Error  = self.mgr.writeDataValues(VsName, value)
            return (Error)

        def CheckValueEqual(self, MmsAdrPath, TestValue ):
            return(self.ReadDataPoint(MmsAdrPath,None) == TestValue)

        def CheckValueInf(self, MmsAdrPath, TestValue):
            return(self.ReadDataPoint(MmsAdrPath,None) < TestValue)

        def CheckValueSup(self, MmsAdrPath, TestValue):
            return(self.ReadDataPoint(MmsAdrPath,None) > TestValue)

        def WaitGoose(self, DataSetId, GooseID, Do, Da,  Delays, timeOut):

            return

        def WaitReport(self, DataSetId, GooseID, timeOut):
            return


            ##
            # \b System services  specific instance for system testing
            #
            # @para  _ipAdrTools     the ip adress of the testing tools
            # @param IEC_Connection  the relevant instance of  Communication.SubNetwork.ConnectedAP.PhysConn

        ##
    # \b Dummy Services  'a loop back' instance of ACSI services /
    #
    # @para  _ipAdrTools    Unused (dummy service)
    # @param IEC_Connection  the relevant instance of  Communication.SubNetwork.ConnectedAP.PhysConn

    class Dummy:
        def __init__(self, _ACSI, _ipAdrTools, _desc):
            self.ACSI       = _ACSI
            self.ipAdrTools = _ipAdrTools
            self.desc       = _desc
            self.T          = Trace(TL.DETAIL)
            self.VS         = TEST.CreateDictionary(self.ACSI.iedAdrMMS,self.ACSI.IedName,self.ACSI.APName)

        def Associate(self):
            clientID = self.ACSI.IedName + '/' + self.ACSI.APName
            self.T.Trace(("Assocation with: " + clientID),TL.DETAIL)
            return clientID

        def ReadDataPointReport(self, mmsAdr):
            DataPoint = self.VS['REPORT/'+mmsAdr]
            return(DataPoint)

        def ReadDataPointGoose(self, mmsAdr):
            DataPoint = self.VS['GOOSE/'+mmsAdr]
            return(DataPoint)

        def ReadDataPointACSI(self, mmsAdr):
            ## Lecture du data model LOCAL (loop-back mode)

            DataPoint = self.VS[mmsAdr]
            IntAdr = DataPoint.get('IntAdr')
            Adresse  =  'self.ACSI.DataModel.' + IntAdr
            self.T.Trace(("xxx:"+Adresse + ':' + Adresse), TL.DETAIL)

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
            return (TEST.IED)
        if mode=="SYSTEM":
            return (TEST.System)
        if mode=="DUMMY":
            return (TEST.Dummy)

##
# \b MAIN call the unitary test 'Test_ParcoursDataModel'
if __name__ == '__main__':

    TR1  = Trace(TL.DETAIL)
    TX   = Trace(TL.DETAIL,"Trace_FctTst.txt")
    tIEDfull=[]

    myCpt = 0

    tstAPI  = API_Test("test iedIED")
    dumACSI = tstAPI.getAPI_TXT("DUMMY")
    iedACSI = tstAPI.getAPI_TXT("IED")
    sysACSI = tstAPI.getAPI_TXT("SYSTEM")

    for file in FileListe.lstSystem1:

        GM = globalDataModel(TR1, FL.root + file, None)

        indIED = 0
        T0 = time.time()
        sysTst = sysACSI(None, '10.10.92.55', ' System Testing')    # ASCI Param will change for each IED

        for ied in GM.tIED:
            t0_ied = time.time()
            tIEC_adresse = GM.BrowseDataModel(ied)
            if ied.IP is None:
                ip = '0.0.0.0'
            else:
                ip = ied.IP
            nbDa = len(GM.tIED)

            #     ACSI_(self, _IedName, _IedIP, _APName, _SrvTo, _SrvDesc, _iedAdrMMS):
            IedAP_Model = GM.tIED[indIED].tAccessPoint[0].tServer[0]
            ACSIparam = ACSI(ied.name, ied.IP, ied.tAccessPoint[0].name, IedAP_Model.timeout, IedAP_Model, tIEC_adresse)
            IED_ID    = ied.name + ' - ' + ied.tAccessPoint[0].name

# ACSI initialisation and association for System
            sysTst.ACSI = ACSIparam
            IED1_sys    = sysTst.Associate(ACSIparam)

# ACSI initialisation and association for 'dummy' testing (loop-back)
            dummyTst    = dumACSI(ACSIparam, '0.0.0.0'    , ' Loopback testing')
            ID          = dummyTst.Associate()

# ACSI initialisation and association for IED testing
            iedTst      = iedACSI(ACSIparam, '0.0.0.0'    , ' IED testing')
            IED1        = iedTst.Associate()

            i = 0
            for iec in tIEC_adresse:
                if iec.IntAdr is None:  ## 'q' and 't' are excluded
                    continue

                A = "GM.tIED[" + str(indIED) + "].tAccessPoint[0].Server[0]." + iec.IntAdr  ## 'q' and 't' are excluded
                AdrValue = "GM.tIED[" + str(indIED) + "].tAccessPoint[0].tServer[0]." + iec.IntAdr + ".value"
                try:
                    Test  = eval(AdrValue)  # Verify existence of some initialisation data
                    Value = eval(AdrValue)

                    X1 = dummyTst.ReadDataPoint(iec.mmsAdr)     # Internal address to the data Model
                    X2 = iedTst.ReadDataPoint(iec.mmsAdr)       # Actual MMS adress (related to IED name AP name)
                    X3 = sysTst.ReadDataPoint(iec.u_mmsAdr)     #Actual U_TEST (related to IED name AP name)

                    if (Value != None):
                        TR1.Trace((ied.name + ' - ' + ied.tAccessPoint[0].name +  AdrValue + ": ", Value),TL.GENERAL)
                        i = i + 1
                except Exception as inst:  # No data, an exception is expected hera
                    A = type(inst)
                    if (A == "<class 'AttributeError'>"):
                          break

            TX.Trace(("IED:" + IED_ID + "nbDA:" + str(nbDa) + " NbMmsADr:" + str(i)), TL.GENERAL)
            indIED = indIED + 1

        TempsTotal = str(time.time() - T0)
        TX.Trace(("Total Time:" + file + ':' + TempsTotal), TL.GENERAL)
        TX.Trace(("*** finished *** "), TL.GENERAL)





