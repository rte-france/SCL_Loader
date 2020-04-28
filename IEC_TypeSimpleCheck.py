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

from IEC_Trace      import IEC_Console  as TRACE
from IEC_Trace      import TraceLevel   as TL

from IEC61850_XML_Class import DataTypeTemplates as IecType

class Check:
# CHARACTER STRING

    def VisString64(value):
        if len(value)>64:
            return False
        return value.isprintable()    # Check range of character

    def VisString129(value):
        if len(value)>129:
            return False
        return value.isprintable()    # Check range of character

    def VisString255(value):
        if len(value)>255:
            return False
        return value.isprintable()    # Check range of character

    def Unicode255(value):
        if len(value)>255:
            return False
        return True             # Unicode can mix ASCII and UTF ???

# Special Data Type

    def Quality(self, value):  # TODO any possible test ?
        return True

    def checkTimestamp(self, value):# TODO any possible test ?
                                    # Les bits donnant la précision du timestamp peuvent être incorrecte
                                    # Une date dans les passé est également incorrect.
                                    # Format valide jusqu'à 2037..
        return True

#Scalar Data Type
    def BOOLEAN(value):
        if value == 0:
            return True
        if value == 1:
            return True
        return False

    def INT8U(value):    # 8 bits unsigned, valid from 0 to 255 (0x00-0xFF)
        if value <0:
            return False
        if value >255:
            return False
        return True

    def INT8(value):     # 8 bits signed
        if value <-127:
            return False
        if value >128:
            return False
        return True

    def INT16U(value):   # 16 bit unsigned
        if value > 65535:
            return False
        if value <0:
            return False
        return True

    def INT16(value):   # 16 bits unsigned
        if value > 32767:
            return False
        if value < -32768:
            return False
        return True

    def INT24U(value):   # 24 bits unsigned (used in TimeStamp only)
        if value > 16777215:
            return False
        if value < 0:
            return False
        return True

    def INT32(value):
        if value > (2 ** 16) - 1:
            return False
        if value < - ( 2 ** 16):
            return False
        return True

    def INT32U(value):
        if value > 2 ** 32:
            return False
        if value < 0:
            return False
        return True

    def INT64(value):
        if value > 2 ** 63-1:
            return False
        if value < -2 ** 63:
            return False

    def FLOAT32(value):
        if value > 3.402823466E38:  #MAX_FLOAT IEE754
            return False
        if value < -1.175494351E38: #MIN_FLOAT IEE754
            return False
        return True

    def Check(value):    # Packed List de deux Booléen valeur de 0 à 3
        if value < 0 or value > 3:
            return False
        return True

    def Timestamp(value):   # Stocké dans un INT24
        return True

    def Quality(value):
        return True

    def ObjRef(value):   # Could not find the type definition ? (CDC: ORG) Vstrin 129.
        return True

    def Tcmd(value):     # Could not find the type definition ?
        return True                 # TODO

    def Octet64(value):
        if len(value)>64:
            return False
        return True

    def Enum(iEnumType, value):
        if value is None:
            return None
#recherche par la chaine
        if value.isprintable() is True:
##            print("LA valeur est exprimée par son ID:",value)
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

# Appel 'dynamique' ... potentiellement peu performant
    def Type(type,value):

        if type in IecType.bType.String:
            fName = 'Check.' + type + '("' + value + '")'
 #           print("Fname String:",fName)
        elif type in IecType.bType.Number:
            fName = 'Check.' + str(type) + '(' +  value + ')'
#            print("Fname Scalar:",fName)

        x= eval(fName)

class Test_TypeSimpleCheck:
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

if __name__ == '__main__':

    TRX = TRACE(TL.DETAIL)
    Test_TypeSimpleCheck.main(TRX)
