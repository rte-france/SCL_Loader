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

from importlib import import_module

from IEC61850_XML_Class import Communication

##
# \b ACSI services  Generic instance of ACSI services, intended libIEC61850
#
# @para  _ipAdr          the ip adresse of the IED.
# @param IEC_Connection  the relevant instance of  Communication.SubNetwork.ConnectedAP.PhysConn

class GooseTiming:
#    from libiec61850 import ACSI

    def __init__(self):
        self.tGoose      = 0    # The Goose Time as in GooseMessage.T (may differ form the '.t' timestamp(s) embedded in the DataSet.
        self.GooseTimeStamp = 0 # Le time stamp de la detection de uchangement d'état (quand stNum =0)
        self.tArrivalEth = 0    # Driver Ethernet receiver at Ethernet driver side
        self.tArrivalApp = 0    # Actual time when reaching the application

##  Those 4 time stamsp shall allow to evaluate:
#   - the network transit delay tArrivalEth-tGoose
#   - the transit delay between kernel drive to the application container: tArrivalApp - tArrivalEth
# Beware GooseTimeStamp has a specific time reference.

##
# \b Injection_UI:
#
# This class defines:
#       - a method to define a well balanced  simple 3 Currents/Voltages 50Hz signals.
#       - a method to define any unbalanced 3 Currents/Voltages 45-51Hz signal.
#
# Once the signal is defined, it can be used for injection, several signals signal can be defined.
# For this class the voltage is between 0-100V and current between 0-1A or 0-5A for nomimal voltage / current.
# Non nominal Voltage/Current are limited to XXXX for U and YYY for 5A as per the specification of injection box.

class Injection:
    class Simple:
        def __init__ (self, _Voltage, _Current):
            self.Voltage = _Voltage
            self.Current = _Current

    class Complex:
        def __init__(self, _Ua, _Ub, _Uc, _U0, _Ia, _Ib, _Ic, _I0,_Phases):
            self.Ua = _Ua
            self.Ub = _Ub
            self.Uc = _Uc
            self.U0 = _U0
            self.Ia = _Ia
            self.Ib = _Ib
            self.Ic = _Ic
            self.I0 = _I0
    class State:
        On  = 1     # For event trigger, call back if state changes to ON
        Off = 0     # For event trigger, call back if state changes to OFF
        Any = 2     # For event trigger, call back if state changes

    class Injection_CTVT:

        def __init__(self,_BoxName, _ipAdr):
            self.BoxName = _BoxName
            self.ipAdr   = _ipAdr

        def MuxSelection(self, numSelection):
            if numSelection <1 or numSelection > 4:
                return False
            return

        ##
        # \b InjectionNominal
        #
        #   Frequency default is 50Hz, current phasing 60° and voltag 60% (nominal)
        #   U0 / V0 are nul
        #
        # @param    _Simple  an instance of the Signal.Simple Class.
        #
        def InjectionNominal(self, _Simple):

            signalID = None

            return signalID

        ##
        # \b InjectionDetailed all
        #
        # Each voltage and current is described (Amplitube, Phase, Frequency)
        #
        # @param    Simple  an instance of the Signal.Complex Class.
        #
        def InjectionDetailed(self, _Complex):
            signalID = None
            return signalID

        def StartInjection(self, _signalID):

            return

        def StopInjection(self, _signalID):

            return

        ##
        # \b WaitEvent
        #
        #
        #
        def WaitEvent(self, _IOInput, _iState, _callBack):
            return


        def RegisterEvent(self, _IOInput, _iState, _Method):

            return

        def SetOutput(self, IOInput, state):
            return

    class Injection_SV:
        ##
        # \b InjectionNominal
        #
        #   Frequency default is 50Hz, current phasing 120° and voltage 120% (nominal)
        #   U0 / V0 are nul
        #
        # @param    _Simple  an instance of the Signal.Simple Class.
        #
        def InjectionNominal(self, _Simple):

            return

        ##
        # \b InjectionDetailed all
        #
        # Each voltage and current is described (Amplitube, Phase, Frequency)
        #
        # @param    Simple  an instance of the Signal.Complex Class.
        #
        def InjectionDetailed(self, _Complex):

            return

class ACSI:
    class IEDTesting:
#        from utest import IECToolkit
        ##
        # ACSI
        #
        # @para  _ipAdrTools     the ip adress of the testing tools
        # @param IEC_Connection  the relevant instance of  Communication.SubNetwork.ConnectedAP.PhysConn
        def __init__(self, _ipAdrTools, _IEC_Connection, _ServerTimeOut):
            self.ipAdrTools     = _ipAdrTools
            self.TimeOut        = _ServerTimeOut
            self.IEC_Connection = _IEC_Connection

        def Associate( self, IedName, ApName):

            ACSI.Associate(IedName, ApName , self.ipAdr)
            client = self.ACSI.getACSI(IedName + '/' + ApName)
            if client is not None:
                return (client.associate(self.ipAdr))
            return client

        def ReadDataPoint(self, clientID, ApName, IedName, FC, MmsAdrPath):

            ## Appel du service ACSI ReadDataValue

            print("")

        def WriteDataPoint(self, clientID, ApName, IedName, FC, MmsAdrPath):
            print("")
            ## Appel du service ACSI WriteDataValue


    ##
    # \b System services  specific instance for system testing
    #
    # @para  _ipAdrTools     the ip adress of the testing tools
    # @param IEC_Connection  the relevant instance of  Communication.SubNetwork.ConnectedAP.PhysConn


    class SystemTesting:

        def __init__(self, _ipAdrTools, _IEC_Connection, _ServerTimeOut):
            self.ipAdrTools     = _ipAdrTools
            self.TimeOut        = _ServerTimeOut
            self.IEC_Connection = _IEC_Connection

            UTEST     = import_module("utest")
            self.IEC  = getattr(UTEST,"IECToolKit")

            VSUTIL   = import_module("VsUtils")
            self.VS  = getattr(VSUTIL,"variables")


            self.mgr = IECToolkit.Manager(self._ipAdrTools)       # Connect to system test.

        def Associate(self, IedName, ApName, IPAdr):

            clientID = self.mgr.getACSI(IedName+'/'+ApName)
            if clientID is not None:
                return (clientID.associate(IPAdr))                ## TODO ça semble incorrect.

            return clientID

        def ReadDataPoint(self, serverID, ApName, IedName, MmsAdrPath):

            VsName = ApName+IedName+'/' + MmsAdrPath
            serverID.getDataValues(VsName)   ## ==> Update 'VS'
        # TODO manage time-out
            Value = self.VS[VsName]                                 ## ==> Read 'VS'
            return (Value)

        def WriteDataPoint(self, serverID, ApName, IedName, MmsAdrPath, value):
            VsName = ApName+IedName+'/' + MmsAdrPath
            Error= serverID.getDataValues(VsName, value)
            return (Error)

        def WaitGoose(self, DataSetId, GooseID, Do, Da,  Delays, timeOut):

            ## Lecture VS avec delay 1ms

            ## Returns Delays
            return

        def WaitReport(self, DataSetId, GooseID, timeOut):
            return

            ## Lecture VS avec delay 1ms

        ##
    # \b Dummy Services  'a loop back' instance of ACSI services /
    #
    # @para  _ipAdrTools    Unused (dummy service)
    # @param IEC_Connection  the relevant instance of  Communication.SubNetwork.ConnectedAP.PhysConn

    class Dummy:
        def __init__(self, _ipAdrTools, _IEC_Connection, _ServerTimeOut):
            self.ipAdrTools     = _ipAdrTools
            self.TimeOut        = _ServerTimeOut
            self.IEC_Connection = _IEC_Connection
            
			self.CG = CheckDataInitialValue("CodeGeneration")
            self.GM = globalDataModel(TX,'SCL_files/'+ file, None)
			
            print(">> ipAdrTools:" + _ipAdrTools + " IEC_Connection" + " ServerTimeOut:" + _ServerTimeOut)

        def Associate(self, IedName, ApName, IPAdr):
            # TODO ?
            print("associate)")
            return ("dummy")

        def ReadDataPoint(self, clientID, ApName, IedName, FC, MmsAdrPath):
            ## Lecture du data model LOCAL

            print("")

        def WriteDataPoint(self, clientID, ApName, IedName, FC, MmsAdrPath):
            print("")
             ## Ecriture du Data Model Local

class API_Test:
    def __init__(self, _desc):
        self.desc = _desc

    def getAPI_TXT(self,mode):
        if mode=="IED":
            return (ACSI.IEDTesting)
        if mode=="SYSTEM":
            return (ACSI.SystemTesting)
        if mode=="DUMMY":
            return (ACSI.Dummy)

##
# \b MAIN call the unitary test 'Test_ParcoursDataModel'
if __name__ == '__main__':

    ied = API_Test("test iedIED")
    IED = ied.getAPI_TXT("DUMMY")
    X = IED('A','B','C')

    X.Associate('IedName','ApName',"IpAdr")


