import xml.dom.minidom as dom
from IEC_Trace import IEC_Console   as TConsole
from IEC_Trace import TraceLevel    as TL
from IEC_FileListe import FileListe as FL
from IEC61850_XML_Class import DataTypeTemplates as IECType

import tkinter as tk
# Cette classe s'occupe de charger les définitions de LNodeType et la liste des DO associés:
#<LNodeType id="SIE_A1_MU2/MU01/I01ATCTR1" lnClass="TCTR">
#	<DO name="Mod" type="myMod_0" />
#	<DO name="Beh" type="myBeh_1" />
#	<DO name="Health" type="myHealth_2" />
#   <DO name="NamPlt" type="myNamPlt_10" />
#...
#</LNodeType>



class Parse_LNodeType:
    def __init__(self, _scl, _TRX):
        self.TRX = _TRX
        self.SCL = _scl
        self.dicLNodeType = {}
#
#  Parsing the LNodeType and the associated DOType
#   <LNodeType cdc="UTS" id="SE_UTS_V001">
    def getIEC_LNodeType(self, id):             # Convert dictionary structure to LNodeType class
        iLNode = self.dicLNodeType.get(id)
        if iLNode is None:
            return None
        _lnClass = iLNode.get('lnClass')
        _desc    = iLNode.get('desc')
        _iedType = iLNode.get('iedType')
        _tDO     = iLNode.get('tDO')
        instLNode = IECType.LNodeType(id, _lnClass, _desc, _iedType, _tDO)

        return instLNode

    def GetLnodeDict(self):
        return self.dicLNodeType

    #      <DO name="Op" type="SE_ACT_V005" />
    #      <DO name="NamPlt" type="SE_LPL_V003" desc="Name plate" />
    def Get_DO_Attributes(self, pDO):
        tDO=[]                          # Allocate the table of DO
        pDO = pDO.firstChild.nextSibling
        while pDO:
            if  pDO.localName is None:
                pDO = pDO.nextSibling
                continue
            _name           = pDO.getAttribute("name")
            _type           = pDO.getAttribute("type")
            _accessControl  = pDO.getAttribute("accessControl")
            _transient      = pDO.getAttribute("transient")
            _desc  = pDO.getAttribute("desc")
            iDO= IECType.LNodeType.DOi(_name, _type, _accessControl, _transient, _desc)
            self.TRX.Trace(("     DO:"+_name+" type:"+_type+" desc:"+_desc),TL.DETAIL)
            tDO.append(iDO)
            pDO = pDO.nextSibling
        return tDO

    def Create_LNodeType_Dict(self, DataType):
        tLNodeType   = []
        tDO = []
        for pDT in DataType:
            pDT = pDT.firstChild.nextSibling

            while pDT.nextSibling:
                if pDT.localName is None:
                    pDT = pDT.nextSibling
                    continue
                if pDT.localName == "LNodeType":
                    _id      = pDT.getAttribute("id")
                    _desc    = pDT.getAttribute("desc")
                    _iedType = pDT.getAttribute("iedType")
                    _lnClass = pDT.getAttribute("lnClass")   # Used as the key for the python dictionnay
                    iLNodeType = IECType.LNodeType(_id, _desc, _iedType, _lnClass, [])
                    tLNodeType.append(iLNodeType)
                    self.TRX.Trace(("LNodeType: id:" + _id + " lnClass:" + _lnClass + " iedType:" + _iedType + " desc:" + _desc),TL.DETAIL)
                    tDO = self.Get_DO_Attributes(pDT)
                    self.dicLNodeType[_id] = {"lnClass": _lnClass, "desc": _desc, "iedType": _iedType, "tDO": tDO}

                    pDT = pDT.nextSibling
                    continue
                pDT = pDT.nextSibling
            continue
        return tLNodeType, self.dicLNodeType

class Test_LNodeType:
    def main(directory, file, scl):
        TRX = TConsole(TL.DETAIL)

        TRX.Trace(("---------------------------------------------------"), TL.GENERAL)
        if scl is None:  # UNIT TEST
            scl = dom.parse(directory + file)
        TRX.Trace(("File:" + file), TL.GENERAL)
        DataType     = scl.getElementsByTagName("DataTypeTemplates")
        LNodeType    = Parse_LNodeType(scl, TRX)
        tLNodeType, dicLNodeType = LNodeType.Create_LNodeType_Dict(DataType)
        TRX.Trace(("END OF IEC_LNodeType"), TL.GENERAL)

if __name__ == '__main__':
    fileliste = FL.lstFull  # System level file list
    for file in fileliste:
        Test_LNodeType.main('SCL_files/', file, None)

    fileliste = FL.lstIED  # IED level file list
    for file in fileliste:
        Test_LNodeType.main('SCL_files/', file, None)
