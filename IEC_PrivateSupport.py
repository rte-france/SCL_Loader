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
# Pattern based:
#   - For example "<Private type="GE_...." >    can be mapped to a module/class/function
#     * All private tag starting by 'GE_' or 'RTE-' will be mapped to a common functin
#
# Based on complage tag name:
#   - For example "<Private type="RTE-BAP" >    will be mapped to a SPECIFIC module/class/function
#
#

import sys

"""
from class IEC_Rte_private import RTE_private

class RTE_private:
def __init__(self, _type, _pSCL, _pDataModel):

    self.type = _type                   # _Type is the attribute of private
    self.pSCL = _pSCL                   # pSCL is pointing to the SCL where the 'private' tag was found
                                        # This lets the user deal with its private data
    self.pDataModel = _pDataModel       # The pointer to IEC datamodel build by this software to allow
                                        # manuifactuer to add their private data, using 'setattr'
"""
class DynImport:

    class privateTag:
        def __init__(self, _tag, _FileName,_ClassName, _MethodName):
            self.tag        = _tag
            self.FileName   = _FileName
            self.ClassName  = _ClassName
            self.MethodName = _MethodName

    def __init__(self):

        self.DicoPrivate = {}       # For full tag name like 'RTE-FIP'
        self.TagList     = []       # For generic tag starting a simple name like 'RTE-', 'GE_', 'Siemens-'...

#       dicDoType[id] = {"import": cdc, "commentaire": desc, "tDA": tDA
#                  start with TAG         class name
# Dictionary based:
        self.DicoPrivate['RTE-FIP']     = {"FileName":    'IEC_RTE_private' ,
                                           "ClassName":   'RTE_Private'     ,
                                           "MethodName":  'RTE_FIP' }
        self.DicoPrivate['RTE-BAP']     = {"FileName":    'IEC_RTE_private' ,
                                           "ClassName":   'RTE_Private'     ,
                                           "MethodName":  'RTE_BAP' }

# List based, the matching string is the begining of the private tag
#                                                 KEY/TAG    FileName               ClassName
        self.TagList.append(DynImport.privateTag('RTE-'     , 'IEC_RTE_private'     , 'RTE_Private'    , 'RTE_Generic'))
        self.TagList.append(DynImport.privateTag('Siemens-' , 'IEC_Siemens_private' , 'Private_Siemens', 'Siemens_Generic'))
        self.TagList.append(DynImport.privateTag('ABB_'     , 'IEC_ABB_private'     , 'Private_ABB'    , 'ABB_Generic'))
        self.TagList.append(DynImport.privateTag('GE_'      , 'IEC_GE_private'      , 'Private_GE'     , 'GE_Generic'))
        self.TagList.append(DynImport.privateTag('MiCOM-'   , 'IEC_MiCOM'           , 'Private_MiCOM'  , 'MiCOM_Generic'))


    def getClassMethod(self, privateTag):
        iDico = self.DicoPrivate.get(privateTag)
        if iDico is not None:
            iFileName = iDico.get("FileName")
            iClass    = iDico.get("ClassName")
            iMethod   = iDico.get("MethodName")

            return iFileName,iClass,iMethod,

        for iTag in self.TagList:
            if privateTag.startswith(iTag.tag):
                return iTag.FileName, iTag.ClassName, iTag.MethodName

        return None,None,None


    def DynImport(self, TypePrivate, pSCL, pDataModel):
        # A private XML Tag is:
        #   - <private type='Company name'-'dataId' ... />
        # Example:
        # <Private type="RTE-FIP">
        # 	<rte:FIP xmlns:rte="http://www.rte-france.com" defaultValue="xx" ... "/>
        #   <rte:FIP xmlns:rte="http://www.rte-france.com" defaultValue="yy" ... "/>

        FileName, ClassName, FunctionName =self.getClassMethod(TypePrivate)
        if (FileName is None) or (ClassName is None) or (FunctionName is None):
            print("UNREGISTERED PRIVATE, type" + TypePrivate)
            return

        try:
            pClass = __import__(FileName)  # Example: pClass = __import__(IEC_RTE_private)

            MyClass   = getattr(pClass, ClassName)  # Example: MyClass= getattr(pClass, IEC_RTE_private)
            iMyClass  = MyClass(TypePrivate, pSCL, pDataModel)  # Initialisation of the private class

            iFunction = getattr(iMyClass,FunctionName)
            iFunction(TypePrivate, pSCL, pDataModel)  # Call the actual method

        except ImportError:
            print("FAILED TO IMPORT, File:" + FileName + " Class: " + ClassName + " Fonction" + FunctionName)
        else:
            __exception = sys.exc_info()[0]
            if __exception is not None:
                print('e' + __exception.__name__)

        # TODO ? generalise the definition of 'Private_LN' ?

if __name__ == '__main__':

     Dyn = DynImport()
     x = Dyn.DynImport("RTE-",None, None)


     file, _class, method = Dyn.getClassMethod('RTE-XXX')
     print("RTE-XXX File:", file," Class:", _class, " Method:", method)

     file, _class, method  = Dyn.getClassMethod("RTE-BAP")
     print("RTE-BAP File:", file," Class:", _class, " Method:", method)

     file, _class, method  = Dyn.getClassMethod("RTE-FIP")
     print("RTE-FIP File:", file," Class:", _class, " Method:", method)

     file, _class, method  = Dyn.getClassMethod('GE_xxx')
     print("GE_xxx File:", file," Class:", _class, " Method:", method)



