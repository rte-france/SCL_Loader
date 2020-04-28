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
from IEC_Trace      import IEC_Console   as TConsole
from IEC_FileListe  import FileListe     as FL
from IEC_Trace      import TraceLevel    as TL
from IEC61850_XML_Class import SubNetWork

class Communication:
    def __init__(self,_SubNetwork):
        self.tSubnetwork = _SubNetwork          # 2 sub-network

class ParseCommunication:
    def __init__(self, _scl, _TR):
        self.scl      = _scl
        self.TRX      = _TR

    def ParseAddress(self, pAP, Titre):
        self.TRX.Trace(("     "+Titre+":"), TL.DETAIL) #
        tAdress = []
        pAdr=pAP                                      # Adresse IP Connected AP
        while pAdr.nextSibling:                      # <Address>
            if pAdr.localName is None:               #   <P type="OSI-AP-Title">1,3,9999,23</P>
                pAdr = pAdr.nextSibling               #   <P type="OSI-AE-Qualifier">23</P>
                continue                            #   <P type="OSI-PSEL">00000001</P>
            type  = pAdr.getAttribute("type")        # <P type="OSI-SSEL">0001</P>
            value = pAdr.firstChild.data             # <P type="OSI-TSEL">0001</P>
            self.TRX.Trace(("         "+type+"='"+value+"'"), TL.DETAIL)  # </Address>
            iPtype = SubNetWork.ConnectedAP.PhysConn.PType(type, value)

            tAdress.append(iPtype)
            pAdr = pAdr.nextSibling
            continue
        return(tAdress)
    def ParseConnectedAP(self, SubNet, CnxAP, TRX):
        # Partie Address de connected pAP.
        #            <Address >
        #               < P  type = "IP-SUBNET" > 255.255.255.0 < / P >
        #               ...
        #               < P  type = "OSI-SSEL" > 01 < / P >
        #            </ Address >
        tAddress = []
        if SubNet.firstChild is None:           # cas de: <ConnectedAP iedName="L2_MU_SCU_VIZ_MGU" apName="ETH_2" />
            return CnxAP
        pAP = SubNet.firstChild.nextSibling      # CnxAP
        tGSE = []
        tSMV = []
        while pAP:  # Pour tout les "ConnectedAP"...
            if pAP.localName is None:
                pAP = pAP.nextSibling
                if pAP is None:
                    break
                continue
            if pAP.localName == "Private":
                pAP = pAP.nextSibling
                continue
            if pAP.localName == "Address":
                tAddress = self.ParseAddress(pAP.firstChild.nextSibling,"Address")    #<Adress>
#                tAddress.append(iAddress)
                CnxAP.tAddress = tAddress
            if pAP.localName == "PhysConn":
                _type = pAP.getAttribute("type")
                iPhysConn=SubNetWork.ConnectedAP.PhysConn(_type, None)
                iPhysConn.tPhysAddress = self.ParseAddress(pAP.firstChild.nextSibling,"PhysConn")
                CnxAP.PhysConn.append(iPhysConn)
            if pAP.localName == "SMV":                       # <SMV ldInst="MU01" cbName="MSVCB01" desc="bla...bla>
                _ldInst = pAP.getAttribute("ldInst")         #   <Address> ....
                _cbName = pAP.getAttribute("cbName")
                _desc   = pAP.getAttribute("desc")
                iSMV=SubNetWork.ConnectedAP.SMV(_ldInst,_cbName,_desc)
#                self.TRX.Trace(("     SMV:         ldInst:"+_ldInst+" cbName:"+_cbName+" desc:"+_desc),TL.DETAIL)

                iAddressSMV = pAP.firstChild.nextSibling     #	<Address>
                if (iAddressSMV.localName=="Address"):      #		<P type="MAC-Address">01-0C-CD-04-00-00</P>
                    iAddressSMV = self.ParseAddress(iAddressSMV.firstChild.nextSibling,"SMV Address:")         #		...
                    iSMV.tSMVAddress = iAddressSMV          #		<P type="VLAN-PRIORITY">4</P>
    #                tSMV.append(iSMV)                       #	</Address>
                    CnxAP.tSMV.append(iSMV)

            if pAP.localName == "GSE":                       #<GSE ldInst="PIGO" cbName="GoCB1">
                _ldInst = pAP.getAttribute("ldInst")         #   <Address>
                _cbName = pAP.getAttribute("cbName")         #     <P type="MAC-Address">01-01-19-01-11-01</P>
                _desc   = pAP.getAttribute("desc")           #     <P type="VLAN-ID">00B</P>
                iGSE=SubNetWork.ConnectedAP.GSE(_ldInst,_cbName,_desc) #     <P type="APPID">1911</P>
#                self.TRX.Trace(("     GSE: ldInst:" + _ldInst + " cbName:" + _cbName + " desc:" + _desc), TL.DETAIL)

                pGSE = pAP.firstChild.nextSibling            #     <P type="VLAN-PRIORITY">4</P>
                while pGSE is not None:
                    if(pGSE.localName == "Address"):            #    </Address>
                        _Adr= self.ParseAddress(pGSE.firstChild.nextSibling,"GSE Address:")
                        iGSE.tGSEAddress = _Adr
                        pGSE = pGSE.nextSibling
                    if(pGSE.localName == "MinTime"):           # <MinTime unit="s" multiplier="m">2</MinTime></GSE>
                        _unit        = pGSE.getAttribute("unit")
                        _multiplier  = pGSE.getAttribute("multiplier")
                        _MinTime     = pGSE.firstChild.nodeValue
                        minTime=SubNetWork.ConnectedAP.GSE.Min(_unit,_multiplier,_MinTime)
                        iGSE.minTime = minTime
                        self.TRX.Trace(("     GSE: MinTime.unit:"+_unit+" multi:"+_multiplier+" MinTime="+_MinTime),TL.DETAIL)
                        pGSE = pGSE.nextSibling
                    if(pGSE.localName == "MaxTime"):           # <MaxTime unit="s" multiplier="m">5000</MaxTime>
                        _unit       = pGSE.getAttribute("unit")
                        _multiplier = pGSE.getAttribute("multiplier")
                        _MaxTime    = pGSE.firstChild.nodeValue
                        maxTime    = SubNetWork.ConnectedAP.GSE.Max(_unit, _multiplier, _MaxTime)
                        iGSE.maxTime= maxTime
                        self.TRX.Trace(("     GSE: MaxTime.unit:"+_unit+" multi:"+_multiplier+" MaxTime="+_MaxTime),TL.DETAIL)
                        pGSE = pGSE.nextSibling
                    pGSE = pGSE.nextSibling
                    CnxAP.tGSE.append(iGSE)
            pAP = pAP.nextSibling
            continue
        return CnxAP
    def ParseSubNet(self, pSubNet, iSubNet):
        pSubNet = pSubNet.firstChild

        tAP = []        # Tableau des accès point pour un 'subNetWork'.

        while pSubNet is not None:
            if pSubNet is not None:
                pSubNet = pSubNet.nextSibling

            if pSubNet is None:
                break
            if pSubNet.localName is None:
                continue

            if pSubNet.localName == 'Private':
#                self.TRX.Trace(("Private in SubNetworkSubNetwork"), TL.ERROR)
                continue
    #__init__(self, _name, _type, _desc, _text, _bitRate, _ConnectedAP)

            # TODO ajouter au model le cas du text et BitRate
            if pSubNet.localName == "Text":
                if pSubNet.firstChild is not None:
                    localText = pSubNet.firstChild.data
                else:
                    localText = "pas de texte !"
                self.TRX.Trace(("SubNetWork" + localText), TL.GENERAL)
                iSubNet.text = localText

            if pSubNet.localName == "BitRate":
                Unit  = pSubNet.getAttribute("unit")
                Value = pSubNet.firstChild.data
                _BitRate = SubNetWork.BitRate(Unit, Value)
                iSubNet.bitRate = _BitRate
                self.TRX.Trace(("BitRate:     Unit:" + Unit + "Value:" + Value), TL.DETAIL)

            if pSubNet.localName == "ConnectedAP":  # def __init__(self,_iedName,_apName,_desc,_Address,_SMV,_PhysConn):
                pAP = pSubNet
                _iedName = pAP.getAttribute("iedName")
                _apName = pAP.getAttribute("apName")
                _desc = pAP.getAttribute("desc")
                self.TRX.Trace(("        ConnectedAP: iedName:" + _iedName + " apName:" + _apName + " desc: " + _desc), TL.DETAIL)
                iCnxAP = SubNetWork.ConnectedAP(_iedName, _apName, _desc)
                iCnxAP = self.ParseConnectedAP(pAP, iCnxAP, self.TRX)
                tAP.append(iCnxAP)
                continue

        iSubNet.tConnectedAP = tAP
        return iSubNet
    def ParseCommSection(self, NetWork):
        # Analyse d'un IED
        #
        # <IED..
        #
        #    < Communication >
        #       < SubNetwork
        tNetWork = []
        pSubNet = NetWork[0].firstChild.nextSibling
        while pSubNet:
            if pSubNet is None:
                break

            _name = pSubNet.getAttribute("name")
            _type = pSubNet.getAttribute("type")
            _desc = pSubNet.getAttribute("desc")
            iSubNet = SubNetWork(_name, _type, _desc, 'text', 'bitrate', None)  # None: reservé for ConnectedAP
            self.TRX.Trace(("SubNetWork: name:" + _name + " type:" + _type + " desc:" + _desc), TL.DETAIL)
            iSubNet = self.ParseSubNet(pSubNet,iSubNet)
            tNetWork.append(iSubNet)
            if pSubNet.firstChild is None:
                self.TRX.Trace(("Error: SubNet.firstChild is None"), TL.ERROR)
            if pSubNet.localName is None:
                pSubNet = pSubNet.nextSibling
                continue

            pSubNet = pSubNet.nextSibling
            if pSubNet is not None:
                pSubNet = pSubNet.nextSibling

        return(tNetWork)

        comm = scl.getElementsByTagName("Communication")
        subNetWork =ParseCommunication(comm,TX)
        tNetWork  = subNetWork.ParseCommSection(comm)  # <SubNetWork>

class Test_Communication:
    def main(directory, file, scl):
        TRX = TConsole(TL.DETAIL)

        TRX.Trace(("---------------------------------------------------"), TL.GENERAL)
        if scl is None:  # UNIT TEST
            scl = dom.parse(directory + file)
        TRX.Trace(("File:" + file), TL.GENERAL)
        comm = scl.getElementsByTagName("Communication")
        subNetWork = ParseCommunication(comm, TRX)
        tNetWork = subNetWork.ParseCommSection(comm)  # <SubNetWork>
        TRX.Trace(("FIN IEC_SUBSTATION"), TL.GENERAL)

if __name__ == '__main__':
    fileliste = FL.lstFull  # List of system level files (SCL, SCD,...)
    for file in fileliste:
        Test_Communication.main('SCL_files/', file, None)

    fileliste = FL.lstIED  # List of IED level files (SCL, SCD,...)
    for file in fileliste:
        Test_Communication.main('SCL_files/', file, None)
