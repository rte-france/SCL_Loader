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
# \b RTE_Private Handling RTE private par of the SCL
#
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
        self.TR          = Trace(TL.GENERAL)
    ##
    # \b IDRC: # RTE Specific, SCADA communication
    class IDRC:
        ##
        # \b IDRC:
        #
        #  RTE Specific class to handle SCADA communication
        #
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

    ##
    # \b FIP: Function Input Profile
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

    ##
    # \b BAP: Basic Application Profile
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

    class PhysicalTVTCbinding:
        def __init__(self, _NumOut, _BoardNum, _BrdPos, _ConnName, _ConnRef ):
          self.NumOut    = _NumOut
          self.BoardNum  = _BoardNum
          self.BrdPos    = _BrdPos
          self.ConnName  = _ConnName
          self.ConnRef   = _ConnRef

    class RteParam:
        def __init__(self, _shortLabel, _longLabel, _conf):
            self.shortLabel = _shortLabel
            self.longLabel  = _longLabel
            self.conf       = _conf

    class RtePhysicalTVTCbinding:
        def __init__(self, _NumOut, _BoardNum, _BrdPos, _ConnName, _ConnRef):
            self.NumOut  = _NumOut
            self.BoardNum= _BoardNum
            self.BrdPos  = _BrdPos
            self.ConnName= _ConnName
            self.ConnRef = _ConnRef

    class RTE_ICD_Header:
        def __init__(self, _rteIEDType, _nomFournisseur, _modeleIED, _hwRev, _swRev,  _headerId, _headerVersion, _headerRevision):
            self.rteIEDType     = _rteIEDType
            self.nomFournisseur = _nomFournisseur
            self.modeleIED      = _modeleIED
            self.hwRev          = _hwRev
            self.swRev          = _swRev
            self.headerId       = _headerId
            self.headerVersion  = _headerVersion
            self.headerRevision = _headerRevision

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
                    self.TR.Trace(('Exception in RTE_private FIP' + __exception.__name__),TL.GENERAL)
                    exit(-1)
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
                    self.TR.Trace(('Exception in RTE_private BAP' + __exception.__name__),TL.GENERAL)
                    exit(-1)

            pRTE = pRTE.nextSibling
            if pRTE is not None:
                pRTE = pRTE.nextSibling
        return

    ##
    # \b RTE_DAI_VAL: Basic Application Profile
    #
    #  RTE Specific way to define function behavior in case of data are qualified invalid quality bit(s).
    #
    #  @param   type          - the type of the private: '<Private type="RTE-BAP_VAL">'
    #  @param   _pSCL        - the pointer to the SCL, where the tag was found
    #  @param   _pDataModel  - the pointer to the global model, where the data related to the private tag can be stored typically by dynamically creating data in it.

    def RTE_DAI_VAL(self, type, _pSCL, _pDataModel):

        if _pSCL is None or _pDataModel is None:
            return

        pRTE = _pSCL.firstChild
        if pRTE is not None:
            _value = pRTE.nodeValue

   ##
    # \b RTE_LD_ChangeLog
    #
    #  RTE Specific way to define LD_ChangeLog
    #
    #  @param   type          - the type of the private: '<Private type="RTE-Change-Log">'
    #  @param   _pSCL        - the pointer to the SCL, where the tag was found
    #  @param   _pDataModel  - the pointer to the global model, where the data related to the private tag can be stored typically by dynamically creating data in it.

    def RTE_LD_ChangeLog(self, type, _pSCL, _pDataModel):

        if _pSCL is None or _pDataModel is None:
            return

        pRTE = _pSCL.firstChild
        if pRTE is not None:
            _value = pRTE.nodeValue
            setattr(_pDataModel, "LD_ChangeLog", _value)
            _pDataModel.value = _value

    ##
    # \b RTE_LD_Model_ChangeLog
    #
    #  RTE Specific
    #
    #  @param   type          - the type of the private: '<Private type="RTE-LD-Model-ChangeLog">'
    #  @param   _pSCL        - the pointer to the SCL, where the tag was found
    #  @param   _pDataModel  - the pointer to the global model, where the data related to the private tag can be stored typically by dynamically creating data in it.

    def RTE_LD_Model_ChangeLog(self, type, _pSCL, _pDataModel):

        if _pSCL is None or _pDataModel is None:
            return

        pRTE = _pSCL.firstChild
        if pRTE is not None:
            _value = pRTE.nodeValue
            setattr(_pDataModel, "LD_Model_ChangeLog", _value)
            _pDataModel.value = _value

    ##
    # \b RTE_PARAM
    #
    #  RTE Specific way to define parameter
    #
    #  @param   type          - the type of the private: '<Private type="RTE-PARAM">'
    #  @param   _pSCL        - the pointer to the SCL, where the tag was found
    #  @param   _pDataModel  - the pointer to the global model, where the data related to the private tag can be stored typically by dynamically creating data in it.
    def RTE_PARAM(self, type, _pSCL, _pDataModel):

        if _pSCL is None or _pDataModel is None:
            return

        pRTE = _pSCL.firstChild
        if pRTE is not None:
            pRTE = pRTE.nextSibling

            _shortLabel = pRTE.getAttribute("shortLabel")
            _longLabel  = pRTE.getAttribute("longLabel")
            _conf       = pRTE.getAttribute("conf")
            iRteParam = RTE_Private.RteParam(_shortLabel,_longLabel,_conf)
            setattr(_pDataModel, "RteParam", iRteParam)

    ##
    # \b RTE_PhysicalTVTCbinding
    #
    #  RTE Specific way to define the binding of CT and VT (physical analog inputs for voltage and current)
    #
    #  @param   type          - the type of the private: '<Private type="RTE-PARAM">'
    #  @param   _pSCL        - the pointer to the SCL, where the tag was found
    #  @param   _pDataModel  - the pointer to the global model, where the data related to the private tag can be stored typically by dynamically creating data in it.

    def RTE_PhysicalTVTCbinding(self, type, _pSCL, _pDataModel):
        if _pSCL is None or _pDataModel is None:
            return
        pRTE = _pSCL.firstChild
        if pRTE is not None:
            pRTE = pRTE.nextSibling
            _NumOut   = pRTE.getAttribute("NumOut")
            _BoardNum = pRTE.getAttribute("BoardNum")
            _BrdPos   = pRTE.getAttribute("BrdPos")
            _ConnName = pRTE.getAttribute("ConnName")
            _ConnRef  = pRTE.getAttribute("ConnRef")
            iRtePhysicalTVTCbinding = RTE_Private.PhysicalTVTCbinding(_NumOut, _BoardNum, _BrdPos, _ConnName, _ConnRef)
            setattr(_pDataModel, "RtePhysicalTVTCbinding", iRtePhysicalTVTCbinding)

   ##
    # \b RTE_ICD_HEADER
    #
    #  RTE Specific way to identify an ICD file and its IED.
    #
    #  @param   type          - the type of the private: '<Private type="RTE-ICD_HEADER">'
    #  @param   _pSCL        - the pointer to the SCL, where the tag was found
    #  @param   _pDataModel  - the pointer to the global model, where the data related to the private tag can be stored typically by dynamically creating data in it.

    def RTE_ICD_HEADER(self, type, _pSCL, _pDataModel):
        if _pSCL is None or _pDataModel is None:
            return
        pRTE = _pSCL.firstChild
        if pRTE is not None:
            pRTE = pRTE.nextSibling

            _rteIEDType       = pRTE.getAttribute("rteIEDType")
            _nomFournisseur   = pRTE.getAttribute("nomFournisseur")
            _modeleIED        = pRTE.getAttribute("modeleIED")
            _hwRev            = pRTE.getAttribute("hwRev")
            _swRev            = pRTE.getAttribute("swRev")
            _headerId         = pRTE.getAttribute("headerId")
            _headerVersion    = pRTE.getAttribute("headerVersion")
            _headerRevision   = pRTE.getAttribute("headerRevision")
            iRTE_ICDHeader =  RTE_Private.RTE_ICD_Header(_rteIEDType, _nomFournisseur, _modeleIED, _hwRev, _swRev,  _headerId, _headerVersion, _headerRevision)
            setattr(_pDataModel, "RteICDHeader", iRTE_ICDHeader)
