
from IEC61850_XML_Class import IED

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

class InitData():
    def __init__(self):

        IED2 = IED("IED2", "Protection", "Test View", "V1.0", "V1.0", "V2.0", 'RTE", "-', "gilles", None)
        IED3 = IED("IED3", "Protection", "Test View", "V1.0", "V1.0", "V2.0", 'RTE", "-', "gilles", None)
        IED1 = IED("IED1", "Protection", "Test View", "V1.0", "V1.0", "V2.0", 'RTE", "-', "gilles", None)
        IED4 = IED("IED4", "Protection", "Test View", "V1.0", "V1.0", "V2.0", 'RTE", "-', "gilles", None)

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

        tLN=[]
        LN1 = IED.AccessPoint.Server.LN("LN0", "", "LLN0", "", "LN0_RTE", "essai tree view")
        LN2 = IED.AccessPoint.Server.LN("LN:", "Gil_", "MMXU", "1", "MMXU_RTE", "essai tree view")
        LN3 = IED.AccessPoint.Server.LN("LN:", "Adl_", "XCBR", "0", "XCBR_RTE", "essai tree view")
        tLN.append(LN1)
        tLN.append(LN2)
        tLN.append(LN3)

        LD1.tLN=tLN
        LD2.tLN=tLN
        LD3.tLN=tLN
        LD4.tLN=tLN
        LD5.tLN=tLN


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

        self.treeView = QTreeView()
        self.treeView.setHeaderHidden(False)

        self.treeModel = QStandardItemModel(0,5)
        self.treeModel.setColumnCount(6)
        self.treeModel.setHorizontalHeaderLabels(["IED/AP/SRV/LD/LN", "DO","SDO", "", "DA","SDA"])
        self.treeModel.setHeaderData(self.IED_LD ,  Qt.Horizontal, "IED/AP/SRV/LD")
        self.treeModel.setHeaderData(self.LN     ,  Qt.Horizontal, "LN")
        self.treeModel.setHeaderData(self.DO     ,  Qt.Horizontal, "DO")
        self.treeModel.setHeaderData(self.SDO    ,  Qt.Horizontal, "SDO")
        self.treeModel.setHeaderData(self.DA     ,  Qt.Horizontal, "DA")

        self.rootNode = self.treeModel.invisibleRootItem()

        cptObjet=0
        Line= 0
        for i in range(0, len(tIED.IED)):
            iIED = tIED.IED[i]
            txt =   iIED.name + ',' + iIED.type + ',' + iIED.desc
            _ied =  StandardItem(txt, 12, set_bold=True)
            self.rootNode.appendRow(_ied)
            Line = Line + 1
            for j in range (0, len(iIED.tAccessPoint)):
                iAP = iIED.tAccessPoint[j]
                txt = iAP.name + ',' + iAP.desc
                _ap = StandardItem(txt, 8, set_bold=False)
#                _ied.setData(treeModel.index(0, self.DO), 'XXXX')
                _ied.appendRow(_ap)
                Line = Line + 1

                for k in range (0, len(iAP.tServer)):
                    iSrv = iAP.tServer[k]
                    txt  = iSrv.desc + ',' + iSrv.timeout
                    _srv1 = StandardItem( txt, 8, set_bold=False)
                    _ap.appendRow(_srv1)

                    for idxLD in range (0, len(iSrv.tLDevice)):
                        iLD = iSrv.tLDevice[idxLD]
                        txt = iLD.ldName + ',' + iLD.inst

#                   for idxLN in range(0, len(iLD.tLN)):
#                        iLN = iLD.tLN[0]
#                        txt = iLN.lnPrefix + iLN.lnClass + iLN.lnInst # ' + iLD.inst
 #                       _ln = StandardItem(txt, 10, set_bold=True)

                        _ld0 = StandardItem("==>",10, set_bold=True)
                        _ld2 = StandardItem("DO", 10, set_bold=False)
                        _ld3 = StandardItem("SDO", 10, set_bold=True)
                        _ld4 = StandardItem("DA", 10, set_bold=True)
                        _ld5 = StandardItem("SDA", 10, set_bold=True)

#                        _ied.appendColumn([_ld2, _ld3])

                        self.rootNode.appendRow([_ied,_ld0, _ld2,_ld3,_ld4,_ld5] )

                        Line = Line + 1


        self.treeView.setModel(self.treeModel)
        self.treeView.expandAll()
        self.treeView.doubleClicked.connect(self.getValue)

        self.setCentralWidget(self.treeView)

        return None

    def getValue(self, val):
        print(val.data())
        print(val.row())
        print(val.column())


app = QApplication(sys.argv)

demo = AppDemo()
demo.show()

sys.exit(app.exec_())
