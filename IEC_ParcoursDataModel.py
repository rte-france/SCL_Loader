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
from IEC_FileListe import FileListe

from IEC_LNodeType          import Parse_LNodeType
from IEC_DOType             import Parse_DOType
from IEC_DAType             import Parse_DAType
from IEC_EnumType           import Parse_EnumType
from IEC_Services           import Test_Services
from IEC_Communication      import ParseCommunication
from IEC_IED_Server         import Parse_Server

from IEC_Trace              import IEC_Console   as TConsole
from IEC_Trace              import IEC_TraceFile
from IEC_Trace              import TraceLevel    as TL
from IEC_TypeSimpleCheck    import Check

from IEC61850_XML_Class     import  DataTypeTemplates as IecType

class IECda:
    def __init__(self, Texte, _mmsAdr, _fc, _BasicType,_EnumType, _Value, _Valkind):
        self.mmsAdr       = _mmsAdr         # Adress down to the IEC bType or Struct.
        self.mmsAdrFinal  = 'xx'
        self.acsiAdr      = 'zz'            # Adress ready for ACSI services
        self.fc           = _fc             # Functional Constrain
        self.BasicType    = _BasicType      # 'bType' see IEC61850_
        self.EnumType     = _EnumType
        self.TypeValue    = _Value          # Value    from  DATA TYPE DEFINITION
        self.ValKind      = _Valkind        # ValKlind from  DATA TYPE DEFINITION
        self.ValAdr       =  ''             # Path the ValAdr (when DAI/SDI aws used)

        if _Value == '__None__':
            self.TypeValue = None

#
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
                print("#######################")
#        if self.TypeValue != None:
#            self.TR.Trace(( Texte + 'MMS:' + self.mmsAdrFinal + ','+  iecType+
#                       ', Value:'+ self.TypeValue+ ', VK:'+ _Valkind ),TL.DETAIL)
#        else:
#            self.TR.Trace(( Texte + 'MMS:' + self.mmsAdrFinal + ',' + iecType + ', No Value, VK:'+ _Valkind ),TL.DETAIL)

# FOR DEBUGGING        self.TR.Trace(( Texte + 'MMS:' + self.mmsAdrFinal + ','+  iecType+
#                           ', Value:'+ self.iecTypeValue+ ', VK:'+ _Valkind ),TL.DETAIL)

# Class GlobalModel
#
# For a given SCL file this class will
#
#   - Load all the data definition (LnodeType, DoType, Datype, EnumType)
#   - Extract the IP Address and connection data from the communication and
#     insert it in the Global Model
#   - Generate the table of all Data Point

class globalDataModel:
    def __init__(self, _TR,  file):
        self.TR   = _TR
        self.tIED = []

        self.scl = self.LoadSCLModel(file)

        DataType      = self.scl.getElementsByTagName("DataTypeTemplates")

        self.LNode = Parse_LNodeType(self.scl,self.TR)          # class init
        self.LNode.Create_LNodeType_Dict(DataType)    # Create the 'dictionary' of LNODE

        self.DOType    = Parse_DOType(self.scl, self.TR)        # class init
        self.DOType.Create_DOType_Dict(DataType)     # Create the 'dictionary' of DoType

        self.DAType    = Parse_DAType(self.scl, self.TR)
        self.DAType.Create_DAType_Dict(DataType)

        self.EnumType   = Parse_EnumType(self.scl , self.TR)
        self.EnumType.Create_EnumType_Dict(DataType)

    def TraceDataPoint(self,entete, DA_type, bType2, bType, DataName, fc):
        self.TR.Trace((entete + "    DA_type:" + DA_type + ', bType:' + bType +  ', bType2:' + bType2+
                           ', DataName: ' + DataName + ', FC:' + fc), TL.GENERAL)

    def ParcoursTypeSimple(self,tIEC_adresse, DA_type, bType, idx, DataName, fc, DA, value, valKind):

        if bType in IecType.bType.Simple:  # Type de base ?
            _iecAdr= IECda("Simple-0   : ", DataName, fc, bType, None, value, valKind)
            tIEC_adresse.append(_iecAdr)
            return None

        elif (bType == 'Struct'):
            DA_type = DA[idx].SDO
            SDA = self.DAType.getIEC_DaType(DA_type)

            for m in range(len(SDA.tBDA)):
                bType2= SDA.tBDA[m].type
                if bType2 in IecType.bType.Simple:
                    _iecAdr = IECda("Struct-1   : ", DataName, fc, bType2, None, value, valKind )
                    tIEC_adresse.append(_iecAdr)
                    continue

                elif (bType2 == 'Struct'):
                    DA = self.DAType.getIEC_DaType(DA_type) # DataName SDA.BDA_lst[m].bType)

                    for n in range(len(DA.tBDA)):
                        DA1 = DA.tBDA[n]
                        type1    = DA1.type
                        bType1   = DA1.bType
                        bName    = DA1.name
                        bValue   = DA1.value
                        bValKind = DA1.valKind
                        BaseName = DataName + '$' + DA1.name
                        if ( DA1.type in IecType.bType.Simple):
                            DataName2 = BaseName
                            _iecAdr = IECda("Simple-3   : ",BaseName, fc, DA1.type, None, bValue, bValKind)
                            tIEC_adresse.append(_iecAdr)
                        elif ( DA1.type == 'Enum'):
                            _iecAdr = IECda("Enum-2     : ",BaseName, fc, DA1.bType, type1, bValue, bValKind)
                            tIEC_adresse.append(_iecAdr)
                        elif (DA1.type == 'Struct'):
                            DA2 = self.DAType.getIEC_DaType(DA1.bType)
                            for k in range(len(DA2.tBDA)):
                                DataName2 = BaseName + '$' + DA2.tBDA[k].name
                                bValue    = DA2.tBDA[k].value
                                bValKind  = DA2.tBDA[k].valKind
                                _iecAdr = IECda("Struct-3   : ",DataName2, fc, DA2.tBDA[k].type,DA2.tBDA[k].bType, bValue, bValKind)
                                tIEC_adresse.append(_iecAdr)
                    continue
                elif (bType2 == 'Enum'):
                    DataName2 = DataName + '$' + SDA.tBDA[m].name
                    bValue   = SDA.tBDA[m].value
                    bValKind = SDA.tBDA[m].valKind
                    _iecAdr = IECda("Enum-1     : ",DataName2, fc, SDA.tBDA[m].type, SDA.tBDA[m].bType, bValue, bValKind)
                    tIEC_adresse.append(_iecAdr)
                    continue
                else:
                    self.TraceDataPoint("ELSE           :",DA_type, bType, bType2, DataName, fc)
                    DA = self.DAType.getIEC_DaType(bType2)
                    self.ParcoursDA(tIEC_adresse, DataName, DA, None)
            return None
        elif (bType == 'Enum'):
            bValue   = DA[idx].value
            bValKind = DA[idx].valKind
            _iecAdr = IECda("Enum-0     : ",DataName, fc, bType, DA[idx].type, bValue , bValKind)
            tIEC_adresse.append(_iecAdr)
            return None

        elif (bType is not None):

            DO= self.DOType.getIEC_DoType(bType)
            if DO is not None:
                self.ParcoursDA(tIEC_adresse, DataName, DO.tDA, 'Yes')
            else:
                DA = self.DAType.getIEC_DaType(bType)
                self.ParcoursDA(tIEC_adresse, DataName, DA, 'Yes')


    def ParcoursDA(self, tIEC_adresse, DO_Name, DA, FC):

#        if DA is None:
#            print("Problem DA None !!!!")
#            return

        for i in range(len(DA)):  # Parcours des DA composants le DO.
            type1    = DA[i].type
            bType1   = DA[i].bType
            value    = DA[i].value
            valKind  = DA[i].valKind
            count    = DA[i].count

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
                    bType2 = self.ParcoursTypeSimple(tIEC_adresse, type1, bType1, i, DataName, 'NO', DA, value, valKind )
            else:
                bType2 = self.ParcoursTypeSimple(tIEC_adresse, type1, bType1, i, DataName, fc, DA, value, valKind)

    def ParCoursDataModel(self, scl,IEDinstance, TR):

        tIEC_adresse=[]
        IEDName   = IEDinstance.name

        for i in range (len(IEDinstance.tAccessPoint)):
            for j in range (len(IEDinstance.tAccessPoint[i].tServer)):
                NbLdevice = len(IEDinstance.tAccessPoint[i].tServer[j].tLDevice)
                for k in range(NbLdevice):                              # Browsing all LDevice of one IED
                    LD = IEDinstance.tAccessPoint[i].tServer[j].tLDevice[k]
                    tIEC_adresse= self.ParcoursDataModel_LD(tIEC_adresse, IEDName, LD)

        return tIEC_adresse

    def ParcoursDataModel_LD(self, tIEC_adresse, IEDName, LD):
            for j in range(len(LD.LN)):                         # Browsing LN du LDEVICE
                LN = LD.LN[j]
                txtLN = LD.LN[j].lnPrefix + LD.LN[j].lnClass + LD.LN[j].lnInst
                self.TR.Trace(("Browsing LD:" + LD.inst + " LN:" + txtLN ) , TL.GENERAL)
                LNodeType    = self.LNode.getIEC_LNodeType(LN.lnType)   # Look-up for LNType
                LD.LN[j].tDO = LNodeType.tDO
    #TODO traiter le cas ou on le trouve pas !!!
                for k in range(len(LNodeType.tDO)):          # Browsing DO
                    DO  = LN.tDO[k]
                    iDO = self.DOType.getIEC_DoType(DO.type)          # Look-up for DO Type
                    tDA = iDO.tDA
                    DO_Name  =  IEDName + '$' + LD.inst + '$' + LN.lnPrefix + LN.lnClass + LN.lnInst + '$' + LN.tDO[k].name
                    DO_Name2 = ( IEDName , LD.inst , LN.lnPrefix + LN.lnClass + LN.lnInst, LN.tDO[k].name)
                    self.ParcoursDA(tIEC_adresse, DO_Name, tDA, 'Yes')

            return(tIEC_adresse)

    #def get IP_Adr(tAddress):
    #
    # Recherche une adresse IP dans le tableau 'tAddress' d'un ConnectedAP
    #
    def GetIPAddress(self, tAddress):
        for i in range (0,len(tAddress)):
            self.TR.Trace(("tAddress.type:"+tAddress[i].type + "tAddress.value="+tAddress[i].value),TL.DETAIL)
            if (tAddress[i].type=="IP"):
                return(tAddress[i].value)
        return(None)

    def LoadSCLModel(self, file):
        t0  = time.time()
        scl = dom.parse('SCL_files/' + file)
        t1  = time.time()
        deltaT = t1 - t0
        fileName = 'SCL_files/' + file
        print("Temps pour charger le SCL: " + fileName + ':' + str(deltaT))

        self.tIED = self.getIED_withComm(scl)  # Expect a file list

        comm = scl.getElementsByTagName("Communication")
        subNetWork = ParseCommunication(comm, self.TR)
        tNetWork = subNetWork.ParseCommSection(comm)  # <SubNetWork>
        tServices = Test_Services.main('SCL_files/', file, None)

        return scl

    #<IED name="AUT1A_SITE_1" type=".." manufacturer="..." configVersion="..." originalSclVersion="2007" ...>
    # #		<AccessPoint name="ADMINISTRATION_AP"></AccessPoint>
    # #		<AccessPoint name="PROCESS_AP"></AccessPoint>

    #< Communication >
    #   < SubNetwork type = "8-MMS" name = "RSPACE_PROCESS_NETWORK" >
    #       < ConnectedAP iedName = "AUT1A_SITE_1" apName = "PROCESS_AP" redProt = "prp" >

    def getIED_withComm(self, scl):

        comm = scl.getElementsByTagName("Communication")
        tIEDNet  = ParseCommunication(scl, self.TR)      # Analyse de la section <Communication>
        tNetWork = tIEDNet.ParseCommSection(comm)               #                           <SubNetWork>
                                                                #                               <ConnectedAP...>
        ##      Gather information on server from the data model aspect
        tIEDComm        = Parse_Server(scl, self.TR)              # IED / SERVER / LD
        tIED            = tIEDComm.Parse_IED(self.TR)
    ##

        self.TR.Trace(("nombre de IED/server: "+str(len(tIED)))     , TL.DETAIL)       # 42
        self.TR.Trace(("nombre de subnetWork: "+str(len(tNetWork))) , TL.DETAIL)

    # Supposition: un server par IED !
        for i in range (0,len(tIED)):
    #        iedNameSrv = tIED[i].tAccessPoint[0].tServer[0].IEDName      # Nom de l'IED dans la partie IED
    #        apNameSrv  = tIED[i].tAccessPoint[0].tServer[0].APName       # Nom de l'access point dans la partie IED
            iedNameSrv = tIED[i].name                                     # Nom de l'IED dans la partie IED
            apNameSrv  = tIED[i].tAccessPoint[0].name                     # Nom de l'access point dans la partie IED
        # Recherche de l'addresse IP dans la partie réseau

            for j in range(0,len(tNetWork)):            # Niveau 1: parcours des 'subNetWork' (Ex: STATION-BUS / PROCESS-BUS
                name = tNetWork[j].name                 # network name

                # Il faut que tAdress ne soit pas 'None'.
                iNetwork = tNetWork[j]     # Instance du réseau
                for k in range(0,len(iNetwork.tConnectedAP)):    # Niveau 2: parcours des ConnectedAP

                    iedNameAP = iNetwork.tConnectedAP[k].iedName
                    apName  = iNetwork.tConnectedAP[k].apName

                    if (iedNameAP==iedNameSrv) and (apNameSrv==apName):   # Trouvé l'IED et l'access Point ?
                        if iNetwork.tConnectedAP[k].tAddress is not None:
                            IP= self.GetIPAddress(iNetwork.tConnectedAP[k].tAddress)
                            if IP is None:
                                IP='0.0.0.0'        # Cas des template IED: pas d'adresse IP
                            tIED[i].tAccessPoint[0].tServer[0].IP = IP
                            tIED[i].IP  = IP
                            tIED[i].tAccessPoint[0].tServer[0].tAddress = iNetwork.tConnectedAP[k].tAddress
    #                        self.TR.Trace(("iedNameAP:" + iedNameAP + "iedNameSRV:"+iedNameSrv +"      , apName:" + apName + " adresse IP:" + IP), TL.DETAIL)
                            break
            #            else:
            #                tIED[0].Server[0].IP = None
            #                tIED[0].Server[0].tAddress = None
            #            break
            self.tIED = tIED
        return tIED

class CodeGeneration:
    def __init__(self, ApplicationName):
        self.application = ApplicationName

    class IEDfull:
        def __init__(self, _IEDcomm, _IEDmmsadresse):
            self.IEDcomm        = _IEDcomm
            self.IEDmmsadresse  = _IEDmmsadresse

    class system:
        def __init__(self, _comm, _dataModel, ):
            self.communication   = _comm
            self.dataModel       = _dataModel
            self.tIED            = []

    def GenerateFileHead(self, ied):
        TR2 = IEC_TraceFile(TL.GENERAL, "GeneratedScript/" + ied.name + '.py')
        TR2.Trace(('from utest.ATL import *\n'), TL.GENERAL)
        TR2.Trace(('from VsUtils import variables as vs\n'), TL.GENERAL)
        TR2.Trace(('from utest import IECToolkit\n'), TL.GENERAL)
        TR2.Trace(('import time\n'), TL.GENERAL)
        TR2.Trace(('\n'), TL.GENERAL)
        TR2.Trace(('\n'), TL.GENERAL)

        TR2.Trace(('class CheckDA:\n'), TL.GENERAL)
        TR2.Trace(('\n'), TL.GENERAL)
        TR2.Trace(('    def initialize(self):\n'), TL.GENERAL)
        TR2.Trace(('        pass\n'), TL.GENERAL)
        TR2.Trace(('\n'), TL.GENERAL)

        TR2.Trace(('    def finalize(self):\n'), TL.GENERAL)
        TR2.Trace(('        pass\n'), TL.GENERAL)
        TR2.Trace(('\n'), TL.GENERAL)

        TR2.Trace(('    def execute(self):\n'), TL.GENERAL)
        TR2.Trace(('        '+ ied.name +' = IECToolkit.Manager(' + ip + ')\n'), TL.GENERAL)
    #            IED_AP = ied.Server[0].IEDName + ied.Server[0].APName
        IED_ID = ied.name + ied.tAccessPoint[0].name # tServer[0].IEDName
        TR2.Trace(('        '+ 'I_' + IED_ID + '= mgr.getACSI('+IED_ID+')\n'), TL.GENERAL)

        return TR2

    def GenerateDataPointcheck(self, TR2, iec, IED_ID, index):
        Value = iec.TypeValue
        if Value is None:
            Value = '-'
        TR2.Trace(('\n# ---------------------------------------------------------- \n'), TL.GENERAL)
        if iec.EnumType is None:
    #        TR2.Trace(('# Verification on:' + iec.mmsAdr + '  type:' + iec.BasicType + '\n'), TL.GENERAL)
            TR2.Trace(f'# Verification on: {iec.mmsAdr:40} :type {iec.BasicType:10} value: {Value:20}\n', TL.GENERAL)
        else:
     #       TR2.Trace(('# Verification on:' + iec.mmsAdr + '  Enum:' + iec.EnumType + '\n'), TL.GENERAL)
            TR2.Trace(f'# Verification on: {iec.mmsAdr:40} :type {iec.EnumType:10} value: {Value:20}\n', TL.GENERAL)

    # Line 1 model: # Verification on:L1_PU_GE_D60$Master$LGOS42$InRef59$SP$setSrcRef  type:ObjRef
        TR2.Trace(f'\t\tda=iec[{index:06d}]\n]', TL.GENERAL)

    # Line 2 model:         da=iec[019032]        # # DataType:ObjRef Value: -
    #    TR2.Trace( f'\t\t# DataType: {iec.BasicType:20} Value: {Value}\n', TL.GENERAL)

    # Line 3 model:     value = I_L1_PU_GE_D60.getDataValue(da.mmsAdrFinal))   # L1_PU_GE_D60Master/LLN0.Mod.stVal[ST]
        TR2.Trace( f'\t\tvalue = I_{IED_ID}.getDataValue(da.mmsAdrFinal)        # {iec.mmsAdrFinal} + {Value} \n', TL.GENERAL)

    # Line 4 model:     time.sleep(0.100)
        TR2.Trace(('\t\ttime.sleep(0.100)\n' ), TL.GENERAL)

    # Line 5 model:    CheckDatapoint(da, value)
        TR2.Trace(('\t\tCheckDatapoint(da, value) ' + '\n' ), TL.GENERAL)

    #    TR2.Trace(('        i = i + 1 \n'), TL.GENERAL)
        TR2.Trace(('\n'), TL.GENERAL)

    def GenerateCheckDAivalue(self, TR2, iec, adresse, value):
        TR2.Trace(f'# Expecting: "{value}" as defined by DAI or SDI) \n', TL.GENERAL)
        TR2.Trace(f'\t\tExpectedVal = {adresse:70}\n', TL.GENERAL)
        TR2.Trace(f'\t\tActualValue = getDataValue({iec.mmsAdrFinal})\n', TL.GENERAL)  # Actual Read
        TR2.Trace(f'\t\ttime.sleep(0.100)' + '\n', TL.GENERAL)
        TR2.Trace(f'\t\tif ExpectedVal != ActualValue:' + '\n', TL.GENERAL)
        TR2.Trace(f'\t\t\tSignalErrorOn( da.mmsAdrFinal , ExpectedVal , ActualValue )\n', + TL.GENERAL)

    def CheckDatapointSCL(self, iec):
        bType = iec.BasicType
        if iec.TypeValue != None:
            if bType != None:
                if bType == 'Enum':
                    iEnum = GM.EnumType.getIEC_EnumType(iec.EnumType)
                    Check.Enum(iEnum, iec.TypeValue)
                    # TODO Trace
                else:
                    Check.Type(bType, iec.TypeValue)

                    # TODO Trace

    #
    # ON LINE VERSION
    #       = Test la valeur lue par rapport au type et par rapport à la valeur initiale.
    #
    # TODO A finaliser avec les lectures réelles
    def CheckDatapoint(self, iec, value):
        bType = iec.BasicType
        if iec.TypeValue != None:
            if bType != None:
                if bType == 'Enum':
                    Check.Enum(iec.EnumType, iec.TypeValue, value)
                    # TODO Trace
                else:
                    Check.Type(bType, iec.TypeValue, value )
                    # TODO Trace


if __name__ == '__main__':
    global TR
    TX = TConsole(TL.GENERAL)
    tIEDfull=[]
    for file in FileListe.lstSystem:

        CG = CodeGeneration("CodeGeneration")
        GM = globalDataModel(TX,file)

        indIED = 0
        T0 = time.time()

        for ied in GM.tIED:

            t0 = time.time()
            tIEC_adresse = GM.ParCoursDataModel(GM.scl, ied, TX)
            IEDcomplet   = CG.IEDfull(ied, tIEC_adresse )
            tIEDfull.append(IEDcomplet)
            nbDa = str(len(tIEC_adresse))
            if ied.IP is None:
                ip = '0.0.0.0'
            else:
                ip = ied.IP
            t1 = time.time()
            deltaT = t1 - t0
            Resultat = str(deltaT)
            print("Temps pour l'IED:" + ied.name + '(' + ip + ") Nombre de DA:" + nbDa + "Temps" + Resultat)

#            directAdress = ied.Server[0]
#            'PwrQual$PQi$LLN0$Mod$ST$stVal'
# Manque stVal q t
            TR2 = CG.GenerateFileHead(ied)
            i = 0
            IED_ID = ied.name   # TODO ou ied.name+AP_Name
            for iec in tIEC_adresse:
                CG.GenerateDataPointcheck(TR2, iec, IED_ID, i)
                CG.CheckDatapointSCL(iec)

                if iec.ValAdr != None:
                    A = "GM.tIED[" + str(indIED) +"].tAccessPoint[0].Server[0]."+iec.ValAdr
                    AdrValue = "GM.tIED[" + str(indIED) +"].tAccessPoint[0].tServer[0]."+iec.ValAdr+".value"
                    try:
                        Test  = eval(AdrValue)  # Verify existence of some initialisation data
                        Value = eval(AdrValue)
#                        print("Checking:", AdrValue, "Value:", Value)

                        if (Value!=None):
                            CG.GenerateCheckDAivalue(TR2, iec, AdrValue, Value)

                    except Exception as inst: # No data, an exception is expected hera
#                        print(AdrValue)
                        A = type(inst)
                        if (A == "<class 'AttributeError'>"):
                            break
                i = i + 1
            TR2.TraceClose()
        T1 = time.time()
        TempsTotal = str(T1 - T0)
        print("Temps total de traitement:" + file + ':' + TempsTotal)
    print("fin")
