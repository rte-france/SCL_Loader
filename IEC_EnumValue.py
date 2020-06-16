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

from IEC_Trace import Trace
from IEC_Trace import Level as TL

class IEC_Enum:
    class Dbpos:
        intermediate_state = 0
        pos_off = 1
        pos_on = 2
        bad_state = 3

    class cmdQualEnum:
        pulse = 0
        p_persistent = 2

    class Mod:
        Mod_on = 1
        Mod_blocked = 2
        Mod_test = 3
        Mod_test_blocked = 4
        Mod_off = 5

    class Beh:
        on = 1
        blocked = 2
        test = 3
        test_blocked = 4
        off = 5

    class Health:
        Ok = 1
        Warning = 2
        Alarm = 3

    class CtlModels:
        status_only = 0
        direct_with_normal_security = 1
        sbo_with_normal_security = 2
        direct_with_enhanced_security = 3
        sbo_with_enhanced_security = 4
    class sboClass:
        operate_once = 0
        operate_many = 1

    class orCategory:
        not_supported = 0
        bay_control = 1
        station_control = 2
        remote_control = 3
        automatic_bay = 4
        automatic_station = 5
        automatic_remote = 6
        maintenance = 7
        process = 8

    class occType:
        WeekDay = 1
        WeekOfYear = 2
        DayOfMonth = 3
        DayOfYear = 4
        Time = 0

    class m_month:
        reserved = 0
        February = 2
        March = 3
        April = 4
        May = 5
        June = 6
        July = 7
        August = 8
        September = 9
        October = 10
        November = 11
        December = 12
        January = 1


    class occPer:
        Hour = 0
        Day = 1
        Week = 2
        Month = 3
        Year = 4

    class weekDay:
        reserved = 0
        Monday = 1
        Tuesday = 2
        Wednesday = 3
        Thursday = 4
        Friday = 5
        Saturday = 6
        Sunday = 7

    class direction:
       unknown = 0
       forward = 1
       backward = 2
       both = 3

    class FaultDirection:
       unknown = 0
       forward = 1
       backward = 2
       both = 3


    class PhaseFaultDirection:
       unknown = 0
       forward = 1
       backward = 2


    class Severity:
       unknown = 0
       critical = 1
       major = 2
       minor = 3
       warning = 4

    class Range:
        normal = 0
        high = 1
        low = 2
        high_high = 3
        low_low = 4

    class AngleReference:
        V = 0
        A = 1
        other = 2
        Synchrophasor = 3

    class PhaseAngleReference:
        Va = 0
        Vb = 1
        Vc = 2
        Aa = 3
        Ab = 4
        Ac = 5
        Vab = 6
        Vbc = 7
        Vca = 8
        Vother = 9
        Aother = 10
        Synchrophasor = 11

    class PhaseReference:
        A = 0
        B = 1
        C = 2

    class Sequence:
        pos_neg_zero = 0
        dir_quad_zero = 1

    class HvReference:
        fundamental = 0
        rms = 1
        absolute = 2

    class CurveChar:
        none = 0
        ANSI_Extremely_Inverse = 1
        ANSI_Very_Inverse = 2
        ANSI_Normal_Inverse = 3
        ANSI_Moderate_Inverse = 4
        ANSI_Definite_Time = 5
        Long_Time_Extremely_Inverse = 6
        Long_Time_Very_Inverse = 7
        Long_Time_Inverse = 8
        IEC_Normal_Inverse = 9
        IEC_Very_Inverse = 10
        IEC_Inverse = 11
        IEC_Extremely_Inverse = 12
        IEC_Short_Time_Inverse = 13
        IEC_Long_Time_Inverse = 14
        IEC_Definite_Time = 15
        Reserved = 16
        Polynom_1 = 17
        Polynom_2 = 18
        Polynom_3 = 19
        Polynom_4 = 20
        Polynom_5 = 21
        Polynom_6 = 22
        Polynom_7 = 23
        Polynom_8 = 24
        Polynom_9 = 25
        Polynom_10 = 26
        Polynom_11 = 27
        Polynom_12 = 28
        Polynom_13 = 29
        Polynom_14 = 30
        Polynom_15 = 31
        Polynom_16 = 32
        Multiline_1 = 33
        Multiline_2 = 34
        Multiline_3 = 35
        Multiline_4 = 36
        Multiline_5 = 37
        Multiline_6 = 38
        Multiline_7 = 39
        Multiline_8 = 40
        Multiline_9 = 41
        Multiline_10 = 42
        Multiline_11 = 43
        Multiline_12 = 44
        Multiline_13 = 45
        Multiline_14 = 46
        Multiline_15 = 47
        Multiline_16 = 48

    class F_multiplier:
        y = -24
        z = -21
        a = -18
        f = -15
        p = -12
        n = -9
        micro = -6
        m = -3 #
        c = -2
        d = -1
        da = 1
        h = 2
        k = 3
        M = 6
        G = 9
        T = 12
        P = 15
        E = 18
        Z = 21
        Y = 24

    class SI_Unit:
        none = 1
        m = 2
        kg = 3
        s = 4
        A = 5
        K = 6
        mol = 7
        cd = 8
        deg = 9
        rad = 10
        sr = 11
        Gy = 21
        Bq = 22
        Celsius = 23
        Sv = 24
        F = 25
        C = 26
        S = 27
        H = 28
        V = 29
        ohm = 30
        J = 31
        N = 32
        Hz = 33
        lx = 34
        Lm = 35
        Wb = 36
        T = 37
        W = 38
        Pa = 39
        m2 = 41
        m3 = 42
        m_per_s = 43
        m_per_s2 = 44
        m3_per_s = 45
        m_per_m3 = 46
        M = 47
        kg_per_m3 = 48
        m2_per_s = 49
        W_per_mK = 50
        J_per_K = 51
        ppm = 52
        unit_per_s = 53
        rad_per_s = 54
        W_per_m2 = 55
        J_per_m2 = 56
        S_per_m = 57
        K_per_s = 58
        Pa_per_s = 59
        J_per_kgK = 60
        VA = 61
        Watts = 62
        VAr = 63
        phi = 64
        cos_phi_ = 65
        Vs = 66
        V2 = 67
        As = 68
        A2 = 69
        A2t = 70
        VAh = 71
        Wh = 72
        VArh = 73
        V_per_Hz = 74
        Hz_per_s = 75
        char = 76
        char_per_s = 77
        kgm2 = 78
        dB = 79
        J_per_Wh = 80
        W_per_s = 81
        l_per_s = 82
        dBm = 83

if __name__ == '__main__':
    TRX = Trace.Console(TL.DETAIL)
    TRX.Trace(("IEC_Enum Dbpos",   IEC_Enum.Dbpos.pos_off) , TL.GENERAL)
    TRX.Trace(("IEC_Enum Beh",     IEC_Enum.Beh.blocked)   , TL.GENERAL)
    TRX.Trace(("IEC_Enum Health ", IEC_Enum.Health.Warning), TL.GENERAL)
    TRX.Trace(("IEC_Enum SI_Unit", IEC_Enum.SI_Unit.dBm)   , TL.GENERAL)
