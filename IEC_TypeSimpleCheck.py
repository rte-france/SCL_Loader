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

# -*- coding: utf-8 -*-
from IEC_Trace      import Trace
from IEC_Trace      import Level  as TL

from IEC61850_XML_Class import DataTypeTemplates as IecType

##
# \b IEC_TypeSimpleCheck:
#
# @brief
# This class performs simple 'range' test for most of the data type 'bType'.
# It is mainly checking that is not out of range for its type, including Enumeration typr
#
class Check:
# CHARACTER STRING
    ##
    # \b VisString64
    # @param value      - value to be verified
    def VisString64(value):
        if len(value)>64:
            return False
        return value.isprintable()    # Check range of character

    ##
    # \b VisString129
    # @param value      - value to be verified
    def VisString129(value):
        if len(value)>129:
            return False
        return value.isprintable()    # Check range of character

    ##
    # \b VisString255
    # @param value      - value to be verified
    def VisString255(value):
        if len(value)>255:
            return False
        return value.isprintable()    # Check range of character

    ##
    # \b Unicode255
    # @param value      - value to be verified
    def Unicode255(value):
        if len(value)>255:
            return False
        return True             # Unicode can mix ASCII and UTF ???

# Special Data Type

    ##
    # \b Quality #TODO
    # @param value      - value to be verified
    def Quality(self, value):  # TODO any possible test ?
        return True

    ##
    # \b checkTimestamp #TODO
    # @param value      - value to be verified
    def checkTimestamp(self, value):# TODO any possible test ?
                                    # Les bits donnant la précision du timestamp peuvent être incorrecte
                                    # Une date dans les passé est également incorrect.
                                    # Format valide jusqu'à 2037..
        return True

#Scalar Data Type
    ##
    # \b BOOLEAN
    # @param value      - value to be verified
    def BOOLEAN(value):
        if value == 0:
            return True
        if value == 1:
            return True
        return False

    ##
    # \b INT8U
    # @param value      - value to be verified
    def INT8U(value):    # 8 bits unsigned, valid from 0 to 255 (0x00-0xFF)
        if value <0:
            return False
        if value >255:
            return False
        return True

    ##
    # \b INT8
    # @param value      - value to be verified
    def INT8(value):     # 8 bits signed
        if value <-127:
            return False
        if value >128:
            return False
        return True

    ##
    # \b INT16U
    # @param value      - value to be verified
    def INT16U(value):   # 16 bit unsigned
        if value > 65535:
            return False
        if value <0:
            return False
        return True

    ##
    # \b INT16
    # @param value      - value to be verified
    def INT16(value):   # 16 bits unsigned
        if value > 32767:
            return False
        if value < -32768:
            return False
        return True

    ##
    # \b INT24U
    # @param value      - value to be verified
    def INT24U(value):   # 24 bits unsigned (used in TimeStamp only)
        if value > 16777215:
            return False
        if value < 0:
            return False
        return True

    ##
    # \b INT32
    # @param value      - value to be verified
    def INT32(value):
        if value > (2 ** 16) - 1:
            return False
        if value < - ( 2 ** 16):
            return False
        return True

    ##
    # \b INT32U
    # @param value      - value to be verified
    def INT32U(value):
        if value > 2 ** 32:
            return False
        if value < 0:
            return False
        return True

    ##
    # \b INT64
    # @param value      - value to be verified
    def INT64(value):
        if value > 2 ** 63-1:
            return False
        if value < -2 ** 63:
            return False

    ##
    # \b FLOAT32
    # @param value      - value to be verified
    def FLOAT32(value):
        if value > 3.402823466E38:  #MAX_FLOAT IEE754
            return False
        if value < -1.175494351E38: #MIN_FLOAT IEE754
            return False
        return True

    ##
    # \b Check
    # @param value      - value to be verified
    def Check(value):    # Packed List de deux Booléen valeur de 0 à 3
        if value < 0 or value > 3:
            return False
        return True

    ##
    # \b Timestamp
    # @param value      - value to be verified
    def Timestamp(value):   # Stocké dans un INT24
        return True

    ##
    # \b Quality
    # @param value      - value to be verified
    def Quality(value):
        return True

    ##
    # \b Quality
    # @param value      - value to be verified
    def ObjRef(value):   # Could not find the type definition ? (CDC: ORG) Vstrin 129.
        return True

    ##
    # \b Tcmd
    # @param value      - value to be verified
    def Tcmd(value):     # Could not find the type definition ?
        return True                 # TODO

    ##
    # \b Octet64
    # @param value      - value to be verified
    def Octet64(value):
        if len(value)>64:
            return False
        return True

    ##
    # \b Enum
    # @param value      - value to be verified against its definition
    # @param iEnumType  - the enumeration type to be used for checking the value is in range of the enumeration definition
    def Enum(iEnumType, value):
        if value is None:
            return None
#recherche par la chaine
        if value.isprintable() is True:
            for iEnum in iEnumType.tEnumval:
                if iEnum.strValue == value:
                    return True
# recherche
        else:
            for iEnum in iEnumType.tEnumval:
                if iEnum.id == type:
                    if value > iEnum.max:
                        return False
                    if value < iEnum.min:
                        return False

        return True

    ##
    # \b Enum
    #
    # The function is based on using "eval" to call the method.     # TODO recode without 'eval'
    # @param type       - type of the data
    # @param value      - value to be verified against its definition
    def Type(type,value):

        if type in IecType.bType.String:
             ## fName contains the name of the function and its argument
             fName = 'Check.' + type + '("' + value + '")'
 #           trace("Fname String:",fName)
        elif type in IecType.bType.Number:
            ## fName contains the name of the function and its argument
            fName = 'Check.' + str(type) + '(' +  value + ')'
#            trace("Fname Scalar:",fName)

        ## x is the result of  "check.INT8U(34)" for example
        x = eval(fName)
        return x
##
# \b Test_TypeSimpleCheck: unitary test for all Data Type supported
#
class Test_TypeSimpleCheck:
    ## TRX initialized traces
    def main(TRX):
        if Check.BOOLEAN(0) and Check.BOOLEAN(1):
            TRX.Trace(("BOOLEAN: OK"), TL.DETAIL)

        if Check.BOOLEAN(2) != False:
            TRX.Trace(("ERROR ON BOOLEAN'"), TL.GENERAL)

        if Check.BOOLEAN(-1) != False:
            TRX.Trace(('ERROR ON BOOLEAN'), TL.GENERAL)

        # Unit Test for  "INT8 unsigned"
        if Check.INT8U(0) and Check.INT8U(255):
            TRX.Trace(("INT8U:   OK"), TL.DETAIL)

        if Check.INT8U(-1) != False:
            TRX.Trace(("ERROR ON INT8U'"), TL.GENERAL)

        if Check.INT8U(256) != False:
            TRX.Trace(('ERROR ON INT8U'), TL.GENERAL)

        # Unit Test for  "INT16 unsigned "
        if Check.INT16U(0) and Check.INT16U(65535):
            TRX.Trace(("INT16U:  OK"), TL.DETAIL)

        if Check.INT16U(-1) != False:
            TRX.Trace(("ERROR ON INT16U"), TL.GENERAL)

        if Check.INT16U(65536) != False:
            TRX.Trace(('ERROR ON INT16U'), TL.GENERAL)

        # Unit Test for  "INT16 signed"
        if Check.INT16(-32768) and Check.INT16(32767):
            TRX.Trace(("INT16:   OK"), TL.DETAIL)

        if Check.INT16(-32769) != False:
            TRX.Trace(("ERROR1 ON INT16"), TL.GENERAL)

        if Check.INT16(32769) != False:
            TRX.Trace(('ERROR2 ON INT16'), TL.GENERAL)

        # Unit Test for  "INT32 unsigned"
        if Check.INT32U(2 ** 32) and Check.INT32U(0):
            TRX.Trace(("INT32U:  OK"), TL.DETAIL)

        if Check.INT32U(-1) != False:
            TRX.Trace(("ERROR ON INT32U'"), TL.GENERAL)

        if Check.INT32U(2 ** 32 + 1) != False:
            TRX.Trace(('ERROR ON INT32U'), TL.GENERAL)

        # Unit Test for  FLOAT32
        if Check.FLOAT32(3.4E38) and Check.FLOAT32(-1.1E38):
            TRX.Trace(("FLOAT32: OK"), TL.DETAIL)

        if Check.FLOAT32(3.41E38) != False:  # MAX_FLOAT IEE754
            TRX.Trace(("ERROR ON FLOAT32"), TL.GENERAL)

        if Check.FLOAT32(-1.2E38) != False:  # MAX_FLOAT IEE754
            TRX.Trace(("ERROR ON FLOAT32"), TL.GENERAL)

        if Check.FLOAT32(3.41E40) != False:  # MAX_FLOAT IEE754
            TRX.Trace(("ERROR ON FLOAT32"), TL.GENERAL)

        if Check.FLOAT32(-1.2E40) != False:  # MAX_FLOAT IEE754
            TRX.Trace(("ERROR ON FLOAT32"), TL.GENERAL)

        TRX.Trace(("END OF IEC SIMPLE CHECK"), TL.GENERAL)
##
# \b Test_TypeSimpleCheck:
#
# @brief
# This class performs unitary of the main class above, by calling the Test_TypeSimpleCheck.
if __name__ == '__main__':
    ## TRX initialize the traces
    TRX = Trace(TL.DETAIL)
    Test_TypeSimpleCheck.main(TRX)
