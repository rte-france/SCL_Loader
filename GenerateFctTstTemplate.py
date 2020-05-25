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

from IEC_Trace import Trace
from IEC_Trace import Level    as TL
from IEC_TypeSimpleCheck    import Check

from IEC_ParcoursDataModel import globalDataModel

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView
from PyQt5.Qt import QStandardItemModel, QStandardItem
from PyQt5.QtGui import QFont, QColor

from PyQt5.QtCore import (QDate, QDateTime, QRegExp, QSortFilterProxyModel, Qt,
                          QTime)

class StandardItem(QStandardItem):
    def __init__(self, txt='', font_size=12, set_bold=False, color=QColor(0, 0, 0)):
        super().__init__()

        fnt = QFont('Open Sans', font_size)
        fnt.setBold(set_bold)

        self.setEditable(False)
        self.setForeground(color)
        self.setFont(fnt)
        self.setText(txt)
#        self.value  = txt

class CodeGeneration(QMainWindow):
    IED_LD, DO, FC, DA, SDA, C1, C2, C3 = range(8)

    def __init__(self, ApplicationName, _TL):

        self.application = ApplicationName
        self.TR          = _TL

        super().__init__()
        self.setWindowTitle('IEC browser')
        self.resize(600, 700)

        self.treeView = QTreeView()
        self.treeView.setHeaderHidden(False)
        self.treeView.setColumnWidth(self.IED_LD, 100)
        self.treeView.setColumnWidth(self.DO, 50)
        self.treeView.setColumnWidth(self.FC, 50)
        self.treeView.setColumnWidth(self.DA, 50)
        self.treeView.setColumnWidth(self.C1, 50)
        self.treeView.setColumnWidth(self.C2, 50)
        self.treeView.setColumnWidth(self.C3, 50)

        self.treeModel = QStandardItemModel(0, 9)
        self.treeModel.setColumnCount(10)
        self.treeModel.setHorizontalHeaderLabels(["IED/AP/SRV/LD/LN", "DO", "SDO", "", "DA", "SDA"])
        self.treeModel.setHeaderData(self.IED_LD, Qt.Horizontal, "IED...LN")
        self.treeModel.setHeaderData(self.DO,  Qt.Horizontal, "DO")
        self.treeModel.setHeaderData(self.FC,  Qt.Horizontal, "FC")
        self.treeModel.setHeaderData(self.DA,  Qt.Horizontal, "DA")
        self.treeModel.setHeaderData(self.C1,  Qt.Horizontal, "Struct")
        self.treeModel.setHeaderData(self.C2,  Qt.Horizontal, "Struct")
        self.treeModel.setHeaderData(self.C3,  Qt.Horizontal, "Struct")


        self.rootNode = self.treeModel.invisibleRootItem()

    def getValue(self, val):
        print(val.data())
        print(val.row())
        print(val.column())

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

    def Parse_LN0(self,LD, LN, txtLN):
        self.TR.Trace(("Browsing LD:" + LD.inst + " LN:" + _txtLN), TL.GENERAL)
        print("Fonction:" + LD.inst)
        inputs1 = LN.tInputs
        try:
            X = inputs1.tExtRef
        except AttributeError:
            print('No ExtRef table')
            return
        else:
            for extRef in inputs1.tExtRef:
                print(
                    'INPUT, pLN: ' + extRef.pLN + ' pServT:' + extRef.pServT + " pDO:" + extRef.pDO + " Srv: " + extRef.desc)

        NbRCB = len(LN.tRptCtrl)
        for i in range(0, NbRCB):
            NbClient = len(LN.tRptCtrl[i].RptEnable.tClientLN)

            for j in range(0, NbClient):
                iClient = LN.tRptCtrl[i].RptEnable.tClientLN[j]
                ClientAdresse = (
                    iClient.iedName, iClient.apRef, iClient.ldInst, iClient.lnPrefix, iClient.lnClass,
                    iClient.lnInst)

    def ParcoursDataModel(self, GM, IEDinstance):


        tIEC_adresse=[]
        IEDName   = IEDinstance.name

        cpt= 0
        for i in range (len(IEDinstance.tAccessPoint)):
            IED_Name = IEDinstance.name

            AP_name = IEDinstance.tAccessPoint[i].name
            AP_desc = IEDinstance.tAccessPoint[i].desc

            txt =   IED_Name + ',' + AP_name + ',' + AP_desc
            _ied =  StandardItem(txt, 12, set_bold=True)
            self.rootNode.appendRow(_ied)


            for j in range (len(IEDinstance.tAccessPoint[i].tServer)):
                iServer = IEDinstance.tAccessPoint[i].tServer[j]
                _txt = iServer.desc
                if _txt is None or _txt=='':
                    _txt = 'Server'
                else:
                    _txt = 'Server:'+_srv.desc

                _srv = StandardItem(_txt, 12, set_bold=True)
                _ied.appendRow(_srv)

                NbLdevice = len(IEDinstance.tAccessPoint[i].tServer[j].tLDevice)
                for k in range(NbLdevice):                              # Browsing all LDevice of one IED

                    LD = IEDinstance.tAccessPoint[i].tServer[j].tLDevice[k]
                    name = LD.inst
                    desc = LD.desc
                    _txt = LD.inst + LD.desc + '-0' + LD.ldName
                    _ld = StandardItem(_txt, 12, set_bold=True)
                    _srv.appendRow(_ld)

                    cpt = cpt + 1
                    for m in range(len(LD.LN)):  # Browsing LN du LDEVICE
                        LN = LD.LN[m]
                        _txtLN = LD.LN[m].lnPrefix + LD.LN[m].lnClass + LD.LN[m].lnInst
                        _ln = StandardItem(_txtLN, 12, set_bold=True)
                        _ld.appendRow(_ln)

                        LNodeType = GM.LNode.getIEC_LNodeType(LN.lnType)  # Look-up for LNType
                        LD.LN[j].tDO = LNodeType.tDO
                        # TODO traiter le cas ou on le trouve pas !!!

                        for n in range(len(LNodeType.tDO)):  # Browsing DO
                            tIEC_adresse = []
                            DO  = LNodeType.tDO[n]
                            iDO = GM.DOType.getIEC_DoType(DO.type)  # Look-up for DO Type
                            tDA = iDO.tDA
                            DO_Name = IEDName + '$' + LD.inst + '$' + LN.lnPrefix + LN.lnClass + LN.lnInst + '$' + LD.LN[j].tDO[n].name

                            _do =  StandardItem(LD.LN[j].tDO[n].name, 10, set_bold=True)
                            _ln.appendRow(_do)

                            DO_Name2 = (IEDName, LD.inst, LN.lnPrefix + LN.lnClass + LN.lnInst, LD.LN[j].tDO[k].name)
                            GM.BrowseDA(tIEC_adresse, DO_Name, tDA, 'Yes')

                            for x in range(len(tIEC_adresse)):
                                iIECAdr = tIEC_adresse[x]
                                adrSplit = iIECAdr.mmsAdr.split('$')        #
                                DO =['...']
                                for y in range(4, len(adrSplit)):
                                    DO.append(adrSplit[y])

                                _txtDO = []
                                for y in range(0, len(DO)):                 #
                                    _txtDO.append(StandardItem(DO[y],9, set_bold=False))

                                _ln.appendRow(_txtDO)


        self.treeView.setModel(self.treeModel)
#        self.treeView.expandAll()
        self.treeView.doubleClicked.connect(self.getValue)
        self.treeView.show()

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

    TX = Trace.Console(TL.GENERAL)
    tIEDfull=[]
    for file in FileListe.lstIED:

        app = QApplication(sys.argv)
        CG = CodeGeneration("CodeGeneration", TX)
        GM = globalDataModel(TX,'SCL_files/' + file, None)

#        GM.treeModel.show()

        indIED = 0
        T0 = time.time()

        for ied in GM.tIED:

            t0 = time.time()
            tIEC_adresse = CG.ParcoursDataModel(GM, ied)

            CG.show()
            sys.exit(app.exec_())

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
