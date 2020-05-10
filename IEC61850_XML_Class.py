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
    ##
    # SubNetWork Class description is extracted from IEC61850-6 document
    # @param _name : A name identifying this bus; unique within this SCL file
    # @param _type : The SubNetwork protocol type; protocol types are defined by the SCSMs. In the
    # examples, 8-MMS is used for the protocol defined in IEC 61850-8-1; IP should be used
    # for all IP based protocols except those explicitly standardized. PHYSICAL should be
    # used, if only physical connections shall be modeled, e.g. at a hub.
    # @param _desc : Some descriptive text to this SubNetwork
    # @param _text : Additional text


    def __init__(self, _name, _type, _desc, _text, _bitRate, _ConnectedAP):

    ##  The constructor for SubNetwork is parsing this section of SCL:
    # <SubNetwork name="Subnet1"
    #    <Text>Station bus</Text>
    #    <BitRate unit="b/s">10</BitRate>
    #  capName="AP1" iedName="SF6P1">

        self.name         = _name       ## name from SCL
        self.type         = _type       ## type from SCL
        self.desc         = _desc       ## desc from SCL
        self.text         = _text       ## text from SCL
        self.bitRate      = _bitRate    ## bitRate from SCL
        self.tConnectedAP = _ConnectedAP ## The table of the connected AcessPoint

    ##
    # SubNetWork/bitRAte Class
    # @param _bitRate : Precise the bit rate of the network
    # @param _ConnectedAP   : table of connected Access Point (usually one)
    class BitRate:
        """The class  BitRate, IEC61850 class + the Table of ConnectedAP
        """
        def __init__(self, _unit, _value):                # <BitRate unit="b/s">10</BitRate>
            """The constructor BitRate, IEC61850 class + the Table of ConnectedAP
            """
            self.unit = _unit
            self.value = _value
    ##
    # Connected APClass The ApClass reflect the ConnectedAP section of the SCL
    # @param   iedName(iec)   A name identifying the IED
    # @param   apName(iec)    A name identifying this access point within the IED
    # @param   desc(iec)      Some descriptive text for this access point at this subnetwork
    # @param   redProt(iec)   The redundancy protocol used at this access point: allowed values are hsr, prp. rstp, none;
    #                          no default value, i.e. value not known if the attribute is missing.
    #                          The allowed values are restricted by the IED capabilities (Services/RedProt).
    #
    # @param   tAddress(app)   Table of adresses (P Type) et val
    # @param   tSMV(app)       Table of SMV classes
    # @param   tGSE(app)       Table of GSE classes
    # @param   PhysConn(app)   Table of PhysConn classes
    class ConnectedAP:
        def __init__(self, _iedName, _apName, _desc, _redProt):  #<ConnectedAP iedName="TEMPLATE" apName="P1" desc= "... ">
            self.iedName   = _iedName       # A name identifying the IED
            self.apName    = _apName        # A name identifying this access point within the IED
            self.desc      = _desc          # Some descriptive text for this access point at this subnetwork
            self.redProt   = _redProt       # The redundancy protocol used at this access point: allowed values are hsr, prp. rstp, none;
                                            # no default value, i.e. value not known if the attribute is missing.
                                            # The allowed values are restricted by the IED capabilities (Services/RedProt).
            """
                Attributes
            """
            self.tAddress  = []             ##  Table of adresses (P Type) et val
            self.tSMV      = []             # Table of SMV classes
            self.tGSE      = []             # Table of GSE classes
            self.PhysConn  = []             # Table of PhysConn classes

        ##
        #  GSE Class:   The GSE element defines the address for a GSE control block in this IED.
        #
        #  @param desc(iec)     Textual description
        #  @param ldInst(iec)   The instance identification of the LD within this IED, on which the control block is located. An
        #                       LN is not necessary, as these control blocks are only in LLN0.
        #  @param cbName(iec)   The name of the control block within the LLN0 of the LD ldInst.
        #
        class GSE:
            def __init__(self, _ldInst, _cbName, _desc):
                self.ldInst      = _ldInst      ## ldInst from SCL
                self.cbName      = _cbName      ## cbName from SCL
                self.desc        = _desc        ## desc from SCL
                self.MinTime     = None         ## Will be to a 'MinTime' class if present
                self.MaxTime     = None         ## Will be to a 'MaxTime' class if present
                self.tGSEAddress = []           ## Table of GSE adresses
            ##
            # MinTime: the sending delay on a data change between the first immediate sending
            # of the change and the first repetition in ms.
            # SCL: <nit="s" multiplier="m">2</MinTime>
            class MinTime:
                def __init__(self, _unit, _min, _mul):
                    ## <MinTime unit="s" multiplier="m">1000</MinTime>
                    self.unit       = _unit # unit from SCL
                    self.min        = _min  # MinTime from SCL
                    self.multiplier = _mul  # Multipler from QXL

            ##
            # MaxTime: the source supervision time in ms (supervision heartbeat cycle time).
            # Within this time, a failed message from the source shall be detected by
            # the subscriber.
            # SCL: <MaxTime unit="s" multiplier="m">10</MaxTime>
            class MaxTime:
                def __init__(self, _unit, _max, _mul):
                    ## <MaxTime unit="s" multiplier="m">1000</MaxTime>
                    self.unit       = _unit # unit from SCL
                    self.max        = _max  # MinTime from SCL
                    self.multiplier = _mul  # Multipler from SCL

        ##
        # \b SMV: The SMV element defines the address for a sampled value control block, like the GSE
        # element does for the GSE control blocks. It is also based on the tControlBlock schema type,
        # and therefore has the same attributes as the GSE control block.
        #
        # @param desc(iec):   Textual description.
        # @param ldInst(iec): The instance identification of the LD within this IED, on which the control block is located. An
        #                LN is not necessary, as these control blocks are only in LLN0.
        # @param cbName(iec):  The name of the control block within the LLN0 of the LD ldInst.
        #
        # The SCL is looking like this:
        #  <SMV ldInst="MU01" cbName="MSVCB01">
        #   	<Address>                                               ### Stored in tSMVAdress.
        #   		<P type="MAC-Address">01#-0C-CD-04-00-00</P>
        #   		<P type="VLAN-ID">000</#P>
        #   		<P type="VLAN-PRIORITY#">4</P>
        #           <P type="APPID">4000</#P>sociés

        class SMV:
            def __init__(self,_ldInst,_cbName, _desc):
                                                        ##
                self.ldInst      = _ldInst              # ldInst from SCL
                self.cbName      = _cbName              # cbName from SCL
                self.desc        = _desc                # desc   from SCL
                self.tSMVAddress = []                   # tSMVAddress table following the SMV Tag.

        ##
        #  \b Physical connection parameters
        #   The element PhysConn defines the type(s) of physical connection for this access point. The
        #   parameter values depend on the type of physical connection, and their types (meaning) have
        #    to be defined in the stack mapping. Additional types may be introduced for documentation
        #    purposes
        #
        # @param PhysConn:  type  Connection or RedConn

        class PhysConn:                                  # <PhysConn type="Connection">         # Checked
            def __init__(self, _type, _PhysAddress):     #     <P type="Type">FOC</P> Type, Plug, Cable, Port
                self.type        =  _type                #     <P type="Plug">LC</P>
                self.tPhysAddress = _PhysAddress         # </PhysConn>

            ##
            # \b P \b type
            # \b Type 10BaseT, 100BaseT etc. for electrical connection FOC for optical connection Radio for radio connection, for example WLAN
            #
            # \b Plug RJ45 for electrical plug ST for bajonet plug (optical glass)
            #
            # \b Cable The identification of a physical cable for this connection, which connects this connection point to another connection point
            #
            # \b Port The identification of a port or terminal at this access point to which a cable is connected (see connection
            class PType:                                               # <Address>
                def __init__(self, _type, _value):                     # 	<P type="MAC-Address">01-0C-CD-04-00-00</P>
                    self.type  = _type                                 # 	<P type="VLAN-ID">000</P>
                    self.value = _value                                # </Address>




##
# \b IED
# @param name   The identification of the IED. Within an ICD file describing a device type, the name shall
#               be TEMPLATE. The IED name shall not be an empty string and not None and shall be
#               unique within an SCL file
#@param desc    The description text
#@param type    The (manufacturer specific) IED product type
#@param         manufacturer The manufacturer's name
#@param         configVersion The basic configuration version of this IED configuration
#@param         originalSclVersion The original SCL schema version of the IEDs ICD file; optional, default “2003”
#@param         originalSclRevision The original SCL schema revision of the IEDs ICD file; optional, default “A”
#@param         originalSclRelease The original SCL schema release of the IEDs ICD file; optional, default ‘1’: Observe that
#               2003A had no release at all
#@param engRight The engineering right transferred by a SED file (only fix, dataflow), or the current state
#               in an SCD file. Values are full, dataflow, fix, the default is full
#@param owner   The owner project of this IED, i.e. the Header id of that SCD file of that project which
#               has the right to use the IED tool for this IED. The default is the Header id of the SCD file
#               containing the IED
class IED:
    def __init__(self, _name, _type, _desc, _originalSclVersion, _originalSclRevision,
                       _configVersion, _manufacturer, _engRight, _owner):
        self.Server             = None
        self.name               = _name                 ## IEC attribute
        self.type               = _type                 ## IEC attribute
        self.desc               = _desc                 ## IEC attribute
        self.originalSclVersion = _originalSclVersion   ## IEC attribute
        self.originalSclRevision= _originalSclRevision  ## IEC attribute
        self.configVersion      = _configVersion        ## IEC attribute
        self.manufacturer       = _manufacturer         ## IEC attribute
        self.engRight           = _engRight             ## IEC attribute
        self.owner              = _owner                ## IEC attribute
    ##
    # Application data
        self.IP                 = None                  ## APP IP address from the communication
        self.tAddress           = []                    ## APP Table of MMS adresses
        self.tDAI               = []                    ## APP Table of actual DOI/..SDI../DAI/ values.
        self.tAccessPoint       = []                    ## APP Table of AccessPoint

    ##
    # \b AccessPoint List of network access point for a given IED (for example ADMIN versus DataModel)
    # @param name   Reference identifying this access point within the IED
    # @param desc    Reference identifying this access point within the IED
    # @param router The presence and setting to true defines this IED to have a router function.
    #               By default, its value is false (no router function).
    # @param clock  The presence and setting to true defines this IED to be a master clock at this bus.
    #               By default, its value is false (no master clock).
    class AccessPoint:
        def __init__(self, _name, _desc, _router, _clock):
            self.name   = _name         ## IEC   Reference identifying this access point within the IED
            self.desc   = _desc         ## IEC   Reference identifying this access point within the IED
            self.router = _router       ## IEC   The presence and setting to true defines this IED to have a router function.
            self.clock  = _clock        ## IEC   The presence and setting to true defines this IED to be a master clock at this bus.
            self.tServer = []           ## APP   The table of server for this AccessPoint

        ##
        # \b Server an IEC1850 data server attached to a AccessPoint (potentially more than one).
        # The server is where network adresses are defined
        #
        # @param timeout(iec)   Time out in seconds: if a started transaction (for example selection of a setting group) is
        #                       not completed within this time, it is cancelled and reset
        # @param desc(iec)      A descriptive text
        class Server:
            def __init__(self, _desc, _timeout):
                self.desc            = _desc     ## IEC A descriptive text
                self.timeout         = _timeout  ## IEC Transaction timeout
                self.authentication  = None      ## APP default value, else an instance of Authentication
                self.tLDevice        = []        ## APP LDevices are created by setattr(...)
                self.tAddress        = []        ## APP Adresses for communication section

            ##
            # \b Authentication
            #
            #  @param none  No authentication
            #  @param password      defined in the stack mappings (SCSMs)
            #  @param weak          defined in the stack mappings (SCSMs)
            #  @param strong        defined in the stack mappings (SCSMs)
            #  @param certificate   defined in the stack mappings (SCSMs)
            class Authentication:
                def __init__(self, _none, _password, _weak, _strong, _certificate):
                    self.none          = _none          ## IEC  No authentication
                    self.password      = _password      ## Defined in the stack mappings (SCSMs)
                    self.weak          = _weak          ## Defined in the stack mappings (SCSMs)
                    self.strong        = _strong        ## Defined in the stack mappings (SCSMs)
                    self.certificate   = _certificate   ## Defined in the stack mappings (SCSMs)

            # Certains classes remain to be added (GOOSESecurity/SMV Security ServerAt...).
            # This is just because it is not needed yet...
            ##
            # \b LDevice
            #
            #  @param   inst(iec)   Identification of the LDevice within the IED. Its value cannot be the empty string.
            #                       It is always used as key part for references to logical devices within the SCL file.
            #  @param   desc(iec)   The description text
            #  @param   ldName(iec) The explicitly specified name of the logical device according to IEC 61850-7-1 and
            #                       IEC 61850-7-2 within the communication. If missing, the default is the IED name
            #                       concatenated with the inst value defined above
            class LDevice:
                def __init__(self, _inst, _ldName, _desc):
                    self.inst    = _inst    ##  IEC  Identification of the LDevice within the IED.
                    self.desc    = _desc    ##  IEC  Text
                    self.ldName = _ldName   ##  IEC  The explicitly specified name of the logical device according to IEC 61850-7-1
                    ##   self.LN0    = _LN0 (APP)   Dynamically added by their name using setAttr.
                    ##   self.tLNode = [] (APP)     Dynamically added by their name using setAttr

            ##
            # \b LN
            #
            # @param _localName(app)    LN0 or LN (according to IEC61850 standard, there should be two classes).
            # @param _prefix(iec)       The LN prefix part
            # @param _lntype(iec)       The instantiable type definition of this logical node, reference to a LNodeType definition
            # @param _inst(iec)         The LN instance number identifying this LN – an unsigned integer
            # @param _lnClass(iec)      The LN class according to IEC 61850-7-x
            # @param _desc(iec)         The description text for the logical node
            class LN:
                def __init__(self, _localName, _prefix, _lnType, _inst, _lnClass, _desc):   # Checked
            # Partie générique commune à LN0 et LNODE (LN)
                    self.localName  = _localName## (APP) LN or LN0
                    self.lnPrefix   = _prefix   ## The LN prefix part
                    self.lnType     = _lnType   ## The instantiable type definition of this logical node, reference to a LNodeType definition
                    self.lnInst     = _inst     ## The LN instance number identifying this LN – an unsigned integer
                    self.lnClass    = _lnClass  ## The LN class according to IEC 61850-7-x
                    self.lnDesc     = _desc     ## The description text for the logical node
                    self.tDataSet   =  []       ## Array of DataSet associé à ce LN0
                    self.tSVCtrl    =  []       ## Array of SampleValueControl block à ce LN0
                    self.tGSECtrl   =  []       ## Array of GSEControl
                    self.tInputs    =  []       ## Array of inputs/Extrefs
                    self.tLogCtrl   =  []       ## Array of LogControl
                    self.tRCB       =  []       ## Array of RCB
            ##      self.DO_Name    = ...       ## Dynamically added with 'setattr' to get actual DO_Name

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
                    def __init__(self, _rptID,_confRev,_buffered,_bufTime,_indexed,_intgPd,_name,_desc,_datSet): # Checked
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
                        def __init__(self,  _iedName, _ldInst, _prefix, _lnClass, _lnInst, _doName, _daName, _intAddr, _desc, _service,
                                            _srcLDInst, _srcPrefix, _srcLNClass, _srcLNInst, _srcCBName, _pDO, _pLN, _pDA, _pServT):

                            self.iedName     = _iedName     # The name of the IED from where the input comes. For IED internal references the value @ may be used.
                            self.ldInst      = _ldInst      # The LD instance name from where the input comes
                            self.prefix      = _prefix      #The LN prefix
                            self.lnClass     = _lnClass     # The LN class according to IEC 61850-7-x. Used to indicate the lnClass of the concrete binding part within a SCD.
                            self.lnInst      = _lnInst      # The instance id of this LN instance of above LN class in the IED; missing for a reference in LLN0.
                                                            # For backwards compatibility also the empty string shall be accepted for LLN0
                            self.doName      = _doName      #  A name identifying the DO (within the LN).In case of structured DO, the name
                                                            # parts are concatenated by dots (.).Used to indicate the DO (within the LN)
                                                            # of the concrete binding part within a SCD.
                            self.daName      = _daName      #The attribute designating the input. The IED tool should use an empty value if it has some
                                                            # default binding (intAddr) for all process input attributes of a DO (fc = ST or MX), especially for t and q.
                                                            #  If the attribute belongs to a data type structure, then the structure name parts shall be separated by dots (.)
                            self.intAddr     = _intAddr     # The internal address to which the input is bound. Only the IED tool of the concerned IED
                                                            # shall use the value. All other tools shall preserve it unchanged
                            self.desc        = _desc        # A free description / text. Can e.g. be used at system engineering time to
                                                            # tell the IED engineer the purpose of this incoming data
                            self.serviceType = _service     #SubNetWork Optional, values: Poll, Report, GOOSE, SMV, Used to indicate the used service if the data flow is configured.

                            self.srcLDInst   = _srcLDInst   # The LD inst of the source control block – if missing, same as ldInst above
                            self.srcPrefix   = _srcPrefix   # The prefix of the LN instance, where the source control block resides; if missing, no prefix
                            self.srcLNClass  = _srcLNClass  # The LN class of the LN, where the source control block resides; if missing, LLN0
                            self.srcLNInst   = _srcLNInst   # The LN instance number of the LN where the source control block resides – if missing, no instance number exists (LLN0)
                            self.srcCBName   = _srcCBName   # The source CB name; if missing, then all othere srcXX attributes should also be missing, i.e. no source control block is given.

                            self.pDO         = _pDO         # A preconfigured DO name to indicate an expected DO name and CDC. Any binding must match the CDC.
                            self.pLN         = _pLN         # A preconfigured LN class indicating an expected LN class containing the DO indicated by pDO
                            self.pDA         = _pDA         # Aa preconfigured data attribute indicating the expected attribute. If configured, any bound
                                                            # attribute must match the data type specified by specified pDO CDC and pDA attribute value
                            self.pServT      = _pServT      # A preconfigured service type indicating an expected service type. if configured, serviceType must match its value.

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
                    def __init__(self, _name, _smvID, _smpRate, _nofASDU, _confRev, _multicast, _smpMod,
                                                    _datSet, _desc, _securityEnabled): # checked
                        self.name     = _name
                        self.smvID    = _smvID
                        self.smpRate  = _smpRate
                        self.nofASDU  = _nofASDU
                        self.confRev  = _confRev
                        self.multicast=_multicast
                        self.smpMod   = _smpMod
                        self.datSet   = _datSet
                        self.desc     = _desc
                        self.securityEnabled = _securityEnabled

                    class smvOption:    # todo not parsed !!!! 
                        def __init__(self, _refreshTime, _sampleRate, _dataSet, _security, _synchSourceId):
                            self.refreshTime   = _refreshTime
                            self.sampleRate    = _sampleRate
                            self.dataSet       = _dataSet
                            self.security      = _security
                            self.synchSourceId = _synchSourceId

                class SettingControlBlock:
                    def __init__(self, _desc, _numOfSGs, _actSG, _resvTms):         # Checked
                        self.desc      = _desc          # The description text
                        self.numOfSGs  = _numOfSGs      # The number of setting groups available. The value shall be > 0.
                        self.actSG     = _actSG         # The number of the setting group to be activated when loading the configuration.
                                                        # The default value is 1. Any SCL value shall be > 0.
                        self.resvTms   = _resvTms       # The time in seconds the SGCB stays reserved for editing. After this time
                                                        # the IED automatically closes an edit session, if the client has not closed
                                                        # it or not confirmed any changes (see IEC 61850-7-2). If this function is not supported,
                                                        # the attribute shall be missing. The appropriate IED capability (Table 11) defines
                                                        # if a system tool can modify any value supplied by the IED tool.

                class GSEControl:
                    def __init__(self,_name,_datSet,_type,_confRev,_appID,_fixedOffs,_securityEnabled,_desc):
                        self.name           =_name
                        self.datSet         =_datSet
                        self.type           =_type
                        self.confRev        =_confRev
                        self.appID          =_appID
                        self.fixedOffs      =_fixedOffs
                        self.securityEnabled = _securityEnabled
                        self.desc           = _desc

                class DOI:
                    def __init__(self, _name, _desc, _ix, _accessControl):              #todo _ix Not Managed
                        self.name       = _name
                        self.desc       = _desc
                        self.ix         = _ix
                        self.accessControl = _accessControl
                    class DAI:
                        def __init__(self, _name, _value, _sAddr, _valKind, _desc, _ix, _valImport): #todo _ix Not Managed
                            self.name      = _name
                            self.value     = _value
                            self.sAddr     = _sAddr
                            self.valKind   = _valKind
                            self.desc      = _desc
                            self.ix        = _ix
                            self.valImport = _valImport

                        class SDI:  # Utilisé notamment pour les Contrôles complexes
                            def __init__(self, _name, _sAddr, _ix, _desc):  # , _tSDI):
                                self.name  = _name
                                self.ix    = _ix
                                self.sAddr = _sAddr
                                self.desc  = _desc

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
                        def __init__(self,_ldInst,_prefix,_lnClass,_lnInst,_doName,_daName,_fc,_ix):    # Checked
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
        Simple = ["BOOLEAN", "INT8" ,"INT16" ,"INT24" , "INT32" , "INT64",
                             "INT8U","INT16U","INT24U", "INT32U",
                  "FLOAT32", "FLOAT64",
                  "Dbpos"  , "Tcmd",                # 'Enum' need to be treated as specific type.
                  "Quality", "Timestamp",
                  "VisString32","VisString64", "VisString65", "VisString129","VisString255","Unicode255",
                  "Octet64",
                  "EntryTime",                      # 'Struct' need to be treated as specific type.
                  "Check"  , "ObjRef",

                  "Currency",
                  "PhyComAddr", "TrgOps", "OptFlds", "SvOptFlds","LogOptFlds",
                  "EntryID",
                  "AnalogueValueCtlF",
                  "Octet6", "Octet16"          # Edition 2.1
                  ]

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
    ##
    #  GSE Class:   The GSE element defines the address for a GSE control block in this IED.

    #  @param id(iec)       A reference identifying this LN type within this SCL section; used by the LN attribute
    #                       LNType of from a LNode definition in the process section to reference this definition
    #  @param desc(iec)     An additional text describing this LN type
    #  @param iedType(iec)  The manufacturer IED type of the IED to which this LN type belongs - deprecated
    #  @param lnClass(iec)  The LN base class of this type as specified in IEC 61850-7-x; observe that here an enumeration exists,
    #  @param _tDO (app)    The table of Data Object of this LNODE Type.

    class LNodeType:
        def __init__(self, _id, _desc, _iedType, _lnClass, _tDO):
            self.id         = _id           # A reference identifying this LN type within this SCL section; used by the LN attribute
                                            # LNType of from a LNode definition in the process section to reference this definition
            self.desc       = _desc         # An additional text describing this LN type
            self.iedType    = _iedType      # The manufacturer IED type of the IED to which this LN type belongs - deprecated
            self.lnClass    = _lnClass      # The LN base class of this type as specified in IEC 61850-7-x; observe that here an enumeration exists,
                                            # which allows extensions (names containing only capital letters)
            self.tDO = _tDO                 # Table of the DO element


        ##
        #  DO element of a LNodeType
        #
        #   @param  name(iec)            # The data object name as specified for example in IEC 61850-7-4
        #   @param  type(iec)            # The type references the id of a DOType definition
        #   @param  accessControl(iec)   # Access control definition for this DO. If it is missing, then any higher-level access control definition applies
        #   @param  transient(iec)       # If set to true, it indicates that the Transient definition from IEC 61850-7-4 applies
        #   @param  desc(iec)            # Descriptive text for the DO element
        class DOi:
            def __init__(self, _name, _type, _accessControl, _transient, _desc, ):
                self.name           = _name             # The data object name as specified for example in IEC 61850-7-4
                self.type           = _type             # The type references the id of a DOType definition
                self.accessControl  = _accessControl    # Access control definition for this DO. If it is missing, then any higher-level access control definition applies
                self.transient      = _transient        # If set to true, it indicates that the Transient definition from IEC 61850-7-4 applies
                self.desc           = _desc             # Descriptive text for the DO element

    ##
    # DO Type An instantiable data object type; referenced from LNodeType or from the
    #         SDO element of another DOType. Instantiable version based on the
    #         CDC definitions from IEC 61850-7-3
    #
    #  @param  id(iec)      The (global) identification of this DOType. Used to reference this type.
    #  @param  iedType(iec) The type of the IED to which this DOType belongs. The empty string allows
    #                       references for all IED types, or from the Substation section without IED identification.
    #  @param  cdc(iec)     The basic CDC (Common Data Class) as defined in IEC 61850-7-3.
    #  @param  desc(iec)    Description of this DOType
    #  @param  tDA(app)     Table of DA.

    class DOType:
        def __init__(self, _id, _iedType, _cdc, _desc, _tDA):   # checked
            self.id      = _id          # The (global) identification of this DOType. Used to reference this type.
            self.iedType = _iedType     # The type of the IED to which this DOType belongs. The empty string allows
                                        # references for all IED types, or from the Substation section without IED identification.
            self.cdc     = _cdc         # The basic CDC (Common Data Class) as defined in IEC 61850-7-3.
            self.desc    = _desc        # Description of this DOType
            self.tDA  = _tDA            # Table of DA.


        ##
        #
        #  @param _desc(iec)    Some descriptive text for the attribute
        #  @param _name(iec)    The attribute name; the type tAttributeNameEnum restricts to the attribute names
        #                       from IEC 61850-7-3, plus new ones starting with lower case letters
        #  @param _fc(iec)      The functional constraint for this attribute; fc=SE always also implies fc=SG;
        #                f      c=SG means that the values are visible, but not editable
        #  @param _dchg(iec)    Defines which trigger option is supported by the attribute (value true means supported).
        #  @param _qchg(iec     One of those allowed according to IEC61850-7-3 shall be chosen.
        #  @param _dupd(iec)
        #
        #  @param _sAddr(iec)   an optional short address of this  attribute (see 9.5.4.3)
        #
        #  @param _bType(iec)   The basic type of the attribute, taken from tBasicTypeEnum (see 9.5.4.2)
        #  @param _type(iec)    The basic type of the attribute, taken from tBasicTypeEnum (see 9.5.4.2)
        #  @param _count(iec)   Optional. Shall state the number of array elements or reference the attribute stating
        #                       this number in case that this attribute is an array. A referenced attribute shall exist
        #                        in the same type definition. The default value 0 states that the attribute is no array.
        #  @param _valKind(iec) Determines how the value shall be interpreted if any is given – see Table 46
        #  @param _valImport(iec) if true, an IED / IED configurator can import values modified by another tool from an SCD file,
        #                        even if valKind=RO or valKind=Conf. It is the responsibility of the IED configurator
        #                        to assure value consistency and value allowance even if valImport is true.
        #
        #  @param _DO(app)        Used to distinguish DO from SDO (only one class for both) (implementation specific)
        #  @param _SDO(app)
        #  @param _value(iec/app) To store pre-defined value at DAi level

        class DAinst:
            def __init__(self, _desc,_name,_fc,_dchg,_qchg,_dupd,_sAddr,_bType,_type
                            ,_count,_valKind,_valImp,_DO,_SDO,_value):

                self.desc    = _desc    # Some descriptive text for the attribute
                self.name    = _name    # The attribute name; the type tAttributeNameEnum restricts to the attribute names
                                        # from IEC 61850-7-3, plus new ones starting with lower case letters
                self.fc      = _fc      # The functional constraint for this attribute; fc=SE always also implies fc=SG;
                                        # fc=SG means that the values are visible, but not editable
                self.dchg    = _dchg    # Defines which trigger option is supported by the attribute (value true means supported). One of those allowed according to IEC61850-7-3 shall be chosen.
                self.qchg    = _qchg    #  One of those allowed according to IEC61850-7-3 shall be chosen.
                self.dupd    = _dupd

                self.sAddr   = _sAddr   # an optional short address of this  attribute (see 9.5.4.3)

                self.bType   = _bType   # The basic type of the attribute, taken from tBasicTypeEnum (see 9.5.4.2)
                self.type    = _type    # The basic type of the attribute, taken from tBasicTypeEnum (see 9.5.4.2)
                self.count   = _count   # Optional. Shall state the number of array elements or reference the attribute stating
                                        # this number in case that this attribute is an array. A referenced attribute shall exist
                                        # in the same type definition. The default value 0 states that the attribute is no array.
                self.valKind  = _valKind # Determines how the value shall be interpreted if any is given – see Table 46
                self.valImport= _valImp # if true, an IED / IED configurator can import values modified by another tool from an SCD file,
                                        # even if valKind=RO or valKind=Conf. It is the responsibility of the IED configurator
                                        # to assure value consistency and value allowance even if valImport is true.

                self.DoDaSdo = _DO      # Used to distinguish DO from SDO (only one class for both) #implementation
                self.SDO     = _SDO
                self.value   = _value   #TODO  Actual value ???

    class DAType:
        def __init__(self, _id, _desc, _protNs, _iedType):
            self.id = _id  # id du type
            self.desc = _desc  # description
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
