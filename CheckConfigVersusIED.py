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

from IEC_Trace              import Trace
from IEC_Trace              import Level   as TL
from IEC_TypeSimpleCheck    import Check

from IEC_ParcoursDataModel import globalDataModel

class IECToolkit:
    def Manager(ip):
        print("initiate for ip:" + ip)

class CheckDataInitialValue:
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

    def CheckDataPoint(self, mmsAdr, value):
        x  = self.IED_AP.getValue(mmsAdr)
        return x == value

    class CodeGen:
        def __init__(self, _ied, File):
            self.ied    = _ied
            self.IP     = _ied.IP
            self.TX     =  Trace.File(TL.GENERAL,File)

            self.TX.Trace(('from utest.ATL import *\n'), TL.GENERAL)
            self.TX.Trace(('from VsUtils import variables as vs\n'), TL.GENERAL)
            self.TX.Trace(('from utest import IECToolkit\n'), TL.GENERAL)
            self.TX.Trace(('import time\n'), TL.GENERAL)
            self.TX.Trace(('\n'), TL.GENERAL)
            self.TX.Trace(('\n'), TL.GENERAL)

            self.TX.Trace(('class CheckDA:\n'), TL.GENERAL)
            self.TX.Trace(('\n'), TL.GENERAL)
            self.TX.Trace(('    def initialize(self):\n'), TL.GENERAL)
            self.TX.Trace(('        pass\n'), TL.GENERAL)
            self.TX.Trace(('\n'), TL.GENERAL)

            self.TX.Trace(('    def finalize(self):\n'), TL.GENERAL)
            self.TX.Trace(('        pass\n'), TL.GENERAL)
            self.TX.Trace(('\n'), TL.GENERAL)

            self.TX.Trace(('    def execute(self):\n'), TL.GENERAL)
            self.TX.Trace(('        '+ self.ied.name +' = IECToolkit.Manager(' + self.ied.IP + ')\n'), TL.GENERAL)
        #            IED_AP = ied.Server[0].IEDName + ied.Server[0].APName
            self.IED_ID = self.ied.name + self.ied.tAccessPoint[0].name # tServer[0].IEDName
            self.TX.Trace(('        '+ 'I_' + self.IED_ID + '= mgr.getACSI('+self.IED_ID+')\n'), TL.GENERAL)

        def DataPointcheck(self, iec, index):
            Value = iec.TypeValue
            if Value is None:
                Value = '-'
            self.TX.Trace(('\n# ---------------------------------------------------------- \n'), TL.GENERAL)
            if iec.EnumType is None:
        #        TR2.Trace(('# Verification on:' + iec.mmsAdr + '  type:' + iec.BasicType + '\n'), TL.GENERAL)
                self.TX.Trace(f'# Verification on: {iec.mmsAdr:40} :type {iec.BasicType:10} value: {Value:20}\n', TL.GENERAL)
            else:
         #       TR2.Trace(('# Verification on:' + iec.mmsAdr + '  Enum:' + iec.EnumType + '\n'), TL.GENERAL)
                self.TX.Trace(f'# Verification on: {iec.mmsAdr:40} :type {iec.EnumType:10} value: {Value:20}\n', TL.GENERAL)

        # Line 1 model: # Verification on:L1_PU_GE_D60$Master$LGOS42$InRef59$SP$setSrcRef  type:ObjRef
            self.TX.Trace(f'\t\tda=iec[{index:06d}]\n]', TL.GENERAL)

        # Line 2 model:         da=iec[019032]        # # DataType:ObjRef Value: -
        #    TR2.Trace( f'\t\t# DataType: {iec.BasicType:20} Value: {Value}\n', TL.GENERAL)

        # Line 3 model:     value = I_L1_PU_GE_D60.getDataValue(da.mmsAdrFinal))   # L1_PU_GE_D60Master/LLN0.Mod.stVal[ST]
            self.TX.Trace( f'\t\tvalue = I_{self.IED_ID}.getDataValue(da.mmsAdrFinal)        # {iec.mmsAdrFinal} + {Value} \n', TL.GENERAL)

        # Line 4 model:     time.sleep(0.100)
            self.TX.Trace(('\t\ttime.sleep(0.100)\n' ), TL.GENERAL)

        # Line 5 model:    CheckDatapoint(da, value)
            self.TX.Trace(('\t\tCheckDatapoint(da, value) ' + '\n' ), TL.GENERAL)

        #    TR2.Trace(('        i = i + 1 \n'), TL.GENERAL)
            self.TX.Trace(('\n'), TL.GENERAL)

        def CheckDAivalue(self, iec, adresse, value):
            self.TX.Trace(f'# Expecting: "{value}" as defined by DAI or SDI) \n', TL.GENERAL)
            self.TX.Trace(f'\t\tExpectedVal = {adresse:70}\n', TL.GENERAL)
            self.TX.Trace(f'\t\tActualValue = getDataValue({iec.mmsAdrFinal})\n', TL.GENERAL)  # Actual Read
            self.TX.Trace(f'\t\ttime.sleep(0.100)' + '\n', TL.GENERAL)
            self.TX.Trace(f'\t\tif ExpectedVal != ActualValue:' + '\n', TL.GENERAL)
            self.TX.Trace(f'\t\t\tSignalErrorOn( da.mmsAdrFinal , ExpectedVal , ActualValue )\n', + TL.GENERAL)

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

        def Terminate(self, ied):
            self.TX.Close()

    class OnLine:
        def __init__(self, _ied, File):
            self.ied    = _ied
            self.IED_AP = IECToolkit.Manager(_ied.IP)
            self.TX     =  Trace.Console(TL.GENERAL)
            self.CnxIED = self.IED_AP.Associate()
            self.IED_ID  = self.ied.name + self.ied.tAccessPoint[0].name

        def DataPointcheck(self, iec,  index):
            Value = iec.TypeValue
            if Value is None:
                Value = '-'

            if iec.EnumType is None:
                self.TX.Trace(f'# Verification on: {iec.mmsAdr:40} :type {iec.BasicType:10} value: {Value:20}\n',
                          TL.GENERAL)
            else:
                self.TX.Trace(f'# Verification on: {iec.mmsAdr:40} :type {iec.EnumType:10} value: {Value:20}\n', TL.GENERAL)

            da=iec[index]
            value = self.IED_ID.getDataValue(da.mmsAdrFinal)        # {iec.mmsAdrFinal} + {Value} \n', TL.GENERAL)
            time.sleep(0.100)
            self.CheckDatapoint(da, value)


        def CheckDAivalue(self, TR2, iec, adresse, value):
            ExpectedVal = iec.Value
            ActualValue = self.IED_ID.getDataValue(iec.mmsAdrFinal)
            time.sleep(0.100)
            if ExpectedVal != ActualValue:
                SignalErrorOn( iec.mmsAdrFinal , ExpectedVal , ActualValue )

        def CheckDatapointSCL(self, iec, value):
            bType = iec.BasicType

            if iec.TypeValue != None:
                if bType != None:
                    if bType == 'Enum':
                        iEnum = GM.EnumType.getIEC_EnumType(iec.EnumType, value)
                        Check.Enum(iEnum, iec.TypeValue)
                        # TODO Trace
                    else:
                        Check.Type(bType, iec.TypeValue,value)

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

    def CheckAllValue(mode):

        TX = Trace.Console(TL.GENERAL)
        tIEDfull=[]
        for file in FileListe.lstIED :

            CG = CheckDataInitialValue("CodeGeneration")
            GM = globalDataModel(TX,file)

            indIED = 0
            T0 = time.time()

            for ied in GM.tIED:

                t0 = time.time()
                tIEC_adresse = GM.BrowseDataModel(ied)
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

                Check1 = CheckDataInitialValue.CodeGen(ied,file)

#                Check2 = CheckDataInitialValue.OnLine(ied,'')

    #            directAdress = ied.Server[0]
    #            'PwrQual$PQi$LLN0$Mod$ST$stVal'
    # Manque stVal q t
                i = 0
                IED_ID = ied.name   # TODO ou ied.name+AP_Name
                for iec in tIEC_adresse:
                    Check1.DataPointcheck(iec, i)
#                    Check2.CheckDatapointSCL(iec.IP, i)

                    if iec.ValAdr != None:
                        A = "GM.tIED[" + str(indIED) +"].tAccessPoint[0].Server[0]."+iec.ValAdr
                        AdrValue = "GM.tIED[" + str(indIED) +"].tAccessPoint[0].tServer[0]."+iec.ValAdr+".value"
                        try:
                            Test  = eval(AdrValue)  # Verify existence of some initialisation data
                            Value = eval(AdrValue)
    #                        print("Checking:", AdrValue, "Value:", Value)

                            if (Value!=None):
                                CG.DataPointcheck(iec, AdrValue, Value)

                        except Exception as inst: # No data, an exception is expected hera
    #                        print(AdrValue)
                            A = type(inst)
                            if (A == "<class 'AttributeError'>"):
                                break
                    i = i + 1
                Check1.TX.Close()
            T1 = time.time()
            TempsTotal = str(T1 - T0)
            print("Temps total de traitement:" + file + ':' + TempsTotal)
        print("fin")


if __name__ == '__main__':

    TX = Trace.Console(TL.GENERAL)
    tIEDfull=[]

    CheckDataInitialValue.CheckAllValue('Connected')
    CheckDataInitialValue.CheckAllValue('CodeGeneration')