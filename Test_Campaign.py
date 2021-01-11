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

from IEC61850_XML_Class import DataTypeTemplates as DT
from GenerateFctTstTemplate import CodeGeneration

from TreeView_DataModel import DataModelTree
from DataType_View      import DataType_Table
from DataType_View      import LNODETYPE, DOTYPE, DATYPE, ENUMTYPE

from scl_loader import SCD_handler, DataTypeTemplates

import sys
import os
import time
import textwrap

from PyQt5.QtWidgets import QMainWindow,QApplication,QDesktopWidget,QVBoxLayout,QHBoxLayout, QTableWidget, QTreeWidgetItem
from PyQt5.QtWidgets import QFileDialog,QTableView,QWidget,QTreeWidget, QPushButton,QFrame,QCheckBox,QTreeView,QMessageBox
from PyQt5.Qt        import QStandardItemModel, QStandardItem, QThread, Qt
from PyQt5.QtGui import QFont, QColor

#                          QTime, QModelIndex, QStringListModel)

IED_LD, TYPE, VALUE, DESC, DESC2 = range(5)

import scl_loader as SCD

class LoadSCL(object):
    def __init__(self,fname):
        print("init")
        self.fname=fname
        self.T0 = time.time()
    def __enter__(self):
        HERE = os.path.abspath(os.path.dirname(__file__))
        filepath = os.path.join(HERE, self.fname)
        self.sclMgr = SCD_handler(filepath, True)

        for iSection in dir(self.sclMgr):
            if iSection.startswith('__'):
                continue
            if iSection.startswith('get'):
                continue
            if iSection.startswith('datatype'):
                continue
            if iSection == "Communication":
                continue
            if iSection =="Header":
                continue
            break               # Found the section 'Substation'
        try:
            self.Poste = eval("self.sclMgr."+iSection)
            if self.Poste.tag != 'Substation':
                print("Error with substation section")
                exit(-1)
            print("Le nom du poste est:" , self.Poste.name)

        except Exception as e:
            print(e)

        self.data   = DataTypeTemplates(filepath)
        self.T1  = time.time()
        self.delta = self.T1-self.T0
        return (self.sclMgr, self.data, self.Poste, self.delta)

    def __exit__(self,  exc_type, exc_val, exc_tb):
        print("SCL loaded with success")
#        return(self.T1 - self.T0)

class QTreeWidgetItem(QTreeWidgetItem):

    def __init__(self, txt='', font_size=12, set_bold=False, color=QColor(0, 0, 0)):
        super().__init__()

        fnt = QFont('Open Sans', font_size)
        fnt.setBold(set_bold)

#        self.setEditable(False)  # Permet l'édition de la cellule.
#        self.setForeground(color)
#        self.setFont(fnt)
        self.setText(0, txt)
        self.layoutMainView = None
        self.nameMainView   = 'DataModel'

## \b DataModelTree:  class to handle the view on the IEC61850 model.
#
# This function is getting its data from SCL Manager.
#
# @param _winLayout         : layout used for the Function Buttons
# @param _containerLayout   : layout used for the data model
#
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self,  parent)
        self.setWindowTitle('Création Campagne de Test')

    class AppDemo(QTreeWidget):
        def __init__(self, _fname):
            super().__init__()

            self.resize(800, 900)
            self.line = 0
            self.dataKey = ''
            self.fname = _fname
            self.tIED = []

            qr = self.frameGeometry()  # geometry of the main window
            cp = QDesktopWidget().availableGeometry().center()  # center point of screen
            qr.moveCenter(cp)  # move rectangle's center point to screen's center point
            self.move(qr.topLeft())  # top left of rectangle becomes top left of window centering it

            self.winLayout = QVBoxLayout()  ## Most the HMI is vertical
            self.winLayout.setSpacing(10)

            with LoadSCL(self.fname) as (self.sclMgr, self.DataTypes, self.Poste, delta):   #, self.T_LoadSCL):
                print("Chargement SCL initial:", delta)         # str(self.T_LoadSCL))

            self.createBay_IED_list(self.Poste)
            self.tIED  = self.sclMgr.get_all_IEDs()


            ## MAIN VIEW, start with treeView

            self.treeLayout = QVBoxLayout()
            self.nameMainView = 'DataModel'

            self.containerLayout = QHBoxLayout()  # Container for 2 vertical layout

            self.setLayout(self.winLayout)
            ## Creation of all widgets
            self.treeView = self.CreateTreeView()

            ## Initial View is Data Model
            self.datatype = DataType_Table(self.winLayout, self.containerLayout)

            ## Initial View is Data Model

#            self.tIED = tIED  ## Required for buttons.
            for iIED in self.tIED:
                self.add_IED(iIED)  # Return the column head

            self.winLayout.addLayout(self.containerLayout)  # Finall
            # y add this to the globalLayout
            self.setLayout(self.winLayout)
            self.show()

        ## \b CreateTableView:  create an empty tree  view.
        #
        #
        def CreateTreeView(self):
            self.treeLayout = QVBoxLayout()
            self.containerLayout.addLayout(self.treeLayout)         # add the Tree View

            self.treeView = QTreeWidget()
            self.treeView.setHeaderHidden(False)
            self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
            self.treeView.customContextMenuRequested.connect(self.openMenu)
            self.treeView.clicked.connect(self.openMenu)

            self.treeView.headerItem().setText(0, "BAY")
            self.treeView.headerItem().setText(1, "IED")
            self.treeView.headerItem().setText(2, "AccessPoint")
            self.treeView.headerItem().setText(3, "IP")
            self.treeView.headerItem().setText(4, "Logical Device")

            self.treeView.expandAll()
            self.treeView.setColumnWidth(0, 200)
            self.treeView.setColumnWidth(1, 100)
            self.treeView.setColumnWidth(2, 100)
            self.treeView.setColumnWidth(3, 100)
            self.treeView.setColumnWidth(4, 100)
            self.treeView.setColumnWidth(5, 100)

            self.treeLayout.addWidget(self.treeView)
#            self.rootNode = self.treeModel.invisibleRootItem()
            return self.treeView #, self.treeModel

        ## \b openMenu:  pop up menu (TODO)
        #
        #
        def openMenu(self, value):
            return
            x=value.x()
            y=value.y()

        ## \b openMenu:  pop up menu (TODO)
        #
        #
        def getValue(self, val):
            indexes = self.treeView.selectedIndexes()

            for ix in indexes:
                text = ix.data()
                print('==> ' + text)

            print(val.data())
            print(val.row())
            print(val.column())

        def DisplayTree(self, tIED, Communication):
            self.Communication  = Communication
            self.tIED = tIED    ## Required for buttons.
            for iIED in tIED:
                T_IED = self.add_IED(iIED)  # Return the column head

        def getIPadr(self, iedName, apNAme):
            for iComm in self.sclMgr.Communication.get_children('SubNetwork'):
                if iComm.type == "8-MMS":
                    for iCnxAP in iComm.get_children('ConnectedAP'):
                        if iCnxAP.iedName == iedName and iCnxAP.apName == apNAme:
                            for iAdr in iCnxAP.get_children('Address'):
                                for iP in iAdr.P:
                                    if iP.type == "IP":
                                        return iP.Val
            return('0.0.0.0')

        def createBay_IED_list(self, Poste):

            tBay = []
            for iStation in Poste.get_children():
                for iBay in iStation.get_children():
                    print(iBay.name)
                    iBay.tIED=[]
                    tBay.append(iBay)
                    for iIED in iBay.get_children():
                        if iIED.tag =="Function":
                            X = iIED.name.split('_')
                            IEDname = X[1] + '_' + X[2] + '_' + X[3]
                            FCname  = X[4] + '_' + X[5]
                            iBay.tIED.append((iIED.name,FCname))
                            print('       '+iIED.name)

            print('xx')

        def add_IED(self, iIED: SCD.SCDNode):
            self.dataKey = iIED.name
            self.line = self.line + 1

            _ied = QTreeWidgetItem(iIED.name, 12, set_bold=True)
            _ied.setFlags(Qt.ItemIsUserCheckable)
            _ied.statusTip(0)
            _ied.setCheckState(0, True)
            _desc = QTreeWidgetItem(iIED.type+"WW", 11, set_bold=False)

            self.treeView.addTopLevelItem(_ied) #, _desc, _toto))
            _ied.setFlags(Qt.ItemIsUserCheckable)

            for iAP in iIED.get_children('AccessPoint'):
                if iAP.name == "ADMINISTRATION_AP":
                    continue
                IP_Adresse = self.getIPadr(iIED.name, iAP.name)
                self.add_AP(_ied, iAP, iIED.name, IP_Adresse)

        def add_AP(self, T_IED: QTreeWidgetItem, iAP: SCD.SCDNode, iedName: str, IP_Adresse):

            _vide =QTreeWidgetItem(" ", 11, set_bold=True)
            _ap  = QTreeWidgetItem(iAP.name, 11, set_bold=True)
            _txt = QTreeWidgetItem(iAP.desc, 11, set_bold=False)
            _ip  = QTreeWidgetItem( IP_Adresse, 11, set_bold=False)
            T_IED.addChild((_ap)) #,_txt,_ip))

#            self.treeView.addTopLevelItems((_ap,_ip)) #, _txt, _ip))
            for iSRV in iAP.get_children('Server'):
                self.add_SRV(_ap, iSRV)

        def add_SRV(self, T_AP: QTreeWidgetItem, iSRV: SCD.SCDNode):

            if hasattr(iSRV, 'timeout'):
                _srv1 = QTreeWidgetItem(('Server, ' + str(iSRV.timeout)), 10, set_bold=True)
            else:
                _srv1 = QTreeWidgetItem('Server', 10, set_bold=True)
            _txt2=  QTreeWidgetItem('Server', 10, set_bold=True)
            T_AP.setText(1, ("DESCRIPTION")) # addTopLevelItems((_ap, _ip, _vide2, _txt))
            T_AP.setText(2, ("XXXXXX"))
            T_AP.addChild(_srv1)  # ,_txt,_ip))
#            self.treeView.addTopLevelItems((_srv1, _txt2))

            for iLD in iSRV.get_children('LDevice'):
                self.add_LD(_srv1, iLD)

        def add_LD(self, T_SRV: QTreeWidgetItem, iLD: SCD.SCDNode):
            ldName = iLD.inst + ', ' + iLD.ldName
            _ldName = QTreeWidgetItem(ldName, 11, set_bold=False)

            _ldName.setFlags(Qt.ItemIsUserCheckable)
            _ldName.setFlags(Qt.ItemIsUserCheckable)
            _ldName.setCheckState(0,True)

            _desc = QTreeWidgetItem(iLD.desc, 11, set_bold=False)
            T_SRV.addChild(_ldName)



if __name__ == '__main__':

    #    TX = Trace.Console(TL.GENERAL)
    tIEDfull = []

    myCpt = 0

    app = QApplication(sys.argv)
    Win = MainWindow()
    demo = Win.AppDemo('SCL_files\SCD_SITE_20200928.scd')
    sys.exit(app.exec_())
