import xml.dom.minidom as dom
import time
from IEC_FileListe import FileListe

from IEC_Trace              import IEC_Console   as TConsole
from IEC_Trace              import IEC_TraceFile
from IEC_Trace              import TraceLevel    as TL
from IEC_TypeSimpleCheck    import Check

from IEC_ParcoursDataModel import globalDataModel

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

    TX = TConsole(TL.GENERAL)
    tIEDfull=[]
    for file in FileListe.lstIED :

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
