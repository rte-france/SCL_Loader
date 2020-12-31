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

from scl_loader import SCD_handler

import sys
import os
import time
import textwrap

from PyQt5.QtWidgets import QMainWindow,QApplication,QDesktopWidget,QVBoxLayout,QHBoxLayout, QTableWidget, QTableWidgetItem
from PyQt5.QtWidgets import QFileDialog,QTableView,QWidget,QPushButton,QFrame,QCheckBox,QTreeView,QMessageBox
from PyQt5.Qt        import QStandardItemModel, QStandardItem, QThread, Qt
from PyQt5.QtGui import QFont, QColor

#                          QTime, QModelIndex, QStringListModel)

IED_LD, TYPE, VALUE, DESC, DESC2 = range(5)


class LoadSCL(object):
    def __init__(self,fname):
        print("init")
        self.fname=fname
        self.T0 = time.time()
    def __enter__(self):
        HERE = os.path.abspath(os.path.dirname(__file__))
        filepath = os.path.join(HERE, self.fname[0])
        self.sclMgr = SCD_handler(filepath, True)
        self.T1  = time.time()
        self.delta = self.T1-self.T0
        return (self.sclMgr,self.delta)

    def __exit__(self,  exc_type, exc_val, exc_tb):
        print("SCL loaded with success")
#        return(self.T1 - self.T0)

class StandardItem(QStandardItem):

    def __init__(self, txt='', font_size=12, set_bold=False, color=QColor(0, 0, 0)):
        super().__init__()

        fnt = QFont('Open Sans', font_size)
        fnt.setBold(set_bold)

        self.setEditable(False)  # Permet l'édition de la cellule.
        self.setForeground(color)
        self.setFont(fnt)
        self.setText(txt)
        self.layoutMainView = None
        self.nameMainView   = 'DataModel'

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Sample')

    class AppDemo(QWidget):

        def __init__(self):
            super().__init__()
            self.setWindowTitle('RTE IEC68150 ENGINEERING TOOLS')
            self.resize(800, 900)
            self.line = 0
            self.dataKey = ''
            self.fname = None
            self.tIED = []

            self.fname = []

            qr = self.frameGeometry()  # geometry of the main window
            cp = QDesktopWidget().availableGeometry().center()  # center point of screen
            qr.moveCenter(cp)  # move rectangle's center point to screen's center point
            self.move(qr.topLeft())  # top left of rectangle becomes top left of window centering it

            self.winLayout = QVBoxLayout()           ## Most the HMI is vertical
            self.winLayout.setSpacing(10)

            AppButtons = self.ApplicationButtons()      # Top application button (TEMPLATE, SELECT FILE)
            self.winLayout.addLayout(AppButtons)


## MAIN VIEW, start with treeView

            self.treeLayout = QVBoxLayout()
            self.nameMainView = 'DataModel'

            self.ButtonSection,self.frameLeft = self.leftButtons()

            self.containerLayout= QHBoxLayout()                     # Container for 2 vertical layout
            self.containerLayout.addLayout(self.ButtonSection)      # Set of buttons on the LEFT
            self.containerLayout.addWidget(self.frameLeft)          # Set the frame

            self.setLayout(self.winLayout)
## Creation of all widgets

## Initial View is Data Model
            self.datatype = DataType_Table(self.winLayout, self.containerLayout)

## Initial View is Data Model
            self.DataModelTree = DataModelTree(self.winLayout, self.containerLayout)
            self.FT_frame = self.datatype.DataTypeButtons(self.winLayout, self.DataModelTree.FC_frame)

            self.treeView , self.treeModel   = self.DataModelTree.CreateTreeView()
            self.FC_frame = self.DataModelTree.FCbuttons(self.winLayout, self.datatype.DT_frame)

            self.tableView  = None
            self.ShowDataModel()

            self.winLayout.addLayout(self.containerLayout)               # Finally add this to the globalLayout
            self.setLayout(self.winLayout)
            self.show()

        ## CheckValue, Template, LoadFile
        def ApplicationButtons(self):
            ## Layout for the set of action buttons
            hLayout = QHBoxLayout()

            ## Check Value Button
            CheckValue = QPushButton()
            CheckValue.setText(' CHECK VALUE ')
            CheckValue.clicked.connect(self.ExecCheckValue)
            hLayout.addWidget(CheckValue)

            ##  Template Generation Button
            template = QPushButton()
            template.setText(' TEMPLATE ')
            template.clicked.connect(self.ExecTemplate)
            hLayout.addWidget(template)

            ##  Open File  Button
            OpenFile = QPushButton()
            OpenFile.setText(' SELECT FILE ')
            OpenFile.clicked.connect(self.getFile)
            hLayout.addWidget(OpenFile)

            ## Add horizontal layout of buttons to the grid layout.
            return hLayout

        ## Call Back Functions for vertical Buttons
        def ShowDataModel(self):
            print('Data Model Button')
            self.MainView = 'DataModel'

            self.commuteView(self.winLayout, self.FT_frame, self.FC_frame,"Data Type" , "Function Constraint")

            try:
                if self.datatype.currentView == LNODETYPE:
                    self.commuteView(self.containerLayout, self.datatype.LNtableView, self.treeView, LNODETYPE,"TreeView")
                elif self.datatype.currentView == DOTYPE:
                    self.commuteView(self.containerLayout, self.datatype.DOTypeView,  self.treeView, DOTYPE,   "TreeView")
                elif self.datatype.currentView == DATYPE:
                    self.commuteView(self.containerLayout, self.datatype.DATypeView,  self.treeView, DATYPE,   "TreeView")
                elif self.datatype.currentView == ENUMTYPE:
                    self.commuteView(self.containerLayout, self.datatype.EnumTypeView,self.treeView, ENUMTYPE, "TreeView")
            except:
                print("Not initialized")
                pass

            self.containerLayout.update()
            self.treeView.repaint()
            self.treeView.show()

        def ShowCommunication(self):
            print('Show Communication Button')

        def ShowDataType(self):
            print('ShowDataType Button')

            self.MainView = 'DataType'
            if self.tableView is not None:
                self.tableView.setVisible(False)
                self.datatype.DisplayTableLNODE()
                return

            self.commuteView(self.winLayout,      self.FC_frame, self.FT_frame,"Function Constraint", "Data Type")

            if self.datatype.currentView == LNODETYPE:
                self.commuteView(self.containerLayout,self.treeView, self.datatype.LNtableView,"TreeView",LNODETYPE)
            elif self.datatype.currentView == DOTYPE:
                self.commuteView(self.containerLayout,self.treeView, self.datatype.DOTypeView,"TreeView",DOTYPE)
            elif self.datatype.currentView == DATYPE:
                self.commuteView(self.containerLayout,self.treeView, self.datatype.DATypeView,"TreeView", DATYPE)
            elif self.datatype.currentView == ENUMTYPE:
                self.commuteView(self.containerLayout,self.treeView, self.datatype.EnumTypeView,"TreeView",ENUMTYPE)

        def commuteView(self, Layout, ViewFrom, ViewTo, NameFrom, NameTo):
            print("Replace view:" + NameFrom + " by view to" + NameTo)

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
#            self.currentView = NameTo

        def setTableViewLnode(self):
            if self.nameMainView == 'DataType':
                print('Table View already active')
                return

        ## Buttons: Data Model, Communication, Data Type [Horizontal Layout]
        def leftButtons(self):

            Left_frame = QFrame(self)
            #            self.frame.setFrameShape(QFrame.StyledPanel)
            #            self.frame.setFrameShadow(QFrame.Raised)
            Left_frame.setLineWidth(4)
            Left_frame.setStyleSheet("background-color: rgb(200, 255, 255)")
            Left_frame.setStyleSheet("foreground-color: blue;\n")
            Left_frame.setFrameStyle(QFrame.Box | QFrame.Sunken)

            LeftButtons = QVBoxLayout(Left_frame)
            LeftButtons.addWidget(Left_frame)

            ## Check Value Button
            DataModel = QPushButton()
            DataModel.setText(' DATA MODEL ')
            DataModel.clicked.connect(self.ShowDataModel)
            LeftButtons.addWidget(DataModel)

            ##  Template Generation Button
            Communication = QPushButton()
            Communication.setText(' COMMUNICATION ')
            Communication.clicked.connect(self.ShowCommunication)
            LeftButtons.addWidget(Communication)

            ##  Open File  Button
            DataType = QPushButton()
            DataType.setText(' DATA TYPE ')
            DataType.clicked.connect(self.ShowDataType)
            LeftButtons.addWidget(DataType)

            return LeftButtons,Left_frame


        def ExecCheckValue(self):
            print('Check Value Button')

        def ExecTemplate(self):

            if self.fname is not None:
                print('Launch Template Generation')
                CG = CodeGeneration("CodeGeneration","FctTemplate",self.sclMgr)
                CG.GenerateTemplate(self.fname[0],self.tIED)

            else:
                msg = QMessageBox()
                msg.setWindowTitle("Alert")
                msg.setText("You need to load file first")
                x= msg.exec_()

        def getFile(self):

            self.fname = QFileDialog.getOpenFileName(self, 'Open file', 'D:\OneDrive\SCL_View\SCL_files\*.*',
                                         " IEC61850 files")

            with LoadSCL(self.fname) as (sclMgr,delta):   #, self.T_LoadSCL):
                print("Chargement SCL initial:")         # str(self.T_LoadSCL))

            print("Chargement all IED       :")
            self.treeView.setUpdatesEnabled(False)
            self.tIED =  sclMgr.get_all_IEDs()
            T2 = time.time()

#            class DataType_Table:
#                def __init__(self, _containerLayout):
            self.datatype.Initialize(sclMgr)

            self.DataModelTree.DisplayTree(self.tIED)

            self.treeView.expandAll()
            self.treeView.setUpdatesEnabled(True)
            self.show()

        def wrap(self, string, lenght):
            return '\n'.join(textwrap.wrap(string, lenght))

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
#            print(col1, col2, data)

    ### KEEP
    #        for ix in indexes:
    #            text = ix.data()
    #            print ('==> ' + text)
    #        print(self.treeView.sel)

    #        if len(indexes) > 0:
    #           level = 0
    # KEEP
            index = indexes[0]

            path = ''
            while index.parent().isValid():
                item = index.data()
                _item = item.split(',')
                IECitem = _item[0]
                path =  IECitem + '.' + path
                index = index.parent()

            path = index.data() + '.' + path    # Insert last Data bit.
##            print ("Path:" +   path)
            act_IED=0
            act_TypeDefinition = 1
            act_ReadWriteData = 2
            menu = QMenu()
            if col1 == 0:          ## data path
                act_IED =menu.addAction(self.tr(" IED "))
    #            info = InfoIPAdr()
            elif col1  == 1:        ## Server
                act_TypeDefinition =menu.addAction(self.tr(" Type definition "))
            elif col2 == 2:
                act_ReadWriteData =menu.addAction(self.tr(" Read Write DATA "))
    #            info = InfoIPAdr()
    #            info.initUI(self.t_AdrIP) # self.tIP_Adr
    #        elif level == 3:
    #            menu.addAction(self.tr(" Logical Device"))
    #        elif level == 5:
    #            menu.addAction(self.tr(" Logical Node"))
    #        elif level == 6:
    #            menu.addAction(self.tr(" Data Object"))
    #            info = InfoIPAdr()
    #        elif level == 7:
    #            menu.addAction(self.tr(" Data Attribute"))

            action = menu.exec_(self.treeView.viewport().mapToGlobal(value))
            if action == act_IED:
                print("IED information")
            if action == act_TypeDefinition:
                print("Defition du type")
            if action == act_ReadWriteData:
                print("Read Write DATA")

        def getValue(self, val):
            indexes = self.treeView.selectedIndexes()

            for ix in indexes:
                text = ix.data()
                print('==> ' + text)

            print(val.data())
            print(val.row())
            print(val.column())


if __name__ == '__main__':

    #    TX = Trace.Console(TL.GENERAL)
    tIEDfull = []

    myCpt = 0

    app = QApplication(sys.argv)
    Win = MainWindow()
    demo = Win.AppDemo()
    demo.show()
    sys.exit(app.exec_())

