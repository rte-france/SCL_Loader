import xml.dom.minidom as dom
import time
from IEC_FileListe import FileListe

from IEC_Trace              import IEC_Console   as TConsole
from IEC_Trace              import IEC_TraceFile
from IEC_Trace              import TraceLevel    as TL
from IEC_TypeSimpleCheck    import Check

from IEC_ParcoursDataModel import globalDataModel

class CodeGeneration:
    def __init__(self, ApplicationName, _TL):
        self.application = ApplicationName
        self.TR          = _TL
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

        return TR2


    def ParcoursDataModel(self, GM, IEDinstance):

        tIEC_adresse=[]
        IEDName   = IEDinstance.name

        for i in range (len(IEDinstance.tAccessPoint)):
            for j in range (len(IEDinstance.tAccessPoint[i].tServer)):
                NbLdevice = len(IEDinstance.tAccessPoint[i].tServer[j].tLDevice)
                for k in range(NbLdevice):                              # Browsing all LDevice of one IED
                    LD = IEDinstance.tAccessPoint[i].tServer[j].tLDevice[k]
                    tIEC_adresse= self.ParcoursDataModel_LD(GM, tIEC_adresse, IEDName, LD)

        return tIEC_adresse

# RTE/R#Space
# In each LD/LN0 provides a set of DO named inRef
# - private BAP ..
# - private FIP ..
#  - DAI 'setSrcRef': which give the MMS adresse of the data point/: XX_VirtualLDCMDDJ_LDCMDDJ_1/FXUT1.Op.general
#  - DAI 'intAddr
#  - DAI 'Purpose' : description du signal

#     chacun de ses InRef contient

#

    def ParcoursDataModel_LD(self, GM, tIEC_adresse, IEDName, LD):
            for j in range(len(LD.LN)):                         # Browsing LN du LDEVICE
                LN = LD.LN[j]
                txtLN = LD.LN[j].lnPrefix + LD.LN[j].lnClass + LD.LN[j].lnInst
                LNodeType    = GM.LNode.getIEC_LNodeType(LN.lnType)   # Look-up for LNType
                if (LNodeType.lnClass=='LLN0'):
                    self.TR.Trace(("Browsing LD:" + LD.inst + " LN:" + txtLN), TL.GENERAL)
                    print("Fonction:" + LD.inst)
                    inputs1 = LN.tInputs
                    try:
                        X = inputs1.tExtRef
                    except AttributeError:
                        print('No ExtRef table')
                        continue
                    else:
                        for extRef in inputs1.tExtRef:
                            print('INPUT, pLN: '  + extRef.pLN + ' pServT:' + extRef.pServT + " pDO:" + extRef.pDO + " Srv: " + extRef.desc)

                    NbRCB = len(LN.tRptCtrl)
                    for i in range(0,NbRCB):
                        NbClient = len(LN.tRptCtrl[i].RptEnable.tClientLN)

                        for j in range(0, NbClient):
                            iClient = LN.tRptCtrl[i].RptEnable.tClientLN[j]
                            ClientAdresse = (iClient.iedName, iClient.apRef , iClient.ldInst, iClient.lnPrefix, iClient.lnClass, iClient.lnInst)


#                        " GET SMV ADRESSE FROM 'RTE_LLN0_CB_SMV_INT'
                    # InReport Control Get the list Client LN
                    # The ReportControl contains the data Set.
                    # ==> On peut mettre à jour les données relatives aux clients. Et mettre ces informations en données d'entrées / par LD.
            #









            return(tIEC_adresse)


if __name__ == '__main__':

    TX = TConsole(TL.GENERAL)
    tIEDfull=[]
    for file in FileListe.lstSystem:

        CG = CodeGeneration("CodeGeneration", TX)
        GM = globalDataModel(TX,file)

        indIED = 0
        T0 = time.time()

        for ied in GM.tIED:

            t0 = time.time()
            tIEC_adresse = CG.ParcoursDataModel(GM, ied)



#            IEDcomplet   = CG.IEDfull(ied, tIEC_adresse )
#            tIEDfull.append(IEDcomplet)
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
