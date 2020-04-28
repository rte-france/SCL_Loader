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

# Implementation of PrivateClass:

from IEC_LN              import Parse_LN
from IEC61850_XML_Class  import IED
from IEC_Trace           import IEC_TraceFile as TConsole
from IEC_Trace           import TraceLevel as TL
import sys

class IDRC:  # RTE Specific, SCADA communication
    def __init__(self, _value, _sLabel, _Appear, _Disappear, _Invalid, _Transient, _IndLocal):
        self.value = _value
        self.sLabel = _sLabel
        self.Appear = _Appear
        self.Disappear = _Disappear
        self.Invalid = _Invalid
        self.Transient = _Transient
        self.IndLocal = _IndLocal

class RTE_Private:
    def __init__(self, _type, _pSCL, _pDataModel):
        self.type        = _type
        self.pSCL        = _pSCL
        self.pDataModel  = _pDataModel
        self.TR          = TConsole(TL.GENERAL,None)

    def RTE_Generic(self, type, _pSCL, _pDataModel):

        if type == "RTE_FunctionUUID":
            _value = self.pSCL.firstChild.data
            self.TR.Trace(("Rte Private: ") + type, TL.DETAIL)
        if type == "RTE_FunctionIndice":
            _value = self.pSCL.firstChild.data
            self.TR.Trace(("Rte Private: ") + type, TL.DETAIL)

        if type == "RTE-IRDC":
            pIDRC       = _pSCL.firstChild.nextSibling
            _value      = pIDRC.getAttribute("value")
            _sLabel     = pIDRC.getAttribute("shortLabel")
            _Appear     = pIDRC.getAttribute("additionnalLabelForAppearance")
            _Disappear  = pIDRC.getAttribute("additionnalLabelForDisappearance")
            _Invalid    = pIDRC.getAttribute("additionnalLabelForInvalidity")
            _Transient  = pIDRC.getAttribute("transientSignal")
            _IndLocal   = pIDRC.getAttribute("bayLocalModeIndependentSignal")
            iIDRC = IDRC(_value, _sLabel, _Appear, _Disappear, _Invalid, _Transient, _IndLocal)
            setattr(_pDataModel, 'IDRC', iIDRC)
            self.TR.Trace(("Rte Private: IDRC: ") + _sLabel + " value:" + _value, TL.GENERAL)

    def RTE_FIP(self,type, _pSCL, _pDataModel):
        pRTE = self.pSCL.firstChild.nextSibling
        while pRTE is not None:
            _defaultValue  = pRTE.getAttribute("defaultValue")
            _dataStreamKey = pRTE.getAttribute("dataStreamKey")
            irteFIP = IED.AccessPoint.Server.LN.Inputs.rteFIP(_defaultValue, _dataStreamKey)
            self.TR.Trace(("Rte Private: FIP ") + type, TL.DETAIL)

            try:
                self.pDataModel.tFIP.append(irteFIP)
            except:
                setattr(self.pDataModel,'tFIP',[])
                self.pDataModel.tFIP.append(irteFIP)
            else:
                __exception = sys.exc_info()[0]
                if __exception is not None:
                    print('e' + __exception.__name__)

            pRTE = pRTE.nextSibling
            if pRTE is not None:
                pRTE = pRTE.nextSibling

        return

    def RTE_BAP(self, type, _pSCL, _pDataModel):

        pRTE = self.pSCL.firstChild.nextSibling
        while pRTE is not None:
            _variant       = pRTE.getAttribute("variant")
            _defaultValue  =  pRTE.getAttribute("defaultValue")
            _dataStreamKey = pRTE.getAttribute("dataStreamKey")
            irteBAP = IED.AccessPoint.Server.LN.Inputs.rteBAP(_variant, _defaultValue, _dataStreamKey)
            self.TR.Trace(("Rte Private: BAP ") + type, TL.DETAIL)
            try:
                self.pDataModel.tBAP.append(irteBAP)
            except AttributeError:
                setattr(self.pDataModel,'tBAP',[])
                self.pDataModel.tBAP.append(irteBAP)
            else:
                __exception = sys.exc_info()[0]
                if __exception is not None:
                    print('e' + __exception.__name__)

            pRTE = pRTE.nextSibling
            if pRTE is not None:
                pRTE = pRTE.nextSibling
        return

#   RtePrivate = DynImp(_type, pType, LN_LN0.DOI.DAI)


