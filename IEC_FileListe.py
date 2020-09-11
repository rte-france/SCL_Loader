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

##
# \b FileListe: Place holder to define the list of SCL files to be used for unit testing: lstED and lstSystem
#
class FileListe:
    ##  lstIED        a list of IED level file (IID, ICD, CID...)
    lstIED    = ['LD_all.scl']
    ##  lstSystem     a list of system configuration level file (SCD, SSD...)
##    lstSystem = ['SCD_SITE_BCU_4ZSSBO_1_20200901.SCD','SCD_SITE_MUB_4ZBRAN_1_20200901.SCD'] # 'SCL_20200415.scl']  'OUT_SCL_SITE_PALLUAU_3T.scd'# 'LD_all.scl']
    lstSystem = ['SCD_SITE_20200901.SCD'] # 'SCL_20200415.scl']  'OUT_SCL_SITE_PALLUAU_3T.scd'# 'LD_all.scl']
    ##  lstFull       the concatenation of the two previous list
    lstFull   =  lstIED+lstSystem
