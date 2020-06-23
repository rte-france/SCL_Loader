#
# Copyright (c) 2019-2020, RTE (https://www.rte-france.com)
# See AUTHORS.txt
#
# This Source Code Form is subject to the terms of the Apache License, version 2.0.
# If a copy of the Apache License, version 2.0 was not distributed with this file,
# you can obtain one at http://www.apache.org/licenses/LICENSE-2.0.
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of [R#SPACE], [IEC61850 Digital Control System testing.
#

from importlib import import_module

##
# \b Injection_UI:
#
# This class defines:
#       - a method to define a well balanced  simple 3 Currents/Voltages 50Hz signals.
#       - a method to define any unbalanced 3 Currents/Voltages 45-51Hz signal.
#
# Once the signal is defined, it can be used for injection, several signals signal can be defined.
# For this class the voltage is between 0-100V and current between 0-1A or 0-5A for nomimal voltage / current.
# Non nominal Voltage/Current are limited to XXXX for U and YYY for 5A as per the specification of injection box.

class Injection:
    class Simple:
        # Simple injection
        # Nominal value for phase A , B, c
        def __init__ (self, _Voltage, _Current, _Frequency):
            self.Voltage  =   _Voltage    ## from 0 to 100.
            self.Current  =   _Current    ## from 0 to 5A.
            self.Frequenc =  _Frequency   ## 45 to 65 Hz.
    ##
    #
    # @param Ua,Ub,UBc  : for physical VT: the range is from 0 to 100V (nominal condition), when used for Sample Value,
    #                       the actual range is described the TVTR Logical Node.
    #
    # @param phUa,phUb,phUc, phIa,phIb,phIc: The unit is degree (°), the range -180 to +180°
    #
    # @param Ia,Ib,Icc  : for physical VT: the range is from 0 to 1A or 5A (nominal condition), when used for Sample Value,
    #                       the actual range is described the TVTR Logical Node.
    # @pâram                      the actual range is described the TVTR Logical Node.

    class Complex:
        def __init__(self, _Ua, _phUa, _Ub, _phUb, _Uc, _phUc, _U0, _Ia, _phIa, _Ib,_phIb, _Ic, _phIc,_I0, _Freq):
            self.Ua     = _Ua       ## Voltage in V 0-100V (Physical)
            self.phUa   = _phUa     ## Phase in degre ° (nominal 0)
            self.Ub     = _Ub       ## Voltage in V 0-100V
            self.phUb   = _phUb     ## Phase in degre ° (nominal 120)
            self.Uc     = _Uc       ## Voltage in V 0-100V
            self.phUc   = _phUc     ## Phase in degre ° (nominal -120)
            self.U0     = _U0
            self.Ia     = _Ia       ## Current in Ampere 0-1 or 0-5A  for In, up to 30In for fault
            self.phIa   = _phIa     ## Phase in degre (nominal 120°)
            self.Ib     = _Ib       ## Current in Ampere 0-1 or 0-5A  for In, up to 30In for fault
            self.phIb   = _phIb     ## Phase in degre (nominal -0°)
            self.Ic     = _Ic       ## Current in Ampere 0-1 or 0-5A  for In, up to 30In for fault
            self.phIc   = _phIc     ## Phase in degre (nominal -120°)
            self.I0     = _I0
            self.Freq   = _Freq     ## Frequency from 45 to 65 Hz
    class State:
        On  = 1     # For event trigger, call back if state changes to ON
        Off = 0     # For event trigger, call back if state changes to OFF
        Any = 2     # For event trigger, call back if state changes

    class Injection_CTVT:

        def __init__(self,_BoxName, _ipAdr):
            self.BoxName = _BoxName
            self.ipAdr   = _ipAdr

        def MuxSelection(self, numSelection):
            if numSelection <1 or numSelection > 4:
                return False
            return

        ##
        # \b InjectionNominal
        #
        #   Frequency default is 50Hz, current phasing 60° and voltag 60% (nominal)
        #   U0 / V0 are nul
        #
        # @param    _Simple  an instance of the Signal.Simple Class.
        #
        def InjectionNominal(self, _Simple):

            signalID = None

            return signalID

        ##
        # \b InjectionDetailed all
        #
        # Each voltage and current is described (Amplitube, Phase, Frequency)
        #
        # @param    _Complex  an instance of the Signal.Complex Class.
        #
        def InjectionDetailed(self, _Complex):
            signalID = None
            return signalID

        def StartInjection(self, _signalID):

            return

        def StopInjection(self, _signalID):

            return

        ##
        # \b WaitEvent
        #
        #
        #
        def WaitEvent(self, _IOInput, _iState, _callBack):
            return


        def RegisterEvent(self, _IOInput, _iState, _Method):

            return

        def SetOutput(self, IOInput, state):
            return

    class Injection_SV:
        ##
        # \b InjectionNominal
        #
        #   Frequency default is 50Hz, current phasing 120° and voltage 120% (nominal)
        #   U0 / V0 are nul
        #
        # @param    _Simple  an instance of the Signal.Simple Class.
        #
        def InjectionNominal(self, _Simple):

            return

        ##
        # \b InjectionDetailed all
        #
        # Each voltage and current is described (Amplitube, Phase, Frequency)
        #
        # @param    _Complex  an instance of the Signal.Complex Class.
        #
        def InjectionDetailed(self, _Complex):

            return
