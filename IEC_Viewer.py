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
from IEC61850_XML_Class import DataTypeTemplates as DT

import sys
import textwrap
import PyQt5
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QLineEdit, QLabel, QMessageBox, QMenu,QFrame,QDesktopWidget
from PyQt5.QtWidgets import QDialogButtonBox, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QWidget, QCheckBox, QLabel
from PyQt5.QtWidgets import QFileDialog
from PyQt5.Qt import QStandardItemModel, QStandardItem
from PyQt5.QtGui import QFont, QColor

from PyQt5.QtCore import (QDate, QDateTime, QRegExp, QSortFilterProxyModel, Qt,
                          QTime, QModelIndex, QStringListModel)


from IEC_FileListe import FileListe as FL
from IEC_Trace import Trace
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

class IED_IP:
    def __init__(self,_iedName, _APName, _IP):
        self.iedName = _iedName
        self.APName  = _APName
        self.IP      = _IP

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Sample')

    class AppDemo(QWidget):

        IED_LD, TYPE, VALUE, DESC, DESC2 = range(5)

        def __init__(self, _TL):
            super().__init__()
            self.setWindowTitle('RTE IEC68150 ENGINEERING TOOLS')
            self.resize(800, 900)

            qr = self.frameGeometry()  # geometry of the main window
            cp = QDesktopWidget().availableGeometry().center()  # center point of screen
            qr.moveCenter(cp)  # move rectangle's center point to screen's center point
            self.move(qr.topLeft())  # top left of rectangle becomes top left of window centering it

            self.grid = QGridLayout()
            self.grid = QVBoxLayout()
            self.grid.setSpacing(10)

#            title = QLabel('xxxxxxxxxxxxxx Title xxxxxxxxxxxxxx')
#            self.grid.addWidget(title) #, 0, 0, 1, 3)

    ## Button to access to other functions
            self.OpenFile = QPushButton()
            self.button2 = QPushButton()
            self.button3 = QPushButton()
            self.OpenFile.setText(' SELECT FILE ')
            self.button2.setText(' CHECK VALUE ')
            self.button3.setText(' EDIT  ')
            self.hLayout = QHBoxLayout()
            self.hLayout.addWidget(self.OpenFile)
            self.hLayout.addWidget(self.button2)
            self.hLayout.addWidget(self.button3)
            self.grid.addLayout(self.hLayout)

    ## Tick boxes for filtering for funnctional constraint
#            i = 0

            self.OpenFile.clicked.connect(self.getFile)
            self.frame = QFrame(self)
#            self.frame.setFrameShape(QFrame.StyledPanel)
#            self.frame.setFrameShadow(QFrame.Raised)
            self.frame.setStyleSheet("background-color: rgb(200, 255, 255)")
            self.frame.setStyleSheet("foreground-color: blue;\n")
            self.frame.setFrameStyle(QFrame.Box | QFrame.Sunken)
            self.frame.setLineWidth(4)

            self.hLayoutButtons = QHBoxLayout(self.frame)
            self.hLayoutButtons.addWidget(self.frame)


            self.box      = []
            i = 0
            for fc in DT.FC.lstFC:
                chkbox = QCheckBox(fc,self.frame)
                if i==0 or i==2 or i==4 or i==6:
                    chkbox.setChecked(False)
                else:
                    chkbox.setChecked(True)
                self.box.append(chkbox)
                self.hLayoutButtons.addWidget(chkbox)
                chkbox.stateChanged.connect(lambda:self.butState(chkbox))
                i = i + 1

            self.checkAllButton    = QPushButton("ALL",self.frame)
            self.checkAllButton.clicked.connect(self.selectAll)
            self.hLayoutButtons.addWidget(self.checkAllButton)

            self.checkNoneButton  = QPushButton("None",self.frame)
            self.checkNoneButton.clicked.connect(self.selectNone)
            self.hLayoutButtons.addWidget(self.checkNoneButton)

            self.grid.addLayout(self.hLayoutButtons)
            self.grid.addWidget(self.frame)



            self.application = 'ApplicationName'  ## name A name of the application
            self.TR = _TL  ## Trace Level used
            self.LNodeType = None  ## Access to the LNodeType dictionary
#            self.GM = GM  ## The Global Data Model of the SCL used
            self.FileId = None  ## File ID of the output file
            self.IED_ID = None  ## IED name + AcccessPoint Name

            self.line    = 0
            self.dataKey = ''

            self.t_AdrIP = []

            self.treeView = QTreeView()
            self.treeView.setHeaderHidden(False)

            self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
            self.treeView.customContextMenuRequested.connect(self.openMenu)
            self.treeView.clicked.connect(self.openMenu)

#            model =       QStandardItemModel(list_view)
            self.treeModel = QStandardItemModel(self.treeView)
            self.treeModel.setColumnCount(6)
            #        self.treeModel.setHorizontalHeaderLabels(["IED/AP/SRV/LD/LN", "Desc", "SDO", "", "DA","SDA"])
            self.treeModel.setHeaderData(self.IED_LD, Qt.Horizontal, "IED/AP/SRV/LD")         # 0
            self.treeModel.setHeaderData(self.TYPE,   Qt.Horizontal, "Type")                  # 1
            self.treeModel.setHeaderData(self.VALUE,  Qt.Horizontal, "Value")                 # 2 ==> Read / Write data
            self.treeModel.setHeaderData(self.DESC,   Qt.Horizontal, "Object 'desc'")         # Object 'desc'
            self.treeModel.setHeaderData(self.DESC2,  Qt.Horizontal, "Type 'desc'")           # Data Type Desction

            self.grid.addWidget(self.treeView) #,2,0,1, 10)
            self.rootNode = self.treeModel.invisibleRootItem()

            self.setLayout(self.grid)
            self.show()
            self.treeView.doubleClicked.connect(self.getValue)

            self.treeView.setModel(self.treeModel)
            self.treeView.expandAll()
            self.treeView.setColumnWidth(0, 300)
            self.treeView.setColumnWidth(1, 200)
            self.treeView.setColumnWidth(2, 100)
            self.treeView.setColumnWidth(3, 100)

            return None

        def getFile(self):

            fname = QFileDialog.getOpenFileName(self, 'Open file', 'D:\OneDrive\SCL_GIL\SCL_files\*.*', " IEC61850 files")

            if fname:
                self.GM = globalDataModel(TX, fname[0], None)
                self.DisplayTree(self.GM.tIED,self.GM)
                self.treeView.expandAll()
                self.show()


        def butState(self,box):
            self.rootNode.model().layoutAboutToBeChanged.emit()
#            self.treeView.dataChanged(self)
    #       self.treeView.setModel(self.treeModel)

            self.rootNode.model().layoutChanged.emit()
            self.treeView.setModel(self.treeModel)
            self.treeView.expandAll()
            self.rootNode.removeRows(0,self.rootNode.rowCount())
            self.DisplayTree(self.GM.tIED,self.GM)
            self.treeView.expandAll()
            self.show()

        def selectNone(self):
            for button in self.box:
                if button.isChecked()==True:
                    button.setChecked(False)
#                    button.repaint()           # Affichage progressif...
            self.hLayoutButtons.invalidate()    # Plus lent que button.repaint()

        def selectAll(self):
            for button in self.box:
                if button.isChecked()==False:
                    button.setChecked(True)
 #                   button.repaint()           # Affichage progressif...
            self.hLayoutButtons.invalidate()    # Plus lent que button.repaint()

        def getFC_Checked(self, fc):
            for chkBox in self.box:
                txt = chkBox.text()
                if chkBox.text() == fc:
                    x= chkBox.isChecked()
                    return x

        def DisplayTree(self, tIED, GM):
            #        tIED = GM.tIED
            for iIED in tIED:
                T_IED = self.add_IED(iIED)  # Return the column head
                iedName = iIED.name
                for iAP in iIED.tAccessPoint:
                    T_AP = self.add_AP(T_IED, iAP)
                    apName = iAP.name
                    for iSRV in iAP.tServer:
                        T_SRV = self.add_SRV(T_AP, iSRV)
                        IP_Adr = IED_IP(iedName, apName, iSRV.IP)
                        self.t_AdrIP.append(IP_Adr)

                        for iLD in iSRV.tLDevice:
                            T_LD = self.add_LD(T_SRV, iLD)
                            mmsAdr = iLD.inst
                            for iLN in iLD.LN:
                                T_LN = self.add_LN(T_LD, iLN)

                                for iDO in iLN.tDO:
                                    iDOType = GM.DOType.getIEC_DoType(iDO.type)
                                    if iDOType is None:
                                        break
                                    _DO = self.Insert_DO_DOI(' DO ', T_LN, iDO, iDOType)
                                    if _DO is None:
                                        break
                                    self.add_DO_tDA(_DO, iDO, iLN.tDOI)

        def wrap(self, string, lenght):
            return '\n'.join(textwrap.wrap(string, lenght))

        def add_IED(self,iIED):
            self.dataKey = iIED.name
            self.line    = self.line + 1
            _ied  = StandardItem(iIED.name , 12, set_bold=True)
            _desc = StandardItem(iIED.type , 11, set_bold=False)
            _vide1 = StandardItem('.', 11, set_bold=False)
            _vide2 = StandardItem('.', 11, set_bold=False)

            self.rootNode.appendRow((_ied,_vide1,_vide2, _desc))
            return _ied

        def add_AP(self, T_IED, iAP):
            _ap  = StandardItem(iAP.name, 8, set_bold=False)
            _txt = StandardItem(iAP.desc, 8, set_bold=False)
            _vide1 = StandardItem('.', 11, set_bold=False)
            _vide2 = StandardItem('.', 11, set_bold=False)
            T_IED.appendRow((_ap, _vide1,_vide2, _txt))
            return _ap

        def add_SRV(self, T_AP, iSRV):
            if iSRV.timeout is not None:
                _srv1 = StandardItem(( 'Server,'+ iSRV.IP + ' , ' + iSRV.timeout ), 10, set_bold=True)
            else:
                _srv1 = StandardItem(('Server,' + iSRV.IP ), 10, set_bold=True)

            _vide1 = StandardItem('.', 11, set_bold=False)
            _vide2 = StandardItem('.', 11, set_bold=False)
            _desc = StandardItem(iSRV.desc, 10, set_bold=False)
            T_AP.appendRow((_srv1, _vide1, _vide2, _desc))
            return _srv1

        def add_LD(self, T_SRV, iLD):
            ldName  = iLD.inst + ', ' + iLD.ldName
            _ldName = StandardItem(ldName,    11, set_bold=False)
            _desc   = StandardItem(iLD.desc,  11, set_bold=False)
            _vide1 = StandardItem('.', 11, set_bold=False)
            _vide2 = StandardItem('.', 11, set_bold=False)
            T_SRV.appendRow((_ldName, _vide1, _vide2, _desc))
            return _ldName

        def add_LN(self, T_LD, iLN):
            txtLN = iLN.lnPrefix + iLN.lnClass + iLN.lnInst  # ' + iLD.inst
            _ln = StandardItem(txtLN, 10, set_bold=True)
            _lnClass = StandardItem(iLN.lnClass, 10, set_bold=True)
            _lnDesc = StandardItem(iLN.lnDesc, 10, set_bold=False)
            _vide1 = StandardItem('.', 10, set_bold=False)
            _vide2 = StandardItem('.', 10, set_bold=False)
            T_LD.appendRow((_ln, _lnClass,_vide1, _vide2, _lnDesc))
            return _ln

        def Insert_DO_DOI(self, do_doi, _ln, iDOi, iDOType):

            if iDOType is not None:
    #            print("DOI:" + iDOi.DOname + ',' + iDOi.type + ',' + iDOType.desc)
                _DO       = StandardItem(iDOi.DOname + ', ' + iDOType.cdc + ',' + do_doi + ':' + iDOType.desc, 9, set_bold=True)
                _desc     = StandardItem(iDOi.desc   , 9, set_bold=False)
                _type     = StandardItem(iDOi.type   , 9, set_bold=False)
                _typeDesc = StandardItem(iDOType.desc, 9, set_bold=False)
                if iDOi.value is None:
                    _value = StandardItem('__DO__', 10, set_bold=False)
                else:
                    _value = StandardItem(iDOi.value  , 10, set_bold=False)

                _ln.appendRow((_DO, _type, _value, _desc,_typeDesc))  # , 'xx'))

            else:
                return None
            return  _DO

        def Insert_SDO_DOI(self, _DO, iDO):
            _SDO      = StandardItem(iDO.name, 9, set_bold=True)
            _desc     = StandardItem(iDO.desc   , 9, set_bold=False)
            _type     = StandardItem(iDO.type   , 9, set_bold=False)
    #            _typeDesc = StandardItem(iDOType.desc, 9, set_bold=False)
            if iDO.value is None:
                _value = StandardItem('__DO__', 10, set_bold=False)
            else:
                _value = StandardItem(iDO.value  , 10, set_bold=False)

            _DO.appendRow((_SDO, _type, _value, _desc)) #,_typeDesc))  # , 'xx'))
            return _SDO

        def getDADOName(self, DA_DO):
            if type(DA_DO).__name__ == "DOI":
                name = DA_DO.DOname
            else:
                name = DA_DO.name
            return name
        def checkDODAName(self, DA, DOname):
            DAName = self.getDADOName(DA)
            return DAName == DOname

        def addDA(self, _DO, iDA,tDOI, iDOname ):

            for iDO in tDOI:
                if (iDO.DOname == iDOname):
                    for iDAi in iDO.tDAI:
                        if iDAi.name == iDA.name:
    #                        print("DAI for:"+iDO.DOname + '.' + iDAi.name + iDAi.value)
                            iDA.value = iDAi.value

    #                try:
    #                    for iSDI in iDO.tSDI1:
    #                        print(".................SDI for:"+iSDI.SDIname)
    #                except:
    #                    pass

            if iDA.bType != 'Struct':
                self.addDA_DA(_DO, iDA, iDA)
            else:
                if self.getFC_Checked(iDA.fc):
                    _DA   = StandardItem(iDA.name + '[' + iDA.fc + ']', 10, set_bold=True)
                    _Type = StandardItem(iDA.bType, 10, set_bold=False)
                    _value =StandardItem(iDA.value, 10, set_bold=False)
                    _desc = StandardItem(iDA.desc , 10, set_bold=False)
                    _DO.appendRow((_DA, _Type, _value, _desc))
                    if iDA.bType == 'Struct':
                        iDA = self.GM.DAType.getIEC_DaType(iDA.type)
                        self.Structure(_DA, iDA)

        #    def addSDI(self, _DO, SDI_name):
    #        _name  = StandardItem(SDI_name, 10, set_bold=True)
    #        _DO.appendRow((_name))
    #        return _name

        def add_DO_tDA(self, _DO, iDO, tDOI):
            for iDA in iDO.tDA:
                if iDA.do_sdo == 'SDO':

                    _SDO = self.Insert_SDO_DOI(_DO, iDA)
                    instDO = self.GM.DOType.getIEC_DoType(iDA.type)
                    for iDA in instDO.tDA:
                        self.addDA(_SDO,iDA,tDOI,iDO.DOname)
                else:
                   self.addDA(_DO,iDA,tDOI,iDO.DOname)

        def addDA_DA(self, _DO, iDA,daType):
            if not self.getFC_Checked(iDA.fc):
                return

            _DA = StandardItem(iDA.name + ' [' + iDA.fc +' ] ', 9, set_bold=False)
            _DAtype_desc = StandardItem(iDA.desc + '[' + daType.desc + ']', 9, set_bold=False)
            _DA_value    = StandardItem(iDA.value, 9, set_bold=False)
            _DA_desc     = StandardItem(iDA.desc , 9, set_bold=False)
            if daType.bType == 'Enum':

                name = StandardItem('Enum [' + iDA.type + ']', 8, set_bold=False)
                value = StandardItem(iDA.value, 8, set_bold=False)
                desc  = StandardItem(iDA.desc,  8, set_bold=False)
                _DO.appendRow((_DA, name, value, desc))

            elif daType.bType == 'Struct':
                _DA_type = StandardItem(iDA.bType + '(' + iDA.type + ')', 10, set_bold=False)
                _DO.appendRow((_DA, _DA_type, DA_value, _DA_desc ))
            else:
                _DA_type = StandardItem(iDA.bType , 9, set_bold=False)
                _DO.appendRow((_DA, _DA_type, _DA_value, _DA_desc, _DAtype_desc))

            return

        def EnumerationFull(self, DaName, typeEnum, _DA):
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
            _EnumVal = StandardItem(self.wrap(iEnumTxt, 100), 8, set_bold=False)
            return ((_DA_Name, _EnumVal))

        def Structure(self, _DA,  iDA ):

            for jDA in iDA.tBDA:
                _SDA   = StandardItem(jDA.name , 8, set_bold=False)
                _type  = StandardItem(jDA.type , 8, set_bold=False)
                _value = StandardItem(jDA.value, 8, set_bold=False)

                if jDA.type == 'Enum':
    ##                (name, id) = self.Enumeration('Enum Structure ( '+jDA.bType+ ') ', _SDA)
                    name  = StandardItem( 'Enum(s) ('+jDA.bType + ')' , 8, set_bold=False)
                    value = StandardItem( jDA.value , 8, set_bold=False)
                    _DA.appendRow((_SDA, name, value))
                    continue

                _DA.appendRow((_SDA, _type, _value))

                if jDA.type == 'Struct':
                    subDAType = self.GM.DAType.getIEC_DaType(jDA.bType)
                    self.Structure(_SDA, subDAType)

        def msgbtn(i):
            print("Button pressed is:", i.text())

        def findDOI(self, iLN, do_name):

            try:
                for iDOi in iLN.tDOI:
                    if iDOi.DOname == do_name:
                        return iDOi
            except:
                print ("do_name:", do_name)
            return None

        def findDAI(self, iDO, da_name):
            for iDAi in iDO.tDAI:
                if iDAi.name == da_name:
                    return iDAi
            return None

        def findDA(self, iDO, da_name):
            for iDA in iDO.tDA:
                if iDA.name == da_name:
                    return iDA
            return None


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
    TX = Trace(TL.DETAIL, "Trace_FctTst.txt")
    tIEDfull = []

    myCpt = 0


    app = QApplication(sys.argv)
    Win = MainWindow()
    demo = Win.AppDemo(TX)
    demo.show()
    sys.exit(app.exec_())

MainWindow