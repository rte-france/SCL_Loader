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


##
# \b SubStation     Description of the electrotechnical hardware of the substation
#
# Global container for the electrotechnical description of the substation
#
# @param   name(iec)    The substation name
# @param   desc(iec)    A description text of the substationn
#
class SubStation:
    def __init__(self, _name, _desc):
        self.name     = _name           ##
        self.desc     = _desc           ##

        self.tVoltage           = []    ## Defined in sub class Equipment container.
        self.tPowerTransformer  = []    ## Defined in sub class Equipment container.
        self.tFunction          = []    ## Defined in sub class Equipment container.
        self.tBay               = []

#    class EquipmentContainer:
#        def __init__(self, _xx):
#            self.xx          = _xx
#            self.tVoltage    = []

    ##
    # \b VoltageLevel
    #
    # The substation is described per VoltageLevel
    class VoltageLevel:
        ##
        # @param _name      Name of the voltage level
        # @param _desc      Description text
        def __init__(self, _name, _desc):
            self.name      = _name      ## name
            self.desc      = _desc      ## desctiption text

            self.tBay       = []        ## tBay      : Table of Bay in the substation
            self.tPwrTfo    = []        ## tPwrTfo   : Table of transfromer for the voltage level
            self.tFunction  = []        ## tFunction :
        ##
        # Voltage is a sub-class of Voltage Level
        #
        #  @param unit          # Unit for voltage : V or kV
        #  @param _multiplier   #
        #  @param _value        # 100
        class Voltage:
            def __init__(self, _unit, _multiplier, _value):
                self.unit = _unit
                self.multiplier = _multiplier
                self.value = _value

        class PowerTransformer: # uniquePowerTransformerInVoltageLevel
            def __init__(self,_name, _desc, _type, _virtual):
                self.name    = _name
                self.desc    = _desc
                self.type    = _type
                self.virtual = _virtual

    ##
    # Function is used by Bay, Voltage Level et Substation.
    class Function:
        def __init__(self, _name, _desc):
            self.name = _name
            self.desc = _desc

    class ConductingEquipment:
        def __init__(self, _name, _desc, _virtual, _sx_y, _sx_x, _sx_dir):
            self.name    = _name
            self.desc    = _desc
            self.virtual = _virtual
            self.sx_y    = _sx_y
            self.sx_x    = _sx_x
            self.sx_dir  = _sx_dir
            self.tTerminal = []

    class LNode:
        def __init__(self,_lnInst,_lnClass,_iedName,_ldInst,_prefix,_lnType ):
            self.lnInst =_lnInst      ## lnInst  The LN instance identification. Can only be missing for lnClass=LLN0, meaning as value here the empty string.
            self.lnClass=_lnClass     ## lnClass The LN class as defined in IEC 61850-7-x.
            self.iedName=_iedName     ## iedName The name of the IED which contains the LN, none if used for specification (default if attribute is not specified).
            self.ldInst =_ldInst      ## ldInst  The LD instance on the IED which contains the LN within a specification (SSD file), where iedName=None, this shall result in unique LN instance identification, i.e. may contain the LD name
            self.prefix =_prefix      ## prefix  The LN prefix used in the IED (if needed; default, if not specified, is the empty string). Can be used for more detailed function specification than possible by LN class alone, if the LN is not allocated to an IED
            self.lnType =_lnType      ## lnType  The logical node type definition containing more detailed functional specification. Might be missing, if the LN is allocated to an IED.

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

    class SubEquipement:
        def __init__(self, _name, _desc, _phase, _virtual):
            self.name    = _name    ##  The identification of the subEquipment relative to the equipment designation (for example L1, if related to phase A)
            self.desc    = _desc    ##  A textual description of the subEquipment relative to the device
            self.phase   = _phase   ##  The phase to which the subEquipment belongs. The following phase values are allowed: A,
                                    ##  B, C, N (neutral), all (meaning all three phases), none (default, meaning not phase
                                    ##  related). The following additional values are only allowed, if the ConductingEquipment
                                    ##  above has type VTR: AB, BC, CA, meaning a VT connected in between the appropriate
                                    ##  phases.
            self.virtual = _virtual ##  Set to true, if the subEquipment (for example phase CT) does not exist in reality, but its
                                    ##  values are just calculated. Optional, default is false

        class Terminal:
            def __init__(self, _name, _desc, _conNode, _subName, _vName, _bayName, _cNodeName,_lineName, _neutralPoint):
                self.name            = _name        ## The optional relative name of the terminal at this Equipment. The default is the empty
                                                    ## string, which means that the name of the ConnectivityNode is also the terminal
                     				                ## identification.
                self.desc            = _desc        ## Descriptive text to the terminal
                self.connectivityNode=_conNode      ## The pathname of the connectivity node to which this terminal connects. If the Equipment##
                                                    ## shall not be connected, then the whole Terminal element shall be removed.
                self.substationName  = _subName     ## The name of the substation containing the connectivityNode
                self.voltageLevelName=  _vName      ## The name of the voltage level containing the connectivityNode
                self.bayName         = _bayName     ##         The name of the bay containing the connectivityNode
                self.cNodeName       = _cNodeName   ##         The (relative) name of the connectivityNode within its bay
                self.lineName        = _lineName      ### unclear !!
                self.neutralPoint    = _neutralPoint  ### unclear !!

            class ConnectivityNode:
                def __init__(self,_name, _desc, _pathName, _sx_y, _sx_x):
                    self.name     = _name
                    self.desc     = _desc
                    self.pathName = _pathName
                    self.sx_y     = _sx_y
                    self.sx_x     = _sx_x

    ##
    # GeneralEquipment can be used by Function, SubFunction et tEquipement container
    class GeneralEquipment:
        def __init__(self, _name, _type, _use):
            self.name    = _name
            self.type    = _type            ##  Example AXN, BAT, MOT, FAN, FIL, PMP, VLV
            self.use     = _use             ##

##
# \b Communication: create of the top-level of the data model for the communication section of the SCL
# @brief
# @b Description
#   The  class 'communication' is a table of subNetWork
class Communication:
    def __init__(self,_SubNetwork):
        self.tSubnetwork = _SubNetwork          # 2 sub-network

    ##
    # \b SubNetwork Define the communication architecture
    #
    # This class define the communication architecture at from the 'subNetWork' level.
    # Each SubNetwork will en composed of:
    #   - a Bit Rate description
    #   - a set of ConnectedAP
    class SubNetwork:   # <SubNetwork name="LAN"  type="8-MMS" desc="blabla...
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
            #  \b PhysConn connection parameters
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
                # \b PType 10BaseT, 100BaseT etc. for electrical connection FOC for optical connection Radio for radio connection, for example WLAN
                #
                # \b Plug \b RJ45 for electrical plug ST for bajonet plug (optical glass)
                #
                # \b Cable The identification of a physical cable for this connection, which connects this connection point to another connection point
                #
                # \b Port The identification of a port or terminal at this access point to which a cable is connected (see connection
                class PType:                                               # <Address>
                    def __init__(self, _type, _value):                     # 	<P type="MAC-Address">01-0C-CD-04-00-00</P>
                        self.type  = _type                                 # 	<P type="VLAN-ID">000</P>
                        self.value = _value                                # </Address>

##
# \b IED The description of a IED, actual device.
# @param name               The identification of the IED. Within an ICD file describing a device type, the name shall
#                           be TEMPLATE. The IED name shall not be an empty string and not None and shall be unique within an SCL file
#@param desc                The description text
#@param type                The (manufacturer specific) IED product type
#@param manufacturer        The manufacturer's name
#@param configVersion       The basic configuration version of this IED configuration
#@param originalSclVersion  The original SCL schema version of the IEDs ICD file; optional, default “2003”
#@param originalSclRevision The original SCL schema revision of the IEDs ICD file; optional, default “A”
#@param originalSclRelease  The original SCL schema release of the IEDs ICD file; optional, default ‘1’: Observe that
#                           2003A had no release at all
#@param engRight            The engineering right transferred by a SED file (only fix, dataflow), or the current state
#                           in an SCD file. Values are full, dataflow, fix, the default is full
#@param owner               The owner project of this IED, i.e. the Header id of that SCD file of that project which
#                           has the right to use the IED tool for this IED. The default is the Header id of the SCD file
#                           containing the IED
class IED:
    def __init__(self, _name, _desc, _type, _originalSclVersion, _originalSclRevision,
                       _configVersion, _manufacturer, _engRight, _owner):
        self.Server             = None
        self.name               = _name                 ## The identification of the IED, 'Template' in ICD, unique in SCD.
        self.desc               = _desc                 ## The description text
        self.type               = _type                 ## The (manufacturer specific) IED product type
        self.originalSclVersion = _originalSclVersion   ## The manufacturer's name
        self.originalSclRevision= _originalSclRevision  ## The basic configuration version of this IED configuration
        self.configVersion      = _configVersion        ## The original SCL schema version of the IEDs ICD file; optional, default “2003”
        self.manufacturer       = _manufacturer         ## The original SCL schema revision of the IEDs ICD file; optional, default “A”
        self.engRight           = _engRight             ## The original SCL schema release of the IEDs ICD file; optional, default ‘1’
        self.owner              = _owner                ## The owner project of this IED, i.e. the Header id of that SCD file of that project
        self.IP                 = None                  ## APP IP address from the communication
        self.tAddress           = []                    ## APP Table of MMS adresses
        self.tDAI               = []                    ## APP Table of actual DOI/..SDI../DAI/ values.
        self.tAccessPoint       = []                    ## APP Table of the Access-Point for this IED

    ##
    # \b AccessPoint List of network access point for a given IED (for example ADMIN versus DataModel)
    # @param name   Reference identifying this access point within the IED
    # @param desc   The description text
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
            # \b Authentication data required for authentication to this server
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
            # \b LDevice   a Logical Device, a set of functionally consistant Logical Node.
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
            # \b LN A Logical Node, a set data consistant to describe a technical 'topic".
            #
            # @param _localName(app)    LN0 or LN (according to IEC61850 standard, there should be two classes).
            # @param _prefix(iec)       The LN prefix part
            # @param _lntype(iec)       The instantiable type definition of this logical node, reference to a LNodeType definition
            # @param _inst(iec)         The LN instance number identifying this LN – an unsigned integer
            # @param _lnClass(iec)      The LN class according to IEC 61850-7-x
            # @param _desc(iec)         The description text for the logical node
            class LN:
                def __init__(self, _prefix, _lnType, _inst, _lnClass, _desc):   # Checked
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

                ##
                #
                # \b LogControl  a control block for Log objects
                #
                # @param name       name the name of the log control block
                # @param desc       A description text
                # @param datSet     The name of the data set whose values shall be logged; datSet should only be missing within an ICD-File, or for an unused control block.
                # @param intgPd     Integrity scan period in milliseconds – see IEC 61850-7-2.
                # @param ldInst     The identification of the LD where the log resides; if missing, the same LD where this control block is placed.
                # @param prefix     Prefix of LN where the log resides; if missing, empty string
                # @param lnClass    Class of the LN where the log resides; if missing, LLN0
                # @param lnInst     Instance number of LN, where the log resides; missing for LLN0
                # @param logName    Relative name of the log within its hosting LN; name of the log element
                # @param logEna     TRUE enables immediate logging; FALSE prohibits logging until enabled online
                # @param reasonCode If true, the reason code for the event trigger is also stored into the log – see IEC 61850-7-2

                class LogControl:
                    def __init__(self, _name, _desc, _datSet, _intgPd, _ldInst, _logName,_prefix,_lnClass,_lnInst, _logEna, _reasonCode):
                        self.name       = _name             ## name the name of the log control block
                        self.desc       = _desc             ## A description text
                        self.datSet     = _datSet           ## The name of the data set whose values shall be logged; datSet should only be
                        self.intgPd     = _intgPd           ## Integrity scan period in milliseconds – see IEC 61850-7-2.
                        self.ldInst     = _ldInst           ## The identification of the LD where the log resides; if missing, the same LD
                        self.prefix     = _prefix           ## Prefix of LN where the log resides; if missing, empty string
                        self.lnClass    = _lnClass          ## Class of the LN where the log resides; if missing, LLN0
                        self.lnInst     = _lnInst           ## Instance number of LN, where the log resides; missing for LLN0
                        self.logName    = _logName          ## Relative name of the log within its hosting LN; name of the log element
                        self.logEna     = _logEna           ## TRUE enables immediate logging; FALSE prohibits logging until enabled online
                        self.reasonCode = _reasonCode       ## If true, the reason code for the event trigger is also stored into the log –

                ##
                # \b ReportControl   Report Control Block
                #
                #
                # @param  name	    Name of the report control block. This name is relative to the LN hosting the RCB, and shall be unique within the LN
                # @param  desc	    The description text
                # @param  datSet	The name of the data set to be sent by the report control block; datSet should only be missing within an ICD-File, or to indicate an unused control block. The referenced data set must be in the same LN as the control block.
                # @param  intgPd	Integrity period in milliseconds – see IEC 61850-7-2. Only relevant if trigger option period is set to true
                # @param  rptID	Identifier for the report control block, optional; if not used, its value shall be set to NULL (see IEC 61850-7-2)
                # @param  confRev	The configuration revision number of this report control block. The value 0 is only allowed for a control block without data set reference. A reset by the system configurator is not allowed.
                # @param  buffered	Specifies if reports are buffered or not – see IEC 61850-7-2; default: false
                # @param  bufTime	Buffer time – see IEC 61850-7-2; default: 0
                # @param  indexed	If true, the report control block instance names are built from the supplied name, followed by an index number from 01 up to maximum 99. Default: true. The value false is not allowed for SCT created instances.

                class ReportControl:
                    def __init__(self, _name,_desc,_datSet,_intgPd, _rptID,_confRev,_buffered,_bufTime,_indexed): # Checked
                        self.name      = _name              ##  name	    Name of the report control block.
                        self.desc      = _desc              ##  desc	    The description text
                        self.dataset   = _datSet            ##  datSet	    The name of the data set to be sent by the report control block
                        self.intgPd    = _intgPd            ##  intgPd	    Integrity period in milliseconds – see IEC 61850-7-2. Only relev
                        self.rptID     = _rptID             ##  rptID	    Identifier for the report control block, optional.
                        self.confRev   = _confRev           ##  confRev	    The configuration revision number of this report control block.
                        self.buffered  = _buffered          ##  buffered	Specifies if reports are buffered or not – see IEC 61850-7-2; de
                        self.bufTime   = _bufTime           ##  bufTime	    Buffer time – see IEC 61850-7-2; default: 0
                        self.indexed   = _indexed           ##  indexed	    If true, the report control block instance names are built from supplied name, followed by an index number from 01 up to maximum 99.
                        self.TrgOps    = None

                    ##
                    # \b OptFields Optional data for Report
                    #
                    class OptFields:
                        def __init__(self,_seqNum,_timeStamp,_dataSet,_reasonCode,_dataRef,_entryID,_configRef,_bufOvfl):
                            self.seqNum     = _seqNum
                            self.timeStamp  = _timeStamp
                            self.dataSet    = _dataSet
                            self.reasonCode = _reasonCode
                            self.dataRef    = _dataRef
                            self.entryID    = _entryID
                            self.configRef  = _configRef
                            self.bufOvfl    = _bufOvfl

                    ##
                    # \b RptEnabled Enabling report
                    #
                    # @param max    The maximum number of client
                    #
                    class RptEnabled:
                        def __init__(self, _max):
                            self.max = _max                 ## the maximum possilbe number of Report.
                            self.tClientLN = []

                        ##
                        # \b ClientLN
                        #
                        # @param iedName    The name of the IED where the LN resides
                        # @param ldInst     The instance identification of the LD where the LN resides
                        # @param prefix     The LN prefix
                        # @param lnClass    The LN class according to IEC 61850-7-4
                        # @param lnInst     The instance id of this LN instance of below LN class in the IED
                        # @param desc       optional descriptive text, e.g. about purpose of the client
                        # @param apRef      Application reference

                        class ClientLN:
                                def __init__(self, _iedName, _ldInst, _lnPrefix, _lnClass, _lnInst, _desc, _apRef):
                                    self.iedName   = _iedName   ## The name of the IED where the LN resides
                                    self.ldInst    = _ldInst    ## The instance identification of the LD where the LN resides
                                    self.lnPrefix  = _lnPrefix  ## The LN prefix
                                    self.lnClass   = _lnClass   ## The LN class according to IEC 61850-7-4
                                    self.lnInst    = _lnInst    ## The instance id of this LN instance of below LN class in the IED
                                    self.desc      = _desc      ## optional descriptive text, e.g. about purpose of the client
                                    self.apRef     = _apRef     ## Application reference

                ##
                # \b TrgOps a class is common to RCB and LogControl to define the condition used to get a report.
                # @param _qchg      new transmission of Goose or Report for a change on quality
                # @param _dchg      new transmission of Goose or Report for a change on data
                # @param _dupd      new transmission of Goose or Report for a change on data update
                # @param _period    transmission is periodical (report)
                # @param _gi        transmission triggered by a general interroagation request

                class TrgOps:
                    def __init__(self,_qchg, _dchg, _dupd, _period, _gi ):
                        self.dchg  = _qchg      ##  qchg      new transmission of Goose or Report for a change on quality
                        self.qchg  = _dchg      ##  dchg      new transmission of Goose or Report for a change on data
                        self.dupd  = _dupd      ##  dupd      new transmission of Goose or Report for a change on data update
                        self.period= _period    ##  period    transmission is periodical (report)
                        self.gi    = _gi        ##  gi        transmission triggered by a general interroagation request

                ##
                # \b Inputs  the list of the input data for a given Logical device
                #
                #  @param _tRef a table of external reference
                class Inputs:
                    def __init__(self, _tRef):
                        self.tExtRef = _tRef
                    ##
                    # \b ExtRef a IEC61850 data path to an external data point.
                    #
                    #  @param _iedName    The name of the IED from where the input comes. For IED internal references the value @ may be used.
                    #  @param _ldInst     The LD instance name from where the input comes
                    #  @param _prefix     The LN prefix
                    #  @param _lnClass    The LN class according to IEC 61850-7-x. Used to indicate the lnClass of the concrete binding part within a SCD.
                    #  @param _lnInst     The instance id of this LN instance of above LN class in the IED; missing for a reference in LLN0.
                    #                     For backwards compatibility also the empty string shall be accepted for LLN0
                    #  @param _doName     A name identifying the DO (within the LN).In case of structured DO, the name
                    #                     parts are concatenated by dots (.).Used to indicate the DO (within the LN)
                    #                     of the concrete binding part within a SCD.
                    #  @param _daName     The attribute designating the input. The IED tool should use an empty value if it has some
                    #                     default binding (intAddr) for all process input attributes of a DO (fc = ST or MX), especially for t and q.
                    #                      If the attribute belongs to a data type structure, then the structure name parts shall be separated by dots (.)
                    #  @param _intAddr    The internal address to which the input is bound. Only the IED tool of the concerned IED
                    #                     shall use the value. All other tools shall preserve it unchanged
                    #  @param _desc       A free description / text. Can e.g. be used at system engineering time to
                    #                     tell the IED engineer the purpose of this incoming data
                    #  @param _service    SubNetWork Optional, values: Poll, Report, GOOSE, SMV, Used to indicate the used service if the data flow is configured.
                    #
                    #  @param _srcLDInst  The LD inst of the source control block – if missing, same as ldInst above
                    #  @param _srcPrefix  The prefix of the LN instance, where the source control block resides; if missing, no prefix
                    #  @param _srcLNClass The LN class of the LN, where the source control block resides; if missing, LLN0
                    #  @param _srcLNInst  The LN instance number of the LN where the source control block resides – if missing, no instance number exists (LLN0)
                    #  @param _srcCBName  The source CB name; if missing, then all othere srcXX attributes should also be missing, i.e. no source control block is given.
                    #
                    #  @param _pDO        A preconfigured DO name to indicate an expected DO name and CDC. Any binding must match the CDC.
                    #  @param _pLN        A preconfigured LN class indicating an expected LN class containing the DO indicated by pDO
                    #  @param _pDA        Aa preconfigured data attribute indicating the expected attribute. If configured, any bound
                    #                     attribute must match the data type specified by specified pDO CDC and pDA attribute value
                    #  @param _pServT     A preconfigured service type indicating an expected service type. if configured, serviceType must match its value.


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

                ##
                # \b SampledValueControl  A control block for Sample Values
                #
                # @param name	    A name identifying this SMV control block
                # @param desc	    The description text
                # @param datSet	    The name of the data set whose values shall be sent; datSet should only be missing within an ICD-File, or to indicate an unused control block. A referenced data set must reside in LLN0.
                # @param confRev	The configuration revision number of this control block; mandatory. It is recommended to increment it by 10000 on any configuration change, to distinguish this from online configuration changes leading to an increment of 1 only
                # @param smvID	    Multicast CB: the MsvID for the sampled value definition as defined in IEC 61850-7-2
                #                   Unicast    CB: the UsvID as defined in  IEC 61850-7-2
                # @param multicast	false indicates Unicast SMV services only meaning that smvID = UsvID
                # @param smpRate	Sample rate as defined in IEC 61850-7-2. If no smpMod is defined, in samples per period, else as stated by smpMod.
                # @param nofASDU	Number of ASDU (Application service data unit) – see IEC 61850-9-2
                # @param smpMod     	The sampling mode as defined in IEC 61850-7-2; default: SmpPerPeriod; if supported by the IED, also SmpPerSec and SecPerSample can be choosen. In these cases smpRate defines the appropriate sample number per second, or seconds between samples.
                # @param securityEnabled Default: None. Allows to configure the security options per control block instance: Signature or SignatureAndEncryption. Only those indicated by the McSecurity element of the SMVSetting are allowed

                class SampledValueControl:
                    def __init__(self, _name, _desc, _datSet, _confRev, _smvID, _multicast, _smpRate, _nofASDU,  _smpMod, _securityEnabled): # checked
                        self.name     = _name                     # @param name	    A name identifying this SMV control block
                        self.desc     = _desc                     # @param desc	    The description text
                        self.datSet   = _datSet                   # @param datSet   The name of the data set whose values shall be sent.
                        self.confRev  = _confRev                  # @param confRev	The configuration revision number of this control block; mandatory.
                        self.smvID    = _smvID                    # @param smvID	 Multicast CB: the MsvID for the sampled value definition as defined (Unicast: deprecated)
                        self.multicast=_multicast                 # @param multicast Indicates Unicast SMV services only meaning that smvID = UsvI
                        self.smpRate  = _smpRate                  # @param smpRate	Sample rate as defined in IEC 61850-7-2. If no smpMod is defined, i
                        self.nofASDU  = _nofASDU                  # @param nofASDU	Number of ASDU (Application service data unit) – see IEC 61850-9-2
                        self.smpMod   = _smpMod                   # @param smpMod	The sampling mode as defined in IEC 61850-7-2; default: SmpPerPeriod; i
                        self.securityEnabled = _securityEnabled   # @param securityEnabled Default: None. Allows to configure the security options per control block instance

                    ##
                    # \b smvOption  Sample Values options
                    #
                    #  @param refreshTime       The meaning of the options is described in IEC 61850-7-2.
                    #  @param sampleRate        If any of the attributes is set to true, the appropriate values shall be included into the SMV telegram
                    #  @param dataSet           If the attribute is set to true, the dataset name shall be included into the SMV telegram
                    #  @param security          See IEC61850-9-2...
                    #  @param synchSourceId     if true, the SV message contains the identity of the synchronizing master clock according to IEC 61850-9-3; default = false

                    class smvOption:    # todo not parsed !!!! 
                        def __init__(self, _refreshTime, _sampleRate, _dataSet, _security, _synchSourceId):
                            self.refreshTime   = _refreshTime    ## The meaning of the options is described in IEC 61850-7-2.
                            self.sampleRate    = _sampleRate     ## If any of the attributes is set to true, the appropriate values shall be included into the SMV telegram
                            self.dataSet       = _dataSet        ## If the attribute is set to true, the dataset name shall be included into the SMV telegram
                            self.security      = _security       ## See IEC61850-9-2...
                            self.synchSourceId = _synchSourceId  ## if true, the SV message contains the identity of the synchronizing master clock according to IEC 61850-9-3; default = false

                ##
                # \b SettingControlBlock    A control block for Settings
                #
                # @param desc	    The description text
                # @param numOfSGs   The number of setting groups available. The value shall be > 0.
                # @param actSG      The number of the setting group to be activated when loading the configuration. The default value is 1. Any SCL value shall be > 0.
                # @param resvTms    The time in seconds the SGCB stays reserved for editing. After this time the IED automatically closes an edit session, if the client has not closed it or not confirmed any changes (see IEC 61850-7-2). If this function is not supported, the attribute shall be missing. The appropriate IED capability (Table 11) defines if a system tool can modify any value supplied by the IED tool.

                class SettingControlBlock:
                    def __init__(self, _desc, _numOfSGs, _actSG, _resvTms):         # Checked
                        self.desc      = _desc          ## The description text
                        self.numOfSGs  = _numOfSGs      ## The number of setting groups available. The value shall be > 0.
                        self.actSG     = _actSG         ## The number of the setting group to be activated when loading the configuration.
                        self.resvTms   = _resvTms       ## The time in seconds the SGCB stays reserved for editing.

                ##
                # \b GSEControl      A control bloc to control GOOSE exchanges
                #
                # @param name	    The name identifying this GOOSE control block
                # @param desc	    A description text
                # @param datSet	    The name of the data set to be sent by the GSE control block. For type=GSSE,
                #                   the FCDA definitions in this data set shall be interpreted as DataLabels according
                #                   to IEC 61850-7-2. The attribute datSet should only be missing within an ICD-File,
                #                   or to indicate an unused control block. It resides in LLN0 like the control block
                # @param confRev	The configuration revision number of this control block. It is recommended to
                #                   increment this by 10 000 on each configuration change, to distinguish this from
                #                   online changes leading to an increment of 1 only
                # @param type	    If the type is GSSE (deprecated), then only single indication and double indication
                #                   data types are allowed for the data items referenced in the data set, otherwise
                #                   all data types are allowed. Note that on stack level, each type might be mapped
                #                   differently to message formats. The default type value is GOOSE
                # @param appID	    A system wide unique identification of the application to which the GOOSE message belongs
                # @param fixedOffs	        Default value false. If set to true it shows all receivers, that the values
                #                           within the GOOSE message have fixed offset in the GOOSE message until a
                #                           reconfiguration. This might mean for an MMS mapping that e.g. for integer
                #                           values always the maximum size is used, although ASN.1 would allow a shorter coding.
                # @param securityEnabled	Default: None. Allows to configure the security options per control block instance:
                #                           Signature or SignatureAndEncryption. Only those indicated by the McSecurity element
                #                           of the GSESetting are allowed.

                class GSEControl:
                    def __init__(self,_name,_desc,_datSet,_confRev,_type,_appID,_fixedOffs,_securityEnabled):
                        self.name           =_name                  ## The name identifying this GOOSE control block
                        self.desc           = _desc                 ## A description text
                        self.datSet         =_datSet                ## The name of the data set to be sent by the GSE control block.
                        self.confRev        =_confRev               ## The configuration revision number of this control block.
                        self.type           =_type                  ## The default type value is GOOSE (GSSE is deprecated)
                        self.appID          =_appID                 ## A system wide unique identification of the application to which the GOOSE message belong
                        self.fixedOffs      =_fixedOffs             ## Default value false. If set to true it shows all receivers, that the values GOOSE message have fixed offset in the GOOSE message.
                        self.securityEnabled = _securityEnabled     ## Default: None. Allows to configure the security options per control block instance.

                ##
                # \b DOI  A data object instance, allow to defined values at DO Level
                #
                # @param desc	    A description text
                # @param name	    A standardized DO name for example from IEC 61850-7-4. It is the root name part as defined
                #                   in the LNodeType definition. Its value must be unique at this level, i.e. there shall be
                #                   at maximum one DOI element for the same data object.
                # ix                Index of a data element in case of an array type; shall not be used if DOI has no array type
                # accessControl     Access control definition for this data. The empty string (default) means that the higher-level
                #                   access control definition applies. Possible values are SCSM dependent
                class DOI:
                    def __init__(self, _desc, _name, _ix, _accessControl):              #todo _ix Not Managed
                        self.desc       = _desc         ## A description text
                        self.name       = _name         ## A standardized DO name for example from IEC 61850-7-4
                        self.ix         = _ix           ## Index of a data element in case of an array type
                        self.accessControl = _accessControl ## Access control definition for this data. The empty string (default) means that the higher-level.

                    ##
                    # \b DAI A data attribute instance, allow to defined values at DA Level
                    #
                    # @param desc(iec)      The description text for the DAI element
                    # @param name(iec)	    The name of the Data attribute whose value is given. It is the last name part in a structured attribute name.
                    # @param sAddr(iec)	    Short address of this Data attribute
                    # @param valKind(iec)	The meaning of the value from the engineering phases. If missing, the valKind from the type definition applies for any attached value.
                    # @param ix(iec)	    Index of the DAI element in case of an array type
                    # @param valImport(iec)	if true, an IED / IED configurator can import values modified by another tool, even if valKind=RO or valKind=Conf; the default value is defined in the DatatypeTemplate section. It is the responsibility of the IED configurator to assure value consistency and value allowance even if valImport is true.
                    # @param value(APP)     implementation artefact, the declared value (if present) is stored here
                    class DAI:
                        def __init__(self, _desc, _name, _sAddr, _valKind,  _ix, _valImport, _value): #todo _ix Not Managed
                            self.desc      = _desc          ## desc	        The description text for the DAI element
                            self.name      = _name          ## name	        The name of the Data attribute whose value is given.
                            self.sAddr     = _sAddr         ## sAddr	    Short address of this Data attribute
                            self.valKind   = _valKind       ## valKind	    The meaning of the value from the engineering phases. If missing, the va
                            self.ix        = _ix            ## ix	        Index of the DAI element in case of an array type
                            self.valImport = _valImport     ## valImport	if true, an IED / IED configurator can import values modified by another
                            self.value     = _value         ## value        implementation artefact, the declared value is stored here.

                        ##
                        # \b SDI A Sub Data attribute instance, allow to defined values at Sub Data Level
                        #
                        # @param desc(iec)      The description text for the DAI element
                        # @param name(iec)	    The name of the Data attribute whose value is given. It is the last name part in a structured attribute name.
                        # @param ix(iec)	    Index of the DAI element in case of an array type
                        # @param sAddr(iec)	    Short address of this Data attribute

                        class SDI:  # Utilisé notamment pour les Contrôles complexes
                            def __init__(self, _desc, _name, _ix,_sAddr ):  # , _tSDI):
                                self.desc  = _desc          ## desc	        The description text for the DAI element
                                self.name  = _name          ## name	        The name of the Data attribute whose value is given.
                                self.ix    = _ix            ## ix	        Index of the DAI element in case of an array type
                                self.sAddr = _sAddr         ## sAddr	    Short address of this Data attribute

                    ##
                    # \b IEC_90_2  for IEC61850-90-2 communication (substation to substation communication)
                    #
                    # @param _externalScl : define SCL for the other part of the link
                    # @param _iedName     : name of the IED
                    # @param _ldInst      : identification of the logical device
                    # @param _prefix      : LN prefix
                    # @param _lnClass     : LN class
                    # @param _lnInst      : LN instance
                    # @param _doName      : Data Object to read (?)

                    class IEC_90_2:             # Private defined by WG10 eTr, technical report for 90-2 communication
                        def __init__(self,_externalScl,_iedName, _ldInst, _prefix,_lnClass,_lnInst,_doName):
                            self.externalScl = _externalScl  ## define SCL for the other part of the link
                            self.iedName     = _iedName      ## name of the IED
                            self.ldInst      = _ldInst       ## identification of the logical device
                            self.prefix      = _prefix       ## LN prefix
                            self.lnClass     = _lnClass      ## LN class
                            self.lnInst      = _lnInst       ## LN instance
                            self.doName      = _doName       ## Data Object to read (?)
                            
                    class IEC104:              # Private define by WG10 TR 90-2 IEC60870-104 SCADA communication
                        def __init__(self,_casdu,_ioa,_ti,_usedBy,_inverted):
                            self.casdu    = _casdu
                            self.ioa      = _ioa
                            self.ti       = _ti
                            self.usedBy   = _usedBy
                            self.inverted = _inverted

                ##
                # \b DataSet create a set of data for communication via GOOSE or Report
                #
                # @param name	    The name of the data set, ACSI string of 32 character.
                # @param desc	    A description text

                class DataSet:
                    def __init__(self, _name, _desc):
                        self.name  = _name       ##  name   The name of the data set, ACSI string of 32 character
                        self.desc  = _desc       ##  desc   A description text
                        self.tFCDA = []

                    ##
                    # \b FCDA   the list of data objet and attributes that constitutes a Data Set
                    #
                    # @param ldInst	    The LD where the DO resides; shall always be specified except for GSSE
                    # @param prefix	    Prefix identifying together with lnInst and lnClass the LN where the DO resides;
                    #                   optional, default value is the empty string
                    # @param lnClass	LN class of the LN where the DO resides; shall always be specified except for GSSE DataLabel empty string
                    # @param lnInst	    Instance number of the LN where the DO resides; shall be specified except for LLN0
                    # @param doName	    A name identifying the DO (within the LN). A name standardized in IEC 61850-7-4.
                    #                   The doName attribute is optional only if the data set is assigned to a GSSE control block.
                    #                   For elements or parts of structured data object types, all name parts are contained, separated by dots (.),
                    #                   down to (but without) the level where the fc is defined. If an SDO array element is selected,
                    #                   the appropriate name part shall contain at its end before a possible dot the array element number
                    #                   in the form (ArrayElementNumber).
                    # @param daName	    The attribute name – if missing, all attributes with functional characteristic given by fc are selected.
                    #                   For elements or parts of structured data types, all name parts are contained, separated by dots (.),
                    #                   starting at the level where the fc is defined. If an attribute’s array element is selected,
                    #                   the appropriate attribute name part shall contain at its end before any separating dot the array element
                    #                   number in the form (ArrayElementNumber).
                    # @param fc	        All attributes of this functional constraint are selected.
                    #                   Possible constraint values see IEC 61850-7-2 or the fc definition in 9.5
                    # @param ix	        An index to select an array element in case that one of the data elements is an array.
                    #                   The ix value shall be identical to the ArrayElementNumber value in the doName or daName part.
                    class FCDA:
                        def __init__(self,_ldInst,_prefix,_lnClass,_lnInst,_doName,_daName,_fc,_ix):    # Checked
                            self.ldInst  = _ldInst      ## The LD where the DO resides
                            self.prefix  = _prefix      ## Prefix identifying together with lnInst and lnClass the LN where the DO resides
                            self.lnClass = _lnClass     ## LN class of the LN where the DO resides;
                            self.lnInst  = _lnInst      ## Instance number of the LN where the DO resides
                            self.doName  = _doName      ## A name identifying the DO (within the LN). A name standardized in IEC 61850-7-4.
                            self.daName  = _daName      ## The attribute name – if missing, all attributes with functional characteristic given by fc are selected
                            self.fc      = _fc          ## All attributes of this functional constraint are selected. See IEC 61850-7-2 or the fc definition in 9.5
                            self.ix      = _ix          ## An index to select an array element in case that one of the data elements is an array.
##
#  \b DataTypeTemplates   Describe all the data type used in IEC61850 datamodel
#
#  The normalised classes of DataTypeTemplace are:
#   - LNODEType
#   - DOType
#   - DAType
#   - EnumType.
#
# However, this class also embed useful classes: FC, bType, Quality, TimeQuality, Timestamp, PhyComAddr, TriggerConditions, GooseMessge
#
class DataTypeTemplates:

    ##
    #  FC          : The set of standardized functional class
    class FC:
            lstFC = ['ST', 'MX', 'CF', 'DC', 'SP', 'SV', 'SG', 'SE', 'SR', 'OR', 'BL', 'EX', 'CO']

    ##
    # \b bType The complete list of basic type (without Enum nor Struct for application purpose)
    #
    #   bType  : The actualised list of basic types. Due to implementation issues, 'Enum' and 'Struct' are not in this list.
    #   String : A subset of bType for all String type
    #   Number : A subset of bType for all kind of numbers.
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
#                  "AnalogueValueCtlF",
                  "Octet6", "Octet16"          # Edition 2.1
                  ]

        String  = ["BOOLEAN","VisString64","VisString129","VisString255","Unicode255",
                   "ObjRef", "Quality", "Timestamp","Tcmd"]     # TODO String or Number ?

        Number =  ["Check",
                   "INT8U","INT16U","INT32U","INT8","INT16","INT32","INT64",
                   "FLOAT32","Octet64"]
    ##
    #   Quality     : The detailed quality bits
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
    ##
    #   TimeQuality : The detailed quality bits for time
    class TimeQuality:
        def _init__ (self,_Leap, _Failure_,_NotSync, _Precision):
            self.LeapSecond     = _Leap          # Boolean
            self.ClockFailure   = _Failure_      # Boolean
            self.NotSync        = _NotSync       # Boolean
            self.Precision      = _Precision     # INT 5 bits Number of significant bits
                                                 # in the FractionOfSecond:
    ##
    #   Timestamp   : The time stamp structure
    class Timestamp:
        def __init__(self,_SecondSinceEpoch,_FractionOfSecond,_TimeQuality):
            self.second   = _SecondSinceEpoch   # Since 01/01/1970 -UTC
            self.fraction = _FractionOfSecond   #NOTE 1 The resolution is the smallest unit by
                                                # which the time stamp is updated (potentially ~60ns)
            self.quality  = _TimeQuality
    ##
    #  PhyComAddr  : This Physical communication address.
    #  WARNING d'après IEC61850-8-1, le 'EntryTime' des BRCB est exprimé en S depuis 01/01/1984
    class PhyComAddr:
        def __init__(self, _Addr, _PRIORITY, _VID, _APPID):     # Défini dans IEC61850-1-2
            self.Addr       = _Addr         #Octet String 6         ==> [Adr Mac] bytes en python
            self.PRIORITY   = _PRIORITY     #Unsigned8 de 0 à7      ==> int en python
            self.VID        = _VID          #Unsigned16 de 0 à 4095 ==> int en python
            self.APPID      = _APPID        #Unsigned16             ==> int en python

    ##
    # TriggerConditions: this class is used for GOOSE and Report
    #
    class TriggerConditions:                # 6 bits IEC61850-8-1 § 8.1.3.9
        def __init_(self, _reserved, _dChg,_qChg,_dUpdate,_IntPeriod,_GI):
            self.reserved  = _reserved      # N/A
            self.dChg      = _dChg          # Boolean
            self.qChg      = _qChg          # Boolean
            self.dUpdate   = _dUpdate       # Boolean
            self.IntPeriod = _IntPeriod     # Boolean
            self.GI        = _GI            # Boolean

    ##
    # \b GooseMessage: the list of the properties/attributes of a GOOSE message
    #
    # @param DatSetRef    # ObjectRefernce    (String129, value from GOCB)
    # @param GoID         # VisibleString     (String129, value from GOCB)
    # @param GoCBRef      # ObjectRefernce    (String129, value from GOCB)
    # @param T            # TimeStamp (if 0 the driver will the time
    # @param StNum        # INT32U
    # @param SqNum        # INT32U
    # @param Simulation   # Boolean (True : simulation active)
    # @param ConfRev      # INT32U  (value from GOCB)
    # @param NdsComn      # BOOLEAN  value from GOCB)
    # @param DatSet       # Data à encoder et à envoyer
    # @param mode          # Envoi d'une seule trame ou d'un flux.

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
    # \b LNodeType: the type definition for a LNODE
    #
    # @param _id(iec)           # A reference identifying this LN type within this SCL section;
    # @param _desc(iec)         # An additional text describing this LN type
    # @param _iedType(iec)      #  The manufacturer IED type of the IED to which this LN type belongs - deprecated
    # @param _lnClass(iec)      # The LN base class of this type as specified in IEC 61850-7-x
    # @param _tDO(APP)          # Table of the DO element (application usage)

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
        #  DOI element of a LNodeType
        #
        #   @param  name(iec)            # The data object name as specified for example in IEC 61850-7-4
        #   @param  type(iec)            # The type references the id of a DOType definition
        #   @param  accessControl(iec)   # Access control definition for this DO. If it is missing, then any higher-level access control definition applies
        #   @param  transient(iec)       # If set to true, it indicates that the Transient definition from IEC 61850-7-4 applies
        #   @param  desc(iec)            # Descriptive text for the DO element
        class DOI:
            def __init__(self, _name, _type, _accessControl, _transient, _desc, ):
                self.name           = _name             # The data object name as specified for example in IEC 61850-7-4
                self.type           = _type             # The type references the id of a DOType definition
                self.accessControl  = _accessControl    # Access control definition for this DO. If it is missing, then any higher-level access control definition applies
                self.transient      = _transient        # If set to true, it indicates that the Transient definition from IEC 61850-7-4 applies
                self.desc           = _desc             # Descriptive text for the DO element

    ##
    # \b DOType An instantiable data object type; referenced from LNodeType or from the
    # SDO element of another DOType. Instantiable version based on the CDC definitions from IEC 61850-7-3
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
        #  \b DAI  A data attribute instance, with the possibility to define a value
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

        class DAI:
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
    ##
    # \b DAType the definition of a Data Attribute type.
    #
    # An instantiable structured attribute type; referenced from within a DA element of a DOType,
    # or from within another DAType for nested type definitions. Based on the attribute structure definitions of IEC 61850-7-3
    #
    # @param _id        Data Type id, unique a the the SCL
    # @param _desc      Description text
    # @param _protNS    protNS
    # @param _iedType   iedType
    class DAType:
        def __init__(self, _id, _desc, _protNs, _iedType):
            self.id         = _id  # id du type
            self.desc       = _desc  # description
            self.protNs     = _protNs  # NameSpace
            self.iedType    = _iedType  # iedType
            self.tBDA = []  # Table of the BDA related to this DA.

        ##
        # \b BDA Sub-classe to handle BDA instanciations.
        #
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

        ##
        # \b ProtNs Protected name space
        #
        # The properties of the class are the attroibutes of IEC61850 DA Object.
        class ProtNs:
            def __init__(self, _type):
                self.type = _type

    ##
    # \b EnumType An instance of an enumeration data type
    #
    # @param _id     unique id (SCL scope) of the type
    # @param _desc   Text description of the EnumType
    #
    class EnumType:
        def __init__(self, _id, _desc):
            self.id       = _id         # id du type
            self.desc     = _desc       # Description of the EnumType
            self.tEnumval = []          # Table of the possible value / name for the EnumType
            self.min      = 0           # Not part of IEC61850, added in order to verify that
            self.max      = 0           # values are in the correct range from min to max (included)

        ##
        # \b EnumVal: child class to handle the list 'EnumVal BDA' associated to a EnumType
        # @param _ord        Actual numerical value used
        # @param _strValue   String used to state the value
        # @param _desc       Description text
        #
        class EnumVal:
            def __init__(self, _ord, _strValue, _desc):
                self.ord      = _ord        # Actual numerical value used
                self.strValue = _strValue   # String used to state the value
                self.desc     = _desc
