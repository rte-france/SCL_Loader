
from IEC61850_XML_Class import IED

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView
from PyQt5.Qt import QStandardItemModel, QStandardItem
from PyQt5.QtGui import QFont, QColor

from PyQt5.QtCore import (QDate, QDateTime, QRegExp, QSortFilterProxyModel, Qt,
                          QTime)


class StandardItem(QStandardItem):
    def __init__(self, _Line, _Column, txt='', font_size=12, set_bold=False, color=QColor(0, 0, 0)):
        super().__init__()

        fnt = QFont('Open Sans', font_size)
        fnt.setBold(set_bold)

        self.setEditable(False)
        self.setForeground(color)
        self.setFont(fnt)
        self.setText(txt)
        self.Line   = _Line
        self.column = _Column
#        self.value  = txt

class InitData():
    def __init__(self):

        IED1 = IED("IED1", "Protection", "Test View", "V1.0", "V1.0", "V2.0", 'RTE", "-', "gilles", None,None,None,None,None)
        IED2 = IED("IED2", "Protection", "Test View", "V1.0", "V1.0", "V2.0", 'RTE", "-', "gilles", None,None,None,None,None)
        IED3 = IED("IED3", "Protection", "Test View", "V1.0", "V1.0", "V2.0", 'RTE", "-', "gilles", None,None,None,None,None)
        IED4 = IED("IED4", "Protection", "Test View", "V1.0", "V1.0", "V2.0", 'RTE", "-', "gilles", None,None,None,None,None)

        AP = IED.AccessPoint("AP1" ,"Server", "No", "PTP")

        IED1.tAccessPoint.append(AP)
        IED2.tAccessPoint.append(AP)
        IED3.tAccessPoint.append(AP)
        IED4.tAccessPoint.append(AP)

        SRV = IED.AccessPoint.Server("Server A","100")

        IED1.tAccessPoint[0].tServer.append(SRV)
        IED2.tAccessPoint[0].tServer.append(SRV)
        IED3.tAccessPoint[0].tServer.append(SRV)
        IED4.tAccessPoint[0].tServer.append(SRV)

        LD1 = IED.AccessPoint.Server.LDevice("A", "Protection"  , "Test view")
        LD2 = IED.AccessPoint.Server.LDevice("A", "Mesure"      , "Test view")
        LD3 = IED.AccessPoint.Server.LDevice("A", "Test"        , "Test view")
        LD4 = IED.AccessPoint.Server.LDevice("A", "Automation"  , "Test view")
        LD5 = IED.AccessPoint.Server.LDevice("A", "Supervision" , "Test view")

        tLD=[]
        tLD.append(LD1)
        tLD.append(LD2)
        tLD.append(LD3)
        tLD.append(LD4)
        tLD.append(LD5)

        IED1.tAccessPoint[0].tServer[0].tLDevice = tLD
        IED2.tAccessPoint[0].tServer[0].tLDevice = tLD
        IED3.tAccessPoint[0].tServer[0].tLDevice = tLD
        IED4.tAccessPoint[0].tServer[0].tLDevice = tLD

        tIED = []
        tIED.append(IED1)
        tIED.append(IED2)
        tIED.append(IED3)
        tIED.append(IED4)

        self.IED = tIED

class AppDemo(QMainWindow):
    IED_LD, LN, DO, SDO, DA, SDA = range(6)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('IEC browser')
        self.resize(500, 700)


        tIED = InitData()

        treeView = QTreeView()
        treeView.setHeaderHidden(False)

        treeModel = QStandardItemModel(0,5)
        treeModel.setColumnCount(6)
        treeModel.setHorizontalHeaderLabels(["IED/AP/SRV/LD/LN", "DO","SDO", "", "DA","SDA"])
        treeModel.setHeaderData(self.IED_LD ,  Qt.Horizontal, "IED/AP/SRV/LD")
        treeModel.setHeaderData(self.LN     ,  Qt.Horizontal, "LN")
        treeModel.setHeaderData(self.DO     ,  Qt.Horizontal, "DO")
        treeModel.setHeaderData(self.SDO    ,  Qt.Horizontal, "SDO")
        treeModel.setHeaderData(self.DA     ,  Qt.Horizontal, "DA")

        rootNode = treeModel.invisibleRootItem()

        cptObjet=0
        Line= 0
        for i in range(0, len(tIED.IED)):
            iIED = tIED.IED[i]
            txt =   iIED.name + ',' + iIED.type + ',' + iIED.desc
            _ied =  StandardItem(Line, 0,txt, 12, set_bold=True)
            rootNode.appendRow(_ied)
            Line = Line + 1
            for j in range (0, len(iIED.tAccessPoint)):
                iAP = iIED.tAccessPoint[j]
                txt = iAP.name + ',' + iAP.desc
                _ap = StandardItem(Line, 0,txt, 8, set_bold=False)
#                _ied.setData(treeModel.index(0, self.DO), 'XXXX')
                _ied.appendRow(_ap)
                Line = Line + 1

                for k in range (0, len(iAP.tServer)):
                    iSrv = iAP.tServer[k]
                    txt  = iSrv.desc + ',' + iSrv.timeout
                    _srv = StandardItem(Line, 0, txt, 8, set_bold=False)
                    _ap.appendRow(_srv)
                    Line = Line + 1

                    for l in range (0, len(iSrv.tLDevice)):
                        iLD = iSrv.tLDevice[l]
                        txt = iLD.ldName + ',' + iLD.inst
#                        _ld = StandardItem(Line, 1, "SDO", 10, set_bold=True)
#                        _ld = StandardItem(Line, 2, "222", 10, set_bold=True)
#                        _ld = StandardItem(Line, 3, "333", 10, set_bold=True)
                        _ld = StandardItem(Line, 4, "444", 10, set_bold=True)
                        treeModel.insertRow(1,_ld)

                        Line = Line + 1

#                        _ld.setData(
#                        _srv.appendRow(_ld)
#                        _ld.setData(0,"XXXX")

#                        cptObjet=cptObjet+1

#                        treeModel.insertRow(1,_ld)
#                        treeModel.setData(treeModel.index(cptObjet, self.DO),  'DO')
#                        treeModel.setData(treeModel.index(cptObjet, self.SDO), 'SDO')

        treeView.setModel(treeModel)
        treeView.expandAll()
        treeView.doubleClicked.connect(self.getValue)

        self.setCentralWidget(treeView)

    def getValue(self, val):
        print(val.data())
        print(val.row())
        print(val.column())


app = QApplication(sys.argv)

demo = AppDemo()
demo.show()

sys.exit(app.exec_())
