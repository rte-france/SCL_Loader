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

from PyQt5.Qt     import QStandardItemModel, QStandardItem,QFrame,QCheckBox,QPushButton, QHBoxLayout, QVBoxLayout, QTreeView
from PyQt5.QtGui  import QFont, QColor
from PyQt5.QtCore import Qt

import logging
import re
import scl_loader as SCD
from IEC61850_XML_Class import DataTypeTemplates as DT

from scl_loader import *
from PyQt5.QtWidgets import QMainWindow

IED_LD, TYPE, VALUE, DESC, DESC2 = range(5)

REG_DO = r'(?:\{.+\})?S?DO'
REG_DA = r'(?:\{.+\})?[BS]?DA'

DOmatch = {'DO', 'SDO'}
DAmatch = {'DA', 'BDA','SDA'}
LOGGER = logging.getLogger(__name__)

class IED_IP:
    def __init__(self,_iedName, _APName, _IP):
        self.iedName = _iedName
        self.APName  = _APName
        self.IP      = _IP

class StandardItem(QStandardItem):
    def __init__(self, txt='', font_size=12, set_bold=False, color=QColor(0, 0, 0)):
        super().__init__()

        fnt = QFont('Open Sans', font_size)
        fnt.setBold(set_bold)

        self.setEditable(False)  # Permet l'édition de la cellule.
        self.setForeground(color)
        self.setFont(fnt)
        self.setText(txt)

class DataModelTree():
    def __init__(self, _winLayout, _containerLayout, parent=None) :
        self.t_AdrIP    = []
        self.line       = 0
        self.containerLayout = _containerLayout
        self.winLayout  = _winLayout
        self.box = []
        self.FC_frame   = self.FCbuttons(self.winLayout, None)  # Functional Constraint Selection buttons
        self.treeView   = None
        self.treeLayout = None
        self.treeModel  = None

    def CreateTreeView(self):

        self.treeLayout = QVBoxLayout()
        self.containerLayout.addLayout(self.treeLayout)         # add the Tree View

        self.treeView = QTreeView()
        self.treeView.setHeaderHidden(False)
        self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.openMenu)
        self.treeView.clicked.connect(self.openMenu)

        self.treeModel = QStandardItemModel(self.treeView)
        self.treeModel.setColumnCount(6)
        self.treeModel.setHeaderData(IED_LD, Qt.Horizontal, "IED/AP/SRV/LD")         # 0
        self.treeModel.setHeaderData(TYPE,   Qt.Horizontal, "Type")                  # 1
        self.treeModel.setHeaderData(VALUE,  Qt.Horizontal, "Value")                 # 2 ==> Read / Write data
        self.treeModel.setHeaderData(DESC,   Qt.Horizontal, "Object 'desc'")         # Object 'desc'
        self.treeModel.setHeaderData(DESC2,  Qt.Horizontal, "Type 'desc'")           # Data Type Desction

        self.treeView.doubleClicked.connect(self.getValue)

        self.treeView.setModel(self.treeModel)
        self.treeView.expandAll()
        self.treeView.setColumnWidth(0, 300)
        self.treeView.setColumnWidth(1, 200)
        self.treeView.setColumnWidth(2, 100)
        self.treeView.setColumnWidth(3, 100)

        self.treeLayout.addWidget(self.treeView)
        self.rootNode = self.treeModel.invisibleRootItem()
        return self.treeView, self.treeModel

    def openMenu(self, value):
        return
        x=value.x()
        y=value.y()

    def getValue(self, val):
        indexes = self.treeView.selectedIndexes()

        for ix in indexes:
            text = ix.data()
            print('==> ' + text)

        print(val.data())
        print(val.row())
        print(val.column())

    ## Functional selection buttons
    def FCbuttons(self, winLayout, DT_frame):
        self.FC_frame = QFrame()
        self.FC_frame.setLineWidth(4)
        self.FC_frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.FC_frame.setStyleSheet("QFrame {background-color: rgb(200, 255, 255);"
                            "border-width: 2;"
                            "border-radius: 6;"
                            "border-style: solid;"
                            "border-color: rgb(10, 10, 10)}"
                            )
        self.hLayoutButtons = QHBoxLayout(self.FC_frame)

        i = 0
        for fc in DT.FC.lstFC:
            chkbox = QCheckBox(fc, self.FC_frame)
            chkbox.setChecked(True)
            self.box.append(chkbox)
            self.hLayoutButtons.addWidget(chkbox)
            chkbox.stateChanged.connect(lambda: self.butState(chkbox))
            i = i + 1

        checkAllButton = QPushButton("ALL", self.FC_frame)
        checkAllButton.clicked.connect(self.selectAll)
        self.hLayoutButtons.addWidget(checkAllButton)

        checkNoneButton = QPushButton("None", self.FC_frame)
        checkNoneButton.clicked.connect(self.selectNone)
        self.hLayoutButtons.addWidget(checkNoneButton)

        if DT_frame is None:        ## Initial View case.
            self.winLayout.addLayout(self.hLayoutButtons)
            self.winLayout.addWidget(self.FC_frame)
            return self.FC_frame

##      IF not in initial case, need to replace widget.

        DT_frame.setVisible(False)
        self.FC_frame.setVisible(True)
        self.FC_frame.setUpdatesEnabled(True)
        self.winLayout.addWidget(self.FC_frame)

        Result = self.winLayout.replaceWidget(DT_frame, self.FC_frame, Qt.FindChildrenRecursively)

#        if Result is not None:
#            print(type(Result))
#        print('Result_3:', Result)
        self.FC_frame.repaint()
        self.FC_frame.show()
        return  self.FC_frame

    def butState(self,box):
        try:
            X = self.tIED
        except:
            print(" IED not loaded yet")
            return
            pass

        self.rootNode.model().layoutAboutToBeChanged.emit()

        self.rootNode.model().layoutChanged.emit()
        self.treeView.setModel(self.treeModel)
        self.treeView.expandAll()
        self.rootNode.removeRows(0,self.rootNode.rowCount())

        self.DisplayTree(self.tIED)
        self.treeView.expandAll()
        self.treeView.update()
        self.treeView.repaint()

    def selectNone(self):
        for button in self.box:
            if button.isChecked() == True:
                button.setChecked(False)
        #                    button.repaint()           # Affichage progressif...
        self.FC_frame.repaint()
        self.FC_frame.show()
        self.hLayoutButtons.invalidate()  # Plus lent que button.repaint()

    def selectAll(self):
        for button in self.box:
            if button.isChecked() == False:
                button.setChecked(True)
        #                   button.repaint()           # Affichage progressif...
        self.FC_frame.repaint()
        self.FC_frame.show()
        self.hLayoutButtons.invalidate()  # Plus lent que button.repaint()

    def getFC_Checked(self, fc):
        for chkBox in self.box:
            if chkBox.text() == fc:
                x = chkBox.isChecked()
                return x
#
    def DisplayTree(self, tIED, ProcessAP):
        self.tIED = tIED    ## Required for buttons.
        for iIED in tIED:
            T_IED = self.add_IED(iIED ,ProcessAP)  # Return the column head

    def check_DO_SDO(self, tag):
        return re.fullmatch(REG_DO, tag)
##        return tag in DOmatch

    def check_DA_SDA_DAI(self, tag):
        return re.fullmatch(REG_DA, tag)
##        return tag in DAmatch
 ##      re.fullmatch(REG_DA, tag)

    def add_IED(self, iIED: SCD.SCDNode, ProcessAP):
        self.dataKey = iIED.name
        self.line = self.line + 1
        _ied = StandardItem(iIED.name, 12, set_bold=True)
        _desc = StandardItem(iIED.type, 11, set_bold=False)
        _vide1 = StandardItem('.', 11, set_bold=False)
        _vide2 = StandardItem('.', 11, set_bold=False)
        for iAP in iIED.get_children('AccessPoint'):
            IPadr = 'TbD'
            try:
                tP = eval('ProcessAP' + '.' + iIED.name + '.Address.P')
                for iP in tP:
                    if iP.type == 'IP':
                        IPadr = '[' + iP.Val + ']'
                        self.rootNode.appendRow((_ied, _vide1, _vide2, _desc))
                        self.add_AP(_ied, iAP, iIED.name, IPadr)
                        print('IP:'+iP.Val)
                        break
    #            IP_Adr = IED_IP(iedName, apName, ip)
    #            self.t_AdrIP.append(IP_Adr)

            except Exception as e:
                print("Pas d'adresse IP", e)


    def add_AP(self, T_IED: StandardItem, iAP: SCD.SCDNode, iedName: str, ipAdr: str):
        _ap = StandardItem(iAP.name, 8, set_bold=False)
        _txt = StandardItem(iAP.desc, 8, set_bold=False)
        _ip  = StandardItem(ipAdr, 11, set_bold=False)
        _vide2 = StandardItem('.', 11, set_bold=False)
        T_IED.appendRow((_ap, _ip, _vide2, _txt))

        for iSRV in iAP.get_children('Server'):
            self.add_SRV(_ap, iSRV, iedName, iAP.name)

    def add_SRV(self, T_AP: StandardItem, iSRV: SCD.SCDNode, iedName: str, apName: str):

        if hasattr(iSRV, 'timeout'):
            _srv1 = StandardItem(('Server, ' + str(iSRV.timeout)), 10, set_bold=True)
        else:
            _srv1 = StandardItem('Server,', 10, set_bold=True)

        _vide1 = StandardItem('.', 11, set_bold=False)
        _vide2 = StandardItem('.', 11, set_bold=False)
        _desc = StandardItem(iSRV.desc, 10, set_bold=False)
        T_AP.appendRow((_srv1, _vide1, _vide2, _desc))

        for iLD in iSRV.get_children('LDevice'):
            self.add_LD(_srv1, iLD)

    def add_LD(self, T_SRV: StandardItem, iLD: SCD.SCDNode):
        ldName = iLD.inst + ', ' + iLD.ldName
        _ldName = StandardItem(ldName, 11, set_bold=False)
        _desc = StandardItem(iLD.desc, 11, set_bold=False)
        _vide1 = StandardItem('.', 11, set_bold=False)
        _vide2 = StandardItem('.', 11, set_bold=False)
        T_SRV.appendRow((_ldName, _vide1, _vide2, _desc))

        if hasattr(iLD, 'LLN0'):
            self.add_LN(_ldName, iLD.LLN0)
        elif hasattr(iLD, 'LN0'):
            self.add_LN(_ldName, iLD.LN0)
        for iLN in iLD.get_children('LN'):
            self.add_LN(_ldName, iLN)

    def add_LN(self, T_LD: StandardItem, iLN: SCD.SCDNode):
        txtLN = (iLN.lnPrefix or '') + (iLN.lnClass or '') + str(iLN.inst or '')  # ' + iLD.inst
        _ln = StandardItem(txtLN, 10, set_bold=True)
        _lnClass = StandardItem(iLN.lnClass, 10, set_bold=True)
        _lnDesc = StandardItem(iLN.lnDesc, 10, set_bold=False)
        _vide1 = StandardItem('.', 10, set_bold=False)
        _vide2 = StandardItem('.', 10, set_bold=False)
        T_LD.appendRow((_ln, _lnClass, _vide1, _vide2, _lnDesc))

        if iLN.lnClass == 'LLN0':
            inputs = iLN.get_children('Inputs')
#            try:
#                tExtRefs = inputs[0] #.get_children('ExtRef')
#                _ExtRef = tExtRefs.ExtRef
#                for iExtRef in _ExtRef:
#                    print (iExtRef.iedName, iExtRef.doName)
#            except:
#                print("xx")
#                pass


        for iDO in iLN.get_children('DO'):
            self.add_SDI(_ln, iDO)

    def add_SDI(self, parent_item: StandardItem, iDI: SCD.SCDNode, is_parent_struct: bool = False):
        try:
            fc = iDI.fc
            if self.getFC_Checked(iDI.fc) == False:
                return
        except:
            pass

        _DI = None
        _type = None
        font_size = 9
        if is_parent_struct:
            font_size = 8

        if self.check_DO_SDO(iDI.tag):  ## re.fullmatch(REG_DO, iDI.tag):
            di_txt = '{}, {}, DO : '.format(iDI.name, iDI.cdc)
            _DI = StandardItem(di_txt, font_size, set_bold=True)
            _type = StandardItem(iDI.type, font_size, set_bold=False)
        elif self.check_DA_SDA_DAI(iDI.tag) and iDI.bType == 'Struct': # and not is_parent_struct: ## re.fullmatch(REG_DA, iDI.tag)
            fc = iDI.fc
            if fc is None:
                di_txt = '{} : '.format(iDI.name)
            else:
                di_txt = '{} [{}]: '.format(iDI.name, fc)
            _DI = StandardItem(di_txt, font_size, set_bold=False)
            _type = StandardItem(iDI.bType + ':' + iDI.type, font_size, set_bold=False)
        else:
            di_txt = '{}: '.format(iDI.name)
            _DI     = StandardItem(di_txt, font_size, set_bold=False)
            _type   = StandardItem('Struct', font_size, set_bold=False)

        _desc = StandardItem(iDI.desc, font_size, set_bold=False)
        _vide1 = StandardItem(' -****- ', font_size, set_bold=False)

        if hasattr(iDI, 'Val') and iDI.Val is not None:
            _value = StandardItem(str(iDI.Val), font_size, set_bold=False)
        else:
            _value = StandardItem('.', font_size, set_bold=False)

        parent_item.appendRow((_DI, _type, _value, _desc, _vide1))

        for child in iDI.get_children():
            if self.check_DO_SDO(child.tag):                                ###  re.fullmatch(REG_DO, child.tag):
                self.add_SDI(_DI, child, is_parent_struct)
            elif self.check_DA_SDA_DAI(child.tag)  and child.bType == 'Struct': ### re.fullmatch(REG_DA, child.tag)
                self.add_SDI(_DI, child, is_parent_struct)
            elif self.check_DA_SDA_DAI(child.tag):                           ### re.fullmatch(REG_DA, child.tag):
                self.add_leaf(_DI, child, is_parent_struct)

    def add_leaf(self, parent_item: StandardItem, iLeaf: SCD.SCDNode, is_parent_struct: bool):

        fc = iLeaf.fc
        if self.getFC_Checked(fc) == False:
           return

        if fc is not None:
            di_txt = '{} [{}]: '.format(iLeaf.name, fc)
        else:
            di_txt = ' {}:'.format(iLeaf.name)
            pass

        font_size = 9
        if is_parent_struct:
            font_size = 8

        _DA = StandardItem(di_txt, font_size, set_bold=False)
        try:
            txt= iLeaf.bType
            _type = StandardItem(txt, font_size, set_bold=False)
        except:
            _type = StandardItem(iLeaf.name, font_size, set_bold=False)

        _desc = StandardItem(iLeaf.desc, font_size, set_bold=False)
        _vide1 = StandardItem('.', font_size, set_bold=False)

        if hasattr(iLeaf, 'Val') and iLeaf.Val is not None:
            _value = StandardItem(str(iLeaf.Val), font_size, set_bold=False)
            value = iLeaf.Val
        else:
            _value = StandardItem('.', font_size, set_bold=False)
        parent_item.appendRow((_DA, _type, _value, _desc, _vide1))

        name = iLeaf.name
        mms = []
        while iLeaf is not None:
            fc=None
            try:
                fc = iLeaf.fc
            except AttributeError:
                mms.insert(0, iLeaf.name)
            else:
                if fc is not None:
                    mms.insert(0, iLeaf.name+'[' + fc + ']')
                else:
                    mms.insert(0, iLeaf.name)
            try:
                iLeaf = iLeaf.parent()
            except:
                break

