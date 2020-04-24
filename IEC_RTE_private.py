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

from IEC_LN        import Parse_LN
from IEC_LN        import LN_LN0

class IDRC:  # RTE Specific, SCADA communication
    def __init__(self, _value, _sLabel, _Appear, _Disappear, _Invalid, _Transient, _IndLocal):
        self.value = _value
        self.sLabel = _sLabel
        self.Appear = _Appear
        self.Disappear = _Disappear
        self.Invalid = _Invalid
        self.Transient = _Transient
        self.IndLocal = _IndLocal

class Private_RTE:
    def __init__(self, _type, _pSCL, _pDataModel):
        self.type        = _type
        self.pSCL        = _pSCL
        self.pDataModel  = _pDataModel

    def RTE_Generic(self, type, _pSCL, _pDataModel):
        print("RTE Private tag:", type)

    def Private_LN(self, type, _pSCL, _pDataModel):
        if (type == "RTE_FIP"):

            pRTE = _pSCL.firstChild.nextSibling
            while pRTE is not None:
                _defaultValue  = pRTE.getAttribute("defaultValue")
                _dataStreamKey = pRTE.getAttribute("dataStreamKey")
                irteFIP = LN_LN0.Inputs.rteFIP(_defaultValue, _dataStreamKey)
                try:
                    _pDataModel.tFIP.append(irteFIP)
                except:
                    setattr(_pDataModel,'tFIP',[])
                    _pDataModel.tFIP.append(irteFIP)

                pRTE = pRTE.nextSibling
                if pRTE is not None:
                    pRTE = pRTE.nextSibling
            return

        if (type == "RTE_BAP"):
            pRTE = _pSCL.firstChild.nextSibling
            while pRTE is not None:
                _variant = pRTE.getAttribute("variant")
                _defaultValue = pRTE.getAttribute("defaultValue")
                _dataStreamKey = pRTE.getAttribute("dataStreamKey")
                irteBAP = LN_LN0.Inputs.rteBAP(_variant, _defaultValue, _dataStreamKey)
                try:
                    self._tBAP.append(irteBAP)
                except:
                    setattr(_pDataModel,'tBAP',[])
                    _pDataModel._tBAP.append(irteBAP)

                pRTE = pRTE.nextSibling
                if pRTE is not None:
                    pRTE = pRTE.nextSibling
            return

        if type == "RTE_IDRC":
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

        if type == "RTE_FunctionUUID":
            _value = _pSCL.firstChild.data
            print("YOUPI:"+_value)

        if type == "RTE_FunctionIndice":
            _value = _pSCL.firstChild.data
            print("YOUPI:"+_value)

#   RtePrivate = DynImp(_type, pType, LN_LN0.DOI.DAI)


