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

"""@package docstring
#This class analyse the communication TAG:
#< Communication >
#    <SubNetwork name = "ELECTRE" type = "8-MMS" >
#    <Private type = "Siemens-Start-Address" > 10.3.86.1 < / Private >
#    <ConnectedAP iedName = "SIP5TERNA" apName = "E" >
#        <Address >
#            <P type = "IP" xsi:type = "tP_IP" > 10.3.86.19 < / P >
#            <P type = "IP-SUBNET" xsi:type = "tP_IP-SUBNET" > 255.255.255.0 </P>
"""


class SubStation:
    def __init__(self, _name, _desc):
        self.name     = _name
        self.desc     = _desc
        self.tVoltage = []

    class VoltageLevel:
        def __init__(self, _name, _nomFreq, _numPhases, _desc):
            self.name       = _name
            self.nomFreq    = _nomFreq
            self.numPhase   = _numPhases
            self.desc       = _desc

            self.tBay       = []
            self.tPwrTfo    = []

        class PowerTransformer:
            def __init__(self,_name, _desc, _type, _virtual):
                self.name    = _name
                self.desc    = _desc
                self.type    = _type
                self.virtual = _virtual

        class GeneralEquipment:
            def __init__(self, _name, _type):
                self.name    = _name
                self.type    = _type

        class Voltage:
            def __init__(self, _unit, _multiplier, _value):
                self.unit       = _unit
                self.multiplier = _multiplier
                self.value      = _value

        class Bay:
            def __init__(self, _name, _desc, _sxy_x, _sxy_y):
                self.name  = _name
                self.desc  = _desc
                self.sxy_x = _sxy_x
                self.sxy_y = _sxy_y
                self.tConductingEquipment = []
                self.tConnectivityNode    = []
                self.tFunction            = []
                self.tLNode               = []

            class ConductingEquipment:
                def __init__(self, _name, _desc, _virtual, _sx_y, _sx_x, _sx_dir ):
                    self.name    = _name
                    self.desc    = _desc
                    self.virtual = _virtual
                    self.sx_y    = _sx_y
                    self.sx_x    = _sx_x
                    self.sx_dir  = _sx_dir
                    self.tTerminal = []
                class Terminal:
                    def __init__(self,_name,_connectivityNode,_substationName,_voltageLevelName,_bayName,_cNodeName):
                        self.name              = _name
                        self.connectivityNode  = _connectivityNode
                        self.substationName    = _substationName
                        self.voltageLevelName  = _voltageLevelName
                        self.bayName           = _bayName
                        self.cNodeName         = _cNodeName

            class ConnectivityNode:
                def __init__(self,_name, _desc, _pathName, _sx_y, _sx_x):
                    self.name     = _name
                    self.desc     = _desc
                    self.pathName = _pathName
                    self.sx_y     = _sx_y
                    self.sx_x     = _sx_x
            class Function:
                def __init__(self,_name, _desc):
                    self.name     = _name
                    self.desc     = _desc
            class LNode:
                def __init__(self,_iedName,_lnClass,_lnType,_lnInst):
                    self.iedName = _iedName
                    self.lnClass = _lnClass
                    self.lnType  = _lnType
                    self.lnInst  = _lnInst

class SubNetWork:   # <SubNetwork name="LAN"  type="8-MMS" desc="blabla...
    """Documentation for a class.
    More details.
    This class xxxx analyse the communication TAG:
    < Communication >
        <SubNetwork name = "ELECTRE" type = "8-MMS" >
        <Private type = "Siemens-Start-Address" > 10.3.86.1 < / Private >
        <ConnectedAP iedName = "SIP5TERNA" apName = "E" >
            <Address >
                <P type = "IP" xsi:type = "tP_IP" > 10.3.86.19 < / P >
                <P type = "IP-SUBNET" xsi:type = "tP_IP-SUBNET" > 255.255.255.0 </P>
    """
    def __init__(self, _name, _type, _desc, _text, _bitRate, _ConnectedAP):
        """The constructor xxx, IEC61850 class + the Table of ConnectedAP
        """
        self.name         = _name                         # <SubNetwork name="Subnet1"
        self.type         = _type                         #  ...                       type="8-MMS"
        self.desc         = _desc                         #  ...                       desc="blabla" />
        self.text         = _text                         #  <Text>Station bus</Text>
        self.bitRate      = _bitRate                      #  <BitRate unit="b/s">10</BitRate>
        self.tConnectedAP = _ConnectedAP                  #  <ConnectedAP apName="AP1" iedName="SF6P1">

    class BitRate:
        """The class  BitRate, IEC61850 class + the Table of ConnectedAP
        """
        def __init__(self, _unit, _value):                # <BitRate unit="b/s">10</BitRate>
            """The constructor BitRate, IEC61850 class + the Table of ConnectedAP
            """
            self.unit = _unit
            self.value = _value
    class ConnectedAP:
        def __init__(self, _iedName, _apName, _desc):  #<ConnectedAP iedName="TEMPLATE" apName="P1" desc= "... ">
            self.iedName   = _iedName
            self.apName    = _apName
            self.desc      = _desc
            self.tAddress  = []             # Table of adresses (P Type) et val
            self.tSMV      = []             # Table of SMV classes
            self.tGSE      = []             # Table of GSE classes
            self.PhysConn  = []             # Table of PhysConn classes

        class GSE:
            def __init__(self, _ldInst, _cbName, _desc):
                self.ldInst      = _ldInst
                self.cbName      = _cbName
                self.desc        = _desc
                self.min         = None         # Will be to a 'Min' class if present
                self.max         = None         # Will be to a 'Max' class if present
                self.tGSEAddress = []           # Table of GSE adresses

            class Min:
                def __init__(self, _unit, _min, _mul):
                    self.unit       = _unit
                    self.min        = _min  # <MinTime unit="s" multiplier="m">1000</MinTime>
                    self.multiplier = _mul

            class Max:
                def __init__(self, _unit, _max, _mul):
                    self.unit       = _unit
                    self.max        = _max  # <MaxTime unit="s" multiplier="m">10</MaxTime>
                    self.multiplier = _mul

        class SMV:                                       #  <SMV ldInst="MU01" cbName="MSVCB01">
            def __init__(self,_ldInst,_cbName, _desc):   #   	<Address>
                self.ldInst      = _ldInst               #   		<P type="MAC-Address">01#-0C-CD-04-00-00</P>
                self.cbName      = _cbName               #   		<P type="VLAN-ID">000</#P>
                self.desc        = _desc                 #   		<P type="VLAN-PRIORITY#">4</P>
                self.tSMVAddress = []                    #        <P type="APPID">4000</#P>sociés

        class PhysConn:                                  # <PhysConn type="Connection">
            def __init__(self, _type, _PhysAddress):     #     <P type="Type">FOC</P>
                self.type        =  _type                #     <P type="Plug">LC</P>
                self.tPhysAddress = _PhysAddress         # </PhysConn>

            class PType:                                               # <Address>
                def __init__(self, _type, _value):                     # 	<P type="MAC-Address">01-0C-CD-04-00-00</P>
                    self.type  = _type                                 # 	<P type="VLAN-ID">000</P>
                    self.value = _value                                # </Address>

class IED:
    def __init__(self, _Server, _tDevice, _name, _type, _desc, _originalSclVersion, _originalSclRevision,
                       _configVersion, _manufacturer, _engRight, _owner, _ip, _tAddress):
        self.Server             = _Server
##      self.tLDevice           = _tDevice              # Table of Ldevices
        self.name               = _name                 # IEC attribute
        self.type               = _type                 # IEC attribute
        self.desc               = _desc                 # IEC attribute
        self.originalSclVersion = _originalSclVersion   # IEC attribute
        self.originalSclRevision= _originalSclRevision  # IEC attribute
        self.configVersion      = _configVersion        # IEC attribute
        self.manufacturer       = _manufacturer         # IEC attribute
        self.engRight           = _engRight             # IEC attribute
        self.owner              = _owner                # IEC attribute
        self.IP                 = _ip                   # IP adress from the communication
        self.tAddress           = _tAddress             # Table of MMS adresses
        self.tDAI               = []                    # Table of actual DOI/..SDI../DAI/ values.
        self.tAccessPoint       = []                    # Table of AccessPoint

    class AccessPoint:
        def __init__(self, _name, _desc, _router, _clock):
            self.name   = _name
            self.desc   = _desc
            self.router = _router
            self.clock  = _clock
            self.tServer = []

        class Server:
            def __init__(self, _desc, _timeout):
                self.desc    = _desc
                self.timeout = _timeout
                self.authentication = None
                self.tLDevice= []               # LDevices are created by setattr(...)
                self.tAddress= []               # Adresses for communication section

            class LDevice:
                def __init__(self, _inst, _ldName, _desc):
                    self.inst   = _inst
                    self.ldName = _ldName
                    self.desc   = _desc
#                    self.LN0    = _LN0         # Dynamically added by name
#                    self.tLNode = []           # Dynamically added by name

            class Authentication:
                def __init__(self, _none, _password, _weak, _strong, _certificate):
                    self.none          = _none
                    self.password      = _password
                    self.weak          = _weak
                    self.strong        = _strong
                    self.certificate   = _certificate

            # Certains classes remain to be added (GOOSESecurity/SMV Security ServerAt...).
            # This is just because it is not needed yet...

            class LN:
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
                        self.rptID     = _rptID
                        self.confRev   = _confRev
                        self.buffered  = _buffered
                        self.bufTime   = _bufTime
                        self.indexed   = _indexed
                        self.intgPd    = _intgPd
                        self.name      = _name
                        self.desc      = _desc
                        self.dataset   = _datSet
                        self.TrgOps    = None
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
                            self.tClientLN = []
                        class ClientLN:
                                def __init__(self, _apRef,_iedName, _ldInst, _lnPrefix, _lnClass,  _lnInst):
                                    self.apRef     = _apRef
                                    self.iedName   = _iedName
                                    self.ldInst    = _ldInst
                                    self.lnPrefix  = _lnPrefix
                                    self.lnClass   = _lnClass
                                    self.lnInst    = _lnInst
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
                                     _srcLNClass, _srcLDInst, _pServT, _intAddr, _pLN, _pDO, _desc, _prefix):

                            self.doName      = _doName
                            self.daName      = _daName
                            self.serviceType = _service
                            self.iedName     = _iedName
                            self.ldInst      = _ldInst
                            self.lnClass     = _lnClass
                            self.lnInst      = _lnInst
                            self.srcCBName   = _srcCBName
                            self.srcLNClass  = _srcLNClass

                            self.srcLDInst   = _srcLDInst
                            self.pServT      = _pServT
                            self.intAddr     = _intAddr
                            self.pLN         = _pLN
                            self.pDO         = _pDO
                            self.desc        = _desc
                            self.prefix      = _prefix

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


class DataTypeTemplates:

# Addition to the DataTypeTemplate:
    class FC:
        lstFC = ['ST', 'MX', 'CF', 'DC', 'SP', 'SV', 'SG', 'SE', 'SR', 'OR', 'BL', 'EX', 'CO']

    class bType:
        Simple = ["VisString64","VisString129","VisString255","Unicode255",
                  "Quality", "Timestamp", "BOOLEAN", "Check", "Dbpos",
                  "INT8U","INT16U","INT32U","INT8","INT16","INT32","INT64",
                  "FLOAT32", "ObjRef","Tcmd","Octet64","EntryID","entryID"]

        String  = ["BOOLEAN","VisString64","VisString129","VisString255","Unicode255",
                   "ObjRef", "Quality", "Timestamp","Tcmd"]     # TODO String or Number ?

        Number =  ["Check",
                   "INT8U","INT16U","INT32U","INT8","INT16","INT32","INT64",
                   "FLOAT32","Octet64"]

    # The following type declaration are only prototypes versions:
    class Quality:
        def __init__(self,_Validity,_Overflow, _OutofRange,_BadReference,_Oscillatory,
                          _Failure,  _OldData, _Inconsistent,_Inaccurate, _Source, _Test, _OperatorBlocked):
            self.Validity       = _Validity     # Enum 0-3 (Good 0, Invalid 1, Réservé 2, Questionable 3)
            self.Overflow 	    = _Overflow 	# BOOLEAN
            self.OutofRange     = _OutofRange   # BOOLEAN
            self.BadReference   = _BadReference # BOOLEAN
            self.Oscillatory    = _Oscillatory  # BOOLEAN
            self.Failure 	    = _Failure 	    # BOOLEAN
            self.OldData 	    = _OldData 	    # BOOLEAN
            self.Inconsistent   = _Inconsistent # BOOLEAN
            self.Inaccurate     = _Inaccurate   # BOOLEAN
            self.Source         = _Source       # Enum: Process 0, Substituted 1
            self.Test           = _Test         # BOOLEAN  (Test active with TRUE)
            self.OperatorBlocked= _OperatorBlocked # BOOLEAN

    class TimeQuality:
        def _init__ (self,_Leap, _Failure_,_NotSync, _Precision):
            self.LeapSecond     = _Leap          # Boolean
            self.ClockFailure   = _Failure_      # Boolean
            self.NotSync        = _NotSync       # Boolean
            self.Precision      = _Precision     # INT 5 bits Number of significant bits
                                                 # in the FractionOfSecond:
    class Timestamp:
        def __init__(self,_SecondSinceEpoch,_FractionOfSecond,_TimeQuality):
            self.second   = _SecondSinceEpoch   # Since 01/01/1970 -UTC
            self.fraction = _FractionOfSecond   #NOTE 1 The resolution is the smallest unit by
                                                # which the time stamp is updated (potentially ~60ns)
            self.quality  = _TimeQuality

    ### WARNING d'après IEC61850-8-1, le 'EntryTime' des BRCB est exprimé en S depuis 01/01/1984
    class PhyComAddr:
        def __init__(self, _Addr, _PRIORITY, _VID, _APPID):     # Défini dans IEC61850-1-2
            self.Addr       = _Addr         #Octet String 6         ==> [Adr Mac] bytes en python
            self.PRIORITY   = _PRIORITY     #Unsigned8 de 0 à7      ==> int en python
            self.VID        = _VID          #Unsigned16 de 0 à 4095 ==> int en python
            self.APPID      = _APPID        #Unsigned16             ==> int en python

    ### CLASS LIEE AUX GOOSE
    # Use case TbD
    class TriggerConditions:                # 6 bits IEC61850-8-1 § 8.1.3.9
        def __init_(self, _reserved, _dChg,_qChg,_dUpdate,_IntPeriod,_GI):
            self.reserved  = _reserved      # N/A
            self.dChg      = _dChg          # Boolean
            self.qChg      = _qChg          # Boolean
            self.dUpdate   = _dUpdate       # Boolean
            self.IntPeriod = _IntPeriod     # Boolean
            self.GI        = _GI            # Boolean

    class GooseMessage:
        def __init_(self, _DatSetRef, _GoID, _GoCBRef, _T, _StNum,_SqNum,
                          _Simulation, _ConfRev, _NdsComn, _DatSet, _mode):
            self.DatSetRef  = _DatSetRef    # ObjectRefernce    (String129, value from GOCB)
            self.GoID       = _GoID         # VisibleString     (String129, value from GOCB)
            self.GoCBRef    = _GoCBRef      # ObjectRefernce    (String129, value from GOCB)
            self.T          = _T            # TimeStamp (if 0 the driver will the time
            self.StNum      = _StNum        # INT32U
            self.SqNum      = _SqNum        # INT32U
            self.Simulation = _Simulation   # Boolean (True : simulation active)
            self.ConfRev    = _ConfRev      # INT32U  (value from GOCB)
            self.NdsCom     = _NdsComn      # BOOLEAN  value from GOCB)
            self.DatSet     = _DatSet       # Data à encoder et à envoyer
            self.mode       = _mode         # Envoi d'une seule trame ou d'un flux.

    class LNodeType:
        def __init__(self, _id, _lnClass, _desc, _iedType, _tDO):
            self.id = _id
            self.lnClass = _lnClass
            self.desc = _desc
            self.iedType = _iedType
            self.tDO = _tDO

        class DOi:
            def __init__(self, _name, _type, _desc):
                self.name = _name
                self.type = _type
                self.desc = _desc

    # DO Type
    class DOType:
        def __init__(self, _id, _cdc, _desc, _tDA):
            self.name = ""
            self.id   = _id
            self.cdc  = _cdc
            self.desc = _desc
            self.tDA  = _tDA      # Table of DA.

        class DAinst:
            def __init__(self, _DO   , _SDO, _type, _fc   , _name, _count, _bType, _valKind,_valImp,
                              _sAddr, _qchg, _dchg, _desc ,_dupd, _value):
                self.DoDaSdo = _DO
                self.SDO     = _SDO
                self.type    = _type
                self.fc      = _fc
                self.name    = _name
                self.count   = _count
                self.bType   = _bType
                self.valKind = _valKind
                self.valImport = _valImp
                self.sAddr   = _sAddr
                self.qchg    = _qchg
                self.dchg    = _dchg
                self.dupd    = _dupd
                self.desc    = _desc
                self.value   = _value

    class DAType:
        def __init__(self, _id, _desc, _protNs, _iedType):
            self.id = _id  # id du type
            self.desc = _desc  # descriptiop
            self.protNs = _protNs  # NameSpace
            self.iedType = _iedType  # iedType
            self.tBDA = []  # Table of the BDA related to this DA.

        # Sub-classe to handle BDA instanciations.
        # The properties of the class are the attrobiutes of IEC61850 DA Object.
        #       <BDA name-="cmdQual" bType="Enum" type="SE_cmdQual_V001" />
        #       <BDA name="orIdent" bType="Octet64" />
        #       <BDA name="mag" bType="Struct" type="SE_instMag_V001" />
        #       <BDA name="numPls" bType="INT32U" />

        class BDA:
            def __init__(self, _name, _type, _bType, _valKind, _value):
                self.name    = _name  # Nom du champ dans le SCL
                self.SDO     = _type
                self.type    = _type  # Type défini dans le SCL (enum ou Structure)
                self.bType   = _bType  # Basic Type, usually without further definition in the SCL
                self.valKind = _valKind
                self.value   = _value

        class ProtNs:  # TODO
            def __init__(self, _type):
                self.type = _type

    class EnumType:
        def __init__(self, _id, _desc):
            self.id       = _id         # id du type
            self.desc     = _desc
            self.tEnumval = []          # Table of the possible value / name for the EnumType
            self.min      = 0           # Not part of IEC61850, added in order to verify that
            self.max      = 0           # values are in the correct range from min to max (included)

        # Child class to handle the list 'EnumVal BDA' associated to a EnumType
        #    < EnumVal ord = "1" > Ok < / EnumVal >
        #    < EnumVal ord = "2" > Warning < / EnumVal >

        class EnumVal:
            def __init__(self, _ord, _strValue, _desc):
                self.ord      = _ord        # Actual numerical value used
                self.strValue = _strValue   # String used to state the value
                self.desc     = _desc
