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
import time
from IEC_FileListe import FileListe as FL

from IEC_LNodeType          import Parse_LNodeType
from IEC_DOType             import Parse_DOType
from IEC_DAType             import Parse_DAType
from IEC_EnumType           import Parse_EnumType
from IEC_Services           import Test_Services
from IEC_Communication      import ParseCommunication
from IEC_IED_Server         import Parse_Server

from IEC_Trace              import Trace   as TConsole
from IEC_Trace              import Level   as TL
from IEC_TypeSimpleCheck    import Check

from IEC61850_XML_Class     import  DataTypeTemplates as IecType


##
# \b IECda: handle a single final data attribute
#
#   This class is used to store information about a DA with its value adn MMS adress
#   The constructor is mainly building the MMS Adress of the DA, so that it can be
#   used by ACSI services. In particular, it placing the FC at the appropriate place.
#
#
#   @param  Texte -     only for debugging purpose, it precises the type of data..
#   @param  _mmAdr      the MMS address as built by BrowseTypeSimple
#   @param  _fc         the FC of the data point
#   @param  _BasicType  the IEC basicType as defined in DataTypeTemplates.bType
#                       (excluding Enum and Struct which need some specific treatment).
#   @param  _EnumpType  in case on Enum, the enum type (will be used to check Enum range)
#   @param  _Value      The expected value of the data point (from the type definition or from DAi)
#   @param  _Valkind    The 'valKind' associated to the DA.
#
class IECda:
    def __init__(self, Texte, _mmsAdr, _fc, _BasicType, _EnumType, _Value, _Valkind):
        self.mmsAdr       = _mmsAdr         ## Adress down to the IEC bType or Struct.
        self.fc           = _fc             ## Functional Constrain
        self.BasicType    = _BasicType      ## 'bType' see IEC61850_XML_Class (enum and struct are not treated as bType)
        self.EnumType     = _EnumType       ## EnumType
        self.TypeValue    = _Value          ## Value    from  DATA TYPE DEFINITION
        self.ValKind      = _Valkind        ## ValKlind from  DATA TYPE DEFINITION
        self.mmsAdrFinal  = 'xx'
        self.acsiAdr      = 'zz'            ## Adress ready for ACSI services
        self.ValAdr       =  ''             ## Path the ValAdr (when DAI/SDI aws used)

        if _Value == '__None__':
            self.TypeValue = None

        FC='xx'
        mmsAdrSplit = _mmsAdr.split('$')
        posFC = -1                          # Position of functional Constraint
        # La FC (Functional Constraint, n'est pas à la bonne place :
        for i in range(2, len(mmsAdrSplit)):  # La FC est au moins en position
            if mmsAdrSplit[i] in IecType.FC.lstFC:
                FC = mmsAdrSplit[i]
                posFC = i                     # Position de la FC
                break

        _newMmsAdr = ''
        for i in range(0, len(mmsAdrSplit)):
            if (i <= 1):  # Pösition de placement de la FC
                _newMmsAdr = _newMmsAdr  + mmsAdrSplit[i]
                if i == 1:
                    self.ValAdr = self.ValAdr + '_' + mmsAdrSplit[i] + '_'
                continue
            if (i == 2):  # Pösition de placement de la FC
                _newMmsAdr = _newMmsAdr  + '/' + mmsAdrSplit[i]
                self.ValAdr = self.ValAdr + '.' + mmsAdrSplit[i]
                continue
            if (i != posFC):
                _newMmsAdr = _newMmsAdr + '.' + mmsAdrSplit[i]
                self.ValAdr = self.ValAdr + '.' + mmsAdrSplit[i]

        if _BasicType == "Quality" or _BasicType == "Timestamp":
            self.ValAdr = None
#        else:
#            self.ValAdr = self.ValAdr+'['+FC+']'
#            print("Adresse à vérifier:", self.ValAdr) # Reading the internal data tree, FC is not needed

        _newMmsAdr = _newMmsAdr +'['+FC+']'
        self.mmsAdrFinal = _newMmsAdr

        if _BasicType in IecType.bType.Simple:
            iecType = _BasicType
        else:
            if _EnumType is not None:
                iecType = "Enum: "+_EnumType
            else:
                print("#######################")        # TODO replace by a TRACE with TL.ERROR level.
"""
        txtValKind =  self.ValKind
        if txtValKind is None:
            txtValKind = ''
        txtValue = self.TypeValue
        if txtValue is None:
            txtValue = ''
        print( Texte + 'MMS:' + self.mmsAdrFinal + ','+  iecType + ', Value:'+ txtValue+ ', VK:'+ txtValKind)
"""
##
#
# \b globalDataModel Collect all Data Type Templates (LnodeType, DoType, Datype, EnumType)
#
# Function Hierachy
#   - LoadSCLModel              - Invoke all class/Method to build the full DataModel
#       - getIED_withComm       - Browse IED and AccessPoint, get the IP from communication part and store it in the AccessPoint Class
#   - BrowseDataModel           - for a IED instance, browse all AccessPoint and Logical Device
#       - BrowseDataModel_LD    - for a Logical Device instance, browse all LN and their DO
#           - BrowseDA          - for a given DO, SDO, BDA, browse the DA
#           - BrowseTypeSimple  - for a given DA if a type is 'final' build the MMS adresses, otherwise recusively call BrowseDA
#   - TraceDataPoint            - For debugging purpose, print the details of a given data point
#   - GetIPAddress              - Search the IP adresse of a given IED/AccessPoint
#
# @param    _TR     _TR instance of the trace system
# @param    file    SCL file to use (SCD, IID, ICD, ...)

class globalDataModel:
    def __init__(self, _TR,  file, _SCL):
        self.TR   = _TR                 ##_TR instance of the trace system
        self.tIED = []

        self.scl = self.LoadSCLModel(file, _SCL)


        DataType      = self.scl.getElementsByTagName("DataTypeTemplates")

        self.LNode = Parse_LNodeType(self.scl,self.TR)          # class init
        self.LNode.Create_LNodeType_Dict(DataType)    # Create the 'dictionary' of LNODE

        self.DOType    = Parse_DOType(self.scl, self.TR)        # class init
        self.DOType.Create_DOType_Dict(DataType)     # Create the 'dictionary' of DoType

        self.DAType    = Parse_DAType(self.scl, self.TR)
        self.DAType.Create_DAType_Dict(DataType)

        self.EnumType   = Parse_EnumType(self.scl , self.TR)
        self.EnumType.Create_EnumType_Dict(DataType)
        ##
        # \b LoadSCLModel
        #
        # Load the SCL file and parse the communication structure
        #
        #   @param file the SCL file name, without the directory.
        #

    def LoadSCLModel(self, fileName, _SCL):
        t0 = time.time()
        if _SCL is None:
            _SCL = dom.parse(fileName)
        t1 = time.time()
        deltaT = t1 - t0
        print("Time to load the SCL file: " + fileName + ':' + str(deltaT))  # TODO use Trace !

        self.tIED = self.getIED_withComm(_SCL)  # Expect a file list

        comm = _SCL.getElementsByTagName("Communication")
        subNetWork = ParseCommunication(comm, self.TR)
        tNetWork = subNetWork.ParseCommSection(comm)  # <SubNetWork>
        tServices = Test_Services.main('', fileName, _SCL)

        return _SCL

    #<IED name="AUT1A_SITE_1" type=".." manufacturer="..." configVersion="..." originalSclVersion="2007" ...>
    # #		<AccessPoint name="ADMINISTRATION_AP"></AccessPoint>
    # #		<AccessPoint name="PROCESS_AP"></AccessPoint>

    #< Communication >
    #   < SubNetwork type = "8-MMS" name = "RSPACE_PROCESS_NETWORK" >
    #       < ConnectedAP iedName = "AUT1A_SITE_1" apName = "PROCESS_AP" redProt = "prp" >

    ##
    # \b getIED_withComm Browse IED and AccessPoint hierachy, get the IP from communication part and store it in the AccessPoint Class
    #
    #  @param   scl     The scl as loaded in memory

    def getIED_withComm(self, scl):

        comm    = scl.getElementsByTagName("Communication")
        tIEDNet  = ParseCommunication(scl, self.TR)      # Analyse de la section <Communication>
        tNetWork = tIEDNet.ParseCommSection(comm)               #                           <SubNetWork>
                                                                #                               <ConnectedAP...>
        ##      Gather information on server from the data model aspect
        tIEDComm        = Parse_Server(scl, self.TR)              # IED / SERVER / LD
        tIED            = tIEDComm.Parse_IED(self.TR)

        self.TR.Trace(("nombre de IED/server: "+str(len(tIED)))     , TL.DETAIL)       # 42
        self.TR.Trace(("nombre de subnetWork: "+str(len(tNetWork))) , TL.DETAIL)

    # Supposition: un server par IED !              # TODO extend to n Server
        for i in range (0,len(tIED)):
            iedNameSrv = tIED[i].name                                     # Nom de l'IED dans la partie IED
            apNameSrv  = tIED[i].tAccessPoint[0].name                     # Nom de l'access point dans la partie IED
        # Recherche de l'addresse IP dans la partie réseau

            for j in range(0,len(tNetWork)):            # Level 1: browsin 'subNetWork' (Ex: STATION-BUS / PROCESS-BUS
                name = tNetWork[j].name                 # network name

                # Il faut que tAdress ne soit pas 'None'.
                iNetwork = tNetWork[j]     # Instance du réseau
                for k in range(0,len(iNetwork.tConnectedAP)):    # Niveau 2: parcours des ConnectedAP

                    iedNameAP = iNetwork.tConnectedAP[k].iedName
                    apName    = iNetwork.tConnectedAP[k].apName

                    if (iedNameAP==iedNameSrv) and (apNameSrv==apName):   # Trouvé l'IED et l'access Point ?
                        if iNetwork.tConnectedAP[k].tAddress is not None:
                            IP= self.GetIPAddress(iNetwork.tConnectedAP[k].tAddress)
                            if IP is None:
                                IP='0.0.0.0'        # Cas des template IED: pas d'adresse IP
                            tIED[i].tAccessPoint[0].tServer[0].IP = IP
                            tIED[i].IP  = IP
                            tIED[i].tAccessPoint[0].tServer[0].tAddress = iNetwork.tConnectedAP[k].tAddress
                            self.TR.Trace(("iedNameAP:" + iedNameAP + "iedNameSRV:"+iedNameSrv +"      , apName:" + apName + " adresse IP:" + IP), TL.DETAIL)
                            break
            self.tIED = tIED
        return tIED
    ##
    #
    # \b BrowseDataModel
    #
    # Going through all AccessPoint, Servers and logical device
    #
    # @param    IEDinstance  the IED concerned
    # @return   tIEC_adresse the table of IEC/MMS adresse (empty at this stage)

    def BrowseDataModel(self, IEDinstance):

        tIEC_adresse=[]
        IEDName   = IEDinstance.name

        for i in range (len(IEDinstance.tAccessPoint)):
            for j in range (len(IEDinstance.tAccessPoint[i].tServer)):
                NbLdevice = len(IEDinstance.tAccessPoint[i].tServer[j].tLDevice)
                for k in range(NbLdevice):                              # Browsing all LDevice of one IED
                    LD = IEDinstance.tAccessPoint[i].tServer[j].tLDevice[k]
                    tIEC_adresse= self.BrowseDataModel_LD(tIEC_adresse, IEDName, LD)

        return tIEC_adresse

    ##
    #
    # \b BrowseDataModel_LD
    #
    # Going through all LN and DO of an IED
    #
    # @param    tIEC_adresse    the table of IEC/MMS address for a given IED
    # @param    IEDName         the name of IED concerned
    # @param    LD              the logical device to be parsed
    # @return   tIEC_adresse    the table of IEC/MMS filled.
    def BrowseDataModel_LD(self, tIEC_adresse, IEDName, LD):
            for j in range(len(LD.LN)):                         # Browsing LN du LDEVICE
                LN = LD.LN[j]
                txtLN = LD.LN[j].lnPrefix + LD.LN[j].lnClass + LD.LN[j].lnInst
                self.TR.Trace(("Browsing LD:" + LD.inst + " LN:" + txtLN ) , TL.GENERAL)
                LNodeType    = self.LNode.getIEC_LNodeType(LN.lnType)   # Look-up for LNType
                LD.LN[j].tDO = LNodeType.tDO
    #TODO traiter le cas ou on le trouve pas !!!
                for k in range(len(LNodeType.tDO)):          # Browsing DO
                    DO  = LN.tDO[k]
                    if DO.name == 'ApcFTrk':
                        print("STOP")
                    iDO = self.DOType.getIEC_DoType(DO.type)          # Look-up for DO Type
                    tDA = iDO.tDA
                    DO_Name  =  IEDName + '$' + LD.inst + '$' + LN.lnPrefix + LN.lnClass + LN.lnInst + '$' + LN.tDO[k].name
                    DO_Name2 = ( IEDName , LD.inst , LN.lnPrefix + LN.lnClass + LN.lnInst, LN.tDO[k].name)
                    self.BrowseDA(tIEC_adresse, DO_Name, tDA, 'Yes')

            return(tIEC_adresse)

    ##
    #
    # \b BrowseDA
    #
    # Going through all the DA of a given DO
    #
    # @param    tIEC_adresse  the table of all IEC/mms adresses for one IED
    # @param    DO_Name         Name of the DO
    # @param    DA      instance of a DA
    # @param    fc      Functional Constraint of the data point
    def BrowseDA(self, tIEC_adresse, DO_Name, DA, FC):

        if DA is None:
            print("Problem DA None !!!!" + DO_Name)
            return

        for i in range(len(DA)):  # Browse des DA composants le DO.
            type1    = DA[i].type
            bType1   = DA[i].bType
            value    = DA[i].value
            valKind  = DA[i].valKind
            try:
                count    = DA[i].count
            except:
                count = ''
                print("zzzzzzzzzzzzzzzzzzz")

            if FC is None:          # Cas du parcours des structures
                fc = ''
                DataName = DO_Name + '$' + DA[i].name  # + '(' + bType1 + '-' + valKind1 + ')'
            else:
                fc = DA[i].fc       # Cas 'normal'.
                if fc == '':
                    DataName = DO_Name + '$' + DA[i].name  # + '(' + bType1 + '-' + valKind1 + ')'
                else:
                    DataName = DO_Name + '$' + fc + '$'+ DA[i].name  # + '(' + bType1 + '-' + valKind1 + '

            if count is not None and count !='':
                cpt = int(count)
                for j in range(0,cpt):
                    DataName = DO_Name + '$' + DA[i].name + str(j)  # + '(' + bType1 + '-' + valKind1 + ')'
                    bType2 = self.BrowseTypeSimple(tIEC_adresse, type1, bType1, i, DataName, 'NO', DA, value, valKind )
            else:
                bType2 = self.BrowseTypeSimple(tIEC_adresse, type1, bType1, i, DataName, fc, DA, value, valKind)

    ##
    #
    # \b BrowseTypeSimple
    #
    # Recursive function which browse a given DA, down the 'stVal', 'q' / 't' depth.
    #
    # @param    tIEC_adresse  the table of all IEC/mms adresses for one IED
    # @param    DA_Type Data Attribute level, DA_name (depends on the DO complexity...)
    # @param    bType2  Data Type or Struct field
    # @param    bType   Data Type or Struct field
    # @param    idx     Index for the table of IEC adresses
    # @param    DataName
    # @pamra    fc      Functional Constraint of the data point
    # @param    DA
    # @param    value   Actual if defined by SCL or type declaration
    # @param    valkind What actions are possible on the data or not.
    def BrowseTypeSimple(self, tIEC_adresse, DA_type, bType, idx, DataName, fc, DA, value, valKind):
        #        if bType=='Enum' or DA_type=='Enum':
        #             print('yyyyyyyyyyy')

        if bType in IecType.bType.Simple:  # Type de base ?
            _iecAdr = IECda("Simple-0   : ", DataName, fc, bType, None, value, valKind)
            tIEC_adresse.append(_iecAdr)
            return None

        elif (bType == 'Struct'):
            DA_type = DA[idx].type
            SDA = self.DAType.getIEC_DaType(DA_type)

            for m in range(len(SDA.tBDA)):
                bType2 = SDA.tBDA[m].type
                if bType2 in IecType.bType.Simple:
                    _iecAdr = IECda("Struct-1   : ", DataName, fc, bType2, None, value, valKind)
                    tIEC_adresse.append(_iecAdr)
                    continue

                elif (bType2 == 'Struct'):
                    DA = self.DAType.getIEC_DaType(DA_type)  # DataName SDA.BDA_lst[m].bType)
###                    self.BrowseDA(tIEC_adresse, DataName, DA, None)
                    for n in range(len(DA.tBDA)):
                        DA1      = DA.tBDA[n]
                        type1    = DA1.type
                        bType1   = DA1.bType
                        bName    = DA1.name
                        bValue   = DA1.value
                        bValKind = DA1.valKind
                        BaseName = DataName + '$' + DA1.name
                        if (DA1.type in IecType.bType.Simple):
                            DataName2 = BaseName
                            _iecAdr = IECda("Simple-3   : ", BaseName, fc, DA1.type, None, bValue, bValKind)
                            tIEC_adresse.append(_iecAdr)
                        elif (DA1.type == 'Enum'):
                            _iecAdr = IECda("Enum-2     : ", BaseName, fc, DA1.bType, type1, bValue, bValKind)
                            tIEC_adresse.append(_iecAdr)
                        elif (DA1.type == 'Struct'):
                            DA2 = self.DAType.getIEC_DaType(DA1.bType)
                            for k in range(len(DA2.tBDA)):
                                DataName2 = BaseName + '$' + DA2.tBDA[k].name
                                bValue = DA2.tBDA[k].value
                                bValKind = DA2.tBDA[k].valKind
                                _iecAdr = IECda("Struct-3   : ", DataName2, fc, DA2.tBDA[k].type, DA2.tBDA[k].bType,
                                                bValue, bValKind)
                                tIEC_adresse.append(_iecAdr)
                    continue
                elif (bType2 == 'Enum'):
                    DataName2 = DataName + '$' + SDA.tBDA[m].name
                    bValue = SDA.tBDA[m].value
                    bValKind = SDA.tBDA[m].valKind
                    _iecAdr = IECda("Enum-1     : ", DataName2, fc, SDA.tBDA[m].type, SDA.tBDA[m].bType, bValue,
                                    bValKind)
                    tIEC_adresse.append(_iecAdr)
                    continue
                else:
                    self.TraceDataPoint("ELSE           :", DA_type, bType, bType2, DataName, fc)
                    DA = self.DAType.getIEC_DaType(bType2)
                    self.BrowseDA(tIEC_adresse, DataName, DA, None)
            return None
        elif (bType == 'Enum'):
            bValue = DA[idx].value
            bValKind = DA[idx].valKind
            _iecAdr = IECda("Enum-0     : ", DataName, fc, bType, DA[idx].type, bValue, bValKind)
            tIEC_adresse.append(_iecAdr)
            return None

        elif (bType is not None):

            DO = self.DOType.getIEC_DoType(bType)
            if DO is not None:
                self.BrowseDA(tIEC_adresse, DataName, DO.tDA, 'Yes')
            else:
                DA = self.DAType.getIEC_DaType(bType)
                self.BrowseDA(tIEC_adresse, DataName, DA, 'Yes')

    ##
    #
    # \b TraceDataPoint
    #
    # For debugging purpose, print the details of a given data point
    #
    # @param    header  Text like Struct-1 , Enum-2, Simple...
    # @param    file    SCL file to use (SCD, IID, ICD, ...)
    # @param    DA_Type Data Attribute level, DA_name (depends on the DO complexity...)
    # @param    bType2  Data Type or Struct field
    # @param    bType   Data Type or Struct field
    # @param    DataName
    # @pamra    fc      Functional Constraint of the data point

    def TraceDataPoint(self,header, DA_type, bType2, bType, DataName, fc):
        self.TR.Trace((header + "    DA_type:" + DA_type + ', bType:' + bType +  ', bType2:' + bType2+
                           ', DataName: ' + DataName + ', FC:' + fc), TL.GENERAL)

    ##
    # \b GetIPAddress(tAddress):
    #
    # Look_up for an IP address in a ConnectedAP structure
    #
    #   @param tAddress  Table of network addresses ConnectedAP.PhysConn.PType
    #
    def GetIPAddress(self, tAddress):
        for i in range (0,len(tAddress)):
            self.TR.Trace(("tAddress.type:"+tAddress[i].type + "tAddress.value="+tAddress[i].value),TL.DETAIL)
            if (tAddress[i].type=="IP"):
                return(tAddress[i].value)
        return(None)



#    def CheckDatapointSCL(self, iec):
#        bType = iec.BasicType
#        if iec.TypeValue != None:
#            if bType != None:
#                if bType == 'Enum':
#                    iEnum = GM.EnumType.getIEC_EnumType(iec.EnumType)
#                    Check.Enum(iEnum, iec.TypeValue)
#                    # TODO Trace
#                else:
#                    Check.Type(bType, iec.TypeValue)

##
# \b Test_DOType: unitary test for Test_ParcoursDataModel
class Test_ParcoursDataModel:
    def main(directory, file, scl):

        TX = TConsole.File(TL.GENERAL, "dump data.txt")
        GM = globalDataModel(TX, directory + file, scl)
        iec_BasicType = ''
        iec_TypeValue = ''
        iec_EnumType  = ''


        T0_Global = time.time()
        for ied in GM.tIED:
            t0_ied = time.time()
            tIEC_adresse = GM.BrowseDataModel(ied)
            if ied.IP is None:
                ip = '0.0.0.0'
            else:
                ip = ied.IP
            nbDa = len(GM.tIED)
            Resultat = str(time.time() - t0_ied)
            TX.Trace(("Time for IED:" + ied.name + '(' + ip + ") Number of DA:" + str(nbDa) + "Time" + Resultat),TL.GENERAL)

            index = 0
            IED_ID = ied.name + ied.tAccessPoint[0].name #  ied.name   # TODO ou ied.name+AP_Name
            for iec in tIEC_adresse:

                if iec.BasicType is None:
                   iec_BasicType = " - "
                if iec.TypeValue is None:
                    iec_TypeValue = " - "
                if iec.EnumType is None:
                    iec_EnumType = " - "

                TX.Trace(( "MMS_ADR" + iec.mmsAdr + " FC:" + iec.fc + " bType:" + iec_BasicType + " EnumType:" + iec_EnumType + "Value:" + iec_TypeValue + "\n" ), TL.GENERAL)
                index = index + 1
        T1 = time.time()
        TempsTotal = str(time.time() - T0_Global)
        TX.Close()
        print("Temps total de traitement:" + file + ':' + TempsTotal)
        print("fin")

##
# \b MAIN call the unitary test 'Test_ParcoursDataModel'
if __name__ == '__main__':
    fileliste = FL.lstFull  # System level file list
    for file in fileliste:
        Test_ParcoursDataModel.main('SCL_files/', file)

    fileliste = FL.lstIED   # IED level file list
    for file in fileliste:
        Test_ParcoursDataModel.main('SCL_files/', file)

