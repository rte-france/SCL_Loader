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

#@package docstring
#This class analyse parse the configuration in order to collect, foe each function/LD:
#    * The input data:
#       * from GOOSE
#       * from REPORT
#       * from SV
#
#    * The output data:
#        * as goose and the subscribers
#        * as report and the subscribers
#

##
# \b DataType_View   This class displays the DataType definition in ttable view and 'setters' function for each LD.
#

from PyQt5.Qt    import QStandardItemModel, QStandardItem, QTableWidgetItem, QTableView, QLabel, QFrame
from PyQt5.Qt    import QTableWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
import logging
LOGGER = logging.getLogger(__name__)


LNCLASS, DO_NAME, LN_DESC, ID = range(4)
LNODETYPE = "LNodeType"
DOTYPE    = "DOType"
DATYPE    = "DAType"
ENUMTYPE  = "EnumType"

class StandardItem(QStandardItem):
    def __init__(self, txt='', font_size=12, set_bold=False, color=QColor(0, 0, 0)):
        super().__init__()

        fnt = QFont('Open Sans', font_size)
        fnt.setBold(set_bold)

        self.setEditable(False)  # Permet l'édition de la cellule.
        self.setForeground(color)
        self.setFont(fnt)
        self.setText(txt)

class DataType_Table:
    def __init__(self, _winLayout,  _containerLayout):
        self.row       = 0
        self.containerLayout  = _containerLayout
        self.winLayout        = _winLayout
        self.nbLNodeType = 0
        self.nbDOType    = 0
        self.nbDAType    = 0
        self.nbEnumType  = 0
        self.currentView = LNODETYPE
        (self.tLNodeType, self.tDOType, self.tDAType, self.tEnumType) = ([], [], [], [])
        (self.LNTableView, self.DOTypeView, self.DATypeView, self.EnumTypeView) = (None,None,None,None)
        self.nameMainView = ''
        self.DT_frame   = None      # Frame used for the Data Type.

    def Initialize(self, _sclMgr):
        self.sclMgr     = _sclMgr
        (self.nbLNodeType, self.nbDOType, self.nbDAType, self.nbEnum) = self.countObject()

    ## \b countObject:  count the number of objects for each type: LNodeType, DOType, DAType and EnumType.
    #
    # This function is getting its data from SCL Manager.
    #
    # @param self           No Paramenter.
    #
    def countObject(self):
        self.tLNodeType, self.tDOType, self.tDAType, self.tEnumType = self.sclMgr.get_Data_Type_Definition()
        for iLNodeType in self.tLNodeType:
            self.nbLNodeType = self.nbLNodeType + 1
            for iDO in iLNodeType.getchildren():
                self.nbLNodeType = self.nbLNodeType + 1

        self.LNTableView = self.CreateTableView(self.nbLNodeType, LNODETYPE, "DO")
        self.SetLNodeTypeTable()

        for iDOType in self.tDOType:
            self.nbDOType = self.nbDOType + 1
            for iDA in iDOType.getchildren():
                self.nbDOType = self.nbDOType + 1
        self.DOTypeView = self.CreateTableView(self.nbDOType, DOTYPE, "DA[FC]")
        self.SetDOTypeTable()

        for iDAType in self.tDAType:
            self.nbDAType = self.nbDAType + 1
            for iBDA in iDAType.getchildren():
                self.nbDAType = self.nbDAType + 1
        self.DATypeView = self.CreateTableView(self.nbDAType, DATYPE, "SDA/STRUCT")
        self.SetDATypeTable()

        for iEnum in self.tEnumType:
            self.nbEnumType = self.nbEnumType + 1
            for iVal in iEnum.getchildren():
                self.nbEnumType = self.nbEnumType + 1

        self.EnumTypeView = self.CreateTableView(self.nbEnumType, ENUMTYPE, "ENUMTYPE")
        self.SetEnumTypeTable()
        return self.nbLNodeType, self.nbDOType, self.nbDAType, self.nbEnumType

    ## \b CreateTableView:  create an empty table view, for each data type.
    #
    # @param nbRow   The number of objects, used to dimensioned the table view.
    # @param Texte1  The title for first column.
    # @param Texte2  The title for second column.
    #
    def CreateTableView(self, nbRow, Texte1, Texte2):

        tableView = QTableWidget(nbRow, 5)
        tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        tableView.customContextMenuRequested.connect(self.openMenu)
        tableView.clicked.connect(self.openMenu)

        tableView.setHorizontalHeaderItem(LNCLASS, QTableWidgetItem(Texte1))
        tableView.setHorizontalHeaderItem(DO_NAME, QTableWidgetItem(Texte2))
        tableView.setHorizontalHeaderItem(LN_DESC, QTableWidgetItem("DESCRIPTION"))
        tableView.setHorizontalHeaderItem(ID, QTableWidgetItem("Type ID"))

        tableView.setColumnWidth(0, 50)
        tableView.setColumnWidth(1, 30)
        tableView.setColumnWidth(2, 50)
        tableView.setColumnWidth(3, 100)
        tableView.setColumnWidth(4, 100)
        self.nameMainView = Texte1 + DATYPE

        return tableView

    ## \b DataTypeButtons:  create an empty table view, for each data type.
    #
    # @param winLayout   The number of objects, used to dimensioned the table view.
    # @param FC_frame   The widget 'frame' which contains the buttons to select which table to display.
    #
    def DataTypeButtons(self, winLayout, FC_frame):
        self.DT_frame = QFrame()
        self.DT_frame.setLineWidth(4)
        self.DT_frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.DT_frame.setStyleSheet("QFrame {background-color: rgb(200, 255, 255);"
                            "border-width: 2;"
                            "border-radius: 6;"
                            "border-style: solid;"
                            "border-color: rgb(10, 10, 10)}"
                            )
        self.hLayoutButtons = QHBoxLayout(self.DT_frame)
        self.hLayoutButtons.addWidget(self.DT_frame)

        LNodeTypeButton = QPushButton(LNODETYPE, self.DT_frame)
        LNodeTypeButton.clicked.connect(self.DisplayTableLNODE)
        self.hLayoutButtons.addWidget(LNodeTypeButton)

        DOTypeButton = QPushButton(DOTYPE,  self.DT_frame)
        DOTypeButton.clicked.connect(self.DisplayTableDOType)
        self.hLayoutButtons.addWidget(DOTypeButton)

        DATypeButton = QPushButton(DATYPE,  self.DT_frame)
        DATypeButton.clicked.connect(self.DisplayTableDAType)
        self.hLayoutButtons.addWidget(DATypeButton)

        EnumTypeButton = QPushButton(ENUMTYPE,  self.DT_frame)
        EnumTypeButton.clicked.connect(self.DisplayTableEnumType)
        self.hLayoutButtons.addWidget(EnumTypeButton)

        print('replaceWidget(self.FC_frame, self.DT_frame)')
        self.commuteView(self.winLayout, FC_frame, self.DT_frame, 'FC Frame', 'DT Frame')

        return self.DT_frame

    def SetLNodeTypeTable(self):
        row = 1
        for iLNodeType in self.tLNodeType:
            name =  iLNodeType.get('lnClass')
            id   =  iLNodeType.get('id')
            desc =  iLNodeType.get('desc')
            self.LNtableView.setCellWidget(row, 0,  QLabel(name))
            self.LNtableView.setCellWidget(row, 3, QLabel(id))
            self.LNtableView.setCellWidget(row, 4, QLabel(desc))
            row = row + 1

            for iDO in iLNodeType.getchildren():
                doName = iDO.get('name')
                doType = iDO.get('type')

                self.LNtableView.setCellWidget(row, 1, QLabel(doName))    # Desc
                self.LNtableView.setCellWidget(row, 3, QLabel(doType))    # DoType
                row = row + 1

        self.LNtableView.setUpdatesEnabled(True)
        self.LNtableView.resizeColumnsToContents()
        self.currentView= LNODETYPE
        print("SetLNodeTypeTable: "+ str(row) +" lines" )

    def SetDOTypeTable(self):
        row =1
        for iDOType in self.tDOType:
            name = iDOType.get('cdc')
            id   = iDOType.get('id')
            desc = iDOType.get('desc')

            self.DOTypeView.setCellWidget(row, 0, QLabel(name))
            self.DOTypeView.setCellWidget(row, 3, QLabel(id))
            self.DOTypeView.setCellWidget(row, 4, QLabel(desc))
            row = row + 1
            for iDA in iDOType.getchildren():
                SDO=''
                _tag  = iDA.tag.split('}')
                daName = iDA.get('name')
                if _tag[1] == "SDO":
                    daName = daName + '{SDO}'
                elif iDA.get('fc') is not None:
                    daName =  daName + '[' + iDA.get('fc') + ']'

                bType = iDA.get('bType')
                try:
                    type  = iDA.get('type')
                    bType = bType + '(' + type+ ')'
                except:
                    pass

                self.DOTypeView.setCellWidget(row, 1, QLabel(daName))  # Desc
                self.DOTypeView.setCellWidget(row, 3, QLabel(bType))  # DoType
                self.DOTypeView.resizeColumnsToContents()
                row = row + 1
                self.DOTypeView.resizeColumnsToContents()

        self.DOTypeView.setUpdatesEnabled(True)
        self.DOTypeView.resizeColumnsToContents()
        print("SetDOTypeTable: "+ str(row) +" lines" )

    def SetDATypeTable(self):
        row = 1
        for iDAType in self.tDAType:
            id   = iDAType.get('id')
            desc = iDAType.get('desc')

            self.DATypeView.setCellWidget(row, 0, QLabel(id))
            self.DATypeView.setCellWidget(row, 3, QLabel(desc))
            row = row + 1
            for iBDA in iDAType.getchildren():
                _tag = iBDA.tag.split('}')
                if _tag[1] == "ProtNs":     # Ignore ProtNs
                    continue

                daName  = iBDA.get('name')
                type    = iBDA.get('type')
                bType =   iBDA.get('bType')
                if type is not None:
                    bType = bType + ' (' + type + ')'

                self.DATypeView.setCellWidget(row, 1, QLabel(daName))  # Desc
                self.DATypeView.setCellWidget(row, 3, QLabel(bType))  # DoType
                self.DATypeView.resizeColumnsToContents()
                row = row + 1
                self.DATypeView.resizeColumnsToContents()

        self.DATypeView.setUpdatesEnabled(True)
        self.DATypeView.resizeColumnsToContents()
        print("SetDATypeTable: "+ str(row) +" lines" )

    def SetEnumTypeTable(self):
        row = 1
        for iEnumType in self.tEnumType:
            id   = iEnumType.get('id')
            desc = iEnumType.get('desc')

            self.EnumTypeView.setCellWidget(row, 0, QLabel(id))
            self.EnumTypeView.setCellWidget(row, 3, QLabel(desc))
            row = row + 1
            print(id , desc)
            for iEnumVal in iEnumType.getchildren():
                _ord = str(iEnumVal.get('ord'))
                _ordName = str(iEnumVal.text)
                print('    ' + _ord + ':' + _ordName)
                self.EnumTypeView.setCellWidget(row, 1, QLabel(_ord))
                self.EnumTypeView.setCellWidget(row, 2, QLabel(_ordName))

                self.EnumTypeView.resizeColumnsToContents()
                row = row + 1
                self.EnumTypeView.resizeColumnsToContents()

        self.EnumTypeView.setUpdatesEnabled(True)
        self.EnumTypeView.resizeColumnsToContents()
        print("Set EnumTypeView: "+ str(row) +" lines" )

    def DisplayTableLNODE(self,):
        if self.currentView=='None':
            self.LNtableView.setVisible(True)
            self.LNtableView.setUpdatesEnabled(True)
            return
        elif self.currentView== LNODETYPE:
            return
        elif self.currentView == DOTYPE:
            self.commuteView(self.containerLayout, self.DOTypeView, self.LNtableView, DOTYPE, LNODETYPE)
            return
        elif self.currentView == DATYPE:
            self.commuteView(self.containerLayout, self.DATypeView, self.LNtableView, DATYPE, LNODETYPE)
            return
        elif self.currentView == ENUMTYPE:
            self.commuteView(self.containerLayout, self.EnumTypeView, self.LNtableView, DATYPE, LNODETYPE)


    def DisplayTableDOType(self):
        if self.currentView==DOTYPE:
            return
        elif self.currentView == LNODETYPE:
            self.commuteView(self.containerLayout, self.LNtableView, self.DOTypeView, LNODETYPE, DOTYPE)
            return
        elif self.currentView == DATYPE:
            self.commuteView(self.containerLayout, self.DATypeView,  self.DOTypeView,  DATYPE, DOTYPE)
        return
        if self.currentView == ENUMTYPE:
            self.commuteView(self.containerLayout, self.EnumTypeView, self.DOTypeView,  DATYPE, DOTYPE)


    def DisplayTableDAType(self):
        if self.currentView==DATYPE:
            return
        if self.currentView == LNODETYPE:
            self.commuteView(self.containerLayout, self.LNtableView, self.DATypeView, LNODETYPE, DATYPE)
            return
        elif self.currentView == DOTYPE:
            self.commuteView(self.containerLayout, self.DOTypeView, self.DATypeView,   DOTYPE, DATYPE)
            return
        elif self.currentView == ENUMTYPE:
            self.commuteView(self.containerLayout, self.EnumTypeView, self.DATypeView,   DOTYPE, DATYPE)

    def DisplayTableEnumType(self):
        if self.currentView==ENUMTYPE:
            return
        elif self.currentView == LNODETYPE:
            self.commuteView(self.containerLayout, self.LNtableView, self.EnumTypeView,LNODETYPE, ENUMTYPE)
            return
        elif self.currentView == DOTYPE:
            self.commuteView(self.containerLayout, self.DOTypeView, self.EnumTypeView, DOTYPE, ENUMTYPE)
            return
        elif self.currentView == DATYPE:
            self.commuteView(self.containerLayout, self.DATypeView, self.EnumTypeView, DOTYPE, ENUMTYPE)
            return


    def commuteView(self, Layout, ViewFrom, ViewTo, NameFrom, NameTo):
        print ("Replace view:" + NameFrom + " by view to" + NameTo)

        ViewFrom.setVisible(False)
        ViewTo.setVisible(True)
        ViewTo.setUpdatesEnabled(True)
        Layout.addWidget(ViewTo)
        Result = Layout.replaceWidget(ViewFrom, ViewTo, Qt.FindChildrenRecursively)
        if Result is not None:
            print(type(Result))
        print('Result_3:', Result)
        Layout.update()
        ViewTo.repaint()
        ViewTo.show()
        self.currentView = NameTo


    def openMenu(self, value):
        return
        x=value.x()
        y=value.y()

#        QPoint
#        globalPos = self.treeView.mapToGlobal(value)

        indexes = self.treeView.selectedIndexes()
        col1 = self.treeView.columnAt(x)
        col2 = self.treeView.columnAt(y)
        data = self.treeView.pos()