
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
import sys

import xml.dom.minidom as dom

from IEC_FileListe      import FileListe  as  FL
from IEC_Trace          import Trace
from IEC_Trace          import Level  as TL
from IEC_LN             import Parse_LN

from IEC61850_XML_Class import IED
from IEC_LN             import Parse_LN
from IEC_PrivateSupport import DynImport
from IEC_LNodeType      import Parse_LNodeType

##
# \b Parse_Server: this class create the list of DoType / Data Attributes elements
# @brief
# @b Description
#   This class is parsing the Server section of the XML and its subsequent LogicalDevices
#
#   The main function is Parse IED, which will invoque Parse_Server method and iterativily call IEC_LN..

class Parse_Server:
    ## \b Description
    #   Constructor is used to keep initialize the Parse_LN class (forwarding TRACE class).
    # @param _scl: pointer to the SCL structure created by miniDOM
    # @param _TRX: Trace function
    def __init__(self, _scl, TR, Dico):       ## Constructor for Server
        self.scl        = _scl          ## Pointer to the SCL as provided by 'minidom'.
        self.TR         = TR            ## Instance of the TRACE service.
        self.pLN        = Parse_LN(TR)  ## Invoking the constructor of ParseLN, to initialize TRACE service.
        self.Dyn        = DynImport()
        self.Dict       = Dico          ## From the global model, access to LNode, DO, DA and Enum Types dictionary


    ##
    # Parse the IED list created by  a  self.scl.getElementsByTagName("IED"
    #
    # Features:
    #   - Detects IED defined without any Server part.
    #   - Parse the AccessPoints and the Servers:
    #       - Created nested tables AccessPoint and tables of servers
    #   - Once the Server level is reached, the parsing continue with:
    #       - Parse_LD_LN
    #           - Parse LN (from IEC_LN class
    #
    # @param  iIED_array: the trace Object type to look up.
    # @param  pServer    pointer to the SCL structure
    # @param  idxAP         index to access a an instance of AccessPoint
    # @param  idxServer     index to access a an instance of Server
    #
    # @return
    #
    # \bThe DataModel is build dynamically by 'setAttr'

    def Parse_LD_LN(self, iIED_array, pServer, idxAP, idxServer):

        tLDevice = []
        LDi     = pServer
        inst    = LDi.getAttribute("inst")        ## Identification of the LDevice within the IED. Identification of the LDevice within the IED. Its value cannot be the empty string.
        ldName  = LDi.getAttribute("ldName")      ## The explicitly specified name of the logical device according to IEC 61850-7-1  and 7-2 within the communication.           
        desc    = LDi.getAttribute("desc")        ## The description text
        trLDevice = "     LDevice: " + ldName + ' inst:' + inst + ' desc:' + desc
        self.TR.Trace(trLDevice, TL.GENERAL)
        iDeviceInstance = IED.AccessPoint.Server.LDevice(inst, ldName, desc)  # LN0 et les LN sont ajoutés après

        iIED_array.tAccessPoint[idxAP].tServer[idxServer].tLDevice.append(iDeviceInstance)

        LDeviceName = ldName + inst
        tLN = []      # Table of LN0 and LNs instanciation in the current Logical Device.
        LN_index = 0  # Index to this array
        pLNi = LDi.firstChild.nextSibling
        lnClass1 = ""
        LNtxt = ""
        while pLNi is not None:
            if pLNi.localName is None:
                pLNi = pLNi.nextSibling
                continue

            if pLNi.localName == 'Private':
                pLNi = pLNi.nextSibling
                continue

            iLN = self.pLN.Parse_LN(pLNi, iIED_array.name, iIED_array.tAccessPoint[idxAP].name, iIED_array.tDAI)
            tLN.append(iLN)

            LNtxt = ("       LN: " + iLN.lnPrefix + '_' + iLN.lnType + '_' + iLN.lnInst + \
                     " Class:" + iLN.lnClass + ' Desc:' + iLN.lnDesc)
            self.TR.Trace((LNtxt), TL.DETAIL)
            # The tree of nested level of DO / SDO / DA / SDA ishnadled in IEC_ParcoursDataModel
            LN_id = iLN.lnPrefix + iLN.lnClass + iLN.lnInst
            #                        tLN.append(iLN)
            LN_index = LN_index + 1
            setattr(iDeviceInstance, LN_id, iLN)  # = LDeviceInstance

            lstDO= self.Dict.LNodeType.getIEC_LNodeType(iLN.lnType)
            iLN.tDO = lstDO.tDO
            for iDO in lstDO.tDO:
                try:
                    x= eval( 'iLN.' +iDO.DOname)
                except:
                    e = sys.exc_info()[0]
                    print(e)

                try:
                    setattr(iLN,iDO.DOname, iDO)

                except TypeError as ex:             # For DOI 'name' is renamed to 'DOame' (The CDC DPL as a 'name' property)
                    print("Exception" + ex)

                lstDA = self.Dict.DoType.getIEC_DoType(iDO.type)
                iDO.tDA = lstDA.tDA
                for iDA in lstDA.tDA:
                    try:
                        setattr(iDO, iDA.name, iDA)
                    except TypeError as ex:         # Risk of name Clash if a DAI is 'name'.
                        print("Exception" + ex)

                    if iDA.bType == 'Struct':
                        typeStruct = iDA.type
                        lstDA2 = self.Dict.DaType.getIEC_DaType(iDA.type)
                        for iDA2 in lstDA2.tBDA:
                            try:
                                setattr(iDA, iDA2.name, iDA2)
                            except TypeError as ex:
                                print("Exception" + ex)

            if (pLNi.nextSibling) is not None:
                pLNi = pLNi.nextSibling
                continue

        LDi = LDi.nextSibling
        iDeviceInstance.LN = tLN
#        Name = iDeviceInstance.inst
        return iDeviceInstance, iDeviceInstance.inst

    ##
    # Parse the IED list created by  a  self.scl.getElementsByTagName("IED"
    #
    # Features:
    #   - Detects IED defined without any Server part.
    #   - Parse the AccessPoints and the Servers:
    #       - Created nested tables AccessPoint and tables of servers
    #   - Once the Server level is reached, the parsing continue with:
    #       - Parse_LD_LN
    #           - Parse LN (from IEC_LN class
    #
    # @param   TR: the trace Object type to look up.
    # @return  tIED_array: the table of IED and their full data model

    def Parse_IED(self,TR):
        LD_index  = 0
        tIED_array   = []       ## Iterative version of the Data Model: Table of LN, Table of DO....
        tIED_struct  = []       ## Named based version of the Data Model:  MEASURE.MMXU.X.X

        IEDlst = self.scl.getElementsByTagName("IED")
        for ied in IEDlst:
            IEDname             = ied.getAttribute("name")                 ## The identification of the IED, 'Template' in ICD, unique in SCD.
            _desc                = ied.getAttribute("desc")                 ## The description text
            _type                = ied.getAttribute("type")                 ## The (manufacturer specific) IED product type
            _manufacturer        = ied.getAttribute("manufacturer")         ## The manufacturer's name
            _configVersion       = ied.getAttribute("configVersion")        ## The basic configuration version of this IED configuration
            _originalSclVersion  = ied.getAttribute("originalSclVersion")   ## The original SCL schema version of the IEDs ICD file; optional
            _originalSclRevision = ied.getAttribute("originalSclRevision")  ## The original SCL schema revision of the IEDs ICD file; optional
            _engRight            = ied.getAttribute("engRight")             ## The engineering right transferred by a SED file
            _owner               = ied.getAttribute("owner")                ## The owner project of this IED,
            self.TR.Trace(("IED:"+IEDname+' type:' + _type + ' desc:' + _desc),TL.DETAIL)

            iIED_array  = IED(IEDname, _desc, _type, _manufacturer, _configVersion, _originalSclVersion, _originalSclRevision, _engRight, _owner)

            iIED_struct = IED(IEDname, _desc, _type, _manufacturer, _configVersion, _originalSclVersion, _originalSclRevision, _engRight, _owner)

            Services = ied.firstChild.nextSibling
    # Skip any Private...
            while (Services.localName is None):
                Services = Services.nextSibling
                continue
    # Skip Service section (Parsed in a different section)

            while Services.localName == "Private":
                type = Services.getAttribute("type")
                self.Dyn.PrivateDynImport(type, Services, iIED_array)
                self.Dyn.PrivateDynImport(type, Services, iIED_struct)
                Services = Services.nextSibling
                Services = Services.nextSibling

            if Services.localName == "Services":
                Services = Services.nextSibling
                Services = Services.nextSibling
            ## AccessPoint.localName: is the key to the ConnectedAP related to this access point
            if Services.localName=="AccessPoint":
                pAcccess = Services

                _name   = pAcccess.getAttribute("name")         ## The description text
                _desc   = pAcccess.getAttribute("desc")         ## Reference identifying this access point within the IED
                _router = pAcccess.getAttribute("router")       ## The presence and setting to true defines this IED to have a router function.
                _clock  = pAcccess.getAttribute("clock")        ## The presence and setting to true defines this IED to be a master clock at this bus.
                _AccessPoint = IED.AccessPoint(_name,_desc,_router,_clock )
                iIED_array.tAccessPoint.append(_AccessPoint)
                idxAccessPoint = len(iIED_array.tAccessPoint)-1

                if Services.firstChild is None:
                    ### In case of a strict client application, the access Point is only declared
                    self.TR.Trace(("AccessPoint: no firstChild"),TL.DETAIL)
                    continue
                else:
                    ServerSection = Services.firstChild.nextSibling

                    if (ServerSection is None):  #Pas de Server, application client pure
                        self.TR.Trace(('Application client:', IEDname, desc ),TL.DETAIL)
                        continue
                    if (ServerSection.firstChild is None):  # Pas de Server, application client pure
                        TR.Trace(('Application client:', IEDname, desc),TL.DETAIL)
                        if (len(iIED_struct.tAccessPoint))> 0:
                            iIED_struct.tAccessPoint[idxAccessPoint].tServer = None
                        else:
                            iIED_struct.tAccessPoint = None
                            iIED_array.Server   = None
                            iIED_struct.Server  = None
                        iIED_array.tLDevice  = None
                        iIED_struct.tLDevice = None
                        continue
                    else:
                        while ServerSection.localName == "Server":
                            _desc    = ServerSection.getAttribute("desc")      ## A descriptive text
                            _timeout = ServerSection.getAttribute("timeout")   ## Time out in seconds: if a started transaction isnot completed within this time, it is cancelled and reset
                            iServer = IED.AccessPoint.Server(_desc,_timeout)
                            iIED_array.tAccessPoint[idxAccessPoint].tServer.append(iServer)

                            idxServer =0

                            pServer   = ServerSection.firstChild.nextSibling
                            while pServer.nextSibling:
                                if pServer.localName is None:
                                    pServer = pServer.nextSibling
                                    continue

                                if pServer.localName == "Authentication":
                                   none        = pServer.getAttribute("none")        ## IEC  No authentication
                                   password    = pServer.getAttribute("password")    ## Defined in the stack mappings (SCSMs)
                                   weak        = pServer.getAttribute("weak")        ## Defined in the stack mappings (SCSMs)
                                   strong      = pServer.getAttribute("strong")      ## Defined in the stack mappings (SCSMs)
                                   certificate = pServer.getAttribute("certificate") ## Defined in the stack mappings (SCSMs)
        # TODO eventually AccesPoint without server
                                   iAuthentication = IED.AccessPoint.Server.Authentication(none,password,weak,strong,certificate)
                                   iIED_array.tAccessPoint[idxAccessPoint].tServer[idxServer].authentication = iAuthentication

                                   pServer = pServer.nextSibling
                                   continue

                                if pServer.localName == "Private":         # TODO est-ce qu'il y a des balises privées RTE ?
                                    pServer = pServer.nextSibling
                                    continue

                                if pServer.localName == "LDevice":
                                    iDeviceInstance,Name = self.Parse_LD_LN(iIED_array, pServer, idxAccessPoint, idxServer)
                                    setattr(iIED_array.tAccessPoint[idxAccessPoint].tServer[idxServer], Name, iDeviceInstance)  # = LDeviceInstance
                                    pServer = pServer.nextSibling
                                    continue

                            ServerSection = ServerSection.nextSibling
                            if ServerSection is None:
                                break
# Version itérative
            tIED_array.append(iIED_array)

# Version structurée
#            iIED_struct.Server   = tServer
#            tIED_struct.append(iIED_struct)
            continue
            self.TR.Trace(("FIN SERVER"), TL.DETAIL)

        self.TR.Trace(("FIN IED"),TL.DETAIL)
        return tIED_array

##
# \b Test_IED_Server: unitary test for Parse_IED

class Test_IED_Server:
    def main(directory, file, scl):
        TRX = Trace.Console(TL.DETAIL)

        TRX.Trace(("---------------------------------------------------"), TL.GENERAL)
        if scl is None:  # UNIT TEST
            scl = dom.parse(directory + file)
        TRX.Trace(("File:" + file), TL.GENERAL)
        iIED = Parse_Server(scl, TRX)

        tIEDglobal= iIED.Parse_IED(TRX)
        TRX.Trace(("END of IEC_IED_Server"), TL.GENERAL)
##
# \b MAIN call the unitary test 'Test_IED_Server for Parse_IED
if __name__ == '__main__':
    fileliste = FL.lstFull  # List of system files (SCD..)
    for file in fileliste:
        Test_IED_Server.main('SCL_files/', file, None)

    fileliste = FL.lstIED   # List of IED files (ICD, IID, ..)
    for file in fileliste:
        Test_IED_Server.main('SCL_files/', file, None)