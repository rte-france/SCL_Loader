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
from IEC_Trace      import Trace
from IEC_Trace      import Level  as TL
from IEC_PrivateSupport import DynImport
from IEC_FileListe  import FileListe as FL
from IEC61850_XML_Class import IED

##
# \b Parse_LN: this class create the list of LN0 and LN as well as all sub-classes
# @brief
# @b Description
#   This class is parsing the Server section of the XML and its subsequent LogicalDevices
#
#   The main function is Parse IED, which will invoque Parse_Server method and iterativily call IEC_LN..
class Parse_LN:
    ##
    # __init__(self , _TR)
    #
    # Constructor for LN parsing, initialieze the DynImport class
    #
    # @param _TR    Trace system

    def __init__(self, _TR):
        self.TRX      = _TR             ## Instance of the TRACE service.
        self.Dyn      = DynImport()     ## Create an instance of DynImpot for private TAG




    ##
    # \b Parse_LN:
    #
    # Main function of this class
    #
    # The function hierarchy is as follow
    #
    # Parse_LN
    #   - private:   <private>  .... </Private>
    #       - Dyn.Import (from IEC_PrivateSupport)
    #   - inputs:
    #           - invoke the method Parse_ExtRef() from this class
    #   - DOI:
    #       - invoke the methode Parse_DOI() from this class
    #           - ParseDAI_VAL() invoked by Parse_DOI()
    #           - Parse_SDI() invoked by Parse_DOI()
    #   - Log (not parsed)             \b #TODO not supported
    #   - SettingControl (not parsed)  \b #TODO not supported
    #   - GSEControl (local to this method)
    #   - LogControl (local to this method)
    #   - SampledValueControl (local to this method)
    #   - DataSet:
    #        - invoke the method Parse_DataSet() from this class
    #   - ReportControl:
    #        - invoke the method Parse_ReportControl() from this class
    #
    # @param pLN        : is the result of scl.getElementsByTagName("DataTypeTemplates")
    # @param IEDname    : Use to create the full IEC oath to the data
    # @param AP_Name    : Use to create the full IEC oath to the data
    # @param tDAI       : table of DAi
    #
    # @return iLN       : The logical node with all its sub-classes.

    def Parse_LN(self, pLN, IEDname, AP_Name, tDAI):
        #
        # LN contains DataSet, ReportControl, GooseControl and DOI/SDI.../SDI/DAI sections (up to 3 levels of SDI
        #
        _lnPrefix = pLN.getAttribute("prefix")      ## The LN prefix part (none for LN0)
        _lnClass  = pLN.getAttribute("lnClass")     ## The LN class according to IEC 61850-7-x or other domain specific standards (LLN0 for LN0)
        _inst     = pLN.getAttribute("inst")        ## The LN instance number identifying this LN – an unsigned integer; leading zeros are
                                                    ## not recommended, as they formally lead to another instance identification (Not presnet for LN0)
        _lnType   = pLN.getAttribute("lnType")      ## The instantiable type definition of this logical node, reference to a LNodeType definition
        _desc     = pLN.getAttribute("desc")        ## The description text for the logical node

        iLN = IED.AccessPoint.Server.LN(_lnPrefix, _lnType, _inst, _lnClass, _desc)

        if pLN.firstChild is not None:  # pLN is used to browse the XML tree
            pLN = pLN.firstChild.nextSibling  #
        else:
            return iLN                   # LN0 is empty, usually the case for ICD IID file

        tiRCB = []  # Tableau des instances des RCB du LN0
        tiSVC = []  # Tableau des instances des SVC du LN0
        tiGCB = []  # Tableau des instances des GCB du LN0
        tiLCB = []  # Tableau des instances des LCB du LN0
        tExtRef = []  # Tableau des ExtRef (Inputs)
        tDS = []  # Tableau des instances des DatatSet du LN0 (l'objet DA contient la liste des FCDA)
        tiDOI = []
        while pLN:
            if pLN.localName is None:
               pLN = pLN.nextSibling
               continue

            if pLN.localName == "Private":
                type = pLN.getAttribute("type")
                self.Dyn.PrivateDynImport(type, pLN, iLN)      # Dynamic import for private
                pLN = pLN.nextSibling
                continue

            if pLN.localName == "Inputs":  # < Inputs >
                #  < ExtRef doName = "SPCSO3" daName = "q" serviceType = "GOOSE"...
                self.TRX.Trace(("      *** Inputs"), TL.DETAIL)
                iLN.tInputs = self.Parse_ExtRef(pLN)
                pLN = pLN.nextSibling
                continue

            if pLN.localName == "DOI":  ### DOI et DAI à TRAITER DANS LE DATA MODEL.
                self.TRX.Trace(("      *** DOI"), TL.DETAIL)
                LN_id = iLN.lnPrefix + iLN.lnClass + iLN.lnInst
                DoName = IEDname + AP_Name + '/' + LN_id  # Use for collecting DAI
                iDOI, iLN = self.Parse_DOI(iLN, pLN, DoName)
                tiDOI.append(iDOI)
                pLN = pLN.nextSibling
                continue

            # TODO ???gérer les balises Log, et SettingControl? .

            if pLN.localName == "Log":  # Non utilisé dans R#Space
                self.TRX.Trace(("      Log: NON TRAITE"), TL.ERROR)
                pLN = pLN.nextSibling
                continue

            if pLN.localName == "LogControl":  # Non utilisé dans R#Space
                self.TRX.Trace(("      LogControl"), TL.DETAIL)
                tiLCB = self.Parse_LogControl(pLN, tiLCB)
                pLN = pLN.nextSibling
                continue

            if pLN.localName == "SettingControl":  # Non utilisé dans R#Space
                self.TRX.Trace(("      SettingControl: NON TRAITE"), TL.ERROR) ## TODO handle the SettingControl class
                pLN = pLN.nextSibling
                continue

            if pLN.localName == "GSEControl":
                self.TRX.Trace(("      GSEControl"), TL.DETAIL)
                _name            = pLN.getAttribute("name")             ## The name identifying this GOOSE control block
                _desc            = pLN.getAttribute("desc")             ## A description text
                _datSet          = pLN.getAttribute("datSet")           ## The name of the data set to be sent by the GSE control block.
                _confRev         = pLN.getAttribute("confRev")          ## The configuration revision number of this control block.
                _type            = pLN.getAttribute("type")             ## The default type value is GOOSE (GSSE is deprecated)
                _appID           = pLN.getAttribute("appID")            ## A system wide unique identification of the application to which the GOOSE message belong
                _fixedOffs       = pLN.getAttribute("fixedOffs")        ## Default value false. If set to true it shows all receivers, that the values GOOSE message have fixed offset.
                _securityEnabled = pLN.getAttribute("securityEnabled")  ## Default: None. Allows to configure the security options per control block instance.
                GOOSE = IED.AccessPoint.Server.LN.GSEControl(_name, _desc, _datSet, _confRev, _type, _appID, _fixedOffs,
                                                             _securityEnabled )
                # Get the list of IED/LD which subscribe to the Goose
                if pLN.firstChild is not None:
                    pIEDlst = pLN.firstChild
                    while pIEDlst.nextSibling is not None:
                        pIEDlst = pIEDlst.nextSibling
                        if pIEDlst.localName == "IEDName":
                            _apRef   = pIEDlst.getAttribute("apRef")
                            _ldInst  = pIEDlst.getAttribute("ldInst")
                            _lnClass = pIEDlst.getAttribute("lnClass")
                            _name = pIEDlst.firstChild.nodeValue
                            self.TRX.Trace(("IED: " + _name + " ,apRef:" + _apRef + " ,ldInst:" + _ldInst + " ,lnClass:+" + _lnClass),TL.DETAIL)
                            IEDSub = IED.AccessPoint.Server.LN.GSEControl.IEDGSESub(_apRef,_ldInst, _lnClass, _name)
                            GOOSE.tIED.append(IEDSub)

                tiGCB.append(GOOSE)
                self.TRX.Trace(("     GSEControl, name: " + _name + " datSet:" + _datSet), TL.DETAIL)
                pLN = pLN.nextSibling
                continue

            if pLN.localName == "SampledValueControl":
                self.TRX.Trace(("      SampledValueControl"), TL.DETAIL)
                _name        = pLN.getAttribute("name")                 ## name	        A name identifying this SMV control block
                _desc        = pLN.getAttribute("desc")                 ## desc	        The description text
                _datSet      = pLN.getAttribute("datSet")               ## datSet       The name of the data set whose values shall be sent.
                _confRev     = pLN.getAttribute("confRev")              ## confRev	    The configuration revision number of this control block; mandatory.
                _smvID       = pLN.getAttribute("smvID")                ## smvID	    Multicast CB: the MsvID for the sampled value definition as defined (Unicast: deprecated)
                _multicast   = pLN.getAttribute("multicast")            ## multicast    Indicates Unicast SMV services only meaning that smvID = UsvI
                _smpRate     = pLN.getAttribute("smpRate")              ## smpRate	    Sample rate as defined in IEC 61850-7-2. If no smpMod is defined, i
                _nofASDU     = pLN.getAttribute("nofASDU")              ## nofASDU	    Number of ASDU (Application service data unit) – see IEC 61850-9-2
                _smpMod      = pLN.getAttribute("smpMod")               ## smpMod	    The sampling mode as defined in IEC 61850-7-2; default: SmpPerPeriod; i
                _securityEnabled = pLN.getAttribute("securityEnabled")  ## securityEnabled Default: None. Allows to configure the security options per control block instance

                SVC = IED.AccessPoint.Server.LN.SampledValueControl(_name, _desc, _datSet, _confRev, _smvID, _multicast,
                                                                    _smpRate, _nofASDU,  _smpMod, _securityEnabled)
                self.TRX.Trace(("     SampledValueControl, name:" + _name + " smvID:" + _smvID + " datSet:" + _datSet), TL.DETAIL)

                # Get the list of IED/LD which subscribe to the Goose
                if pLN.firstChild is not None:
                    pIEDlst = pLN.firstChild
                    while pIEDlst.nextSibling is not None:
                        pIEDlst = pIEDlst.nextSibling
                        if pIEDlst.localName == "IEDName":
                            _apRef   = pIEDlst.getAttribute("apRef")
                            _ldInst  = pIEDlst.getAttribute("ldInst")
                            _lnClass = pIEDlst.getAttribute("lnClass")
                            _name = pIEDlst.firstChild.nodeValue
                            self.TRX.Trace(("IED: " + _name + " ,apRef:" + _apRef + " ,ldInst:" + _ldInst + " ,lnClass:+" + _lnClass), TL.DETAIL)
                            IEDSub = IED.AccessPoint.Server.LN.SampledValueControl.IEDSVCSub(_apRef,_ldInst, _lnClass, _name)
                            SVC.tIED.append(IEDSub)
                        pSVC= pIEDlst
                        if pSVC.localName == "SmvOpts":
                            _refreshTime        = pSVC.getAttribute("refreshTime")
                            _sampleSynchronized = pSVC.getAttribute("sampleSynchronized")
                            _sampleRate         = pSVC.getAttribute("sampleRate")
                            _dataSet            = pSVC.getAttribute("dataSet")
                            _security           = pSVC.getAttribute("security")
                            _synchSourceId      = pSVC.getAttribute("synchSourceId")
                            _timestamp          = pSVC.getAttribute("timestamp")
                            SVC.SmvOption = IED.AccessPoint.Server.LN.SampledValueControl.smvOption(_refreshTime, \
                                    _sampleSynchronized,_sampleRate,_dataSet,_security,_synchSourceId,_timestamp)



                tiSVC.append(SVC)

                #TODO Parse smvOptions
                ##
                # \b smvOption
                #
                #  param refreshTime       The meaning of the options is described in IEC 61850-7-2.
                #  param sampleRate        If any of the attributes is set to true, the appropriate values shall be included into the SMV telegram
                #  param dataSet           If the attribute is set to true, the dataset name shall be included into the SMV telegram
                #  param security          See IEC61850-9-2...
                #  param synchSourceId     if true, the SV message contains the identity of the synchronizing master clock according to IEC 61850-9-3; default = false
                          
                pLN = pLN.nextSibling
                continue

            # Extraction of data Set:
            #   <DataSet name = "DS_TAXD" desc = "Data Set..." >
            #       <FCDA  ldInst = "LD_all" prefix = "" lnInst = "1" lnClass = "TAXD" doName = "EEName"   fc = "DC" />
            #       <FCDA  ldInst = "LD_all" prefix = "" lnInst = "1" lnClass = "TAXD" doName = "EEHealth" fc = "ST" />
            #       <FCDA  ldInst = "LD_all" prefix = "" lnInst = "1" lnClass = "TAXD" doName = "AxDspSv"  fc = "MX" / >
            #       <FCDA  ldInst = "LD_all" prefix = "" lnInst = "1" lnClass = "TAXD" doName = "SmpRte"   fc = "SP" />
            #   </DataSet >

            if pLN.localName == "DataSet":
                _name = pLN.getAttribute("name")      ##
                _desc = pLN.getAttribute("desc")      ##
                self.TRX.Trace(("     DataSet, dsName:" + _name + " desc:" + _desc), TL.DETAIL)
                DS = IED.AccessPoint.Server.LN.DataSet(_name, _desc)  # "" Tableau des  FCDA
                DS = self.Parse_DataSet(pLN, DS)
                tDS.append(DS)
                pLN = pLN.nextSibling
                continue

            if pLN.localName == "ReportControl":
                self.TRX.Trace(("      ReportControl"), TL.DETAIL)
                iRCB = self.Parse_ReportControl(pLN)
                tiRCB.append(iRCB)
                pLN = pLN.nextSibling
                continue

            continue

        iLN.tSVCtrl = tiSVC
        iLN.tDataSet = tDS
        iLN.tGSECtrl = tiGCB
        iLN.tRptCtrl = tiRCB
        iLN.tLogCtrl = tiLCB
        iLN.tiDOI    = tiDOI
        return iLN

    ##
    # \b Parse_DataSet:
    #
    # Parsing the dataset and its list of FCDA
    #
    # @param    pLN : pointer to SCL DataSet section
    # @param    DS  : DataSet object, the tFCDA table is used to collect the list of  FCDA for the DataSet
    #
    # @return  DS: table of FCDA

    def Parse_DataSet(self, pLN, DS):

        FCDAi = pLN.firstChild
        while FCDAi:
            if FCDAi.localName is None:
                FCDAi = FCDAi.nextSibling
                continue
            _ldInst = FCDAi.getAttribute("ldInst")   ## The LD where the DO resides
            _prefix = FCDAi.getAttribute("prefix")   ## Prefix identifying together with lnInst and lnClass the LN where the DO resides
            _lnClass= FCDAi.getAttribute("lnClass")  ##  LN class of the LN where the DO resides;
            _lnInst = FCDAi.getAttribute("lnInst")   ## Instance number of the LN where the DO resides
            _doName = FCDAi.getAttribute("doName")   ## A name identifying the DO (within the LN). A name standardized in IEC 61850-7-4.
            _daName = FCDAi.getAttribute("daName")   ## The attribute name – if missing, all attributes with functional characteristic given by fc are selected
            _cf     = FCDAi.getAttribute("fc")       ## All attributes of this functional constraint are selected. See IEC 61850-7-2 or the fc definition in 9.5
            _ix     = FCDAi.getAttribute("ix")       ## An index to select an array element in case that one of the data elements is an array.
            iFCDA   = IED.AccessPoint.Server.LN.DataSet.FCDA(_ldInst, _prefix, _lnClass, _lnInst, _doName, _daName, _cf, _ix)
            DS.tFCDA.append(iFCDA)
            FCDAi = FCDAi.nextSibling

        return DS

    ##
    # \b Parse_ReportControl
    #
    # Parsing the Report Control structures: RCB, TrgOps, RptEnabled
    #
    # @param    pLN : pointer to SCL ReportControl section
    #
    # @return  DS: table of FCDA

    def Parse_ReportControl(self, pLN):

        _name       = pLN.getAttribute("name")          ##  name	    Name of the report control block.
        _desc       = pLN.getAttribute("desc")          ##  desc	    The description text
        _rptID      = pLN.getAttribute("rptID")         ##  datSet	    The name of the data set to be sent by the report control block
        _datSet     = pLN.getAttribute("datSet")        ##  intgPd	    Integrity period in milliseconds – see IEC 61850-7-2. Only relev
        _intgPd     = pLN.getAttribute("intgPD")        ##  rptID	    Identifier for the report control block, optional.
        _confRev    = pLN.getAttribute("confRev")       ##  confRev	    The configuration revision number of this report control block.
        _buffered   = pLN.getAttribute("buffered")      ##  buffered	Specifies if reports are buffered or not – see IEC 61850-7-2; de
        _bufTime    = pLN.getAttribute("bufTime")       ##  bufTime	    Buffer time – see IEC 61850-7-2; default: 0
        _indexed    = pLN.getAttribute("indexed")       ##  indexed	    If true, the report control block instance names are built from supplied name, followed by an index number from 01 up to maximum 99.

        #    _Opt      = LN.getAttribute("optFields")
        iRCB = IED.AccessPoint.Server.LN.ReportControl(_name, _desc, _datSet, _intgPd, _rptID, _confRev, _buffered, _bufTime, _indexed)
        self.TRX.Trace(("ReportControl: " + _rptID + " name:" + _name + " datSet" + _datSet), TL.DETAIL)
        # Récupération des attribues des sous-sections: TrgOps, OptFields et RptEnabled
        rptCtrl = pLN.firstChild
        while rptCtrl:
            if rptCtrl.localName is None:
                rptCtrl = rptCtrl.nextSibling
                continue
            if rptCtrl.localName == "Private":
                rptCtrl = rptCtrl.nextSibling
                continue
            if rptCtrl.localName == "TrgOps":
                self.TRX.Trace(("ReportControl: TrgOps"), TL.DETAIL)
                _qchg = rptCtrl.getAttribute("qchg")
                _dchg = rptCtrl.getAttribute("dchg")
                _dupd = rptCtrl.getAttribute("dupd")
                _period = rptCtrl.getAttribute("period")
                _gi = rptCtrl.getAttribute("gi")
                iRCB.TrgOps = IED.AccessPoint.Server.LN.TrgOps(_qchg, _dchg, _dupd, _period, _gi)

                rptCtrl = rptCtrl.nextSibling
                continue

            if rptCtrl.localName == "OptFields":
                _seqNum     = rptCtrl.getAttribute("seqNum")
                _timeStamp  = rptCtrl.getAttribute("timeStamp")
                _reasonCode = rptCtrl.getAttribute("reasonCode")
                _dataSet    = rptCtrl.getAttribute("dataSet")
                _dataRef    = rptCtrl.getAttribute("dataRef")
                _entryID    = rptCtrl.getAttribute("entryID")
                _configRef  = rptCtrl.getAttribute("configRef")
                _bufOvfl    = rptCtrl.getAttribute("bufOvfl")
                iRCB.OptField = IED.AccessPoint.Server.LN.ReportControl.OptFields(_seqNum, _timeStamp, _reasonCode, _dataSet,
                                                                                 _dataRef, _entryID, _configRef,_bufOvfl)
                rptCtrl = rptCtrl.nextSibling
                continue

            if rptCtrl.localName == "RptEnabled":
                self.TRX.Trace(("ReportControl: RptEnabled"), TL.DETAIL)
                _max = rptCtrl.getAttribute("max")
                iRCB.RptEnable = IED.AccessPoint.Server.LN.ReportControl.RptEnabled(_max)

                pClientLN = rptCtrl.firstChild
                if pClientLN is not None:
                    pClientLN = pClientLN.nextSibling

                    while pClientLN is not None:
                        if pClientLN.localName == "ClientLN":
                            self.TRX.Trace(("ReportControl: ClientLN"), TL.DETAIL)
#iedName, _ldInst, _lnPrefix, _lnClass, _lnInst, _desc, _apRef):
                            _iedName    = pClientLN.getAttribute("iedName")   ## The name of the IED where the LN resides
                            _ldInst     = pClientLN.getAttribute("ldInst")    ## The instance identification of the LD where the LN resides
                            _prefix     = pClientLN.getAttribute("prefix")    ## The LN prefix
                            _lnClass    = pClientLN.getAttribute("lnClass")   ## The LN class according to IEC 61850-7-4
                            _lnInst     = pClientLN.getAttribute("lnInst")    ## The instance id of this LN instance of below LN class in the IED
                            _desc       = pClientLN.getAttribute("desc")      ## optional descriptive text, e.g. about purpose of the client
                            _apRef      = pClientLN.getAttribute("apRef")     ## Application reference

                            iClientLN = IED.AccessPoint.Server.LN.ReportControl.RptEnabled.ClientLN(_iedName,_ldInst, _prefix, _lnClass, _lnInst, _desc, _apRef)
                            iRCB.RptEnable.tClientLN.append(iClientLN)
                        pClientLN = pClientLN.nextSibling
                        continue

                rptCtrl = rptCtrl.nextSibling
                continue
        return iRCB

    ##
    # \b Parse_LogControl
    #
    # Parsing the LogControl section
    # @param   pLN   : pointer to SCL ReportControl section
    # @param   tiLCB : Table of instance of Log Control Block (empty)
    #
    # @return  tiLCB : Table of instance of Log Control Block completed

    def Parse_LogControl(self, pLN, tiLCB):
        _name       = pLN.getAttribute("name")      ## name the name of the log control block
        _desc       = pLN.getAttribute("desc")      ## A description text
        _datSet     = pLN.getAttribute("datSet")    ## The name of the data set whose values shall be logged; datSet should only be
        _intgPd     = pLN.getAttribute("intgPd")    ## Integrity scan period in milliseconds – see IEC 61850-7-2.
        _ldInst     = pLN.getAttribute("ldInst")    ## The identification of the LD where the log resides; if missing, the same LD
        _prefix     = pLN.getAttribute("prefix")    ## Prefix of LN where the log resides; if missing, empty string
        _lnClass    = pLN.getAttribute("lnClass")   ## Class of the LN where the log resides; if missing, LLN0
        _lnInst     = pLN.getAttribute("lnInst")    ## Instance number of LN, where the log resides; missing for LLN0
        _logName    = pLN.getAttribute("logName")   ## Relative name of the log within its hosting LN; name of the log element
        _logEna     = pLN.getAttribute("logEna")    ## TRUE enables immediate logging; FALSE prohibits logging until enabled online
        _reasonCode = pLN.getAttribute("reasonCode")## If true, the reason code for the event trigger is also stored into the log –

        iLogControl = IED.AccessPoint.Server.LN.LogControl(_name, _desc, _datSet, _intgPd, _ldInst, _prefix, _lnClass, _lnInst, _logName, _logEna,_reasonCode)

        self.TRX.Trace(("      LogControl: name:" + _name + " datSet: " + _datSet + " logName:" + _logName), TL.DETAIL)
        logCtrl = pLN.firstChild
        while logCtrl:
            if logCtrl.localName is None:
                logCtrl = logCtrl.nextSibling
                continue
            if logCtrl.localName == "Private":
                self.TRX.Trace(("      LogControl: Private"), TL.DETAIL)
                logCtrl = logCtrl.nextSibling
                continue
            if logCtrl.localName == "TrgOps":
                self.TRX.Trace(("      LogControl: TrgOps"), TL.DETAIL)
                _qchg = logCtrl.getAttribute("qchg")
                _dchg = logCtrl.getAttribute("dchg")
                _dupd = logCtrl.getAttribute("dupd")
                _period = logCtrl.getAttribute("period")
                _gi = logCtrl.getAttribute("gi")

                iTrgOps = IED.AccessPoint.Server.LN.TrgOps(_qchg, _dchg, _dupd, _period, _gi)
                self.TRX.Trace(("        TrgOps qchg" + _qchg + " dchg:" + _dchg + " dupd:" + _dupd + \
                                " period+" + _period + "_gi" + _gi), TL.DETAIL)
                iLogControl.TrgOps = iTrgOps
                logCtrl = logCtrl.nextSibling
                continue
        tiLCB.append(iLogControl)
        return tiLCB

    ##
    # \b Parse_ExtRef
    #
    # Parse the tInputs sections of a LN0 declaration
    #
    # Features:
    #   - Create instance of an 'ExtRef' object by getting the attributes froml the SCL IED defined without any Server part.
    #   - Dynamically calling Private support class/method if a private is encountered.
    #
    # @return  tInputs: the table of ExtRef objects
    def Parse_ExtRef(self, pLN):
        _tInputs = IED.AccessPoint.Server.LN.Inputs([])

        pExtRef= pLN.firstChild.nextSibling
        while pExtRef:
            if pExtRef.localName is None:
                pExtRef = pExtRef.nextSibling
                continue
            if pExtRef.localName=='Private':
                type=  pExtRef.getAttribute("type")
                self.Dyn.PrivateDynImport(type, pExtRef, IED.AccessPoint.Server.LN.Inputs )

            if pExtRef.localName=='ExtRef':
                _iedName = pExtRef.getAttribute("iedName")
                _ldInst  = pExtRef.getAttribute("ldInst")
                _prefix  = pExtRef.getAttribute("prefix")
                _lnClass = pExtRef.getAttribute("lnClass")
                _lnInst  = pExtRef.getAttribute("lnInst")

                _doName  = pExtRef.getAttribute("doName")
                _daName  = pExtRef.getAttribute("daName")
                _intAddr = pExtRef.getAttribute("intAddr")

                _desc    = pExtRef.getAttribute("desc")

                _serviceType = pExtRef.getAttribute("serviceType")

                _srcLDInst = pExtRef.getAttribute("srcLDInst")
                _srcPrefix = pExtRef.getAttribute("srcPrefix")
                _srcLNClass= pExtRef.getAttribute("srcLNClass")
                _srcLNInst = pExtRef.getAttribute("srcLNInst")
                _srcCBName = pExtRef.getAttribute("srcCBName")

                _pServT     = pExtRef.getAttribute("pServT")
                _pLN        = pExtRef.getAttribute("pLN")
                _pDO        = pExtRef.getAttribute("pDO")
                _pDA        = pExtRef.getAttribute("pDA")

                iExtRef = IED.AccessPoint.Server.LN.Inputs.ExtRef(_iedName, _ldInst, _prefix, _lnClass, _lnInst, _doName, _daName, _intAddr, _desc, _serviceType,
                                            _srcLDInst, _srcPrefix, _srcLNClass, _srcLNInst, _srcCBName, _pDO, _pLN, _pDA, _pServT)

                _tInputs.tExtRef.append(iExtRef)
    
            pExtRef = pExtRef.nextSibling
        return _tInputs

    ##
    # \b Parse_DOI
    #
    # Features:
    #   - Create instance of an 'DAI' and collected sub-sequent value
    #
    # The code of Parse_SDI(pDAI1, iDOI, n, TRX)is used to collect the
    # value of DO/DA looking like this:
    #         <DAI name="SIUnit" valKind="RO">
    #==>        <Val>cos(phi)</Val>           <===
    #          </DAI>
    #
    # @return  pDAI    new value of the pointer to SCL
    # @return  _value   _value found (or None)
    # @return  iDOI     modified instance DOI.

    def Parse_DOI(self, iLN, pDOI, DoName):                 # Instance of LN  & DOI is scl pointto DOI tag
        DOname           = pDOI.getAttribute("name")        ## The name identifying this GOOSE control block
        _type           = pDOI.getAttribute("type")         ## The type references the id of a DOType definition
        _accessControl  = pDOI.getAttribute("accessControl")## The configuration revision number of this control block.
        _transient      = pDOI.getAttribute("transient")    ##
        _desc           = pDOI.getAttribute("desc")         ## A description text
        _ix             = pDOI.getAttribute("ix")           ## Index of a data element in case of an array type; shall not be used if DOI has no array type
        self.TRX.Trace(("DOI: name:" + DOname + " desc:" + _desc), TL.DETAIL)
        iDOI = IED.AccessPoint.Server.LN.DOI(DOname, _type, _accessControl,_transient, _desc, _ix) # None for RTE private Type
        setattr( iLN ,iDOI.DOname,iDOI)

        pDAI = pDOI.firstChild

        while pDAI:
            if pDAI.localName is None:      # <DOIS name = "LEDRS" desc ="RstOper"
                pDAI = pDAI.nextSibling         # <SDI name="Oper">
                continue                        # <SDI name="origin">

            p1 = pDAI
            if p1.localName == "Val":
                _value = p1.firstChild.data
                iDOI.value = _value
                print("xxxxxxxxxxx Value for DOI", iDOI.DOname, _value)
                self.TRX.Trace(("    Balise1 <VAL/>: " + _value), TL.DETAIL)

            if pDAI.localName == "Private":     # <DAI name="orCat" sAddr="96.1.3.10.4" />
                type=pDAI.getAttribute("type")

                if type == "eTr-IEC61850-90-2":
                    pI90_2 = pDAI.firstChild.nextSibling
                    if (pI90_2.nodeName == "eTr-IEC61850-90-2:ProxyOf"):
                        _externalScl  = pI90_2.getAttribute("externalScl")
                        _iedName      = pI90_2.getAttribute("iedName")
                        _ldInst       = pI90_2.getAttribute("ldInst")
                        _prefix       = pI90_2.getAttribute("prefix")
                        _lnClass      = pI90_2.getAttribute("lnClass")
                        _lnInst       = pI90_2.getAttribute("lnInst")
                        _doName       = pI90_2.getAttribute("doName")
                        iDOI.IEC_90_2 = IED.AccessPoint.Server.LN.DOI.IEC_90_2(_externalScl,_iedName,_ldInst, _prefix, _lnClass, _lnInst, _doName )

                elif type == "IEC_60870_5_104": # WG10 PRIVATE
                    p104 = pDAI.firstChild
                    if p104 is not None:
                        p104 = p104.nextSibling

                        if (p104.localName == "Address") and (p104.nodeName == "'IEC_60870_5_104:Address'"):
                            _casdu      = p104.getAttribute("casdu")
                            _ioa        = p104.getAttribute("ioa")
                            _ti         = p104.getAttribute("ti")
                            _usedBy     = p104.getAttribute("usedBy")
                            _inverted   = p104.getAttribute("inverted")
                            iDOI.IEC104 = IED.AccessPoint.Server.LN.DOI.IEC104(_casdu,_ioa, _ti, _usedBy, _inverted )
                else:
                    self.Dyn.PrivateDynImport(type, pDAI, iDOI)
                    pDAI = pDAI.nextSibling
                    continue                                               #     <DAI name="Test" sAddr="96.1.3.10.8" />

            if pDAI.localName == "DAI":                             # <DAI name="ctlNum" sAddr="96.1.3.10.6" />
                pX, value, iDAI = self.Parse_DAI_VAL(pDAI, iDOI)     # <DAI name="T" sAddr="96.1.3.10.7" />
                print("DAI Value"+value)
                iDOI.tDAI.append(iDAI)
                pDAI = pDAI.nextSibling
                continue                                               #     <DAI name="Test" sAddr="96.1.3.10.8" />

            if pDAI.localName == "SDI":                             # <DAI name="Check" sAddr="96.1.3.10.9" />
                self.Parse_SDI(pDAI, iDOI, DoName)
                pDAI = pDAI.nextSibling
                continue

            pDAI = pDAI.nextSibling
    
        return iDOI,iLN

    ##
    # \b Parse_DAI_VAL
    #
    # @param pDAI         The SCL pointer to DAI
    # @param iDOI	      The current instance of a DOI
    #
    # @return   pDAI      pDAI is pointing to the next Tag
    # @return  _value
    # @return  iDOI             The meaning of the value from the engineering phases. If missing, the valKind from the type definition applies for any attached value.

    def Parse_DAI_VAL(self, pDAI, iDOI):
        _value = None
        tDAI = []
        if pDAI.localName == "DAI":
            _name    = pDAI.getAttribute("name")  		# The attribute name; the type tAttributeNameEnum restricts to the attribute names
            											# from IEC 61850-7-3, plus new ones starting with lower case letters
            _fc      = pDAI.getAttribute("fc")    		# The functional constraint for this attribute; fc=SE always also implies fc=SG;
            											# fc=SG means that the values are visible, but not editable
            _dchg    = pDAI.getAttribute("dchg")  		# Defines which trigger option is supported by the attribute (value true means supported). One of those allowed according to IEC61850-7-3 shall be chosen.
            _qchg    = pDAI.getAttribute("qchg")   		#  One of those allowed according to IEC61850-7-3 shall be chosen.
            _dupd    = pDAI.getAttribute("dupd")

            _sAddr   = pDAI.getAttribute("sAddr")   	# an optional short address of this  attribute (see 9.5.4.3)

            _bType   = pDAI.getAttribute("bType")   	# The basic type of the attribute, taken from tBasicTypeEnum (see 9.5.4.2)
            _type    = pDAI.getAttribute("type")    	# The basic type of the attribute, taken from tBasicTypeEnum (see 9.5.4.2)
            _count   = pDAI.getAttribute("count")   	# Optional. Shall state the number of array elements or reference the attribute stating
            											# this number in case that this attribute is an array. A referenced attribute shall exist
            											# in the same type definition. The default value 0 states that the attribute is no array.
            _valKind  = pDAI.getAttribute("valKind")	# Determines how the value shall be interpreted if any is given – see Table 46
            _valImport= pDAI.getAttribute("valImport") 	# if true, an IED / IED configurator can import values modified by another tool from an SCD file,
            											# even if valKind=RO or valKind=Conf. It is the responsibility of the IED configurator
            											# to assure value consistency and value allowance even if valImport is true.
            _desc    = pDAI.getAttribute("desc")   		# Some descriptive text for the attribute
            _DoDaSdo = ''      						    # Used to distinguish DO from SDO (only one class for both) #implementation
            _SDO     = ''
            _value   = ''      						    # Actual initialized value

            iDAI = IED.AccessPoint.Server.LN.DAI( _name, _fc, _dchg, _qchg, _dupd, _sAddr, _bType, _type, _count,
                                                  _valKind, _valImport, _desc, '', '', '')  # _value !
            setattr(iDOI, _name, iDAI)
            tDAI.append(iDAI)

            # Is there a value ?
            p1 = pDAI.firstChild
            if p1 is not None:  # The SCL may contains empty tag like </xxxx> <xxxx/>
                p1 = p1.nextSibling
                if (p1.firstChild is not None):

                    if p1.localName == "Val":
                        _value = p1.firstChild.data
                        iDAI.value = _value
                        self.TRX.Trace(("    Balise1 <VAL/>: " + _value), TL.DETAIL)
                        p1 = p1.firstChild.nextSibling

                    if p1 is not None and p1.localName == "Private":
                        pType = pDAI.firstChild.nextSibling
                        _type = pType.getAttribute("type")
                        self.Dyn.PrivateDynImport(_type, pType, iDAI)

                    setattr(iDOI, _name, iDAI)  # I add the iDAI named '_name' to iDOI
                else:
                    setattr(iDOI, _name, iDAI)
                    _value = None
                    self.TRX.Trace(("    Balise2 <VAL/> vide"), TL.DETAIL)
            else:
                pDAI = pDAI.nextSibling

        return pDAI, _value, iDOI

    """
    The code of Parse_SDI(pDAI1, iDOI, n, TRX)is used to collect the
     value of DO/DA looking like this:
                </DOI>
                <DOI name="CosPhi">
                    <SDI name="phsA">
                        <SDI name="cVal">
                            <SDI name="mag">
                                <DAI name="f" sAddr="MX:0;0x070F2800;DB=0:P;MIN=0;MAX=0"/>
                            </SDI>
                        </SDI>
                        <SDI name="units">
                            <DAI name="SIUnit" valKind="RO">
    ==>                           <Val>cos(phi)</Val>           <=== 
                            </DAI>
                        </SDI>
                    </SDI>
    """

    ##
    # \b Parse_SDI
    # @param   pDAI     : the SCL pointer to a SDI
    # @param   iDOI     : an instance of DO, which may have SDI value to add
    # @param   DoName:
    # @return  sdi_name : the name of the instance
    #
    # \b Principle
    #
    # The instances of SDI is added to the DOI by dynamic creation of an attribute (setattr)
    # The code assume that there is a maximum of three levels of SDI.
    #
    def Parse_SDI(self, pDAI, iDOI, DoName):
        pDAI1 = pDAI
        BaseName = DoName + '.' + iDOI.DOname
        t_IX = [None, None, None, None]
        while pDAI1 is not None:
            if pDAI1.localName is None:
                pDAI1 = pDAI1.nextSibling
                continue
            iSDI1, sdi_name = self.Parse_SDI_Val(pDAI1, iDOI, BaseName, 0, t_IX, '')
            if pDAI1.firstChild is None:  # No value found by Parse_SDI_Val
                pDAI1 = pDAI1.nextSibling
                continue
            pDAI2 = pDAI1.firstChild.nextSibling  # Prochaine balise DAI ou à SDI cas 'origin'.

            if pDAI2.localName == "SDI":  # SDI imbriqué
                while pDAI2 is not None:
                    if pDAI2.localName == "SDI":  # SDI imbriqué
                        iSDI2, sdi_name = self.Parse_SDI_Val(pDAI2, iSDI1, BaseName, 1, t_IX, sdi_name)
                        if pDAI2.firstChild is None:
                            pDAI2 = pDAI2.nextSibling
                            continue
                        pDAI3 = pDAI2.firstChild.nextSibling  # Prochaine balise DAI ou à SDI cas 'origin'.

                        if pDAI3.localName == "SDI":  # SDI imbriqué
                            while pDAI3 is not None:
                                if pDAI3.localName == "SDI":  # SDI imbriqué
                                    iSDI3, sdi_name = self.Parse_SDI_Val(pDAI3, iSDI2, BaseName, 2, t_IX, sdi_name)
                                pDAI3 = pDAI3.nextSibling

                    pDAI2 = pDAI2.nextSibling

            pDAI1 = pDAI1.nextSibling
        return  # tDAI #.nextSibling,

    ##
    # \b Parse_SDI_Val
    #
    # @param   pDAI_v   : the SCL pointer to a SDI
    # @param   iDOI     : an instance of DO, which may have SDI value to add
    # @param   BaseName : used to build the name of the attribute DO.SDO.DA.BDA...
    # @param   n        : SDI1 or SDI2 ou SDI3  (for trace only)
    # @param   t_IX     : Table of value, if the DO is an array.
    # @param   sdi_name : Building the string DA_name.SDA_name.XX_name
    #
    # @return  iSDI: an instance od SDI object with value (if found)
    # @return  sdi_name: tha name of the instance.
    #
    # \b Principle
    # The instances of SDI is added to the DOI by dynamic creation of an attribute (setattr)

    def Parse_SDI_Val(self, pDAI_v, iDOI, BaseName, n, t_IX, sdi_name):
        _desc   = pDAI_v.getAttribute("desc")
        _name   = pDAI_v.getAttribute("name")
        _sdi_ix = pDAI_v.getAttribute("ix")
        _sAddr  = pDAI_v.getAttribute("sAddr")
        _sdi_name = sdi_name + '.' + _name  # </SDI>
        iSDI = IED.AccessPoint.Server.LN.DAI.SDI(_desc, _name, _sdi_ix, _sAddr)

        # Is it a table of SDI ?
        if len(_sdi_ix) > 0:
            t_IX[n] = _sdi_ix

        # Adding the attribute to iDOI dynamically.
        if _sdi_ix is not None and len(_sdi_ix) > 0:
            setattr(iDOI, _name + _sdi_ix, iSDI)
        else:
            setattr(iDOI, _name, iSDI)

        if pDAI_v.firstChild is None:
            self.TRX.Trace(("DAI without value:" + _name+ "sAddr:" + _sAddr),TL.DETAIL)
            return iSDI, sdi_name

        # Reading the Value
        pVAL = pDAI_v.firstChild.nextSibling
        pVAL, value, iSDI = self.Parse_DAI_VAL(pVAL, iSDI)
        if value is not None:
            found = False
            for i in range(0, 2):
                if t_IX[i] is not None:
                    self.TRX.Trace(
                        ("Value for SDI[idx]: " + str(n) + BaseName + sdi_name + '_' + str(t_IX[i]) + '\t:' + value),
                        TL.DETAIL)
                    found = True
                    break
            if not found:
                self.TRX.Trace(("Value for SDI: " + str(n) + BaseName + sdi_name + '\t:' + value), TL.DETAIL)
        return iSDI, sdi_name
##
# \b Test_LN: unitary test for parsing LN

class Test_LN:
    def main(directory, file, scl):
        TRX = Trace(TL.GENERAL)

        scl = dom.parse(FL.root+file)
        TRX.Trace(("scl.getElementsByTagName. "+ file),TL.GENERAL)
        tiLN=[]

        instLN = Parse_LN(TRX)         # Class instance creation
# Parse specifically LN0
        LN_ZERO = scl.getElementsByTagName("LN0")
        TRX.Trace(("ParseLN0................. "+ file),TL.GENERAL)
        for ptrLN in LN_ZERO:
            tDAI = []
            iLN = instLN.Parse_LN(ptrLN, "IED_name", "AP_Name", tDAI)
            tiLN.append(iLN)

# Parse classical LN
        pLN= scl.getElementsByTagName("LN")
        for ptrLN in pLN:
            tDAI = []
            iLN = instLN.Parse_LN(ptrLN, "IED_name", "AP_Name", tDAI)
            tiLN.append(iLN)

        TRX.Trace(("IEC_LN fin"),TL.GENERAL)
##
# \b MAIN call the unitary test 'Test_PTypefor PARSE DoType
if __name__ == '__main__':


    fileliste = FL.lstFull  # File list for System Level (SCL/SCD...)
    for file in fileliste:
        Test_LN.main(FL.root, file, None)

    fileliste = FL.lstIED  # File list for IED Level (ICD, CID, IID...)
    for file in fileliste:
        Test_LN.main(FL.root, file, None)

