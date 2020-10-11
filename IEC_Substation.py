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
from IEC_Trace          import Trace
from IEC_Trace          import Level  as TL
from IEC_PrivateSupport import DynImport
from IEC61850_XML_Class import SubStation

##
# \b Parse_DOType: this class create the list of DoType / Data Attributes elements
# \b Description
#   This class is parsing the "Substation" section of the SCL/SCD.
class ParseSubStation:

    ## \b Description
    #   Constructor is used to keep the dictionary of DOType available.
    #
    # @param _scl: pointer to the SCL structure created by miniDOM
    # @param _TRX: Trace function
    def __init__(self, _scl, _TR):
        self.scl            = _scl                  ##  scl
        self.TRX            = _TR                   ##  TRX instance of Trace System
        self.Dyn            = DynImport()           ## Dyn instance of DynImport to handle private section if any/

    ## \b Description
    #   Constructor is used to keep the dictionary of DOType available.
    #
    # @param _pTal      - pointer to the SCL structure, 'Terminal' TAG
    # @param pCNXNode   - Pointer to the data model at pConnectionNode level

    def ParseTerminal(self, pTal, pCNXNode):
        idxTal = 0
        while (pTal is not None) and (pTal.localName is not None):
            if pTal.localName == "Terminal":
                _name               = pTal.getAttribute("name")                ## _name             The optional relative name of the terminal at this Equipment. The default is the empty
                _desc               = pTal.getAttribute("desc")                ## _desc             Descriptive text to the terminal
                _connectivityNode   = pTal.getAttribute("connectivityNode")    ## _connectivityNode The pathname of the connectivity node to which this terminal connects.
                _substationName     = pTal.getAttribute("substationName")      ## _substationName   The name of the substation containing the connectivityNode
                _voltageLevelName   = pTal.getAttribute("voltageLevelName")    ## _voltageLevelName The name of the voltage level containing the connectivityNode
                _bayName            = pTal.getAttribute("bayName")             ## _bayName           The name of the bay containing the connectivityNode
                _cNodeName          = pTal.getAttribute("cNodeName")           ##  _cNodeName        (relative) name of the connectivityNode within its bay
                _lineName           = pTal.getAttribute("lineName")            ## _lineName         Ed 2    ??
                _neutralPoint       = pTal.getAttribute("neutralPoint")        ## _neutralPoint     Ed 2.1 ???

                iTerminal = SubStation.SubEquipement.Terminal(_name, _desc, _connectivityNode,_substationName,_voltageLevelName, _bayName,_cNodeName,_lineName, _neutralPoint)
                pCNXNode.tTerminal.append(iTerminal)
                idxTal = idxTal + 1

            pTal = pTal.nextSibling
            if pTal is not None:
                pTal = pTal.nextSibling

    ## \b Description
    #
    # Parse the VoltageLevel class
    #
    # @param Substation - the global daa model structure for subStation section of SCL
    # @param pCNXNode   - Pointer to the data model at pConnectionNode level

    def ParseVoltageLevelSection(self, Substation):
        # Analyse d'un IED
        #
        # <IED..
        #
        #    < Communication >
        #       < SubNetwork
        tVoltage = []
        _name = Substation[0].getAttribute("name")      # SubStation name
        _desc = Substation[0].getAttribute("desc")      # Description text
        poste=SubStation(_name,_desc)

        pVoltageLevel = Substation[0].firstChild.nextSibling

        while pVoltageLevel:

            _name       = pVoltageLevel.getAttribute("name")
#            _nomFreq    = pVoltageLevel.getAttribute("nomFreq")
#            _numpPhases = pVoltageLevel.getAttribute("numPhases")
            _desc       = pVoltageLevel.getAttribute("desc")

            Tension = poste.VoltageLevel(_name,_desc)
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
                    iBay     = poste.Bay(_name, _desc, _sx_x, _sx_y)
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
                            iCondEqt = SubStation.ConductingEquipment(_name, _desc, _virtual, _sx_y, _sx_x, _sx_dir )
                            poste.tVoltage[idxVolt].tBay[idxBay].tConductingEquipment.append(iCondEqt)
                            self.TRX.Trace(('Substation/Bay/ConductEqt.name:' + _name + ' desc:' + _desc + ' virtual:' + _virtual +\
                                                                " sxy:y:" + _sx_y + " sxy:x:" + _sx_x), TL.DETAIL)

                            pTal  = pBay.firstChild
                            if pTal is not None:
                                pTal=pTal.nextSibling
                            self.ParseTerminal(pTal, poste.tVoltage[idxVolt].tBay[idxBay].tConductingEquipment[idxConEqt])
                            idxConEqt = idxConEqt+1

                        elif pBay.localName == "ConnectivityNode":
                            _name     = pBay.getAttribute("name")
                            _desc     = pBay.getAttribute("desc")
                            _pathName = pBay.getAttribute("pathName")
                            _sx_y     = pBay.getAttribute("sxy:y")
                            _sx_x     = pBay.getAttribute("sxy:x")
                            iConnNode = SubStation.SubEquipement.Terminal.ConnectivityNode(_name, _desc, _pathName, _sx_y, _sx_x)
                            poste.tVoltage[idxVolt].tBay[idxBay].tConnectivityNode.append(iConnNode)
                            self.TRX.Trace(('Substation/Bay/ConnnectNode.name:' + _name + ' desc:' + _desc + ' pathName:' + _pathName +\
                                                                " sxy:y:" + _sx_y + " sxy:x:" + _sx_x), TL.DETAIL)
                            pTal  = pBay.firstChild
                            if pTal is not None:
                                pTal=pTal.nextSibling
                            self.ParseTerminal(pTal, poste.tVoltage[idxVolt].tBay[idxBay].tConnectivityNode[idxConMode])
                            idxConMode = idxConMode + 1

                        elif pBay.localName == "Function":
                            _name     = pBay.getAttribute("name")
                            _desc     = pBay.getAttribute("desc")
                            iFunction = poste.Function(_name, _desc)
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
                            _lnInst   = pBay.getAttribute("lnInst")
                            _lnClass  = pBay.getAttribute("lnClass")
                            _iedName  = pBay.getAttribute("iedName")
                            _ldInst   = pBay.getAttribute("ldInst")
                            _prefix   = pBay.getAttribute("prefix")
                            _lnType   = pBay.getAttribute("lnType")
                            iLNode    = poste.LNode(_lnInst,_lnClass,_iedName,_ldInst,_prefix,_lnType)
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
##
# \b Test_DOType: unitary test for Substation.
class Test_Substation:
    def main(directory, file, scl):
        TRX = Trace(TL.DETAIL)

        TRX.Trace(("---------------------------------------------------"), TL.GENERAL)
        if scl is None:  # UNIT TEST
            scl = dom.parse(directory + file)
        TRX.Trace(("File:" + file), TL.GENERAL)
        sclSubstation   = scl.getElementsByTagName("Substation")
        if len(sclSubstation)!=0:
            station  = ParseSubStation(sclSubstation, TRX)
            tNetWork = station.ParseVoltageLevelSection(sclSubstation)  # <SubNetWork>
        TRX.Trace(("FIN IEC_SUBSTATION"), TL.GENERAL)
##
# \b MAIN call the unitary test 'Test_Substation'
if __name__ == '__main__':

    Test_Substation.main(FL.root, 'LD_ALL.SCL', None)

    fileliste = FL.lstFull  # Liste de fichier de niveau système et IED
    for file in fileliste:
        Test_Substation.main(FL.root, file, None)

    fileliste = FL.lstIED  # Liste de fichier de niveau système et IED
    for file in fileliste:
        Test_Substation.main(FL.root, file, None)


