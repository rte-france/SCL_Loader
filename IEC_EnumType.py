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
from IEC_FileListe import FileListe as FL
from IEC_Trace import Trace
from IEC_Trace import Level as TL
from IEC61850_XML_Class import DataTypeTemplates as IECType

##
# \b Parse_EnumType: this class load and parse the EnumType and their values.
# In addition, the class identify the minimal and the maximal value of each enumeration, thus
# allowing to verify that a given value of an enumeration is the appropriate range of value.
#
#		<EnumType id="PhaseReferenceKind">
#			<EnumVal ord="0">A</EnumVal>
#			<EnumVal ord="1">B</EnumVal>
#			<EnumVal ord="2">C</EnumVal>
#			<EnumVal ord="3">Synchrophasor</EnumVal>
#		</EnumType>
class Parse_EnumType:
    ## \b Description
    #   Constructor is used to keep the dictionary of EnumType available.
    #
    # @param _scl: pointer to the SCL structure created by miniDOM
    # @param _TRX: Trace function
    #
    def __init__(self, _scl, _TRX):
        ## TRX initialized tracing system
        self.TRX = _TRX     ## TRX initialized tracing system
        self.SCL = _scl     ## SCL pointeur  to SCL with list of DOType
        self.dictEnumType = {}  ## dictEnumType will contain a dictionary of EnumType,  the 'id' of the EnumType is the key
    ##
    # @return the dictionary of EnumType
    def GetEnumTypDict(self):
        return self.dictEnumType


    ##
    # Return a full EnumType for a given Enum 'id'
    #
    # @param   EnumTypeId: the enumeration id to look up.
    # @return  An instance of the EnumType Object elements, including the list of values and min / max limits.
    #
    #			<EnumVal ord="0">A</EnumVal>
    #			<EnumVal ord="1">B</EnumVal>
    #			<EnumVal ord="2">C</EnumVal>
    def getIEC_EnumType(self, EnumTypeId):
        iEnumType = self.dictEnumType.get(EnumTypeId)
        if iEnumType is None:
            return None
        _id          = iEnumType.get('id')
        _desc        = iEnumType.get('desc')
        _min         = iEnumType.get('min')
        _max         = iEnumType.get('max')
        _tEnumval    = iEnumType.get('tEnumVal')
        instEnumType = IECType.EnumType(_id, _desc)

        instEnumType.min      = _min
        instEnumType.max      = _max
        instEnumType.tEnumval = _tEnumval

        return instEnumType

    ##
    # Return a full the list of enumeration values
    #
    # @param   pEnumVal: XML pointer of EnumType.
    # @return  The table of values for the EnumType
    #
    #			<EnumVal ord="0">A</EnumVal>
    #			<EnumVal ord="1">B</EnumVal>
    #			<EnumVal ord="2">C</EnumVal>
    def Get_EnumVal_Atributes(self, pEnumVal):

        tEnumVal = []  # Allocation du tableau des valeurs d'énumération
        pEnumVal = pEnumVal.firstChild.nextSibling
        while pEnumVal:
            if pEnumVal.localName is None:
                pEnumVal = pEnumVal.nextSibling
                continue

            ord   = pEnumVal.getAttribute("ord")
            desc  = pEnumVal.getAttribute("desc")
            text=""
            if pEnumVal.firstChild is not None:
                text  = pEnumVal.firstChild.data      # Enum_Type.txtValue =

            iEnumVal = IECType.EnumType.EnumVal(ord, text, desc)
            tEnumVal.append(iEnumVal)
            pEnumVal = pEnumVal.nextSibling

        return tEnumVal
    ##
    # Create_EnumType_Dict
    # @param DataType: is the result of scl.getElementsByTagName("DataTypeTemplates")
    #
    # @return
    #       dicDoType: the dictionary (used for __main__)
    def Create_EnumType_Dict(self, DataType):
        for pEnum in DataType:
            pEnum = pEnum.firstChild.nextSibling
            while pEnum.nextSibling:
                if pEnum.localName is None:
                    pEnum = pEnum.nextSibling
                    continue

                if pEnum.localName == "EnumType":
                    id        = pEnum.getAttribute("id")
                    desc      = pEnum.getAttribute("desc")
                    tEnumVal  = self.Get_EnumVal_Atributes(pEnum)

                    if (tEnumVal is not None):
                        self.TRX.Trace((id + ':' + str(tEnumVal)),TL.DETAIL)
                        for i in range(len(tEnumVal)):
                            self.TRX.Trace((id + 'value:' + str(tEnumVal[i].ord) + " desc=" + tEnumVal[i].desc),TL.DETAIL)

                    min = int(tEnumVal[0].ord)
                    max = int(tEnumVal[0].ord)
                    for iEnumVal in tEnumVal:
                        if int(iEnumVal.ord) < min:
                            min = int(iEnumVal.ord)
                        if int(iEnumVal.ord) > max:
                            max = int(iEnumVal.ord)
                    self.TRX.Trace(("----------- >Min:" +str(min)+ " Max:" + str(max)),TL.DETAIL)
                    self.dictEnumType[id]= {"id": id, "desc": desc,"min":min, "max":max, "tEnumVal": tEnumVal }

                pEnum = pEnum.nextSibling
        return self.dictEnumType
##
# \b Test_EnumType: unitary test for Parse_EnumType
class Test_EnumType:
    ##
    # Unitary test for Parse_EnumType, invoked by IEC_test.py
    def main(directory, file, scl):
        TRX = Trace(TL.DETAIL)

        TRX.Trace(("---------------------------------------------------"), TL.GENERAL)
        TRX.Trace(("Fichier:", file), TL.GENERAL)
        if scl is None:  # UNIT TEST
            scl = dom.parse(directory + file)
        DataType   = scl.getElementsByTagName("DataTypeTemplates")
        EnumTypeLst = Parse_EnumType(scl, TRX)
        dico = EnumTypeLst.Create_EnumType_Dict(DataType)

        TRX.Trace(("FIN IEC_EnumType"),TL.GENERAL)

##
# \b MAIN call the unitary test 'Test_EnumType' for PARSE_EnumType
if __name__ == '__main__':
    fileliste = FL.lstFull          #  System level file list
    for file in fileliste:
        Test_EnumType.main(FL.root, file, None)

    fileliste = FL.lstIED          # ED level file list
    for file in fileliste:
        Test_EnumType.main(FL.root,file, None)

