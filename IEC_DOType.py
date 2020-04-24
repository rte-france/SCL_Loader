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
from IEC_Trace import IEC_Console   as TConsole
from IEC_Trace import TraceLevel    as TL
from IEC_FileListe import FileListe as FL

# Cette classe s'occupe de charger les définitions de DAType et la liste des DA associés:
#<DOType cdc="DPC" id="myPos_248">
#	<DA bType="Dbpos" dchg="true" fc="ST" name="stVal" />
#	<DA bType="Quality" fc="ST" name="q" qchg="true" />
#	<DA bType="Timestamp" fc="ST" name="t" />
#	<DA bType="Enum" dchg="true" fc="CF" name="ctlModel" valKind="RO" type="CtlModel
#...
#</DOType>

# Une 'sous-classe' est utilisée pour stocker les instances de DA dans le DOType
# La classe principale reflète le contenu de DoType

# Sous-classe pour stocker les DA instancier dans in DO.
# Les propriétés sont celles de l'objet DA dans le SCL (dans le DoType).

# classe principale les DO Type
class DOType:
    def __init__(self, _id, _cdc, _desc, _tDA):
        self.name = ""
        self.id   = _id
        self.cdc  = _cdc
        self.desc = _desc
        self.tDA  = _tDA

    class DAinst:
        def __init__(self, _DO   , _SDO, _type, _fc   , _name, _count, _bType, _valKind,_valImp, \
                          _sAddr, _qchg, _dchg, _desc ,_dupd, _value):
            self.DoDaSdo = _DO
            self.SDO     = _SDO
            self.type    = _type
            self.fc      = _fc
            self.name    = _name
            self.count   = _count
            self.bType   = _bType
            self.valKind = _valKind
            self.valImport = _valImp
            self.sAddr   = _sAddr
            self.qchg    = _qchg
            self.dchg    = _dchg
            self.dupd    = _dupd
            self.desc    = _desc
            self.value   = _value

class Parse_DOType:
    def __init__(self, _scl, _TRX):
        self.TRX = _TRX
        self.SCL = _scl
        self.dicDoType = {}

    #  Get the doType definition from 'doType', based on a Python "dictionary"
    def getIEC_DoType(self, doType):
        iDoType = self.dicDoType.get(doType)
        if iDoType is None:
            return None
        _id   = iDoType.get('id')
        _cdc  = iDoType.get('cdc')
        _desc = iDoType.get('desc')
        _tDA  = iDoType.get('tDA')
        instDoType = DOType(id, _cdc, _desc, _tDA)
        return instDoType

    def GetDOTypeDict(self):
        return self.dicDoType

# < DA bType = "VisString255" fc = "DC" name = "hwRev" valKind = "RO" / >
# < DA bType = "VisString255" fc = "DC" name = "swRev" valKind = "RO" / >
    def Get_DA_Attributes(self, pDA):
        tDA=[]                          # Allocation of DAinst table
        pDA = pDA.firstChild.nextSibling
        while pDA:
            if  pDA.localName is None:
                pDA = pDA.nextSibling
                continue
            if pDA.localName=="DA":
                _FC      = pDA.getAttribute("fc")
                _name    = pDA.getAttribute("name")
                _Type    = pDA.getAttribute("type")
                _bType   = pDA.getAttribute("bType")
                _valKind = pDA.getAttribute("valKind")
                _valImp  = pDA.getAttribute("valImport")
                _sAddr   = pDA.getAttribute("sAddr")
                _qchg    = pDA.getAttribute("qchg")
                _dchg    = pDA.getAttribute("dchg")
                _dupd    = pDA.getAttribute("dupd")
                _desc    = pDA.getAttribute("desc")
                _value = '__None__'     # Si on utilise le None de python ça crash lors d'un print...

                tVAL = pDA.firstChild
                if pDA.firstChild is not None:
                    p1 = tVAL.nextSibling
                    if (p1.firstChild is not None) and p1.localName=="Val":
                        _value = p1.firstChild.data

###IEC_Trace _Type au lieu de FC
                iDA = DOType.DAinst("DA", _Type  , _Type ,_FC   , _name, None, _bType, _valKind, \
                                          _valImp, _sAddr, _qchg, _dchg, _dupd, _desc , _value)
                tDA.append(iDA)
                if _value != '__None__':
                    self.TRX.Trace(("     DA name:"+_name+" FC:"+_FC+" Type"+_Type+" bType:"+_bType + " value:"+_value ),TL.DETAIL)

                self.TRX.Trace(("     DA name:"+_name+" FC:"+_FC+" Type"+_Type+" bType:"+_bType + " value:"+_value ),TL.DETAIL)
                self.TRX.Trace(("        desc:"+_desc+" valKind:"+_valKind+" sAddr:"+_sAddr+" qchg:"+_qchg+" desc:"+_desc),TL.DETAIL)
                self.TRX.Trace(("       value:"+_value),TL.DETAIL)

            if pDA.localName=="SDO":
                _name = pDA.getAttribute("name")
                _type = pDA.getAttribute("type")
                _desc = pDA.getAttribute("desc")
                _count= pDA.getAttribute("count")

                iDA = DOType.DAinst("SDO"    , _type, _type, "", _name,  _count, _type, '_valKind',
                                     '_valImp', '_sAddr', '_qchg', '_dchg', '_dupd', _desc, '__None__')
                tDA.append(iDA)
                self.TRX.Trace(("     SDO- name:" + _name + ", sdo-type:"+ _type),TL.DETAIL)
            pDA = pDA.nextSibling
        return tDA

    def Create_DOType_Dict(self, DataType):
        tDO=[]
        for DT in DataType:
            DT = DT.firstChild.nextSibling

            while DT.nextSibling:
                if DT.localName is None:
                    DT = DT.nextSibling
                    continue

                if DT.localName == "DOType":
                    id   = DT.getAttribute("id")
                    cdc  = DT.getAttribute("cdc")
                    desc = DT.getAttribute("desc")
                    tDA = self.Get_DA_Attributes( DT )
                    iDO = DOType(id, cdc, cdc, tDA)
                    self.dicDoType[id] = {"cdc":cdc, "desc": desc, "tDA": tDA }
                    tDO.append(iDO)

                    DT = DT.nextSibling
                    continue
                DT = DT.nextSibling
            continue

        return tDO, self.dicDoType

#Le code ci-dessous ne s'execute que si on lance la class seule.
class Test_DOType:
    def main(directory, file, scl):
        TRX = TConsole(TL.DETAIL)

        TRX.Trace(("---------------------------------------------------"), TL.GENERAL)
        if scl is None:  # UNIT TEST
            scl = dom.parse(directory + file)
        TRX.Trace(("File:" + file), TL.GENERAL)
        DataType = scl.getElementsByTagName("DataTypeTemplates")
        xDO = Parse_DOType(scl, TRX)
        tDA = xDO.Create_DOType_Dict(DataType)
        TRX.Trace(("END OF IEC_DOType"), TL.GENERAL)

if __name__ == '__main__':
    fileliste = FL.lstFull  # System level file list
    for file in fileliste:
        Test_DOType.main('SCL_files/', file, None)

    fileliste = FL.lstIED   # IED level file list
    for file in fileliste:
        Test_DOType.main('SCL_files/', file, None)



