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

from IEC_Trace  import Trace
from IEC_Trace  import Level as TL
import sys


##
# \b RTE_Private:
# @brief
#   This class handles the XML private extensions for RTE
#
#   The function from this class are called after loading 'dynamically' the class.

class RTE_Private:
    ##
    # \b RTE_Private:
    #
    #  @param   _type       - the type of the private: '<Private type="RTE-BAP">'
    #  @param   _pSCL        - the pointer to the SCL, where the tag was found
    #  @param   _pDataModel  - the pointer to the global model, where the data related to the private tag can be stored typically by dynamically creating data in it.
    def __init__(self, _type, _pSCL, _pDataModel):
        ## type  - the private TAG
        self.type        = _type
        ## pSCL - the pointer to the SCL, where the tag was found
        self.pSCL        = _pSCL
        ## pDataModel - the pointer to the data model
        self.pDataModel  = _pDataModel
        ## TR - the initialized trace service.
        self.TR          = Trace.Console(TL.GENERAL)

    class IDRC:  # RTE Specific, SCADA communication
        ##
        # \b IDRC:
        #
        #
        #  RTE Specific class to handle SCADA communication
        #  @param _value     value of the data point
        #  @param _sLabel    short label for the data point
        #  @param _Appear    short text for 'appearing' event, for example 'DEB'   (BEGinning)
        #  @param _Disappear short text for 'disappearing' event, for example 'FIN'  (ENDing)
        #  @param _Invalid   short text for 'invalidity" casr, for exemple 'DCNX'  (Disconnected)
        #  @param _Transient True or false
        #  @param _IndLocal  Signal is dependant from Local/remote or not
        def __init__(self, _value, _sLabel, _Appear, _Disappear, _Invalid, _Transient, _IndLocal):
            self.value      = _value       ## value     the xvalue of the data point
            self.sLabel     = _sLabel      ## sLabel    short label for the data point
            self.Appear     = _Appear      ## Appear    short text for 'appearing' event, for example 'DEB'   (BEGinning)
            self.Disappear  = _Disappear   ## Disappear short text for 'disappearing' event, for example 'FIN'  (ENDing)
            self.Invalid    = _Invalid     ## Invalid   short text for 'invalidity" casr, for exemple 'DCNX'  (Disconnected)
            self.Transient  = _Transient   ## Transient True or false
            self.IndLocal   = _IndLocal    ## IndLocal  Signal is dependant from Local/remote or not

    class FIP:
        ##
        # \b FIP: Function Input Profile
        #
        #  RTE Specific data class to handle default value for function
        #
        ##   @param  _defaultValue   : default value to use if data source is lost
        ##   @param  _dataStreamKey  : unique key to the data flux concerned
        def __init__(self, _defaultValue, _dataStreamKey):
            ##  defaultValue   : default value to use if data source is lost
            self.defaultValue   = _defaultValue
            ##  dataStreamKey  : unique key to the data flux concerned
            self.dataStreamKey  = _dataStreamKey
    class BAP:
        ##
        # \b BAP: Basic Application Profile
        #
        #  RTE Specific way to define function behavior in case of data are qualified invalid quality bit(s).
        #
        ##   @param  _variant        : identify the variant for the given data flux (dataStreamKey) in case of quality issue.
        ##   @param  _defaultValue   : default value to be for the data stream according to the variant
        ##   @param  _dataStreamKey  : unique key to the data flux concerned
        def __init__(self, _variant, _defaultValue, _dataStreamKey):
            ## variant        : identify the variant for the given data flux (dataStreamKey) in case of quality issue.
            self.variant        = _variant
            ## defaultValue   : default value to be for the data stream according to the variant
            self.defaultValue   = _defaultValue
            ## dataStreamKey  : unique key to the data flux concerned
            self.dataStreamKey  = _dataStreamKey

    ##
    # \b RTE_Generic
    #
    # This method is invoded for generic tags 'RTE-'.
    #
    #  @param   type       - the type of the private: <Private type="RTE-BAP">
    #  @param   _pSCL        - the pointer to the SCL, where the tag was found
    #  @param   _pDataModel  - the pointer to the global model, where the data related to the private tag can be stored typically by dynamically creating data in it.

    def RTE_Generic(self, type, _pSCL, _pDataModel):
        if _pSCL is None or _pDataModel is None:
            return

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
            iIDRC = RTE_Private.IDRC(_value, _sLabel, _Appear, _Disappear, _Invalid, _Transient, _IndLocal)
            setattr(_pDataModel, 'IDRC', iIDRC)
            self.TR.Trace(("Rte Private: IDRC: ") + _sLabel + " value:" + _value, TL.GENERAL)

    ##
    # \b FIP: Function Input Profile
    #
    #  RTE Specific data class to handle default value for function.
    #
    #  @param   type        - the type of the private: <Private type="RTE-BAP">
    #  @param   _pSCL        - the pointer to the SCL, where the tag was found
    #  @param   _pDataModel  - the pointer to the global model, where the data related to the private tag can be stored typically by dynamically creating data in it.
    #
    def RTE_FIP(self,type, _pSCL, _pDataModel):
        if _pSCL is None or _pDataModel is None:
            return

        pRTE = self.pSCL.firstChild.nextSibling
        while pRTE is not None:
            _defaultValue  = pRTE.getAttribute("defaultValue")
            _dataStreamKey = pRTE.getAttribute("dataStreamKey")
            irteFIP = RTE_Private.FIP(_defaultValue, _dataStreamKey)
            self.TR.Trace(("Rte Private: FIP ") + type, TL.DETAIL)

            try:
                self.pDataModel.tFIP.append(irteFIP)    # if append is raising an exception, the attribute need to created
            except:
                setattr(self.pDataModel,'tFIP',[])      # Create the missing attribute
                self.pDataModel.tFIP.append(irteFIP)
            else:
                __exception = sys.exc_info()[0]
                if __exception is not None:
                    print('e' + __exception.__name__)

            pRTE = pRTE.nextSibling
            if pRTE is not None:
                pRTE = pRTE.nextSibling

        return

    ##
    # \b BAP: Basic Application Profile
    #
    #  RTE Specific way to define function behavior in case of data are qualified invalid quality bit(s).
    #
    #  @param   type          - the type of the private: '<Private type="RTE-BAP">'
    #  @param   _pSCL        - the pointer to the SCL, where the tag was found
    #  @param   _pDataModel  - the pointer to the global model, where the data related to the private tag can be stored typically by dynamically creating data in it.

    def RTE_BAP(self, type, _pSCL, _pDataModel):

        if _pSCL is None or _pDataModel is None:
            return

        pRTE = self.pSCL.firstChild.nextSibling
        while pRTE is not None:
            _variant       = pRTE.getAttribute("variant")
            _defaultValue  =  pRTE.getAttribute("defaultValue")
            _dataStreamKey = pRTE.getAttribute("dataStreamKey")
            irteBAP = RTE_Private.BAP(_variant, _defaultValue, _dataStreamKey)
            self.TR.Trace(("Rte Private: BAP ") + type, TL.DETAIL)
            try:
                self.pDataModel.tBAP.append(irteBAP)        # if append is raising an exception, the attribute need to created
            except AttributeError:                                                                                            
                setattr(self.pDataModel,'tBAP',[])          # Create the missing attribute
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


