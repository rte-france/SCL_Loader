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
from IEC_LNodeType import Parse_LNodeType
from IEC_DOType    import Parse_DOType
from IEC_Trace import Trace
from IEC_Trace import Level    as TL
from IEC_TypeSimpleCheck    import Check

from IEC_ParcoursDataModel import globalDataModel

import sys

class CodeGeneration():

    def __init__(self, ApplicationName, _TL):
        self.application = ApplicationName
        self.TR          = _TL
        self.LNodeType   = None

    class IEDfull:
        def __init__(self, _IEDcomm, _IEDmmsadresse):
            self.IEDcomm        = _IEDcomm
            self.IEDmmsadresse  = _IEDmmsadresse

    class system:
        def __init__(self, _comm, _dataModel, ):
            self.communication   = _comm
            self.dataModel       = _dataModel
            self.tIED            = []

    def Parse_LN0(self,BaseName, LD, LN, txtLN):
        self.TR.Trace(("Browsing LD:" + LD.inst + " LN:" + txtLN), TL.GENERAL)
#        print("Fonction:" + LD.inst)
#        inputs1 = LN.tInputs
#        try:
#            X = inputs1.tExtRef
#        except AttributeError:
#            print('No ExtRef table')
#            return
#        else:
#            for extRef in inputs1.tExtRef:
#                print('INPUT, pLN: ' + extRef.pLN + ' pServT:' + extRef.pServT + " pDO:" + extRef.pDO + " Srv: " + extRef.desc)

        NbRCB = len(LN.tRptCtrl)
        for i in range(0, NbRCB):
            NbClient = len(LN.tRptCtrl[i].RptEnable.tClientLN)

            for j in range(0, NbClient):
                iClient = LN.tRptCtrl[i].RptEnable.tClientLN[j]
                ClientAdresse = (
                    iClient.iedName, iClient.apRef, iClient.ldInst, iClient.lnPrefix, iClient.lnClass,
                    iClient.lnInst)

        LNType =  self.LNodeType.getIEC_LNodeType(LN.lnType)
        if LNType is None:
            print("Missing LNOTYPE: ",LNType)
        else:
            for do in LNType.tDO:
                if do.name.startswith("InRef"):
                    DOType = self.DOType.getIEC_DoType(do.type)

                    for da in DOType.tDA:
                        Adr = BaseName + '.' + LD.inst + '.LN0.' + do.name + '.' + da.name
                        try:
                            str= 'LD.LLN0.' + do.name + '.' + da.name + '.value'
                            XX = eval(str)
                            self.TR.Trace(("**** value for DO Type: "+ do.type + '.' + do.name + '.' + da.name + ':' + XX + '\n'),TL.DETAIL)
                        except:
                            self.TR.Trace(("No value for DO Type: "+ do.type + '.' + do.name + '.' + da.name +'\n'),TL.DETAIL)

        return

    def ParcoursDataModel(self, GM, IEDinstance):
        tIEC_adresse=[]
        IEDName   = IEDinstance.name
        cpt= 0
        for i in range (len(IEDinstance.tAccessPoint)):
            IED_Name = IEDinstance.name
            AP_name = IEDinstance.tAccessPoint[i].name

            BaseName  =   IED_Name + '.' + AP_name
            for j in range (len(IEDinstance.tAccessPoint[i].tServer)):
                iServer = IEDinstance.tAccessPoint[i].tServer[j]

                NbLdevice = len(IEDinstance.tAccessPoint[i].tServer[j].tLDevice)
                for k in range(NbLdevice):                              # Browsing all LDevice of one IED

                    LD = IEDinstance.tAccessPoint[i].tServer[j].tLDevice[k]
                    name = LD.inst
                    desc = LD.desc

                    cpt = cpt + 1
                    for m in range(len(LD.LN)):  # Browsing LN du LDEVICE
                        LN = LD.LN[m]
                        _txtLN = LD.LN[m].lnPrefix + LD.LN[m].lnClass + LD.LN[m].lnInst

                        LNodeType = GM.LNode.getIEC_LNodeType(LN.lnType)  # Look-up for LNType
                        # TODO traiter le cas ou on le trouve pas !!!
                        if LN.lnClass == 'LLN0':
                            X1 = self.Parse_LN0(BaseName, LD, LN, _txtLN)

        return


if __name__ == '__main__':

#    TX = Trace.Console(TL.GENERAL)
    TX = Trace.File(TL.DETAIL,"Trace_FctTst.txt")
    tIEDfull=[]

    myCpt = 0

    for file in FileListe.lstSystem:

        CG = CodeGeneration("CodeGeneration", TX)
        GM = globalDataModel(TX,'SCL_files/' + file, None)

        CG.LNodeType = GM.LNode
        CG.DOType    = GM.DOType

        indIED = 0
        T0 = time.time()

        for ied in GM.tIED:

            t0 = time.time()
            myCpt = CG.ParcoursDataModel(GM, ied)
            print("################################### Compteur:"+str(myCpt))

#            directAdress = ied.Server[0]
#            'PwrQual$PQi$LLN0$Mod$ST$stVal'
# Manque stVal q t

        T1 = time.time()
        TempsTotal = str(T1 - T0)
        print("Temps total de traitement:" + file + ':' + TempsTotal)

        TX.Close()
    print("fin")
