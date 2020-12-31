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

import time
import sys

#@package docstring
#This class analyse parse the configuration in order to collect, foe each function/LD:
#    * The input data:
#       * from GOOSE
#       * from REPORT
#       * from SV
#
#    * The output data:
#        * as goose and the subscribers
#        * as report and the subscribers
#

##
# \b CodeGeneration     The goal is to generate 'getter' and 'setters' function for each LD.
#                       The purpose of such 'getter/setters' is to isolate the code logic from its data.
#
# The substation is described per VoltageLevel

class CodeGeneration():


    def __init__(self, ApplicationName, _Directory, _scdMgr):
        self.application = ApplicationName          ## name A name of the application
        self.Directory  = _Directory                ## Storage directory
        self.LNodeType   = None                     ## Access to the LNodeType dictionary
        self.FileId      = None                     ## File ID of the output file
        self.IED_ID      = None                     ## IED name + AcccessPoint Name
        self.FC_ACSI     = ['DC' , 'SV', 'CF']      ##
        self.SEP         = '/'
        self.scdMgr      = _scdMgr                  ## utility to handle SCL file

    class IEDfull:
        def __init__(self, _IEDcomm, _IEDmmsadresse):
            self.IEDcomm        = _IEDcomm
            self.IEDmmsadresse  = _IEDmmsadresse

    ##
    # \b CreateReadData: Generate a Read Data function for a given DA
    #
    # @param mode:      RPT or GSEport Control Block (if NONE, ACSI READ will be used)
    # @param IED_ID:    IED name + Acces Point Name
    # @param mmsAdr:    mmsAdr of the DA (LD.LN.DO.DA ...)
    # @param DA:        DO name or DA name.
    #                   !!!! for 'CF', 'DC' direct read to the Global Model shall be considered
    def CreateReadData(self, mode, IED_ID, mmsAdr, DA):

        path = mmsAdr.split('/')
        LD = path[0]
        LN = path[1]
        if DA.daName == '':
            name = DA.doName
        else:
            name = DA.doName+ '.' + DA.daName
        dataName = LD + '_'+ LN + '_' + name
        if DA.fc in self.FC_ACSI:
            self.FileId.write("\t\tdef GetACSI_"+ dataName + "(  IED_ID, \"" + mmsAdr + "\", DA )\n")
            self.FileId.write("\t\t\tvalue=ReadDataACSI( IED_ID, \"" + mmsAdr + "\")\n")
        else:
            self.FileId.write("\t\tdef GetData_"+ mode + '_' + dataName + "( IED_ID, \"" + mmsAdr + "\", DA, RCB )\n")
            if mode == "RPT":
                self.FileId.write('\t\t\tvalue=VS[ "REPORT/" + ' + ' IED_ID +\"' +   mmsAdr + "\" ]\n")
            else:
                self.FileId.write('\t\t\tvalue=VS[ "GOOSE/+" + ' + ' IED_ID +\"' +  mmsAdr + "\" ]\n")

        self.FileId.write("\t\t\treturn value\n\n")


    ##
    # \b CreateSVGeneration: Generate a Sample Value flux
    #
    # @param IED:       IED name (sender
    # @param SVC:        SVC Control Block def
    # @param Mode:      Physical ==> Used Injection Box connected to the IED (SAMU)
    #                   SVflux   ==> if SAMU(s) is/are connected they are set off-blocked mode
    # @param NomValue   The 3I / 3U are set to Nominal Values
    # @param SpecValue  The 3I / 3U are set to specific and detailed.

    def CreateSVGeneration(self, IED, SVC, Mode):
        self.FileId.write("\t\tdef  GenerateSV(IED, SVC, Mode, NomValue, SpecValue")
        self.FileId.write("\t\t\t   TEST.")


    ##
    # \b FindLD: find an instance of a LD , from a given LD name
    #
    # @param    GM                :  global DAtaModel
    # @param    LDinst            :  The GOOSE subsScripteur instance LD inst  [Several]
    #
    def FindLD(self, LDinst):
        for iIED in self.tIED:
            self.IED_ID = iIED.name + '/' + iIED.PROCESS_AP.name
            for iAP in iIED.get_children('AccessPoint'):
                for iServer in iAP.get_children('Server'):  # There is a server only for IEC aspect.
                    for iLD in iServer.get_children('LDevice'):
                        if iLD.inst == LDinst:
                            return iLD

        return None     # In case the LD is not Found

    ##
    # \b GetInputData: for a given Control Block Name find the associated GOOSE, REPORT or SV
    #
    # Analyse des DO InRef
    # @param fileId :    Python generated file to use
    # @param CB     :    IEC Control Block (Report, Goose or SV)
    # @param Txt    :    Do Name (?)

    def GetInputData(self, CB, Txt):

        nbDA  = 0 # Counting the number of DA
        nbSV  = 0 # Counting the number of flux not the DA.

        Ref = CB.split('/')           ##'XX_BCU_4ZSSBO_1_LDCMDDJ_1/CSWI1.Pos'
        IED_LD = Ref[0]                     # IED + LD Name For
        try:
            CB     = Ref[1]                     # Control Block (GS ou RPT= GSEname ou  RPT
            CBname = CB.split('.')[1]
        except:
            print('xxxxxxx')

        X        = IED_LD.split('_')
        IED_name = X[1] + '_' + X[2] + '_' + X[3]    # Name of the source IED
        LD_name  = X[4] #LD + '_' + X[5]             # Name of the source LD
        self.FileId.write("# Data from IED: "+ IED_name + " Source: " + Txt + '..' + LD_name + " ) \n")

        for ied in self.tIED:
            if ied.name == IED_name:
                # Extract GOOSE DATA
                if '_GSE_' in CBname:
                    self.FileId.write("# Data from IED: "+ IED_name + " Source: " + Txt + '..' + LD_name + " ) \n")
                    GSE = 'ied.tAccessPoint[0].tServer[0].'+LD_name+'.LLN0.tGSECtrl'
                    tGSE = eval(GSE)
                    for iGSE in tGSE:
                        if iGSE.name == CBname:
                            dsName = iGSE.datSet
                            DS = 'ied.tAccessPoint[0].tServer[0].'+LD_name+'.LLN0.tDataSet'
                            tDS = eval(DS)
                            for iDS in tDS:
                                if iDS.name == dsName:
                                    self.FileId.write("#     DataSet:"+dsName + "\n")
                                    for da in iDS.tFCDA:
                                        # AA1J1Q02A1/MON/CMMXU1/A/phsA/cVal[MX]/mag/f"]
                                        mmsAdr = da.ldInst + self.SEP + da.prefix + da.lnClass + da.lnInst + da.fc + self.SEP + da.doName
                                        self.FileId.write(".....DA: " + mmsAdr + "\n")
                                        if da.fc not in self.FC_ACSI:  # Ne pas compter les FC DC et SV
                                            nbDA = nbDA+1

                                        self.CreateReadData("GSE", self.IED_ID, mmsAdr, da)
                    continue

                if '_RPT_' in CBname:
                    RPT = 'ied.tAccessPoint[0].tServer[0].'+LD_name +'.LLN0.tRptCtrl'
                    tRPT = eval(RPT)
                    continue

                if '_SMV_' in CBname:
                    self.FileId.write("# Data from IED: "+ IED_name + " Source: " + Txt + '..' + LD_name + " ) \n")
                    SMV = 'ied.tAccessPoint[0].tServer[0].'+LD_name +'.LLN0.tSVCtrl'
                    tSMV = eval(SMV)
                    for iSMV in tSMV:
                        nbSV=nbSV+1       ## Counting number of flux not number of DA
                        if iSMV.name == CBname:
                            dsName = iSMV.datSet

                            DS = 'ied.tAccessPoint[0].tServer[0].' + LD_name + '.LLN0.tDataSet'
                            tDS = eval(DS)
                            for iDS in tDS:
                                if iDS.name == dsName:
                                    self.FileId.write("#     SMV DataSet:" + dsName + "nb DO in FCDA: " + str(X1))
                                    for da in iDS.tFCDA:
                                        mmsAdr = da.ldInst + self.SEP + da.prefix + da.lnClass + da.lnInst + self.SEP + '[' + da.fc + ']' + da.doName + '.' + da.daName
                                        self.FileId.write(".....DA: " + mmsAdr + '\t' + Txt + "\n")
                    continue

        return nbDA , nbSV

#            self.name = _name  # @param name	    A name identifying this SMV control block
#            self.desc = _desc  # @param desc	    The description text
#            self.datSet = _datSet  # @param datSet   The name of the data set whose values shall be sent.
#            self.confRev = _confRev  # @param confRev	The configuration revision number of this control block; mandatory.
#            self.smvID = _smvID  # @param smvID	 Multicast CB: the MsvID for the sampled value definition as defined (Unicast: deprecated)
#    self.multicast = _multicast  # @param multicast Indicates Unicast SMV services only meaning that smvID = UsvI
# self.smpRate = _smpRate  # @param smpRate	Sample rate as defined in IEC 61850-7-2. If no smpMod is defined, i
# self.nofASDU = _nofASDU  # @param nofASDU	Number of ASDU (Application service data unit) – see IEC 61850-9-2
# self.smpMod = _smpMod  # @param smpMod	The sampling mode as defined in IEC 61850-7-2; default: SmpPerPeriod; i


    ##
    # \b DataSetRead: for a given DataSet, le find the associated GOOSE, REPORT or SV
    #
    # Analyse des DO InRef
    # @param fileId :    Python generated file to use
    # @param LN     :    Logical Node
    # @param DSName :    DataSet name
    # @param type   :   This is 'GSE' or 'SMV' or 'RPT
    #
    # The 'DC' (description), 'SV' (substitution) and 'MX' (Sample Value) are not counted.
    # 'DC' and 'SV' shall not be part of a DS. And the read should be done with a ACSI service.
    #
    def DataSetRead(self, LN, DSName, type):

        nbDA      = 0
        nbSMVflux = 0
        mmsAdr    = ''
        _lnInst   =''
        for iDataSet in LN.get_children('DataSet'):
            if iDataSet.name == DSName:
                self.FileId.write('# DataSet number of DA: ' + str(len(iDataSet.FCDA))+ '\n')
                for iFCDA in iDataSet.FCDA:
                    mmsAdr = '-**-'+iFCDA.ldInst + self.SEP
                    try:                                ## lnInst is not always present.
                        _lninst = str(iFCDA.lnInst)
                    except:
                        _lninst = ''

                    try:                                ## prefix might be missing
                        prefix = iFCDA.prefix
                    except:
                        prefix =''

                    if iFCDA.fc not in self.FC_ACSI:     # Ne pas compter les FC DC et SV  (?)
                        nbDA=nbDA +1

                    # Compte mmsAdr, daName is optional
                    try:
                        _da =  iFCDA.daName             ## daName is optional
                        mmsAdr = mmsAdr + self.SEP + prefix+ iFCDA.lnClass+ _lninst  + self.SEP+ iFCDA.doName + self.SEP + '[' + iFCDA.fc + ']' + iFCDA.daName + ' #### "'
                        out = "Read_DO_DA" + prefix + iFCDA.lnClass + _lnInst + '_' + iFCDA.doName + '_' + iFCDA.fc + '_' + iFCDA.daName       # +'_'+ iFCDA.daName + '"'
                    except:
                        iFCDA.daName=''
                        mmsAdr = mmsAdr + self.SEP + iFCDA.lnClass + _lnInst + '_' + iFCDA.doName + self.SEP + '[' + iFCDA.fc + ']'
                        out = "Read_DO___" + prefix + iFCDA.lnClass + _lnInst + '_' + iFCDA.doName + '_' + iFCDA.fc

                    if type == "GSE":
                        self.CreateReadData("GSE", self.IED_ID, mmsAdr, iFCDA)
                    elif type == "SMV":
                        self.FileId.write('\t\t' + out + '\t\t =get_SVControl( IED_name, "' + mmsAdr + '" , value)' + "\n")
                        nbSMVflux=nbSMVflux+1 # Count flux not DA.
                    elif type == "RPT":
                        self.CreateReadData("RPT",self.IED_ID, mmsAdr, iFCDA)

        return nbDA, nbSMVflux

    ##
    # \b GetGooseSubscriber: for a given LDinst, return the list of Subscribers
    #
    # @param LDinst     : Logical Device Name

    def GetGooseSubscriber(self, LDinst):
        LD = self.FindLD(LDinst) # Looking for the LD / Basename
        tGSE = LD.LLN0.get_children('GSEControl')
        self.GetSubscriberList(tGSE, '# Goose Subscriber:')
    ##
    # \b GetSMVSubscriber: for a given LDinst, return the list of SV Subscribers
    #
    # @param LDinst     : Logical Device Name
    def GetSMVSubscriber(self, LDinst):
        LD = self.FindLD(LDinst)  # Looking for the LD / Basename
        tSVC = LD.LLN0.tSVCtrl
        self.GetSubscriberList(tSVC, '# SV Subscriber')

    ##
    # \b GetSubscriberList: Create a list of subscrinbers for GOOSE and SV
    #
    # @param tGSE_SVC   : Table of Goose or SV Control Block
    # @param txt        : 'Goose Subscriber' or 'SV Subscriber'
    def GetSubscriberList(self, tGSE_SVC, txt):
        for iGSE in tGSE_SVC:
            for iIED in iGSE.IEDName:
                self.FileId.write('#\t\t ' + txt + 'IED client: ' + self.IED_ID + ' LD' + iIED.ldInst + '\n')

#        if len(tGSE_SVC)>0:
#            idx = 0
#            while idx < len(tGSE_SVC):
#                iGSE_SVC = tGSE_SVC[idx]
#                idx = idx + 1
#
#                idxIED = 0
#                while idxIED < len(iGSE_SVC.tIED):
#                    iIED   = iGSE_SVC.tIED[idxIED]
#                    idxIED = idxIED + 1
#                    self.FileId.write('#\t\t ' + txt + 'IED client: ' + self.IED_ID + ' LD' + iIED.ldInst + '\n' )


    ## For each function analyse the input and outp of the function (=LD)

    ##
    # \b Parse_LN0: for a given LD create the list of subscribers for GOOSE and SV and the list of published DATA
    #
    # @param LD         : Instance of a LD
    # @param LN         : Instance of a LN
    # @param txtLN      : txtLN LN_prefix+LN_T

    def Parse_LN0(self, LD, LN, txtLN):
        nbDAPublished = 0
        nbSVPublished = 0

        ## Create a Python file for each LD
        fName = 'Fct_xx'+LD.inst+'.py'
        self.FileId = open(self.Directory + '\\' + fName, "a")

        ## Identify Report Publichisher
        for iRptCtrl in LN.get_children('ReportControl'):
            DSName = iRptCtrl.datSet
            for iClient in iRptCtrl.RptEnabled.ClientLN:
               if '_RPT_' in DSName:
                   self.FileId.write("# Report published with data set:" + DSName + " for Client:" + iClient.iedName + "\n")
                   nbDA, nbSV = self.DataSetRead(LN, DSName, "RPT")
                   nbDAPublished = nbDAPublished + nbDA

        for iGSE in LN.get_children('GSEControl'):
            DSName = iGSE.datSet
            if '_GSE_' in DSName:
                self.FileId.write("# yy GOOSE published with data set:" + DSName + "\n")
                self.GetGooseSubscriber(LD.inst)  # Look for Subscriber to this LD.
                nbDA, nbSV = self.DataSetRead(LN, DSName, "GSE")
                nbDAPublished = nbDAPublished + nbDA

## SVC PUBLISHER

        for iSVCCtrl in LN.get_children('SampleValueControl'):
            DSName = iSVCCtrl.datSet
            if '_SMV_' in DSName:
                self.FileId.write("# xx Sample Value Published\n")
                self.GetSMVSubscriber(LD.inst)  # Look for Subscriber to this LD.
                nbDA, nbSV = self.DataSetRead(LN, DSName, "SMV")
                nbDAPublished = nbDAPublished + nbDA
                nbSVPublished = nbSVPublished + nbSV


        for iDataset in LN.get_children('DataSet'):
            for iFCDA in iDataset.FCDA:
                print('iFCDA:' + iFCDA.name)

    ## First analyse extract the data being pubished via Report, Goose and dSV
        self.FileId.write("# Output data for LD:" + LD.inst + "\n" )

     ## Sample Value Published
        for iSVCCtrl in LN.get_children('SVCtrl'):
            DSName = iSVCCtrl.datSet
            if '_SMV_' in DSName:
                self.FileId.write("# xx Sample Value Published\n")
                self.GetSMVSubscriber(LD.inst) # Look for Subscriber to this LD.
                nbDA, nbSV =self.DataSetRead(LN, DSName, "SMV")
#                nbDAPublished = nbDAPublished + nbDA
                nbSVPublished = nbSVPublished + nbSV

    ## TOTAL
        self.FileId.write('# ....\n')
        self.FileId.write('# LD' + LD.inst + ' Total number of DA published ' + str(nbDAPublished) + '\n')
        self.FileId.write('# ....\n')
    ##
    ## Input data for the LD.
    ##
        nbDASubscribed = 0
        nbSVSubscribed = 0
        self.FileId.write("\n\n # INPUT data for LD:" + str(LD.inst) + '( ' + (LD.desc or '.') + " )\n")

        self.FileId.close()

        dataTypes  = self.scdMgr.datatypes

        LNType = dataTypes.get_type_by_id(LN.lnType)
        if LNType is None:
            print("Missing LNOTYPE: " + LN.lnType)
            exit(-3)

        for iDO  in LNType.getchildren():
            DoName = iDO.get('name')
            if DoName.startswith("InRef"):
                DOType = dataTypes.get_type_by_id(iDO.get('type'))
                for iDA in DOType.getchildren():
                    DaName = iDA.get('name')
                    if DaName.startswith('set'):
                        try:
                            refCB = 'LD.LLN0.' + DoName + '.' + DaName + '.value'
                            CB = eval(refCB)
                            if CB is None or CB==".":     ## Unset
                                print("DA NAME:"+DaName)
                                continue

                            nbDA, nbSV = self.GetInputData(CB, DoName)
                            nbDASubscribed = nbDASubscribed + nbDA
                            nbSVSubscribed = nbSVSubscribed + nbSV

                        except (AttributeError, NameError) as e:
                            print(e)
                            pass

        return nbDAPublished, nbSVPublished, nbDASubscribed, nbSVSubscribed

# Each LD is parsed only once.
    def CheckLD(self, tLD, LDinst):
#        if 'XX' in LDinst:
#            print("stop")
        for i in range (len(tLD)):
            (name , nbInstance) = tLD[i]
            if name == LDinst:
                tLD[i] = (name, nbInstance+1)
                return tLD, False
        tLD.append((LDinst,1))
        return tLD , True

    def ParcoursDataModel(self, iIED, fGlobal):   # :SCD.SCDNode
        tLD = []
        IED_Name = iIED.name
        if IED_Name.startswith("IEDTEST"):
            return

        self.IED_ID =   IED_Name + '/' + iIED.PROCESS_AP.name
        for iAP in iIED.get_children('AccessPoint'):
            for iServer in iAP.get_children('Server'):      # There is a server only for IEC aspect.
                for iLD in iServer.get_children('LDevice'):
                    name = iLD.inst
                    if 'XX' in name:
                        continue
                    tLD, Result = self.CheckLD(tLD, name)
                    if Result == False:
                        continue
                    if hasattr(iLD, 'LLN0') or hasattr(iLD, 'LN0'):
                        nbDAPub,nbFluxSV, nbDASub,nbSV =  self.Parse_LN0(iLD, iLD.LLN0, 'LN0')
                        fGlobal.write( iLD.inst + '\t published : '  +str(nbDAPub) + " \tSV  Published :  "+ str(nbFluxSV))
                        fGlobal.write( ' \tData subscrided: ' + str(nbDASub) + ' \tSV  Subscribed: ' + str(nbSV) + '\n')

                    else:
                        continue

#                    for iLN in iLD.get_children('LN'):
#                        print("iLN:"+iLN.lnClass)
##                        if iLN.lnInst is None:
#                            iLN.lnInst = ""
#                        if iLN.lnPrefix is None:
#                            iLN.lnPrefix = ""
#                        _txtLN = iLN.lnPrefix + iLN.lnClass + iLN.lnInst
#                        LNodeType = self.GM.LNode.getIEC_LNodeType(iLN.lnType)  # Look-up for LNType


        return

    def GenerateTemplate(self, file, _tIED):

        ## Create a Python file for each LD
        fNameGlobal = file + '_Total.txt'
        fIdglobal   = open(fNameGlobal, "a")

        self.tIED = _tIED

        T0 = time.time()
        for ied in self.tIED:
            myCpt = self.ParcoursDataModel(ied,fIdglobal)

        fIdglobal.close()

        T1 = time.time()
        TempsTotal = str(T1 - T0)
        print("Total execution time:" + file + ':' + TempsTotal)



