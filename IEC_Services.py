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
from IEC_FileListe import FileListe as FL
from IEC_Trace import IEC_Console   as TConsole
from IEC_Trace import TraceLevel as TL

# The names used are matching the names of the IEC61850 classes, as well as the attributes.
#
# General convention:
#   pName  : means this a pointer to 'Name', this is usually used when navigating in XML
#   tObject: means this a table of 'class'. Ex: tIED, tServer.
#   iObject: means this an instance of a 'class'

class ServiceWithOptionalMax:
    def __init__(self, _Max):
        self.Max = _Max
    def getMax(self):
        return(self.Max)
class SettingGroups:
    def __init__(self, _Max):
        self.Max = _Max
        self.TR.Trace("**********SettingGroups-non implémenté",TL.DETAIL)
    def getMax(self):
        return(self.Max)
class MinOccurs:
    def __init__(self, _Min):
        self.Min = _Min
        self.TR.Trace("*********SettingGroups-non implémenté",TL.DETAIL)
    def getMin(self):
        return(self.Min)
class ServiceForConfDataSet:
    def __init__(self, _max, _maxAttribute, _modify):
        self.max          = _max
        self.maxAttribute = _maxAttribute
        self.modify       = _modify
class ServiceWithMaxAndMaxAttributes:
    def __init__(self, _Min, _Max):
        self.Min = _Min
        self.Max = _Max
    def getMin(self):
        return(self.Min)
    def getMax(self):
        return(self.Max)
class ServiceConfReportControl:
    def __init__(self, _xx):
        xx = _xx
class ServiceWithMaxNonZero:
    def __init__(self , _Max):
        self.Max = _Max
    def getMax(self):
        return(self.Max)
class ReportSettings:               #TODO
    def __init__(self, _xx):
        xx = _xx

class LogSettings:
    def __init__(self, _logEna, _trgOps, _intgPd):
        self.logEna = _logEna
        self.trgOps = _trgOps
        self.intgPd = _intgPd
    def getlogEna(self):
        return(self.logEna)
    def gettrgOps(self):
        return(self.trgOps)
    def getintgPd(self):
        return(self.intgPd)
class GSESettings:                  #TODO
    def __init__(self, _xx):
        xx = _xx
class SMVSettings:                  #TODO
    def __init__(self, _xx):
        xx = _xx

class GOOSEcapabilities:        # Max, fixedOffs, goose, rGOOSE
    def __init__(self, _Max, _fixedOffs, _goose, _rGOOSE):
        self.Max         = _Max
        self.fixedOffs   = _fixedOffs
        self.goose       = _goose
        self.rGOOSE      = _rGOOSE
    def getMax(self):
        return(self.Max)
    def getfixedOffs(self):
        return(self.fixedOffs)
    def getgoose(self):
        return(self.goose)
    def getrGOOSE(self):
        return(self.rGOOSE)

class ServiceWithMax:
    def __init__(self, _max):
        Max = _max
    def getMax(self):
         return(self.Max)
class SMVsc:            # ServiceWithMax + delivery + deliveryCfonf + sv + RSV
    def __init__(self, _max, _delivery, _deliveryConf, _sv, _rSV):
        self.max            = _max
        self.delivery       = _delivery        # Default value "multicast"
        self.deliveryConf   = _deliveryConf    # Default value "false"
        self.sv             = _sv              # Default value "false"
        self.rSV            = _rSV             # Default value "false"
    def getMax(self):
        return(self.max)
    def getDelivery(self):
        return(self.delivery)
    def getDeliveryConf(self):
        return(self.deliveryConf)
    def getsv(self):
        return(self.sv)
    def getrSV(self):
        return(self.rSV)
class FileHandling:                 #TODO
    def __init__(self, _xx):
        xx = _xx
class ConfLNs:
    def __init__(self, fixPrefix, fixLnInst):
        self.fixPrefix = fixPrefix
        self.fixLnInst = fixLnInst
    def getfixPrefix(self):
        return (self.fixPrefix)
    def getfixLnInst(self):
        return (self.fixLnInst)
class ClientServices:
    def __init__(self,  _goose, _gsse, _bufReport, _readLog , _sv, _supportsLdName, \
                        _maxAttributes, _maxReports, _maxGOOSE, _maxSMV, _rGOOSE, _rSV,_noIctBinding):
        goose = gsse = bufReport = readLog = sv = supportsLdName = 'no'
        maxAttributes = maxReports = maxGOOSE = maxSMV = 0
        _rGOOSE, _rSV, _noIctBinding = 'no'
        if _goose is not None:
            goose = _goose
        if _gsse is not None:
            gsse = _gsse
        if _bufReport is not None:
            bufReport = _bufReport
        if _readLog is not None:
            readLog = _readLog
        if _sv is not None:
            sv = _sv
        if _supportsLdName is not None:
            supportsLdName = _supportsLdName
        if _maxAttributes is not None:
            maxAttributes = _maxAttributes
            if _maxReports is not None:
                maxReports = _maxReports
            if _maxGOOSE is not None:
                maxGOOSE = _maxGOOSE
            if _maxSMV is not None:
                maxSMV = _maxSMV
        if _rGOOSE  is not None:
            rGOOSE = _rGOOSE
        if _rSV  is not None:
            rSV = _rSV
        if _noIctBinding  is not None:
            noIctBinding = _noIctBinding
class DynDataset:
    def __init__(self, _max):
        max = _max
    def getMax (self):
        return self.max
class SupSubscription:              # TODO
    def __init__(self, _xx):
        xx = _xx
class RedProt:                      #TODO
    def __init__(self, _xx):
        xx = _xx
class TimeSyncProt:                 #TODO
    def __init__(self, _xx):
        xx = _xx
class CommProt:                     #TODO
    def __init__(self, _xx):
        xx = _xx
class SettingGroups:                #TODO
    def __init__(self , _SGEdit):
        SGEEdit = _SGEdit
class ReportSetting:
    def __init__(self, _bufTime,_cbName,_rptID,_datSet,_intgPd,_optFields):
        bufTime = _bufTime
        cbName  = _cbName
        rptID   = _rptID
        datSet  = _datSet
        intgPd  = _intgPd
        optFieds= _optFields
class ValueHandling:
    def __init__(self, _setToRO):
        setToRO=_setToRO
    def getValue(self):
        return (self.setToRO)
class IEC_Services:
    SettingGroups           = SettingGroups
    GetDirectory            = 'no'
    GetDataObjectDefinition = 'no'
    DynAssociation          = ServiceWithOptionalMax(12345)
    DataObjectDirectory     = 'no'
    GetDataSetValue         = 'no'
    SetDataSetValue         = 'no'
    DataSetDirectory        = 'no'
    ConfDataSet             = ServiceForConfDataSet
    DynDataSet              = ServiceWithMaxAndMaxAttributes
    ReadWrite               = 'no'
    TimerActivatedControl   = 'no'
    ConfReportControl       = None # ServiceConfReportControl
    GetCBValues             = 'no'
    ConfLogControl          = ServiceWithMaxNonZero(0)
    ReportSettings          = ReportSettings
    LogSettings             = LogSettings
    GSESettings             = GSESettings
    SMVSettings             = SMVSettings
    GSEDir                  = 'no'
    GOOSE                   = GOOSEcapabilities
    GSSE                    = ServiceWithMax
    SMVsc                   = SMVsc            # ServiceWithMax + delivery + deliveryCfonf + sv + RSV
    FileHandling            = FileHandling
    ConfLNs                 = ConfLNs
    ClientServices          = ClientServices
    ConfLdName              = 'no'
    SupSubscription         = SupSubscription
    ConfSigRef              = ServiceWithMaxNonZero(0)
    ValueHandling           = ValueHandling
    RedProt                 = RedProt
    TimeSyncProt            = TimeSyncProt
    CommProt                = CommProt
    ConfSigRef              = ServiceWithMax

class Parse_Services:
    def __init__(self,_IED_name, TRX):
        self.IED_name   = _IED_name
        self.TR         = TRX
        self.tServices  = []

    def Services(self, Services):
        SupportedServices=IEC_Services()  # self.Services

        NbServices = 0

        if Services is None:                # Cas d'une section services vide (Clock)
            return
        if Services.firstChild is None:     #  Cas d'une section services vide (Clock)
            return

        Services = Services.firstChild.nextSibling
        while Services.nextSibling:
            if NbServices > 50:
                self.TR.Trace(("ERROR:  Service non CONNU", Services.localName),TL.GENERAL)
                exit(-1)
                break
            if Services.localName is None:
                Services = Services.nextSibling
                continue
# Traitement des service en yes/no.
            if Services.localName == "GetDirectory":
                NbServices = NbServices + 1
                SupportedServices.GetDirectory = "yes"
                self.TR.Trace(("Services-GetDirectory: yes"), TL.DETAIL)
                Services = Services.nextSibling
                continue
            if Services.localName == "GetDataObjectDefinition":
                NbServices = NbServices + 1
                SupportedServices.GetDataObjectDefinition = 'yes'
                self.TR.Trace(("Services-GetDataObjectDefinition: yes"), TL.DETAIL)
                Services = Services.nextSibling
                continue
            if Services.localName == "DataObjectDirectory":
                NbServices = NbServices + 1
                SupportedServices.DataObjectDirectory = 'yes'
                self.TR.Trace(("Services-DataObjectDirectory: yes"), TL.DETAIL)
                Services = Services.nextSibling
                continue
            if Services.localName == "GetDataSetValue":
                NbServices = NbServices + 1
                SupportedServices.GetDataSetValue = "yes"
                self.TR.Trace(("Services-GetDataSetValue: yes"), TL.DETAIL)
                Services = Services.nextSibling
                continue
            if Services.localName == "SetDataSetValue":
                NbServices = NbServices + 1
                SupportedServices.SetDataSetValue = "yes"
                self.TR.Trace(("Services-SetDataSetValue: yes"), TL.DETAIL)
                Services = Services.nextSibling
                continue
            if Services.localName == "DataSetDirectory":
                NbServices = NbServices + 1
                SupportedServices.DataSetDirectory = "yes"
                self.TR.Trace(("Services-DataSetDirectory: yes"), TL.DETAIL)
                Services = Services.nextSibling
                continue
            if Services.localName == "ReadWrite":
                NbServices = NbServices + 1
                SupportedServices.ReadWrite = "yes"
                self.TR.Trace(("Services-ReadWrite: yes"), TL.DETAIL)
                Services = Services.nextSibling
                continue
            if Services.localName == "TimerActivatedControl":
                NbServices = NbServices + 1
                SupportedServices.TimerActivatedControl = "yes"
                self.TR.Trace(("Services-TimerActivatedControl: yes"), TL.DETAIL)
                Services = Services.nextSibling
                continue
            if Services.localName == "DynAssociation":              ###OK
                NbServices = NbServices + 1
                NbDyn = Services.getAttribute("max")
                if NbDyn is None or NbDyn == '':
                    NbDyn = 0
                SupportedServices.DynAssociation.Max = NbDyn
                if(NbDyn!=0):
                    self.TR.Trace(("Services-DynAssociation: NbDyn" + str(NbDyn)), TL.DETAIL)

                Services = Services.nextSibling
                continue
            if Services.localName == "ClientServices":
                NbServices = NbServices + 1
                gsse          = Services.getAttribute("gsse")
                goose         = Services.getAttribute("goose")
                bufReport     = Services.getAttribute("bufReport")
                readLog       = Services.getAttribute("readLog")
                sv            = Services.getAttribute("sv")
                supportsLdName= Services.getAttribute("supportsLdName")

                Nb1           = Services.getAttribute("Nb1")
                unbufReport   = Services.getAttribute("unbufReport")
                rGOOSE        = Services.getAttribute("rGOOSE")
                rSV           = Services.getAttribute("rSV")

                maxAttributes = Services.getAttribute("maxAttributes")
                maxReports    = Services.getAttribute("maxReports")
                maxGOOSE      = Services.getAttribute("maxGOOSE")
                maxSMV        = Services.getAttribute("maxSMV")

                self.TR.Trace(("Services-ClientServices: gsse:"+            gsse+         \
                                                  " goose:"+           goose+        \
                                                  " bufReport:"+       bufReport+    \
                                                  " readLog:"+         readLog+      \
                                                  " sv:"+              sv+           \
                                                  " supportsLdName:"+  supportsLdName),TL.DETAIL)

                self.TR.Trace(("Services-ClientServices: Nb1:"+              Nb1+          \
                                                  " unbufReport:"+     unbufReport+  \
                                                  " rGOOSE:"+          rGOOSE+       \
                                                  " rSV:"+             rSV),TL.DETAIL)

                self.TR.Trace(("Services-ClientServices: maxAttributes"+     maxAttributes+\
                                                  " maxReports"+        maxReports+   \
                                                  " maxGOOSE"+          maxGOOSE+     \
                                                  " maxSMV"+            maxSMV),TL.DETAIL)

                noIctBinding = Services.getAttribute("noIctBinding")

                # Client <TimeSyncProt sntp="false" c37_238="true" other="true" />
                if Services.firstChild is not None:
                    Sync = Services.firstChild.nextSibling
                    if Sync.localName == "TimeSyncProt":
                        sntp = Sync.getAttribute("sntp")
                        ptp = Sync.getAttribute("c37_238")  # ==> PTP IEE1588
                        other = Sync.getAttribute("other")
                        self.TR.Trace(("                TimeSyncProt sntp:" +sntp +" ptp:" + ptp +" other:" + other),TL.DETAIL)
                        Services = Services.nextSibling
                    continue
                else:
                    SupportedServices.ClientServices=(goose,   gsse, bufReport,  readLog,  sv,  supportsLdName, \
                                   maxAttributes,  maxReports,  maxGOOSE, maxSMV, rGOOSE, rSV, noIctBinding)
                    Services = Services.nextSibling
                    continue
                Services = Services.nextSibling
            if Services.localName == "CommProt":                    #### OK
                NbServices = NbServices + 1
                ipv6 = Services.getAttribute("ipv6")
                self.TR.Trace(("Services-CommProt: " + "ipv6:" + ipv6),TL.DETAIL)
                Services = Services.nextSibling
                continue
            if Services.localName == "ConfDataSet":                 # OK ===============
                NbServices = NbServices + 1
                Max          = Services.getAttribute("max")
                MaxAttribute = Services.getAttribute("maxAttributes")
                Modify       = Services.getAttribute("modify")
                SupportedServices.ConfDataSet=ServiceForConfDataSet(Max,MaxAttribute,Modify)
                self.TR.Trace(("Services-ConfDataSet max: "+Max+" maxAttributes:"+ MaxAttribute + " modify: "+Modify),TL.DETAIL)
                Services = Services.nextSibling
                continue
            if Services.localName == "ConfLogControl":
                NbServices = NbServices + 1
                Log_max = Services.getAttribute("max")
                self.TR.Trace(("Services-ConfLogControl: Log_max: " + Log_max),TL.DETAIL)

                AA= ServiceWithMaxNonZero(Log_max)
                SupportedServices.ConfLogControl = AA
#                self.TR.Trace(("ConfLogControl",SupportedServices.ConfLogControl.getMax()),TL.DETAIL)
                Services = Services.nextSibling
                continue
            if Services.localName == "ConfLNs":                 # OK ##################
                NbServices = NbServices + 1
                fixLnInst = Services.getAttribute("fixLnInst")
                fixPrefix = Services.getAttribute("fixPrefix")
                SupportedServices.ConfLNs=ConfLNs(fixLnInst,fixLnInst)
                self.TR.Trace(("Services-ConfLNs: fixPrefix: "+ fixLnInst+ \
                                           " fixLnInst: "+ fixPrefix),TL.DETAIL)

                Services = Services.nextSibling
                continue
            if Services.localName == "ConfLdName":                      #### OK
                NbServices = NbServices + 1
                self.TR.Trace(("Services-ConfLdName: yes"),TL.DETAIL)
                Services = Services.nextSibling
                continue
            if Services.localName == "GSEDir":                       #### OK
                NbServices = NbServices + 1
                self.TR.Trace(("Services-GSEDir: yes"),TL.DETAIL)
                Services = Services.nextSibling
                continue

            if Services.localName == "ConfReportControl":               # OK #############
                NbServices = NbServices + 1
                Nb1 = Services.getAttribute("max")
                self.TR.Trace(("Services-ConfReportControl: max:"+ Nb1),TL.DETAIL)
                SupportedServices.ConfReportControl = Nb1
                Services = Services.nextSibling
                continue
            if Services.localName == "DataObjectDirectory":
                NbServices = NbServices + 1
                DataObjectDirectory = "Yes"
                self.TR.Trace(("Services-DataObjectDirectory: yes"),TL.DETAIL)
                Services = Services.nextSibling
                continue
            if Services.localName == "DynDataSet":              # OK ##############
                NbServices = NbServices + 1
                DynDataSet = "Yes"
                max = Services.getAttribute("max")
                SupportedServices.DynDataSet = ServiceWithMaxAndMaxAttributes(max,0)
                self.TR.Trace(("Services-DynDataSet: "+max),TL.DETAIL)
                Services = Services.nextSibling
                continue

            if Services.localName == "FileHandling":            # OK ##############
                NbServices = NbServices + 1
                SupportedServices.FileHandling = "Yes"
                self.TR.Trace(("Services-FileHandling:"),TL.DETAIL)
                Services = Services.nextSibling
                continue

            if Services.localName == "GetCBValues":             # OK ##############
                NbServices = NbServices + 1
                SupportedServices.GetCBValues = "Yes"
                self.TR.Trace(("Services-GetCBValues: Yes"),TL.DETAIL)
                Services = Services.nextSibling
                continue

            if Services.localName == "GetDataObjectDefinition":
                NbServices = NbServices + 1
                GetDirectory = "Yes"
                self.TR.Trace(("Services-GetDataObjectDefinition: Yes"),TL.DETAIL)
                Services = Services.nextSibling
                continue
            if Services.localName == "GetDataSetValue":
                NbServices = NbServices + 1
                GetDataSetValue = "Yes"
                self.TR.Trace(("Services-GetDataSetValue: Yes"),TL.DETAIL)
                Services = Services.nextSibling
                continue
            if Services.localName == "GetDirectory":
                NbServices = NbServices + 1
                GetDirectory = "Yes"
                self.TR.Trace(("Services-GetDirectory: Yes"),TL.DETAIL)
                Services = Services.nextSibling
                continue

            if Services.localName == "GOOSE":               #
                NbServices = NbServices + 1
                max   = Services.getAttribute("max")
                fixed = Services.getAttribute("fixedOffs")  # default false
                if (fixed is None) or (fixed==''):
                    fixed = 'false'
                goose  = Services.getAttribute("goose")     # default true
                if (goose is None) or (goose==''):
                    goose = 'true'
                rGOOSE = Services.getAttribute("rGOOSE")    # default false
                if (rGOOSE is None) or (rGOOSE==''):
                    rGOOSE = 'false'

                GOOSEcapabilities=(max,fixed,goose,rGOOSE)

                self.TR.Trace(("Services-GOOSE: max="+max+" fixed="+fixed+" goose="+goose+" rGOOSE="+rGOOSE),TL.DETAIL)

                SupportedServices.GOOSE = GOOSEcapabilities
                Services = Services.nextSibling
                continue

            if Services.localName == "GSSE":               ### OK
                NbServices = NbServices + 1
                max   = Services.getAttribute("max")
                SupportedServices.GSSE = max
                self.TR.Trace(("Services-GSSE: max="+max),TL.DETAIL)
                Services = Services.nextSibling
                continue

            if Services.localName == "ConfSigRef":          ### OK
                NbServices = NbServices + 1
                max = Services.getAttribute("max")
                SupportedServices.ConfSigRef = max
                self.TR.Trace(("Services-ConfSigRef: max=" + max), TL.DETAIL)
                Services = Services.nextSibling
                continue

            if Services.localName == "GSESettings":         ### OK
                NbServices = NbServices + 1
                cbName = Services.getAttribute("cbName")
                datSet = Services.getAttribute("datSet")
                appID  = Services.getAttribute("appID")
                self.TR.Trace(("Services-GSESettings: cbName:" +cbName+" datSet:"+datSet+" appID:"+appID),TL.DETAIL)
                Services = Services.nextSibling
                continue

            if Services.localName == "ReadWrite":
                NbServices = NbServices + 1
                SupportedServices.ReadWrite = "Yes"
                self.TR.Trace(("Services-ReadWrite= Yes"),TL.DETAIL)
                Services = Services.nextSibling
                continue
            if Services.localName == "RedProt":
                NbServices = NbServices + 1
                hsr = Services.getAttribute("hsr")
                prp = Services.getAttribute("prp")
                rstp= Services.getAttribute("rstp")
                self.TR.Trace(("Services-RedProt: hsr:"+hsr+" prp:"+prp+ " rstp:" + rstp),TL.DETAIL)
                Services = Services.nextSibling
                continue

            if Services.localName == "ValueHandling":
                NbServices = NbServices + 1
                setToRO = Services.getAttribute("setToRO")
                if (setToRO is None) or (setToRO == ''):
                    setToRO = 'false'

                V = ValueHandling(setToRO)
                SupportedServices.ValueHandling = V
                self.TR.Trace(("Services-ValueHandling:  setToRO"+setToRO),TL.DETAIL)
                Services = Services.nextSibling
                continue


            if Services.localName == "ReportSettings":                  # OK ############
                NbServices = NbServices + 1
                Report_bufTime = Services.getAttribute("bufTime")
                Report_cbName = Services.getAttribute("cbName")
                Report_rptID = Services.getAttribute("rptID")
                Report_datSet = Services.getAttribute("datSet")
                Report_intgPd = Services.getAttribute("intgPd")
                Report_optFields = Services.getAttribute("optFields")
                self.TR.Trace(( "Services-ReportSettings:"+ \
                       " bufTime:"         + Report_bufTime +      \
                       " Report_cbName:"   + Report_cbName +      \
                       " Report_rptID:"    + Report_rptID +        \
                       " Report_datSet:"   + Report_datSet +       \
                       " Report_intgPd:"   + Report_intgPd +       \
                       " Report_optFields:"+ Report_optFields ),TL.DETAIL)
                RptSetting=(Report_bufTime,Report_cbName,Report_rptID,Report_datSet,Report_intgPd,Report_optFields)
                SupportedServices.ReportSettings=RptSetting
                Services = Services.nextSibling
                continue

            if Services.localName == "LogSettings":              # OK ############
                NbServices = NbServices + 1
                Log_logEna = Services.getAttribute("logEna")
                Log_trgOps = Services.getAttribute("trgOps")
                Log_intgPd = Services.getAttribute("intgPd")

                LogSet = LogSettings(Log_logEna,Log_trgOps,Log_intgPd)
                SupportedServices.LogSettings = LogSet
                self.TR.Trace(( "Services-LogSettings: LogEna="+Log_logEna+\
                                                 "trgOps="+Log_trgOps+\
                                                 "intgPd="+Log_intgPd),TL.DETAIL)
                Services = Services.nextSibling
                continue

            if Services.localName == "SettingGroups":           # OK ############ limité à SGEdit
                NbServices = NbServices + 1

                if (Services.firstChild is None):
                    SupportedServices.SettingGroups.SGEdit = '?'
                    self.TR.Trace(("###Services-SettingGroups: ", SupportedServices.SettingGroups.SGEdit), TL.DETAIL)
                else:
                    S1 = Services.firstChild.nextSibling
                    if S1 is not None:
                        if (S1.nodeName == "SGEdit"):
                            SGEdit = 'yes'
                        if (S1.nodeName=="ConfSG"):
                            xxxConfSG = 'yes'
                        else:
                            self.TR.Trace(("SGEdit NON TRAITE",S1.nodeName),TL.ERROR)

                        SupportedServices.SettingGroups.SGEdit = 'SGEdit'
                        self.TR.Trace(("Services-SettingGroups: ", SupportedServices.SettingGroups.SGEdit),TL.DETAIL)

                Services = Services.nextSibling
                continue

            if Services.localName == "SMVsc":
                NbServices = NbServices + 1
                max = Services.getAttribute("max")
                if (max is None):
                    max = 0
                delivery = Services.getAttribute("delivery")
                if (delivery is None) or (delivery==''):
                    delivery = 'multicast'
                dCfg = Services.getAttribute("deliveryConf")
                if (dCfg is None) or (dCfg == ''):
                    dCfg     = 'false'
                sv = Services.getAttribute("sv")
                if (sv is None) or ( sv == ''):
                    sv = 'true'
                rSV = Services.getAttribute("rSV")
                if (rSV is None) or (rSV == ''):
                    rSV = 'false'

                SupportedServices.SMVsc = SMVsc(max,delivery, dCfg, sv, rSV)

                X1= SupportedServices.SMVsc.getMax()
                X2= SupportedServices.SMVsc.getrSV()

                self.TR.Trace(("Services-SMVsc: "+SupportedServices.SMVsc.getMax() \
                                            +SupportedServices.SMVsc.getDeliveryConf()),TL.DETAIL)

                Services = Services.nextSibling
                continue
            if Services.localName == "SMVSettings":
                NbServices = NbServices + 1
                cbName          = Services.getAttribute("cbName")
                datSet          = Services.getAttribute("datSet")
                svID            = Services.getAttribute("svID")
                optFields       = Services.getAttribute("optFields")
                smpRate         = Services.getAttribute("smpRate")
                samplesPerSec   = Services.getAttribute("samplesPerSec")
                pdcTimeStamp    = Services.getAttribute("pdcTimeStamp")

                self.TR.Trace(( "Services-GSESettings: cbName:"+ cbName +    \
                                             "datSet:"+ datSet +    \
                                               "svID:"+ svID +      \
                                          "optFields:"+ optFields+  \
                                            "smpRate:"+ smpRate+    \
                                      "samplesPerSec:"+ samplesPerSec + \
                                       "pdcTimeStamp:"+ pdcTimeStamp),TL.DETAIL)

                SMVsetting = Services.firstChild.nextSibling
                if (SMVsetting.localName=="SmpRate"):
                    SmpRate = SMVsetting.nodeValue
                    if SmpRate is not None:
                        self.TR.Trace(("Services-SMVSettings:"+SmpRate),TL.DETAIL)

                Services = Services.nextSibling
                continue
            if Services.localName == "SupSubscription":             ### OK
                NbServices = NbServices + 1
                maxGo = Services.getAttribute("maxGo")
                maxSv = Services.getAttribute("maxSv")
                self.TR.Trace(("Services-SupSubscription: maxGo:" + maxGo + " maxSv: "+maxSv),TL.DETAIL)
                Services = Services.nextSibling
                continue

            if Services.localName == "TimeSyncProt":
                NbServices = NbServices + 1
                sntp    = Services.getAttribute("sntp")
                ptp     = Services.getAttribute("c37_238") # ==> PTP IEE1588
                other   = Services.getAttribute("other")
                self.TR.Trace(("Services-TimeSyncProt: sntp:"+sntp+ "ptp:" +ptp+ "other: " + other),TL.DETAIL)
                Services = Services.nextSibling
                continue
            NbServices = NbServices + 1  # Pour forcer la sortie...
        self.TR.Trace(("Nombre de services trouvés: "+str(NbServices)),TL.DETAIL)
        NbServices = 0

        return SupportedServices

###
#   Test unitaire de la class
###
class Test_Services:
    def main(directory, file, scl):
        TRX = TConsole(TL.DETAIL)

        TRX.Trace(("---------------------------------------------------"), TL.GENERAL)
        if scl is None:  # UNIT TEST
            scl = dom.parse(directory + file)
        TRX.Trace(("File:" + file), TL.GENERAL)
        tServices =[]
        IED_lst = scl.getElementsByTagName("IED")
        for IED in IED_lst:
            _type    = IED.getAttribute("type")
            _IEDname = IED.getAttribute("name")
            _desc     = IED.getAttribute("desc")
            SRV = Parse_Services(_IEDname, TRX)

            TRX.Trace(("IED-Name:" + _IEDname + " desc:" + _desc + " type:" + _type), TL.GENERAL)
            pServices = IED.firstChild.nextSibling
            while (pServices):
                if (pServices.nodeName == 'Private'):
                    pServices = pServices.nextSibling
                    continue
                if (pServices.nodeName == 'Services'):
                    tServices.append(SRV.Services(pServices))
                pServices = pServices.nextSibling


if __name__ == '__main__':
    TRX = TConsole(TL.DETAIL)
    fileliste = FL.lstFull  # Liste de fichier de niveau système et IED
    for file in fileliste:
        Test_Services.main('SCL_files/', file, None)

    fileliste = FL.lstIED  # Liste de fichier de niveau système et IED
    for file in fileliste:
        Test_Services.main('SCL_files/', file, None)

    TRX.Trace(("FIN SERVICES"),TL.GENERAL)

