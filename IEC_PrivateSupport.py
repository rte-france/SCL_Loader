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

# This is a preliminary implementation with the data embedded into the code.
# Later on, the data will in a simple XML file.

# This class support the specific of "private" tag in the SCL.
#
# The private tags are used by IED manufacturer and engineering to add specific DATA.
# The private tags defined by the WG10 are directly integrated in the generic
#
# This class is using 'dynamic' class loading to deal with the private tags.
# In simple terms for a private tag 'RTE-BAP' the dynamic code will behave
# as this static code::

# Two mecanisms are provided to call specific module/class/function:
#
# Based on generic private tag pattern:
#
#
# At present this 'hardcoded' locally, but later-on, these data can be placed into a XML file.
import sys
import os
import importlib

from IEC_Trace import Trace
from IEC_Trace import Level as TL

import IEC_RTE_private

##
# \b DynImport: This class is defining a generic dynamic import process for private TAG.
#
# @brief
# In Python it is to load a module ('my_module.py') and from this module invoke a method ('my_method')
# of a given class.
#
# @details
# In order to get this generic, some data structures are build to support various private tags.
# The private tag are described in two set of data structures (currently coded, but #TODO shall in a XML file):
#
#  \h3 GENERIC (list of tags, typically one tag per manufacturer)
#       This is to handle the situation where a particular manufacturer has a generic tag for all its private sfor
#       example for RTE all private have a regular pattern:
#        - For example "<Private type="GE_...." >    can be mapped to a module/class/function
#           All private tag starting by 'GE_' or 'RTE-' will be mapped to a common function:
#           For example:    'RTE-' ,   'Siemens-' , 'ABB_', # GE_', # MiCOM-'
#           The matching rule is simple string comparison using startwith(...).
#
#  \h3 SPECIFIC (dictionary, as many tags as different private types)
#       Based on full tag name:
#               - For example "<Private type="RTE-BAP" >    will be mapped to a SPECIFIC module/class/function
#

class DynImport:
    ##
    # \b privateTag: Define a specific private 'Tag' and its associated file ('module), class and method
    #
    # @param    _tag        - The XML to be matched
    # @param    _FileName   - The python file where the class to be called is, example: IEC_RTE_private.py
    # @param    _ClassName  - The name of the class to use, example 'RTE_Private'
    # @param    _MethodName - The name of the method to call, example 'RTE_BAP' (RTE specific data for handling Basic Application Profile
    #
    # The 'tag' is the entry key to the dictionary, so it has to be unique.
    class privateTag:
        def __init__(self, _tag, _FileName,_ClassName, _MethodName):
            self.tag        = _tag             ## The XML to be matched
            self.FileName   = _FileName        ## The python file where the class is defined.
            self.ClassName  = _ClassName       ## The name of the class to use.
            self.MethodName = _MethodName      ## The name of the method to call.

    ##
    # \b __init__:
    #
    #  Local definition of the dictionaries of the private tags
    #       * Generic dictionary, based on specific private such 'RTE_BAP'
    #       * Table of private tag, based on 'startwith" patterns.
    def __init__(self):
        self.DicoPrivate = {}       ## For full tag name like 'RTE-FIP'
        self.TagList     = []       ## For generic tag starting a simple name like 'RTE-', 'GE_', 'Siemens-'...
        self.TR          = Trace(TL.DETAIL)

        #       dicDoType[id] = {"import": cdc, "commentaire": desc, "tDA": tDA
        #                  start with TAG         class name
        ## Dictionary based:
        self.DicoPrivate['RTE-FIP']         =       { "FileName":     'IEC_RTE_private' ,
                                                      "ClassName":    'RTE_Private'     ,
                                                      "MethodName":   'RTE_FIP' }
        self.DicoPrivate['RTE-BAP']         =       { "FileName":     'IEC_RTE_private' ,
                                                      "ClassName":    'RTE_Private'     ,
                                                      "MethodName":   'RTE_BAP' }
        self.DicoPrivate['RTE-DAI_VAL']     =       { "FileName":     'IEC_RTE_private' ,
                                                      "ClassName":    'RTE_Private'     ,
                                                      "MethodName":   'RTE_DAI_VAL' }
        self.DicoPrivate['RTE-ICD_HEADER']  =       { "FileName":     'IEC_RTE_private' ,
                                                      "ClassName":    'RTE_Private'     ,
                                                      "MethodName":   'RTE_ICD_HEADER' }
        self.DicoPrivate['RTE-LD-ChangeLog']=       { "FileName":     'IEC_RTE_private' ,   # At DAI Level (Namplt/configRev]
                                                      "ClassName":    'RTE_Private'     ,
                                                      "MethodName":   'RTE_LD_ChangeLog' }
        self.DicoPrivate['RTE-LD-Model-ChangeLog']= { "FileName":     'IEC_RTE_private' ,   # At DAI Level (Namplt/swRev]
                                                      "ClassName":    'RTE_Private',
                                                      "MethodName":   'RTE_LD_Model_ChangeLog'}
        self.DicoPrivate['RTE-PARAM']=              { "FileName":     'IEC_RTE_private' ,
                                                      "ClassName":    'RTE_Private',
                                                      "MethodName":   'RTE_PARAM'}
        self.DicoPrivate['RTE-FunctionUUID']=      { "FileName":     'IEC_RTE_private' ,
                                                     "ClassName":    'RTE_Private',
                                                     "MethodName":   'RTE_FunctionUUID'}
        self.DicoPrivate['RTE-FunctionIndice']=    { "FileName":     'IEC_RTE_private' ,
                                                     "ClassName":    'RTE_Private',
                                                     "MethodName":   'RTE_FunctionIndice'}
        self.DicoPrivate['RTE-PhysicalTVTCbinding']={"FileName":     'IEC_RTE_private' ,
                                                     "ClassName":    'RTE_Private',
                                                     "MethodName":   'RTE_PhysicalTVTCbinding'}

        ## List based, the matching string is the begining of the private tag
        #                                             KEY/TAG    FileName               ClassName
        self.TagList.append(DynImport.privateTag('RTE-'     , 'IEC_RTE_private'     , 'RTE_Private'    , 'RTE_Generic'))
        self.TagList.append(DynImport.privateTag('Siemens-' , 'IEC_Siemens_private' , 'Private_Siemens', 'Siemens_Generic'))
        self.TagList.append(DynImport.privateTag('ABB_'     , 'IEC_ABB_private'     , 'Private_ABB'    , 'ABB_Generic'))
        self.TagList.append(DynImport.privateTag('GE_'      , 'IEC_GE_private'      , 'Private_GE'     , 'GE_Generic'))
        self.TagList.append(DynImport.privateTag('MiCOM-'   , 'IEC_MiCOM'           , 'Private_MiCOM'  , 'MiCOM_Generic'))

    ##
    # \b getClassMethod
    #
    # This method look-up for a privaite tag into a dictionary and a list. If found then FileName,iClass,iMethod are returned
    #
    # @param   privateTag a private XML Tag like: <Private type="RTE-BAP">
    #         If the tag is not found the function returns \b None, \b None, \b None
    #
    #  @return  FileName    - The filename ('module') in  which the tag is supported
    #  @return  ClassName   - The class name associated to the tag.
    #  @return  MethodName  - The method to be invoked for the tag.
    #
    def getClassMethod(self, privateTag):
        iDico = self.DicoPrivate.get(privateTag)    ## Try dictionary first
        if privateTag is None:
            return None,None,None
        if iDico is None:
            return None,None,None
        print(privateTag)
        if iDico is not None:
            iFileName = iDico.get("FileName")
            iClass    = iDico.get("ClassName")
            iMethod   = iDico.get("MethodName")

            try:
                pClass = importlib.import_module(iFileName)

            except ImportError:  # The potantial exception should be ImportErrot:, usually bad FileName, ClassName or FunctionName
                self.Trace(("FAILED TO IMPORT, File:" + iFileName ),TL.ERROR)
                exit(-2)

            else:
                __exception = sys.exc_info()[0]
                if __exception is not None:
                    self.TR(("Exception: " + __exception.__name__), TL.ERROR)  # Display the exception, usually bad FileName, ClassName or FunctionName
                    exit(-2)

            return iFileName,iClass,iMethod,

        for iTag in self.TagList:                   ## Try from the list
            if privateTag.startswith(iTag.tag):     ## MATCH ?

                try:
                    pClass = importlib.import_module(iTag.FileName)

                except ImportError:  # The potantial exception should be ImportErrot:, usually bad FileName, ClassName or FunctionName
                    self.TR.Trace(("FAILED TO IMPORT, File:" + iTag.FileName),TL.ERROR)
#               exit(-2)
                else:
                    __exception = sys.exc_info()[0]
                    if __exception is not None:
                        self.TR.Trace(('Exception:' + __exception.__name__),TL.ERROR)  # Display the exception, usually bad FileName, ClassName or FunctionName
#                        exit(-2)

                return iTag.FileName, iTag.ClassName, iTag.MethodName

        return None,None,None                   ## Error Case

    ##
    # \b PrivateDynImport
    #
    #   Actual method to dynamically load the module (fileName) and invoke the method from the appropriate class.
    #   There is a try / catch block to handle the failing case.
    #
    #  @param   TypePrivate - the type of the private: <Private type="RTE-BAP">
    #  @param   pSCL        - the pointer to the SCL, where the tag was found
    #  @param   pDataModel  - the pointer to the global model, where the data related to the private tag can be stored typically by dynamically creating data in it.

    def PrivateDynImport(self, TypePrivate, pSCL, pDataModel):
        ## A private XML Tag is:
        #   - <private type='Company name'-'dataId' ... />
        # Example:
        # <Private type="RTE-FIP">
        # 	<rte:FIP xmlns:rte="http://www.rte-france.com" defaultValue="xx" ... "/>
        #   <rte:FIP xmlns:rte="http://www.rte-france.com" defaultValue="yy" ... "/>

        FileName, ClassName, FunctionName =self.getClassMethod(TypePrivate)
        if (FileName is None) or (ClassName is None) or (FunctionName is None):
            try:
                self.TR.Trace(("UNREGISTERED PRIVATE, type" + TypePrivate),TL.ERROR)
            except:
                self.TR.Trace(("UNREGISTERED PRIVATE without type" ),TL.ERROR)
            return

        try:
            pClass = importlib.import_module(FileName)

            MyClass   = getattr(pClass, ClassName)              # Example: MyClass= getattr(pClass, IEC_RTE_private)
            iMyClass  = MyClass(TypePrivate, pSCL, pDataModel)  # Initialisation of the private class

            iFunction = getattr(iMyClass,FunctionName)
            iFunction(TypePrivate, pSCL, pDataModel)            # Call the actual method

        except ImportError:  # The potantial exception should be ImportErrot:, usually bad FileName, ClassName or FunctionName
            self.TR.Trace(("FAILED TO IMPORT, File:" + FileName + " Class: " + ClassName + " Fonction" + FunctionName),TL.ERROR)
        else:
            __exception = sys.exc_info()[0]
            if __exception is not None:
                self.TR.Trace(('e' + __exception.__name__),TL.ERROR)  # Display the exception, usually bad FileName, ClassName or FunctionName

##
# \b Test DynImport: unitary tests for IEC_PrivateSupport
if __name__ == '__main__':

#    IEC_RTE_private.RTE_Private.RTE_BAP(None,None,None,None)
    TR = Trace(TL.DETAIL)
    Dyn = DynImport()
#     x = Dyn.PrivateDynImport("RTE-",None, None)       # Shall raised an exception !

    x1 = Dyn.PrivateDynImport("RTE-BAP",None, None)
    x2 = Dyn.PrivateDynImport("RTE-FIP",None, None)

    file, _class, method = Dyn.getClassMethod('RTE-XXX')
    TR.Trace(("RTE-XXX File:", file," Class:", _class, " Method:", method),TL.ERROR)

    file, _class, method  = Dyn.getClassMethod("RTE-BAP")
    TR.Trace(("RTE-BAP File:", file," Class:", _class, " Method:", method),TL.ERROR)

    file, _class, method  = Dyn.getClassMethod("RTE-FIP")
    TR.Trace(("RTE-FIP File:", file," Class:", _class, " Method:", method),TL.ERROR)

    file, _class, method  = Dyn.getClassMethod('GE_xxx')
    TR.Trace(("GE_xxx File:", file," Class:", _class, " Method:", method),TL.ERROR)



