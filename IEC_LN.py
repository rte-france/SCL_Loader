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
from IEC_Trace      import IEC_Console  as  TConsole
from IEC_Trace      import TraceLevel   as TL
from IEC_PrivateSupport import DynImport


class LN_LN0:
    def __init__(self, _localName, _lnPrefix, _lnType, _lnInst, _lnClass, _lnDesc):
# Partie générique commune à LN0 et LNODE (LN)
        self.localName  = _localName  # LN or LN0
        self.lnPrefix   = _lnPrefix
        self.lnType     = _lnType
        self.lnInst     = _lnInst
        self.lnClass    = _lnClass
        self.lnDesc     = _lnDesc
        self.tDataSet   =  []       # Array of DataSet associé à ce LN0
        self.tSVCtrl    =  []       # Array of SampleValueControl block à ce LN0
        self.tGSECtrl   =  []       # Array of GSEControl
        self.tInputs    =  []       # Array of inputs/Extrefs
        self.tLogCtrl   =  []       # Array of LogControl
        self.tRCB       =  []       # Array of RCB
###     self.DO_Name    = ...         # Dynamically added with 'setattr' to get actual DO_Name

# Définition de la class Report Control, avec des sous classes
# pour les parties TrgOps, OptField et rptEnabled
#
    class LogControl:
        def __init__(self, _name, _datSet, _logName, _logEna, __TrgOps):
            self.name = _name
            self.datSet = _datSet
            self.logName = _logName
            self.logEna = _logEna
            self.TrgOps = __TrgOps
    class ReportControl:
        def __init__(self, _rptID,_confRev,_buffered,_bufTime,_indexed,_intgPd,_name,_desc,_datSet):
            self.rptID   = _rptID
            self.confRev = _confRev
            self.buffered= _buffered
            self.bufTime = _bufTime
            self.indexed = _indexed
            self.intgPd  = _intgPd
            self.name    = _name
            self.desc    = _desc
            self.dataset = _datSet
            self.TrgOps  = None
        class OptField:
            def __init__(self,_seqNum,_timeStamp,_dataSet,_dataRef,_entryID,_configRef,_reasonCode):
                self.seqNum     = _seqNum
                self.timeStamp  = _timeStamp
                self.dataSet    = _dataSet
                self.dataRef    = _dataRef
                self.entryID    = _entryID
                self.configRef  = _configRef
                self.reasonCode = _reasonCode
        class RptEnable:
            def __init__(self, _max):
                self.max = _max
# The TrgOps Class is common RCB and LogControl
    class TrgOps:
        def __init__(self,_qchg, _dchg, _dupd, _period, _gi ):
            self.dchg  = _qchg
            self.qchg  = _dchg
            self.dupd  = _dupd
            self.period= _period
            self.gi    = _gi
    class Inputs:
        def __init__(self, _tRef):  #, _tFIP, _tBAP):
            self.tExtRef = _tRef

        class ExtRef:
            def __init__(self, _doName, _daName, _service, _iedName, _ldInst, _lnClass, _lnInst, _srcCBName,
                         _srcLNClass):
                self.doName = _doName
                self.daName = _daName
                self.serviceType = _service
                self.iedName = _iedName
                self.ldInst = _ldInst
                self.lnClass = _lnClass
                self.lnInst = _lnInst
                self.srcCBName = _srcCBName
                self.srcLNClass = _srcLNClass
        class rteFIP:
            def __init__(self,_defaultValue, _dataStreamKey):
                self.defaultValue  = _defaultValue
                self.dataStreamKey = _dataStreamKey
        class rteBAP:
            def __init__(self, _variant,_defaultValue, _dataStreamKey):
                self.variant       = _variant
                self.defaultValue  = _defaultValue
                self.dataStreamKey = _dataStreamKey

    class SampledValueControl:
        def __init__(self, _name, _smvID, _smpRate, _nofASDU, _confRev, _multicast, _smpMod, _datSet):
            self.name     = _name
            self.smvID    = _smvID
            self.smpRate  = _smpRate
            self.nofASDU  = _nofASDU
            self.confRev  = _confRev
            self.multicast=_multicast
            self.smpMod   = _smpMod
            self.datSet   = _datSet

    class GSEControl:
        def __init__(self,_name,_datSet,_type,_confRev,_appID,_fixedOffs,_securityEnable,_desc):
            self.name           =_name
            self.datSet         =_datSet
            self.type           =_type
            self.confRev        =_confRev
            self.appID          =_appID
            self.fixedOffs      =_fixedOffs
            self.securityEnable = _securityEnable
            self.desc           = _desc

    class DOI:
        def __init__(self, _name, _desc):
            self.name       = _name
            self.desc       = _desc
        class DAI:
            def __init__(self, _name, _value, _sAddr, _valKind):
                self.name = _name
                self.value = _value
                self.sAddr = _sAddr
                self.valKind = _valKind

            class SDI:  # Utilisé notamment pour les Contrôles complexes
                def __init__(self, _name, _sAddr, _ix):  # , _tSDI):
                    self.name = _name
                    self.ix = _ix
                    self.sAddr = _sAddr
            class RteDAI:  # Rte private data
                def __init__(self, _type, _desc):
                    self.type = _type
                    self.desc = _desc

        class IEC_90_2:             # Private defined by WG10 eTr, technical report for 90-2 communication
            def __init__(self,_externalScl,_iedName, _ldInst, _prefix,_lnClass,_lnInst,_doName):
                self.externalScl = _externalScl
                self.iedName     = _iedName
                self.ldInst      = _ldInst
                self.prefix      = _prefix
                self.lnClass     = _lnClass
                self.lnInst      = _lnInst
                self.doName      = _doName
        class IEC104:              # Private define by WG10 TR 90-2 IEC60870-104 SCADA communication
            def __init__(self,_casdu,_ioa,_ti,_usedBy,_inverted):
                self.casdu    = _casdu
                self.ioa      = _ioa
                self.ti       = _ti
                self.usedBy   = _usedBy
                self.inverted = _inverted
class DataSet:
    def __init__(self, _name, _desc):
        self.name  = _name
        self.desc  = _desc
        self.tFCDA = []
    class FCDA:
        def __init__(self,_ldInst,_prefix,_lnClass,_lnInst,_doName,_daName,_fc,_ix):
            self.ldInst  = _ldInst
            self.prefix  = _prefix
            self.lnClass = _lnClass
            self.lnInst  = _lnInst
            self.doName  = _doName
            self.daName  = _daName
            self.fc      = _fc
            self.ix      = _ix

class Parse_LN:
    def __init__(self, _TR):
        self.TRX      = _TR
        self.Dyn      = DynImport()

    def Parse_ExtRef(self, pLN):
        _tInputs = LN_LN0.Inputs([])

        pExtRef= pLN.firstChild.nextSibling
        while pExtRef:
            if pExtRef.localName is None:
                pExtRef = pExtRef.nextSibling
                continue
            if pExtRef.localName=='Private':
                type=  pExtRef.getAttribute("type")
                print("pExtRef.private:", type)
                self.Dyn.DynImport(type, pExtRef, LN_LN0.Inputs )

            if pExtRef.localName=='ExtRef':
                doName      = pExtRef.getAttribute("doName")
                daName      = pExtRef.getAttribute("daName")
                serviceType = pExtRef.getAttribute("serviceType")
                iedName     = pExtRef.getAttribute("iedName")
                ldInst      = pExtRef.getAttribute("ldInst")
                lnClass     = pExtRef.getAttribute("lnClass")
                lnInst      = pExtRef.getAttribute("lnInst")
                srcCBName   = pExtRef.getAttribute("srcCBName")
                srcLNClass  = pExtRef.getAttribute("srcLNClass")
                iExtRef = LN_LN0.Inputs.ExtRef(doName, daName, serviceType, iedName, ldInst, lnClass, lnInst, srcCBName, srcLNClass)
                _tInputs.tExtRef.append(iExtRef)
    
            pExtRef = pExtRef.nextSibling
    

        return _tInputs
    
    def ParseDAI_VAL(self, pDAI, iDOI):
        _value = None
        if pDAI.localName == "DAI":
            _name    = pDAI.getAttribute("name")
            _sAddr   = pDAI.getAttribute("sAddr")
            _valKind = pDAI.getAttribute("valKind")
            iDAI = LN_LN0.DOI.DAI(_name, _value, _sAddr, _valKind) # _value !
            setattr(iDOI, _name, iDAI)
            # Est-ce qu'une valeur est présente
            p1 = pDAI.firstChild
            if p1 is not None:
                p1 = p1.nextSibling
                if (p1.firstChild is not None):
                    if p1.localName == "Val":
                        _value = p1.firstChild.data
                        iDAI.value = _value
                        self.TRX.Trace(("    Balise1 <VAL/>: " +_value ), TL.DETAIL)
                        p1 = p1.firstChild.nextSibling
    
                    if p1 is not None and p1.localName == "Private":
                        pType = pDAI.firstChild.nextSibling
                        _type = pType.getAttribute("type")
                        self.Dyn.DynImport(_type, pType, iDOI)

                    setattr(iDOI, _name, iDAI)
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
    
    def ParseSDI_Val(self, pDAI_v,iDOI,BaseName, n, t_IX, sdi_name):
        name  = pDAI_v.getAttribute("name")
        sAddr = pDAI_v.getAttribute("sAddr")
        sdi_name = sdi_name + '.' + name  # </SDI>
        sdi_ix   = pDAI_v.getAttribute("ix")
        iSDI = LN_LN0.DOI.DAI.SDI(name, sAddr, sdi_ix)  # None pointeur vers tableau des SDI DAI
        if len(sdi_ix)>0:
            t_IX[n]= sdi_ix
    
        if sdi_ix is not None and len(sdi_ix)>0:
            setattr(iDOI, name+sdi_ix, iSDI)
        else:
            setattr(iDOI, name, iSDI)
        if pDAI_v.firstChild is None:
    #        print("DAI without value:" + name + "sAddr:" + sAddr)
            return iSDI, sdi_name
    
        pVAL = pDAI_v.firstChild.nextSibling
        pVAL , value, iSDI = self.ParseDAI_VAL(pVAL, iSDI)
        if value is not None:
            found = False
            for i in range (0,2):
                if t_IX[i] is not None:
                    self.TRX.Trace(("Valeur pour SDI[idx]: " + str(n) + BaseName  + sdi_name + '_' + str(t_IX[i]) + '\t:' + value ),TL.DETAIL)
                    found = True
                    break
            if not found:
                self.TRX.Trace(("Valeur pour SDI: " + str(n) + BaseName  + sdi_name + '\t:' + value ),TL.DETAIL)
        return iSDI, sdi_name
    def Parse_SDI(self, pDAI, iDOI, DoName):
        pDAI1 = pDAI
        BaseName = DoName + '.' + iDOI.name
        t_IX = [None,None,None,None]
        while pDAI1 is not None:
            if pDAI1.localName is None:
                pDAI1 = pDAI1.nextSibling
                continue
            iSDI1, sdi_name = self.ParseSDI_Val(pDAI1, iDOI, BaseName, 0, t_IX, '')
            if pDAI1.firstChild is None:        # No value found by ParseSDI_Val
                pDAI1 = pDAI1.nextSibling
                continue
            pDAI2 = pDAI1.firstChild.nextSibling  # Prochaine balise DAI ou à SDI cas 'origin'.
    
            if pDAI2.localName == "SDI":  # SDI imbriqué
                while pDAI2 is not None:
                    if pDAI2.localName == "SDI":  # SDI imbriqué
                        iSDI2, sdi_name = self.ParseSDI_Val(pDAI2, iSDI1, BaseName, 1, t_IX, sdi_name)
                        pDAI3 = pDAI2.firstChild.nextSibling  # Prochaine balise DAI ou à SDI cas 'origin'.
    
                        if pDAI3.localName == "SDI":  # SDI imbriqué
                            while pDAI3 is not None:
                                if pDAI3.localName == "SDI":  # SDI imbriqué
                                    iSDI3, sdi_name = self.ParseSDI_Val(pDAI3, iSDI2, BaseName, 2, t_IX, sdi_name)
                                pDAI3 = pDAI3.nextSibling
    
                    pDAI2 = pDAI2.nextSibling
    
            pDAI1 = pDAI1.nextSibling
        return #tDAI #.nextSibling,
    def Parse_DOI(self, iLN, pDOI, DoName):               # Instance of LN  & DOI is scl pointto DOI tag
        _name = pDOI.getAttribute("name")        # Nom du DOI
        _desc = pDOI.getAttribute("desc")
        self.TRX.Trace(("DOI: name:" + _name + " desc:" + _desc), TL.DETAIL)
        iDOI = LN_LN0.DOI(_name, _desc) #, None, None, None)  # None for RTE private Type
        setattr( iLN ,iDOI.name,iDOI)
        pDAI = pDOI.firstChild  # Pointeur DAI ou SDI
    
        while pDAI:  # USE CASE:
            if pDAI.localName is None:                  # <DOI name="LEDRs" desc="RstOper">
                pDAI = pDAI.nextSibling                         # <SDI name="Oper">
                continue                                            # <SDI name="origin">
            if pDAI.localName == "Private":                             # <DAI name="orCat" sAddr="96.1.3.10.4" />
                type=pDAI.getAttribute("type")
# WG10 PRIVATE
                if type == "eTR-IEC61850-90-2":
                    print("Private tag: eTr-IEC61850-90-2")
                    pI90_2 = pDAI.firstChild.nextSibling
                    if (pI90_2.nodeName == "eTr-IEC61850-90-2:ProxyOf"):
                        _externalScl  = pI90_2.getAttribute("externalScl")
                        _iedName      = pI90_2.getAttribute("iedName")
                        _ldInst       = pI90_2.getAttribute("ldInst")
                        _prefix       = pI90_2.getAttribute("prefix")
                        _lnClass      = pI90_2.getAttribute("lnClass")
                        _lnInst       = pI90_2.getAttribute("lnInst")
                        _doName       = pI90_2.getAttribute("doName")
                        iDOI.IEC_90_2 = LN_LN0.DOI.IEC_90_2(_externalScl,_iedName,_ldInst, _prefix, _lnClass, _lnInst, _doName )
# WG10 PRIVATE
                elif type == "IEC_60870_5_104":
                    print("Private tag: IEC_60870_5_104")
                    p104 = pDAI.firstChild.nextSibling

                    if (p104.localName == "Address") and (p104.nodeName == "'IEC_60870_5_104:Address'"):
                        _casdu      = p104.getAttribute("casdu")
                        _ioa        = p104.getAttribute("ioa")
                        _ti         = p104.getAttribute("ti")
                        _usedBy     = p104.getAttribute("usedBy")
                        _inverted   = p104.getAttribute("inverted")
                        iDOI.IEC104 = LN_LN0.DOI.IEC104(_casdu,_ioa, _ti, _usedBy, _inverted )
                else:
                    self.Dyn.DynImport(type, pDAI, LN_LN0.DOI.DAI)

                pDAI = pDAI.nextSibling                             # </SDI>
                continue                                            # <DAI name="ctlVal" sAddr="96.1.3.10.3" />
            if pDAI.localName == "DAI":                             # <DAI name="ctlNum" sAddr="96.1.3.10.6" />
                pX, value, iDAI = self.ParseDAI_VAL(pDAI, iDOI)     # <DAI name="T" sAddr="96.1.3.10.7" />
    #            tDAI.append(iDOI)
                pDAI = pDAI.nextSibling
                continue                                               #     <DAI name="Test" sAddr="96.1.3.10.8" />
            if pDAI.localName == "SDI":                             # <DAI name="Check" sAddr="96.1.3.10.9" />
                self.Parse_SDI(pDAI, iDOI, DoName)
                break
            pDAI = pDAI.nextSibling
    
        return iDOI,iLN
    #<FCDA  ldInst = "System" lnClass = "MMXU" fc = "MX" prefix = "" doName = "A.phsB" daName = "cVal.mag.i" lnInst = "1" / >
    def Parse_FCDA(self, pLN, DS):
    
        FCDAi = pLN.firstChild
        while FCDAi:
            if FCDAi.localName is None:
                FCDAi = FCDAi.nextSibling
                continue
            _ldInst  = FCDAi.getAttribute("ldInst")
            _prefix  = FCDAi.getAttribute("prefix")
            _lnInst  = FCDAi.getAttribute("lnInst")
            _lnClass = FCDAi.getAttribute("lnClass")
            _doName  = FCDAi.getAttribute("doName")
            _daName  = FCDAi.getAttribute("daName")
            _cf      = FCDAi.getAttribute("fc")
            _ix      = FCDAi.getAttribute("ix")
            iFCDA    = DataSet.FCDA(_ldInst, _prefix, _lnInst, _lnClass, _doName, _daName, _cf, _ix)
            DS.tFCDA.append(iFCDA)
            FCDAi = FCDAi.nextSibling
    
        return DS
    def Parse_ReportControl(self, pLN, iLN):
        _RptID    = pLN.getAttribute("rptID")
        _confRev  = pLN.getAttribute("confRev")
        _Buffered = pLN.getAttribute("buffered")
        _BufTime  = pLN.getAttribute("bufTime")
        _Indexed  = pLN.getAttribute("indexed")
        _intgPd   = pLN.getAttribute("intgPD")
        _datSet   = pLN.getAttribute("datSet")
        _name     = pLN.getAttribute("name")
        _desc     = pLN.getAttribute("desc")
    #    _Opt      = LN.getAttribute("optFields")
        iRCB = LN_LN0.ReportControl(_RptID, _confRev, _Buffered, _BufTime, _Indexed, _intgPd, \
                             _datSet, _name, _desc)
        self.TRX.Trace(("ReportControl: " + _RptID + " name:" + _name + " datSet" + _datSet),TL.DETAIL)
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
                self.TRX.Trace(("ReportControl: TrgOps"),TL.DETAIL)
                _qchg   = rptCtrl.getAttribute("qchg")
                _dchg   = rptCtrl.getAttribute("dchg")
                _dupd   = rptCtrl.getAttribute("dupd")
                _period = rptCtrl.getAttribute("period")
                _gi = rptCtrl.getAttribute("gi")
                iRCB.TrgOps = LN_LN0.TrgOps(_qchg, _dchg, _dupd, _period, _gi)
    
                rptCtrl = rptCtrl.nextSibling
                continue
            if rptCtrl.localName == "OptFields":
                self.TRX.Trace(("ReportControl: OptFields"),TL.DETAIL)
                _seqNum     = rptCtrl.getAttribute("seqNum")
                _timeStamp  = rptCtrl.getAttribute("timeStamp")
                _dataSet    = rptCtrl.getAttribute("dataSet")
                _dataRef    = rptCtrl.getAttribute("dataSef")
                _entryID    = rptCtrl.getAttribute("entryID")
                _configRef  = rptCtrl.getAttribute("configRef")
                _reasonCode = rptCtrl.getAttribute("reasonCode")
    
                iRCB.OptField=LN_LN0.ReportControl.OptField(_seqNum, _timeStamp, _dataSet, _dataRef,
                                 _entryID, _configRef, _reasonCode)
                rptCtrl = rptCtrl.nextSibling
                continue
            if rptCtrl.localName == "RptEnabled":
                self.TRX.Trace(("ReportControl: RptEnabled"),TL.DETAIL)
                _max = rptCtrl.getAttribute("max")
                iRCB.RptEnable=iRCB.RptEnable(_max)
                rptCtrl = rptCtrl.nextSibling
                continue
        iLN.tRCB.append(iRCB)
        return iLN
    def ParseLogControl(self, pLN, tiLCB):
    
        _name    = pLN.getAttribute("name")
        _datSet  = pLN.getAttribute("datSet")
        _logName = pLN.getAttribute("logName")
        _logName = pLN.getAttribute("logEna")
        iLogControl = LN_LN0.LogControl(_name, _datSet, _logName, _logName, None)  # None pour la class TrgOps.
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
    
                iTrgOps = LN_LN0.TrgOps(_qchg, _dchg, _dupd, _period, _gi)
                self.TRX.Trace(("        TrgOps qchg" + _qchg + " dchg:" + _dchg + " dupd:" + _dupd + \
                           " period+" + _period + "_gi" + _gi), TL.DETAIL)
                iLogControl.TrgOps = iTrgOps
                logCtrl = logCtrl.nextSibling
                continue
        tiLCB.append(iLogControl)
        return tiLCB

    def Parse_LN_LN0(self, pLN, IEDname, AP_Name, tDAI):
    #
    # LN contains DataSet, ReportControl, GooseControl and DOI/SDI.../SDI/DAI sections (up to 3 levels of SDI
    #
        _lnPrefix= pLN.getAttribute("prefix")
        _lnClass = pLN.getAttribute("lnClass")
        _inst    = pLN.getAttribute("inst")
        _lnType  = pLN.getAttribute("lnType")
        _desc    = pLN.getAttribute("desc")
        if pLN.localName=="LN0":
            iLN = LN_LN0("LN0:", _lnPrefix, _lnType, _inst, _lnClass, _desc )
        else:
            iLN = LN_LN0("LN:" , _lnPrefix, _lnType, _inst, _lnClass, _desc)
    
        if pLN.firstChild is not None:          # LN est utilisé pour le parcour de l'arbre XML
            pLN = pLN.firstChild.nextSibling    #
        else:
    #       LN0 is empty, usually the case for ICD IID file
            return iLN
    
        tiRCB   = []  # Tableau des instances des RCB du LN0
        tiSVC   = []  # Tableau des instances des SVC du LN0
        tiGCB   = []  # Tableau des instances des GCB du LN0
        tiLCB   = []  # Tableau des instances des LCB du LN0
        tExtRef = []  # Tableau des ExtRef (Inputs)
        tDS     = []  # Tableau des instances des DatatSet du LN0 (l'objet DA contient la liste des FCDA)
    
        while pLN:
            if pLN.localName is None:
                pLN = pLN.nextSibling
                continue
            if pLN.localName == "Private":
                type = pLN.getAttribute("type")
                self.Dyn.DynImport(type, pLN, iLN)
                pLN= pLN.nextSibling
                continue
            if pLN.localName == "Inputs":               # < Inputs >
                  #  < ExtRef doName = "SPCSO3" daName = "q" serviceType = "GOOSE"...
                self.TRX.Trace(("      *** Inputs"), TL.DETAIL)
    
                iLN.tInputs = self.Parse_ExtRef(pLN)
    
                pLN = pLN.nextSibling
                continue
            if pLN.localName == "DOI":              ### DOI et DAI à TRAITER DANS LE DATA MODEL.
                self.TRX.Trace(("      *** DOI"), TL.DETAIL)
                LN_id = iLN.lnPrefix + iLN.lnClass + iLN.lnInst
                DoName = IEDname + AP_Name + '/' + LN_id                   # Use for collecting DAI
                iDOI, iLN = self.Parse_DOI(iLN, pLN, DoName)
    
                pLN = pLN.nextSibling
                continue
            # TODO ???gérer les balises Log, et SettingControl? .
            if pLN.localName == "Log":              # Non utilisé dans R#Space
                self.TRX.Trace(("      Log: NON TRAITE"), TL.ERROR)
                pLN= pLN.nextSibling
                continue
            if pLN.localName == "LogControl":       # Non utilisé dans R#Space
                self.TRX.Trace(("      LogControl"), TL.DETAIL)
                tiLCB = self.ParseLogControl(pLN, tiLCB)
                pLN= pLN.nextSibling
                continue
            if pLN.localName == "SettingControl":   # Non utilisé dans R#Space
                self.TRX.Trace(("      SettingControl: NON TRAITE"), TL.ERROR)
                # TODO gérer les LOG.
                pLN= pLN.nextSibling
                continue
            if pLN.localName == "GSEControl":
                self.TRX.Trace(("      GSEControl"), TL.DETAIL)
                name            = pLN.getAttribute("name")
                datSet          = pLN.getAttribute("datSet")
                type            = pLN.getAttribute("type")
                confRev         = pLN.getAttribute("confRev")
                appID           = pLN.getAttribute("appID")
                fixedOffs       = pLN.getAttribute("fixedOffs")
                securityEnable  = pLN.getAttribute("securityEnable")
                desc            = pLN.getAttribute("desc")
                GOOSE = LN_LN0.GSEControl(name, datSet,type,confRev,appID,fixedOffs,securityEnable,desc)
    # TODO LISTE DES IEDs à accrocjer GSECONTROL
    
                tiGCB.append(GOOSE)
                self.TRX.Trace(("     GSEControl, name: " + name + " datSet:" + datSet),TL.ERROR)
                pLN= pLN.nextSibling
                continue
            if pLN.localName == "SampledValueControl":
                self.TRX.Trace(("      SampledValueControl"), TL.DETAIL)
                smvID       =   pLN.getAttribute("smvID")
                name        =   pLN.getAttribute("name")
                smpRate     =   pLN.getAttribute("smpRate")
                nofASDU     =   pLN.getAttribute("nofASDU")
                confRev     =   pLN.getAttribute("confRev")
                multicast   =   pLN.getAttribute("multicast")
                smpMod      =   pLN.getAttribute("smpMod")
                datSet      =   pLN.getAttribute("datSet")
    
                SVC = LN_LN0.SampledValueControl(name, smvID, smpRate, nofASDU, confRev, multicast, smpMod, datSet)
                tiSVC.append(SVC)
                self.TRX.Trace(("     SampledValueControl, name:" + name + " smvID:" + smvID + " datSet:" + datSet),TL.DETAIL)
                pLN= pLN.nextSibling
                continue
            # Extraction des data Set:
            #   <DataSet name = "DS_TAXD" desc = "Data Set..." >
            #       <FCDA  ldInst = "LD_all" prefix = "" lnInst = "1" lnClass = "TAXD" doName = "EEName"   fc = "DC" />
            #       <FCDA  ldInst = "LD_all" prefix = "" lnInst = "1" lnClass = "TAXD" doName = "EEHealth" fc = "ST" />
            #       <FCDA  ldInst = "LD_all" prefix = "" lnInst = "1" lnClass = "TAXD" doName = "AxDspSv"  fc = "MX" / >
            #       <FCDA  ldInst = "LD_all" prefix = "" lnInst = "1" lnClass = "TAXD" doName = "SmpRte"   fc = "SP" />
            #   </DataSet >
            if pLN.localName == "DataSet":
                _name = pLN.getAttribute("name")
                _desc = pLN.getAttribute("desc")
                self.TRX.Trace(("     DataSet, dsName:" + _name + " desc:" + _desc),TL.DETAIL)
                DS = DataSet(_name,_desc)  # "" Tableau des  FCDA
                DS = self.Parse_FCDA(pLN,DS)
                tDS.append(DS)
                pLN= pLN.nextSibling
                continue
    
            if pLN.localName == "ReportControl":
                self.TRX.Trace(("      ReportControl"), TL.DETAIL)
                iLN = self.Parse_ReportControl(pLN, iLN)
                pLN = pLN.nextSibling
                continue
            continue
        iLN.tSVCtrl  = tiSVC
        iLN.tDataSet = tDS
        iLN.tGSECtrl = tiGCB
        iLN.tRptCtrl = tiRCB
        iLN.tLogCtrl = tiLCB
        return iLN

class Test_LN:
    def main(directory, file, scl):
        TRX = TConsole(TL.GENERAL)

        scl = dom.parse('SCL_files/'+file)
        TRX.Trace(("scl.getElementsByTagName. "+ file),TL.GENERAL)
        tiLN=[]

        instLN = Parse_LN(TRX)         # Class instance creation
# Parse specifically LN0
        LN_ZERO = scl.getElementsByTagName("LN0")
        TRX.Trace(("ParseLN0................. "+ file),TL.GENERAL)
        for ptrLN in LN_ZERO:
            tDAI = []
            iLN = instLN.Parse_LN_LN0(ptrLN, "IED_name", "AP_Name", tDAI)
            tiLN.append(iLN)

# Parse classical LN
        pLN= scl.getElementsByTagName("LN")
        for ptrLN in pLN:
            tDAI = []
            iLN = instLN.Parse_LN_LN0(ptrLN, "IED_name", "AP_Name", tDAI)
            tiLN.append(iLN)

        TRX.Trace(("IEC_LN fin"),TL.GENERAL)

if __name__ == '__main__':


    Test_LN.main('SCL_files/', 'IOP_2019_HV_v6_ed2.3.SCL', None)

#    fileliste = FL.lstFull  # File list for System Level (SCL/SCD...)
#    for file in fileliste:
#        Test_LN.main('SCL_files/', file, None)

#    fileliste = FL.lstIED  # File list for IED Level (ICD, CID, IID...)
#    for file in fileliste:
#        Test_LN.main('SCL_files/', file, None)

