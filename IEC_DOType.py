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
import xml.dom.minidom as dom
from IEC_Trace import Trace
from IEC_Trace import Level as TL
from IEC_FileListe import FileListe as FL
from IEC61850_XML_Class import DataTypeTemplates as IECType
from IEC61850_XML_Class import IED

##
# \b Parse_DOType: this class create the list of DoType / Data Attributes elements
# @brief
# @b Description
#   This class is parsing the DOType XML and embed the list of DA for each of the DO.
class Parse_DOType:

    ## \b Description
    #   Constructor is used to keep the dictionary of DOType available.
    #
    # @param _scl: pointer to the SCL structure created by miniDOM
    # @param _TRX: Trace function
    def __init__(self, _scl, _TRX):
        ## TRX initialized tracing system
        self.TRX = _TRX     ## TRX initialized tracing system
        self.SCL = _scl     ## SCL pointeur  to SCL with list of DOType
        self.dicDoType = {} ## dicDoType will contain a dictionary of DOType, the 'id' of the DOTYpe is the key.

    ##
    # Return a full DoType for a given doType 'id'
    # @param doType: the Date Object type to look up.
    # @return  An instance of the Data Object elements, including the list of DA\n
    #    Get the doType definition from 'doType', based on a Python "dictionary"
    def getIEC_DoType(self, doType):

        iDoType = self.dicDoType.get(doType)
        if iDoType is None:
            return None
#        _id   = iDoType.get('id')      # This is the 'key' of the dictionary.
        _cdc     = iDoType.get('cdc')
        _iedType = iDoType.get('iedType')
        _desc    = iDoType.get('desc')
        _tDA     = iDoType.get('tDA')
        instDoType = IECType.DOType(doType, _iedType, _cdc, _desc, _tDA)
        return instDoType
    ##
    # @return the dictionary of DoType
    def GetDOTypeDict(self):
        return self.dicDoType


    ##
    # \b Get_DA_Attributes: retrieve the list of DA and SDO for a DoType.
    #
    # @param pDA: pointer to the SCL structure pointing a xml DA structure
    #

    def Get_DA_Attributes(self, pDA):

        tDA=[]                          # Allocation of DAinst table
        pDA = pDA.firstChild.nextSibling
        while pDA:
            if  pDA.localName is None:
                pDA = pDA.nextSibling
                continue
            if pDA.localName=="DA":
                _desc    = pDA.getAttribute("desc")
                _name    = pDA.getAttribute("name")
                _fc      = pDA.getAttribute("fc")
                _bType   = pDA.getAttribute("bType")
                _type    = pDA.getAttribute("type")
                _count    = pDA.getAttribute("count")
                _valKind = pDA.getAttribute("valKind")
                _valImp  = pDA.getAttribute("valImport")
                _value = '.'     # to avoid any crash due to 'None'

                tVAL = pDA.firstChild
                if pDA.firstChild is not None:
                    p1 = tVAL.nextSibling
                    if (p1.firstChild is not None) and p1.localName=="Val":
                        _value = p1.firstChild.data

                iDA = IED.AccessPoint.Server.LN.DAI(_desc,_name,_fc,_bType,_type,_count,_valKind,_valImp,_value,'DO')

                tDA.append(iDA)
                if _value != '__None__':
                    self.TRX.Trace(("     DA name:"+_name+" Type"+_type+" bType:"+_bType + " value:"+_value ),TL.DETAIL)

                self.TRX.Trace(("     DA name:"+_name+" Type"+_type+" bType:"+_bType + " value:"+_value ),TL.DETAIL)
                self.TRX.Trace(("        desc:"+_desc+" valKind:"+_valKind+" desc:"+_desc),TL.DETAIL)
                self.TRX.Trace(("       value:"+_value),TL.DETAIL)

            if pDA.localName=="SDO":
                _name = pDA.getAttribute("name")
                _type = pDA.getAttribute("type")
                _desc = pDA.getAttribute("desc")
                _count= pDA.getAttribute("count")
                if _count is None:
                    _count = "0"
                iDA = IED.AccessPoint.Server.LN.DAI(_desc, _name, ' ',  _type, _type, _count, '', '', '','SDO')
                tDA.append(iDA)
                self.TRX.Trace(("     SDO- name:" + _name + ", sdo-type:"+ _type),TL.DETAIL)
            pDA = pDA.nextSibling
        return tDA

    ##
    # Create_DOType_Dict
    # @param DataType: is the result of scl.getElementsByTagName("DataTypeTemplates")
    #
    # @return
    #       tDO : the table of Data Object Types
    #       dicDoType: the dictionary (used for __main__)
    def Create_DOType_Dict(self, DataType):
        tDO=[]
        for DT in DataType:
            DT = DT.firstChild.nextSibling

            while DT.nextSibling:
                if DT.localName is None:
                    DT = DT.nextSibling
                    continue

                if DT.localName == "DOType":
                    _id      = DT.getAttribute("id")
                    _iedType = DT.getAttribute("iedType")
                    _cdc     = DT.getAttribute("cdc")
                    _desc    = DT.getAttribute("desc")
                    tDA = self.Get_DA_Attributes( DT )
                    iDO = IECType.DOType(_id, _iedType, _cdc, _desc, tDA)
                    self.dicDoType[_id] = {"iedType": _iedType , "cdc":_cdc, "desc": _desc, "tDA": tDA }
                    tDO.append(iDO)

                    DT = DT.nextSibling
                    continue
                DT = DT.nextSibling
            continue

        return tDO, self.dicDoType

##
# \b Test_DOType: unitary test for PARSE DoType
class Test_DOType:
    ##
    # Unitary for ParseDoType, invoked by IEC_test.py
    def main(directory, file, scl):
        TRX = Trace(TL.DETAIL)

        TRX.Trace(("---------------------------------------------------"), TL.GENERAL)
        if scl is None:  # UNIT TEST
            scl = dom.parse(directory + file)
        TRX.Trace(("File:" + file), TL.GENERAL)
        DataType = scl.getElementsByTagName("DataTypeTemplates")
        xDO = Parse_DOType(scl, TRX)
        tDA = xDO.Create_DOType_Dict(DataType)
        TRX.Trace(("END OF IEC_DOType"), TL.GENERAL)

##
# \b MAIN call the unitary test 'Test_DOTypefor PARSE DoType
if __name__ == '__main__':
    fileliste = FL.lstFull  # System level file list
    for file in fileliste:
        Test_DOType.main(FL.root, file, None)

    fileliste = FL.lstIED   # IED level file list
    for file in fileliste:
        Test_DOType.main(FL.root, file, None)



