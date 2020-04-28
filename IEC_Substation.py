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
from IEC_FileListe      import FileListe  as FL
from IEC_Trace          import IEC_Console  as TConsole
from IEC_Trace          import TraceLevel  as TL
from IEC_PrivateSupport import DynImport
from IEC61850_XML_Class import SubStation

class ParseSubStation:
    def __init__(self, _scl, _TR, _name, _desc):
        self.scl            = _scl
        self.TRX            = _TR
        self.tVoltageLevel  = []
        self.name           = _name
        self.desc           = _desc
        self.Dyn            = DynImport()

    def ParseTerminal(self, pTal, poste, pCNXNode):
        idxTal = 0
        while (pTal is not None) and (pTal.localName is not None):
            if pTal.localName == "Terminal":
                _name = pTal.getAttribute("name")
                _connectivityNode = pTal.getAttribute("connectivityNode")
                _substationName = pTal.getAttribute("substationName")
                _voltageLevelName = pTal.getAttribute("voltageLevelName")
                _bayName = pTal.getAttribute("bayName")
                _cNodeName = pTal.getAttribute("cNodeName")
                iTerminal = pCNXNode.Terminal(_name, _connectivityNode,_substationName,
                                        _voltageLevelName,  _bayName, _cNodeName)
                pCNXNode.tTerminal.append(iTerminal)
                idxTal = idxTal + 1

            pTal = pTal.nextSibling
            if pTal is not None:
                pTal = pTal.nextSibling

    def ParseVoltageLevelSection(self, Substation, file):
        # Analyse d'un IED
        #
        # <IED..
        #
        #    < Communication >
        #       < SubNetwork
        tVoltage = []
        _name = Substation[0].getAttribute("name")
        _desc = Substation[0].getAttribute("desc")

        poste=SubStation(_name,_desc)

        pVoltageLevel = Substation[0].firstChild.nextSibling

        while pVoltageLevel:
            print("pVoltageLevel.nodeName"  + pVoltageLevel.nodeName)

            _name       = pVoltageLevel.getAttribute("name")
            _nomFreq    = pVoltageLevel.getAttribute("nomFreq")
            _numpPhases = pVoltageLevel.getAttribute("numPhases")
            _desc       = pVoltageLevel.getAttribute("desc")

            Tension = poste.VoltageLevel(_name,_nomFreq,_numpPhases,_desc)
            poste.tVoltage.append(Tension)
            pVolt = pVoltageLevel.firstChild
            if pVolt is not None:
                pVolt=pVolt.nextSibling
            idxVolt = len(poste.tVoltage)-1
            while (pVolt is not None) and (pVolt.localName is not None):
                if pVolt.localName == "PowerTransformer":
                    _name    = pVolt.getAttribute("name")
                    _desc    = pVolt.getAttribute("desc")
                    _type    = pVolt.getAttribute("type")
                    _virtual = pVolt.getAttribute("virtual")
                    iTransfo = poste.VoltageLevel.PowerTransformer(_name,_desc, _type, _virtual )
                    poste.tVoltage[idxVolt].tPwrTfo.append(iTransfo)
                    self.TRX.Trace(('Substation/Transformer.name:' + _name  + ' desc:' + _desc + " type:"  + _type),TL.DETAIL)

                if pVolt.localName == "Voltage":
                    _unit       = pVolt.getAttribute("unit")
                    _multiplier = pVolt.getAttribute("multiplier")
                    _value      = pVolt.getAttribute("value")
                    iVolt       = poste.VoltageLevel.Voltage(_unit, _multiplier, _value)
                    poste.tVoltage[idxVolt].Voltage=iVolt
                    self.TRX.Trace(('Substation/Voltage.unit:' + _unit  + ' mul:' + _multiplier + " value:"  + _value ),TL.DETAIL)

                if pVolt.localName == "Bay":
                    _name    = pVolt.getAttribute("name")
                    _desc    = pVolt.getAttribute("desc")
                    _sx_y    = pVolt.getAttribute("sxy:y")
                    _sx_x    = pVolt.getAttribute("sxy:x")
                    iBay     = poste.VoltageLevel.Bay(_name, _desc, _sx_x, _sx_y)
                    poste.tVoltage[idxVolt].tBay.append(iBay)
                    self.TRX.Trace(('Substation/Bay.name:' + _name + ' desc:' + _desc + " sxy:y:" + _sx_y + " sxy:x:" + _sx_x), TL.DETAIL)

                    pBay = pVolt.firstChild
                    if pBay is not None:
                        pBay = pBay.nextSibling
                    idxConEqt  = 0
                    idxConMode = 0
                    idxBay = len(poste.tVoltage[idxVolt].tBay)-1
                    while(pBay is not None) and (pBay.localName is not None):
                        if pBay.localName == "ConductingEquipment":
                            _name    = pBay.getAttribute("name")
                            _desc    = pBay.getAttribute("desc")
                            _virtual = pBay.getAttribute("virtual")
                            _sx_y    = pBay.getAttribute("sxy:y")
                            _sx_x    = pBay.getAttribute("sxy:x")
                            _sx_dir  = pBay.getAttribute("sxy:dir")
                            iCondEqt = poste.VoltageLevel.Bay.ConductingEquipment(_name, _desc, _virtual, _sx_y, _sx_x, _sx_dir )
                            poste.tVoltage[idxVolt].tBay[idxBay].tConductingEquipment.append(iCondEqt)
                            self.TRX.Trace(('Substation/Bay/ConductEqt.name:' + _name + ' desc:' + _desc + ' virtual:' + _virtual +\
                                                                " sxy:y:" + _sx_y + " sxy:x:" + _sx_x), TL.DETAIL)

                            pTal  = pBay.firstChild
                            if pTal is not None:
                                pTal=pTal.nextSibling
                            self.ParseTerminal(pTal, poste, poste.tVoltage[idxVolt].tBay[idxBay].tConductingEquipment[idxConEqt])
                            idxConEqt = idxConEqt+1

                        elif pBay.localName == "ConnectivityNode":
                            _name     = pBay.getAttribute("name")
                            _desc     = pBay.getAttribute("desc")
                            _pathName = pBay.getAttribute("pathName")
                            _sx_y     = pBay.getAttribute("sxy:y")
                            _sx_x     = pBay.getAttribute("sxy:x")
                            iConnNode = poste.VoltageLevel.Bay.ConnectivityNode(_name, _desc, _pathName, _sx_y, _sx_x)
                            poste.tVoltage[idxVolt].tBay[idxBay].tConnectivityNode.append(iConnNode)
                            self.TRX.Trace(('Substation/Bay/ConnnectNode.name:' + _name + ' desc:' + _desc + ' pathName:' + _pathName +\
                                                                " sxy:y:" + _sx_y + " sxy:x:" + _sx_x), TL.DETAIL)
                            pTal  = pBay.firstChild
                            if pTal is not None:
                                pTal=pTal.nextSibling
                            self.ParseTerminal(pTal, poste, poste.tVoltage[idxVolt].tBay[idxBay].tConnectivityNode[idxConMode])
                            idxConMode = idxConMode + 1

                        elif pBay.localName == "Function":
                            _name     = pBay.getAttribute("name")
                            _desc     = pBay.getAttribute("desc")
                            iFunction = poste.VoltageLevel.Bay.Function(_name, _desc)
                            poste.tVoltage[idxVolt].tBay[idxBay].tFunction.append(iFunction)
                            self.TRX.Trace(('Substation/Bay/Function.name: ' + _name + ' desc:' + _desc), TL.DETAIL)

                            pPrivate = pBay.firstChild
                            if pPrivate is not None:
                                pPrivate = pPrivate.nextSibling
                                if pPrivate.localName == "Private":
                                    type = pPrivate.getAttribute("type")
                                    pDataModel = poste.tVoltage[idxVolt].tBay[idxBay].tFunction[0]
                                    self.Dyn.DynImport(type, pPrivate, pDataModel)


                        elif pBay.localName == "LNode":
                            _iedName  = pBay.getAttribute("iedName")
                            _lnClass  = pBay.getAttribute("lnClass")
                            _lnType   = pBay.getAttribute("lnType")
                            _lnInst   = pBay.getAttribute("lnInst")
                            iLNode    = poste.VoltageLevel.Bay.LNode(_iedName,_lnClass, _lnType, _lnInst)
                            poste.tVoltage[idxVolt].tBay[idxBay].tLNode.append(iLNode)
                            self.TRX.Trace(('Substation/Bay/Lnode.iedName: '+ _iedName + " lnClass:" + _lnClass + \
                                       " lnType:" + _lnType + " lnInst:" + _lnInst), TL.DETAIL)
                        pBay = pBay.nextSibling
                        if pBay is not None:
                            pBay = pBay.nextSibling
                pVolt = pVolt.nextSibling
                if pVolt is not None:
                    pVolt = pVolt.nextSibling

            pVoltageLevel = pVoltageLevel.nextSibling
            if pVoltageLevel is not None:
                pVoltageLevel = pVoltageLevel.nextSibling
        return pVoltageLevel

class Test_Substation:
    def main(directory, file, scl):
        TRX = TConsole(TL.DETAIL)

        TRX.Trace(("---------------------------------------------------"), TL.GENERAL)
        if scl is None:  # UNIT TEST
            scl = dom.parse(directory + file)
        TRX.Trace(("File:" + file), TL.GENERAL)
        sclSubstation   = scl.getElementsByTagName("Substation")
        if len(sclSubstation)!=0:
            station  = ParseSubStation(sclSubstation, TRX, file, "toto")
            tNetWork = station.ParseVoltageLevelSection(sclSubstation, file)  # <SubNetWork>
        TRX.Trace(("FIN IEC_SUBSTATION"), TL.GENERAL)

if __name__ == '__main__':

    Test_Substation.main('SCL_files/', 'LD_ALL.SCL', None)

    fileliste = FL.lstFull  # Liste de fichier de niveau système et IED
    for file in fileliste:
        Test_Substation.main('SCL_files/', file, None)

    fileliste = FL.lstIED  # Liste de fichier de niveau système et IED
    for file in fileliste:
        Test_Substation.main('SCL_files/', file, None)


