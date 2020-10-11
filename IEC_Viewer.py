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

from IEC61850_XML_Class import IED

import sys
import textwrap
import PyQt5
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView
from PyQt5.Qt import QStandardItemModel, QStandardItem
from PyQt5.QtGui import QFont, QColor

from PyQt5.QtCore import (QDate, QDateTime, QRegExp, QSortFilterProxyModel, Qt,
                          QTime, QModelIndex, QStringListModel)

# import time
# from IEC_FileListe import FileListe
from IEC_Trace import Trace
# from IEC_Trace import Level    as TL

from IEC_FileListe import FileListe
from IEC_Trace import Trace    as TConsole
from IEC_Trace import Level    as TL
from IEC_ParcoursDataModel import globalDataModel


class StandardItem(QStandardItem):
    def __init__(self, txt='', font_size=12, set_bold=False, color=QColor(0, 0, 0)):
        super().__init__()

        fnt = QFont('Open Sans', font_size)
        fnt.setBold(set_bold)

        self.setEditable(False)  # Permet l'édition de la cellule.
        self.setForeground(color)
        self.setFont(fnt)
        self.setText(txt)


#        self.value  = txt

class InitData():
    def __init__(self):
        TX = TConsole.File(TL.GENERAL, "dump data.txt")
        TR = TConsole.Console(TL.GENERAL)
        #        GM = globalDataModel(TX, 'SCL_files\SCD_SITE_BCU_4ZSSBO_1_20200901.scd' + file, None)
        iec_BasicType = ''
        iec_TypeValue = ''
        iec_EnumType = ''


class AppDemo(QMainWindow):
    IED_LD, DESC, TYPE, VALUE, TAG, DESC2 = range(6)

    def findDOI(self, iLN, do_name):
        for iDOi in iLN.tiDOI:
            if iDOi.DOname == do_name:
                return iDOi
        return None

    def findDAI(self, iDO, da_name):
        for iDAi in iDO.tDAI:
            if iDAi.name == da_name:
                return iDAi
        return None

    def __init__(self, _TL, GM):
        super().__init__()
        self.setWindowTitle('IEC browser')
        self.resize(800, 900)

        self.application = 'ApplicationName'  ## name A name of the application
        self.TR = _TL  ## Trace Level used
        self.LNodeType = None  ## Access to the LNodeType dictionary
        self.GM = GM  ## The Global Data Model of the SCL used
        self.FileId = None  ## File ID of the output file
        self.IED_ID = None  ## IED name + AcccessPoint Name

        tIED = GM.tIED

        self.treeView = QTreeView()
        self.treeView.setHeaderHidden(False)

        #        model =       bQStandardItemModel(list_view)
        self.treeModel = QStandardItemModel(self.treeView)
        self.treeModel.setColumnCount(6)
        #        self.treeModel.setHorizontalHeaderLabels(["IED/AP/SRV/LD/LN", "Desc", "SDO", "", "DA","SDA"])
        self.treeModel.setHeaderData(self.IED_LD, Qt.Horizontal, "IED/AP/SRV/LD")
        self.treeModel.setHeaderData(self.DESC, Qt.Horizontal, "Desc")
        self.treeModel.setHeaderData(self.TYPE, Qt.Horizontal, "Type")
        self.treeModel.setHeaderData(self.VALUE, Qt.Horizontal, "Value")
        self.treeModel.setHeaderData(self.TAG, Qt.Horizontal, "EnumTags")
        self.treeModel.setHeaderData(self.DESC2, Qt.Horizontal, "....")

        self.rootNode = self.treeModel.invisibleRootItem()

        cptObjet = 0
        Line = 0
        for i in range(0, len(tIED)):
            iIED = tIED[i]
            dataKey = iIED.name
            txt = iIED.name

            _ied = StandardItem(txt, 12, set_bold=True)
            _desc = StandardItem(iIED.type, 11, set_bold=False)
            self.rootNode.appendRow((_ied, _desc))

            item = 0;
            for j in range(0, len(iIED.tAccessPoint)):
                iAP = iIED.tAccessPoint[j]
                _ap = StandardItem(iAP.name, 8, set_bold=False)
                _txt = StandardItem(iAP.desc, 8, set_bold=False)
                _ied.appendRow((_ap, _txt))
                item = item + 1
                dataKey = dataKey + '/' + iAP.name

                for k in range(0, len(iAP.tServer)):
                    iSrv = iAP.tServer[k]
                    _srv1 = StandardItem(('IED:' + iSrv.IP + iSrv.desc), 10, set_bold=True)
                    _desc = StandardItem(iSrv.timeout, 10, set_bold=False)
                    _ap.appendRow((_srv1, _desc))
                    dataKey = dataKey + '/' + iSrv.IP
                    item = item + 1

                    for idxLD in range(0, len(iSrv.tLDevice)):
                        iLD = iSrv.tLDevice[idxLD]
                        ldName = iLD.ldName + ',' + iLD.inst
                        _ldName = StandardItem(ldName, 11, set_bold=False)
                        _desc = StandardItem(iLD.desc, 11, set_bold=False)

                        _srv1.appendRow((_ldName, _desc))
                        dataKey = dataKey + '/' + ldName
                        item = item + 1

                        for iLN in iLD.LN:
                            txtLN = iLN.lnPrefix + iLN.lnClass + iLN.lnInst  # ' + iLD.inst
                            _ln = StandardItem(txtLN, 10, set_bold=True)
                            _lnx = StandardItem(txtLN, 10, set_bold=True)
                            _desc1 = StandardItem(iLN.lnDesc, 9, set_bold=False)

                            _ldName.appendRow((_ln, _desc1))
                            dataKey = dataKey + '/' + txtLN
                            item = item + 1

                            for iDO in iLN.tDO:
                                iDOType = GM.DOType.getIEC_DoType(iDO.type)
                                _DO = StandardItem(iDO.DOname + '(' + iDOType.cdc + ')', 9, set_bold=True)
                                _desc2 = StandardItem(iDO.desc, 9, set_bold=False)
                                dataKey = dataKey + '/' + iDO.DOname

                                DOi = self.findDOI(iLN, iDO.DOname)
                                if DOi is not None and DOi.value is not None:
                                    print('found iDOI' + DOi.value)
                                    _type = StandardItem(DOi.type, 9, set_bold=False)
                                    _desc = StandardItem(iDOType.desc, 9, set_bold=False)
                                    _value = StandardItem(DOi.value, 10, set_bold=False)
                                else:
                                    DOi.value = '.'
                                print("_ln.appendRow")
                                _ln.appendRow((_DO, _type, _desc, _value))  # , 'xx'))

                                for iDA in iDO.tDA:
                                    _DA = StandardItem(iDA.name + '[' + iDA.fc + ']', 9, set_bold=True)
                                    dataKey = dataKey + '/' + iDA.name + '[' + iDA.fc + ']'
                                    ###<*** tDAI est vide...
                                    DAi = self.findDAI(iDA, iDA.name)
                                    if DAi is not None and DAi.value is not None:
                                        print('found iDAI' + DAi.value + ',' + DAi.bType + ',' + DAi.type)
                                        _desc3 = StandardItem(DAi.bType + DAi.type, 8, set_bold=False)
                                        _desc4 = StandardItem(DAi.value, 8, set_bold=False)
                                        print("_DA.appendRow")
                                        _DO.appendRow((_DA, _desc3, _desc4))
                                    else:
                                        _desc3 = StandardItem(iDA.bType, 8, set_bold=False)
                                        _desc4 = StandardItem(iDA.type, 8, set_bold=False)
                                        iDA.name + '[' + iDA.fc + ']'

                                        if iDA.bType != 'Enum':
                                            print("X DA append ROW")
                                            _DO.appendRow((_DA, _desc3, _desc4))
                                        else:
                                            (name, id) = self.Enumeration('ENUM:', iDA.type, _DA)
                                            print("X DA append ROW")
                                            _DO.appendRow((_DA, name, id))

                                        if iDA.bType == 'Struct':
                                            iDAType = GM.DAType.getIEC_DaType(iDA.type)
                                            for jDA in iDAType.tBDA:
                                                _SDA = StandardItem(jDA.name, 8, set_bold=True)
                                                _type = StandardItem(jDA.type, 8, set_bold=True)

                                                _DA.appendRow((_SDA, _type))

                                                if jDA.type == 'Enum':
                                                    (name, id) = self.Enumeration('Enum', jDA.bType, _SDA)
                                                    _SDA.appendRow((_DA, name, id))

                            Line = Line + 1

        self.treeView.setModel(self.treeModel)
        self.treeView.expandAll()
        self.treeView.doubleClicked.connect(self.getValue)

        self.setCentralWidget(self.treeView)
        self.treeView.setColumnWidth(0, 300)
        self.treeView.setColumnWidth(1, 200)
        self.treeView.setColumnWidth(2, 100)
        self.treeView.setColumnWidth(3, 100)

        return None

    def wrap(self, string, lenght):
        return '\n'.join(textwrap.wrap(string, lenght))

    def Enumeration(self, DaName, typeEnum, _DA):
        iEnum = GM.EnumType.getIEC_EnumType(typeEnum)
        iEnumTxt = '('
        cpt = 0
        for iVal in iEnum.tEnumval:
            if cpt < len(iEnum.tEnumval) - 1:
                iEnumTxt = iEnumTxt + iVal.strValue + ':' + iVal.ord + ','
            else:
                iEnumTxt = iEnumTxt + iVal.strValue + ':' + iVal.ord + ')'
            cpt = cpt + 1
        _DA_Name = StandardItem(DaName + ':' + iEnum.id, 8, set_bold=False)
        _EnumVal = StandardItem(self.wrap(iEnumTxt, 45), 8, set_bold=False)
        return ((_DA_Name, _EnumVal))

    def getValue(self, val):
        print(val.data())
        print(val.row())
        print(val.column())


if __name__ == '__main__':

    #    TX = Trace.Console(TL.GENERAL)
    TX = Trace(TL.DETAIL, "Trace_FctTst.txt")
    tIEDfull = []

    myCpt = 0

    for file in FileListe.lstIED:

        GM = globalDataModel(TX, 'D:/OneDrive/SCL_gil/SCL_files/' + file, None)

        for ied in GM.tIED:
            app = QApplication(sys.argv)

            demo = AppDemo(TX, GM)
            demo.show()
            sys.exit(app.exec_())

    print("*** FINISHED ")
