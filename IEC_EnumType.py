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
from IEC_FileListe import FileListe as FL
from IEC_Trace import IEC_Console  as TConsole
from IEC_Trace import TraceLevel as TL
from IEC61850_XML_Class import DataTypeTemplates as IECType

class Parse_EnumType:
    def __init__(self, _scl, _TRX):
        self.TRX          = _TRX
        self.SCL          = _scl
        self.dictEnumType = {}

    def GetEnumTypDict(self):
        return self.dictEnumType

    #  Get the doType definition from 'doType', based on a Python "dictionary"
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


##  Collecting the list of values / name of the enumeration
#       <EnumVal name="orIdent" bType="Octet64" />" >
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

    def Create_EnumType_Dict(self, DataType):
# Parcours de l'arbre de l'arbre de la balise <DataTypeTemplates..
# en cherchant les sections EnumTypes
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

class Test_EnumType:
    def main(directory, file, scl):
        TRX = TConsole(TL.DETAIL)

        TRX.Trace(("---------------------------------------------------"), TL.GENERAL)
        TRX.Trace(("Fichier:", file), TL.GENERAL)
        if scl is None:  # UNIT TEST
            scl = dom.parse(directory + file)
        DataType   = scl.getElementsByTagName("DataTypeTemplates")
        EnumTypeLst = Parse_EnumType(scl, TRX)
        dico = EnumTypeLst.Create_EnumType_Dict(DataType)

        TRX.Trace(("FIN IEC_EnumType"),TL.GENERAL)

if __name__ == '__main__':
    fileliste = FL.lstFull          #  System level file list
    for file in fileliste:
        Test_EnumType.main('SCL_files/', file, None)

    fileliste = FL.lstIED          # ED level file list
    for file in fileliste:
        Test_EnumType.main('SCL_files/',file, None)

