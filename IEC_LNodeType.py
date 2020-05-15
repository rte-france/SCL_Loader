import xml.dom.minidom as dom
from IEC_Trace import Trace
from IEC_Trace import Level    as TL
from IEC_FileListe import FileListe as FL
from IEC61850_XML_Class import DataTypeTemplates as IECType


##
# \b Parse_LNodeType: this class create the list of LNodeType and the Data Objects elements
# @brief
# @b Description
#   This class is parsing the LnodeType in XML and embed the list of LNodeType for each of the DO.
#<LNodeType id="SIE_A1_MU2/MU01/I01ATCTR1" lnClass="TCTR">
#	<DO name="Mod" type="myMod_0" />
#	<DO name="Beh" type="myBeh_1" />
# ...

class Parse_LNodeType:
    ## \b Description
    #   Constructor is used to keep the dictionary of DOType available.
    #
    # @image html DO.png        width=300px
    # @param _scl: pointer to the SCL structure created by miniDOM
    # @param _TRX: Trace function
    def __init__(self, _scl, _TRX):
        self.TRX = _TRX
        self.SCL = _scl
        self.dicLNodeType = {}

    ##
    # Return a full DoType for a given doType 'id'
    #
    # @param   id: the Date Object type to look up.
    # @return  An instance of the LNodeType Object elements, including the list of DO
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

    ##
    # @return the dictionary of LnodeType
    def GetLnodeDict(self):
        return self.dicLNodeType

    ##
    #  Create the table of DO elements attached to a given LNodeType
    #
    #  @param pDO  pointer to the SCL structure pointing to the DO list
    #  @return     The table of the DO.
    #
    #      <DO name="Op" type="SE_ACT_V005" />
    #      <DO name="NamPlt" type="SE_LPL_V003" desc="Name plate" />
    #
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
            _desc           = pDO.getAttribute("desc")
            iDO= IECType.LNodeType.DOI(_name, _type, _accessControl, _transient, _desc)
            self.TRX.Trace(("     DO:"+_name+" type:"+_type+" desc:"+_desc),TL.DETAIL)
            tDO.append(iDO)
            pDO = pDO.nextSibling
        return tDO

    ##
    # CreateLNodeType_Dict
    #
    # @param DataType: is the result of scl.getElementsByTagName("DataTypeTemplates")
    #
    # @return
    #       tLNodeType : the table of LNodeType objects
    #       self.dicLNodeType: the dictionary (used by  Test_LNodeType)
    #
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

##
# \b Test_LNodeType: unitary test for PARSE DoType
class Test_LNodeType:
    ##
    # Unitary for ParseDoType, invoked by IEC_test.py
    def main(directory, file, scl):
        TRX = Trace.Console(TL.DETAIL)

        TRX.Trace(("---------------------------------------------------"), TL.GENERAL)
        if scl is None:  # UNIT TEST
            scl = dom.parse(directory + file)
        TRX.Trace(("File:" + file), TL.GENERAL)
        DataType     = scl.getElementsByTagName("DataTypeTemplates")
        LNodeType    = Parse_LNodeType(scl, TRX)
        tLNodeType, dicLNodeType = LNodeType.Create_LNodeType_Dict(DataType)
        TRX.Trace(("END OF IEC_LNodeType"), TL.GENERAL)
##
# \b MAIN call the unitary test 'Test_LNodeType for PARSE LNodeType
if __name__ == '__main__':
    fileliste = FL.lstFull  # System level file list
    for file in fileliste:
        Test_LNodeType.main('SCL_files/', file, None)

    fileliste = FL.lstIED  # IED level file list
    for file in fileliste:
        Test_LNodeType.main('SCL_files/', file, None)
