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
from IEC_Trace import IEC_Console as TConsole
from IEC_Trace import TraceLevel as TL
from IEC_FileListe import FileListe as FL

# This class is used to collect the DAType definition and the associated DA:
#<DAType id="operDWCHT" desc="My Operate suff" >
#			<BDA name="ctlValxxx" bType="BOOLEAN"/>
#			<BDA name="originxxx" bType="Struct" type="Originator"/>
#			<BDA name="ctlNum" bType="INT8U"/>


# Class equivalent to <DAtype>:
#   <DAType id="AnalogueValue" desc="DA..."/>
# 	<DAType id="CalendarTime" desc="DA..."/>
# 	<DAType id="Cell" desc="DA..."/>
# 	<DAType id="DPCOperate" desc="DA..."/>
# 	<DAType id="Originator" desc="DA..."/>
# 	<DAType id="PulseConfig" desc="DA..."/>
class DAType:
    def __init__(self, _id, _desc, _protNs, _iedType):
        self.id      = _id         # id du type
        self.desc    = _desc       # descriptiop
        self.protNs  = _protNs     # NameSpace
        self.iedType = _iedType    # iedType
        self.tBDA    = []          # Table of the BDA related to this DA.

    # Sub-classe to handle BDA instanciations.
    # The properties of the class are the attrobiutes of IEC61850 DA Object.
    #       <BDA name-="cmdQual" bType="Enum" type="SE_cmdQual_V001" />
    #       <BDA name="orIdent" bType="Octet64" />
    #       <BDA name="mag" bType="Struct" type="SE_instMag_V001" />
    #       <BDA name="numPls" bType="INT32U" />

    class BDA:
        def __init__(self, _name, _type, _bType, _valKind, _value):
            self.name    = _name    # Nom du champ dans le SCL
            self.SDO     = _type
            self.type    = _type   # Type défini dans le SCL (enum ou Structure)
            self.bType   = _bType  # Basic Type, usually without futher definition in the SCL
            self.valKind = _valKind
            self.value   = _value
    class ProtNs:                   # TODO
        def __init__(self, _type):
            self.type = _type

class Parse_DAType:
    def __init__(self, _scl, _TRX):
        self.TRX = _TRX
        self.SCL = _scl
        self.dictDaType = {}

    #  Get the doType definition from 'doType', based on a Python "dictionary"
    def getIEC_DaType(self, doType):
        iDaType = self.dictDaType.get(doType)
        if iDaType is None:
            return None
        _id      = iDaType.get('id')
        _desc    = iDaType.get('desc')
        _protNs  = iDaType.get('type')
        _iedType = iDaType.get('iedType')
        _tBDA    = iDaType.get('tBDA')
        instDaType = DAType(id, _desc, _protNs,_iedType)
        instDaType.tBDA = _tBDA
        return instDaType

    def GetDATypeDict(self):
        return self.dictDaType

##  Collecting the the list of the BDA for a given DA
#       <BDA name="orIdent" bType="Octet64" />" >
    def Get_BDA_Attributes(self,BDA):

        tBDA = []  # Allocate the array of BDA (global au SCL)
        BDA = BDA.firstChild.nextSibling
        while BDA:
            if BDA.localName is None:
                BDA = BDA.nextSibling
                continue
            if BDA.localName=="BDA":
                _id      = BDA.getAttribute("name")
                _type    = BDA.getAttribute("type")
                _bType   = BDA.getAttribute("bType")
                _valKind = BDA.getAttribute("valKind")
                self.TRX.Trace(("     BDA: ID=" + _id + " type:" + _type +  ", bType:" + _bType + ", valKind:" +_valKind ),TL.DETAIL)

                _value = None
                tVAL = BDA.firstChild
                if BDA.firstChild is not None:
                    p1 = tVAL.nextSibling
                    if (p1.firstChild is not None):
                        _value = p1.firstChild.data
                        if _value is None:
                            continue
                        self.TRX.Trace(("     BDA value ##" + _id + ' -' + _type + ' -' + _bType + ' -'
                                                       + _valKind + ' -' + _value ) , TL.DETAIL)

                BDAinst = DAType.BDA(_id, _bType, _type, _valKind, _value)
                tBDA.append(BDAinst)

            if BDA.localName=="ProtNs":     #TODO
                self.TRX.Trace(("****YY*****     Prot Ns "),TL.ERROR)
            BDA = BDA.nextSibling
        return tBDA

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

class Test_DAType:
    def main(directory, file, scl):
        TRX = TConsole(TL.DETAIL)

        TRX.Trace(("---------------------------------------------------"), TL.GENERAL)
        if scl is None:  # UNIT TEST
            scl = dom.parse(directory + file)
        TRX.Trace(("File:" + file), TL.GENERAL)
        DataType   = scl.getElementsByTagName("DataTypeTemplates")
        DATypeTypeLst = Parse_DAType(scl, TRX)
        dico = DATypeTypeLst.Create_DAType_Dict(DataType)

        TRX.Trace(("FIN IEC_DAType"),TL.GENERAL)

if __name__ == '__main__':
    fileliste = FL.lstFull          # Liste de fichier de niveau système et IED
    for file in fileliste:
        Test_DAType.main('SCL_files/',file, None)

    fileliste = FL.lstIED          # IED level file list
    for file in fileliste:
        Test_DAType.main('SCL_files/',file, None)



