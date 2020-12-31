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
# -*- coding: utf-8 -*-

import xml.dom.minidom as dom
from IEC_Trace import Trace
from IEC_Trace import Level as TL
from IEC_FileListe import FileListe as FL

from IEC61850_XML_Class import DataTypeTemplates as IECType

##
# \b Parse_DAType: this class create the list of DAType and the associated BDA elements
# @brief
# @b Description
# An instantiable structured attribute type; referenced from within a DA
# element of a DOType, or from within another DAType for nested type
# definitions. Based on the attribute structure definitions of IEC 61850-7-3
#
# Class equivalent to <DAtype>:
#   <DAType id="AnalogueValue" desc="DA..."/>
# 	<DAType id="CalendarTime" desc="DA..."/>
# 	<DAType id="Cell" desc="DA..."/>
class Parse_DAType:

    ## \b Description
    #   Constructor is used to keep the dictionary of DAType available.
    #
    # @param _scl: pointer to the SCL structure created by miniDOM
    # @param _TRX: Trace function
    def __init__(self, _scl, _TRX):
                                    ##
        self.TRX = _TRX             ## TRX Trace function
        self.SCL = _scl             ## Pointer to the sCL
        self.dictDaType = {}        ## Dictionary used to store and retrieve de DAType
    ##
    # Return a full DAType for a given doType 'id'
    # @param doType: the Date Object type to look up.
    # @return  An instance of the Data Object elements, including the list of DA\n
    #    Get the doType definition from 'daType' id , based on a Python "dictionary"
    def getIEC_DaType(self, doType):
        iDaType = self.dictDaType.get(doType)
        if iDaType is None:
            return None
        _id      = iDaType.get('id')        ## id of the DaType
        _desc    = iDaType.get('desc')      ## desc of the DaType
        _protNs  = iDaType.get('type')      ## type of the DaType
        _iedType = iDaType.get('iedType')   ## iedType of the DaType (deprecated)
        _tBDA    = iDaType.get('tBDA')
        instDaType = IECType.DAType(id, _desc, _protNs,_iedType)
        instDaType.tBDA = _tBDA
        return instDaType
    ##
    # @return the dictionary of DAType
    def GetDATypeDict(self):
        return self.dictDaType

    ##
    # \b Get_BDA_Attributes: retrieve the list of BDA for a DAType.
    #
    # @param pBDA: pointer to the SCL structure pointing a <DA structure>
    #
    # XML extract:
    # 		<DAType id="_Oper_V1.0.0">
    # 			<BDA name="Check" bType="Check"/>
    # 			<BDA name="T" bType="Timestamp"/>
    # 			<BDA name="Test" bType="BOOLEAN"/>
    #           ...
    def Get_BDA_Attributes(self,pBDA):

        tBDA = []  # Allocate the array of pDBA (global au SCL)
        pDBA = pBDA.firstChild.nextSibling
        while pDBA:
            if pDBA.localName is None:
                pDBA = pDBA.nextSibling
                continue
            if pDBA.localName=="BDA":
                _id      = pDBA.getAttribute("name")
                _type    = pDBA.getAttribute("type")
                _bType   = pDBA.getAttribute("bType")

                _valKind = pDBA.getAttribute("valKind")
                self.TRX.Trace(("     BDA: ID=" + _id + " type:" + _type +  ", bType:" + _bType + ", valKind:" +_valKind ),TL.DETAIL)

                _value = None
                tVAL = pDBA.firstChild
                if pDBA.firstChild is not None:
                    p1 = tVAL.nextSibling
                    if (p1.firstChild is not None):
                        _value = p1.firstChild.data
                        if _value is None:
                            continue
                        self.TRX.Trace(("     DBA value ##" + _id + ' -' + _type + ' -' + _bType + ' -'
                                                       + _valKind + ' -' + _value ) , TL.DETAIL)

                BDAinst = IECType.DAType.BDA(_id, _bType, _type, _valKind, _value)
                tBDA.append(BDAinst)

            if pDBA.localName=="ProtNs":     #TODO
                self.TRX.Trace(("****YY*****     Prot Ns "),TL.ERROR)
            pDBA = pDBA.nextSibling
        return tBDA
    ##
    # CreateDAType_Dict
    #
    # @param DataType: is the result of scl.getElementsByTagName("DataTypeTemplates")
    #
    # @return
    #       tBDA: the table of BDA objects
    #
    def Create_DAType_Dict(self, DataType):
        tDAType=[]  # Allocation du tableau

        for DA in DataType:
            DA = DA.firstChild.nextSibling
            while DA.nextSibling:
                if DA.localName is None:
                    DA = DA.nextSibling
                    continue

                if DA.localName == "DAType":
                    id      = DA.getAttribute("id")
                    desc    = DA.getAttribute("desc")
                    protNs  = DA.getAttribute("protNs")
                    iedType = DA.getAttribute("iedType")
                    tBDA   = self.Get_BDA_Attributes(DA)

                    self.dictDaType[id] = {"desc": desc, "protNs": protNs, "iedType": iedType, "tBDA": tBDA }
                    DA = DA.nextSibling
                    continue

                DA = DA.nextSibling
            continue
        return tBDA
##
# \b Test_DAType: unitary test for parsing DAType
class Test_DAType:
    ##
    # Unitary test for Parse_DAType, invoked by IEC_test.py
    def main(directory, file, scl):
        TRX = Trace(TL.DETAIL)

        TRX.Trace(("---------------------------------------------------"), TL.GENERAL)
        if scl is None:  # UNIT TEST
            scl = dom.parse(directory + file)
        TRX.Trace(("File:" + file), TL.GENERAL)
        DataType   = scl.getElementsByTagName("DataTypeTemplates")
        DATypeTypeLst = Parse_DAType(scl, TRX)
        dico = DATypeTypeLst.Create_DAType_Dict(DataType)

        TRX.Trace(("FIN IEC_DAType"),TL.GENERAL)

##
# \b MAIN call the unitary test 'Test_DOTypefor PARSE DoType
if __name__ == '__main__':
    fileliste = FL.lstFull          # Liste de fichier de niveau système et IED
    for file in fileliste:
        Test_DAType.main(FL.root,file, None)

    fileliste = FL.lstIED          # IED level file list
    for file in fileliste:
        Test_DAType.main(FL.root,file, None)



