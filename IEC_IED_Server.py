
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

import xml.dom.minidom as dom

from IEC_FileListe      import FileListe  as  FL
from IEC_Trace          import IEC_Console as TConsole
from IEC_Trace          import TraceLevel  as TL
from IEC_LN             import Parse_LN

from IEC61850_XML_Class import IED
from IEC_LN             import Parse_LN


##
# \b Parse_Server: this class create the list of DoType / Data Attributes elements
# @brief
# @b Description
#   This class is parsing the Server section of the XML and its subsequent LogicalDevices
#
#   The main function is Parse IED, which will invoque Parse_Server method and iterativily call IEC_LN..

class Parse_Server:
    def __init__(self, _scl, TR):       ## Constructor for Server
        ## \b Description
        #   Constructor is used to keep initialize the Parse_LN class (forwarding TRACE class).
        # @param _scl: pointer to the SCL structure created by miniDOM
        # @param _TRX: Trace function

        self.scl        = _scl          ## Pointer to the SCL as provided by 'minidom'.
        self.TR         = TR            ## Instance of the TRACE service.
        self.pLN        = Parse_LN(TR)  ## Invoking the constructor of ParseLN, to initialize TRACE service.

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
        inst    = LDi.getAttribute("inst")
        ldName  = LDi.getAttribute("ldName")
        desc    = LDi.getAttribute("desc")
        trLDevice = "     LDevice: " + ldName + ' inst:' + inst + ' desc:' + desc
        self.TR.Trace(trLDevice, TL.GENERAL)
        iDeviceInstance = IED.AccessPoint.Server.LDevice(inst, desc, ldName)  # LN0 et les LN sont ajoutés après

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
            if (pLNi.nextSibling) is not None:
                pLNi = pLNi.nextSibling
                continue

        LDi = LDi.nextSibling
        iDeviceInstance.LN = tLN
        Name = '_' + iDeviceInstance.inst + '_'
        setattr(iIED_array.tAccessPoint[idxAP].tServer[idxServer], Name, iDeviceInstance )  # = LDeviceInstance

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
        tIED_array   = []       # Iterative version of the Data Model: Table of LN, Table of DO....
        tIED_struct  = []       # Named based version of the Data Model:  MEASURE.MMXU.X.X

        IEDlst = self.scl.getElementsByTagName("IED")
        for ied in IEDlst:
            type                = ied.getAttribute("type")
            IEDname             = ied.getAttribute("name")
            desc                = ied.getAttribute("desc")
            originalSclVersion  = ied.getAttribute("originalSclVersion")  # Key to access the type details
            originalSclRevision = ied.getAttribute("originalSclRevision")
            configVersion       = ied.getAttribute("configVersion")
            manufacturer        = ied.getAttribute("manufacturer")
            engRight            = ied.getAttribute("engRight")
            owner               = ied.getAttribute("owner")
            self.TR.Trace(("IED:"+IEDname+' type:'+type+' desc:'+desc),TL.DETAIL)

            iIED_array  = IED(IEDname, type, desc, originalSclVersion, originalSclRevision \
                                          , configVersion ,manufacturer, engRight, owner)

            iIED_struct = IED(IEDname, type, desc, originalSclVersion, originalSclRevision \
                                          , configVersion ,manufacturer, engRight, owner)
            Services = ied.firstChild.nextSibling
    # Skip any Private...
            while (Services.localName is None) or (Services.localName=="Private"):
                Services = Services.nextSibling
                continue
    # Skip Service section (Parsed in a different section)
            if Services.localName=="Services":
                Services = Services.nextSibling
                Services = Services.nextSibling
            ## AccessPoint.localName: is the key to the ConnectedAP related to this access point
            if Services.localName=="AccessPoint":
                pAcccess = Services

                _name   = pAcccess.getAttribute("name")
                _desc   = pAcccess.getAttribute("desc")
                _router = pAcccess.getAttribute("router")
                _clock  = pAcccess.getAttribute("clock")
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
                    _desc    = ServerSection.getAttribute("desc")
                    _timeout = ServerSection.getAttribute("timeout")
                    iServer = IED.AccessPoint.Server(_desc,_timeout)
                    iIED_array.tAccessPoint[idxAccessPoint].tServer.append(iServer)

                    idxServer =0

                    pServer   = ServerSection.firstChild.nextSibling
                    while pServer.nextSibling:
                        if pServer.localName is None:
                            pServer = pServer.nextSibling
                            continue

                        if pServer.localName == "Authentication":        # On ne traite pas section ...
                           none        = pServer.getAttribute("none")
                           password    = pServer.getAttribute("password")
                           weak        = pServer.getAttribute("weak")
                           strong      = pServer.getAttribute("strong")
                           certificate = pServer.getAttribute("certificate")
# TODO eventually AccesPoint without server
                           iAuthentication = IED.AccessPoint.Server.Authentication(none,password,weak,strong,certificate)
                           iIED_array.tAccessPoint[idxAccessPoint].tServer[idxServer].authentication = iAuthentication

                           pServer = pServer.nextSibling
                           continue
                        if pServer.localName == "Private":         # TODO est-ce qu'il y a des balises privées RTE ?
                            pServer = pServer.nextSibling
                            continue

                        if pServer.localName == "LDevice":
                            self.Parse_LD_LN(iIED_array, pServer, idxAccessPoint, idxServer)
                            pServer = pServer.nextSibling
                            break

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
        TRX = TConsole(TL.DETAIL)

        TRX.Trace(("---------------------------------------------------"), TL.GENERAL)
        if scl is None:  # UNIT TEST
            scl = dom.parse(directory + file)
        TRX.Trace(("File:" + file), TL.GENERAL)
        iIED = Test_IED_Server(scl, TRX)

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