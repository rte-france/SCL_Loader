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

import time, sys
from IEC_FileListe import FileListe as FL
from IEC_Trace import Trace
from IEC_Trace import Level    as TL
from IEC_ParcoursDataModel import globalDataModel

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

global SEP
SEP     = '/'         # Separator in MMS adress (U-Test)
global FC_ACSI
FC_ACSI = ['DC' , 'SV', 'CF']   # Functional constraint that shall be read through ACSI services.

##
# \b CodeGeneration     The goal is to generate 'getter' and 'setters' function for each LD.
#                       The purpose of such 'getter/setters' is to isolate the code logic from its data.
#
# The substation is described per VoltageLevel

class CodeGeneration():


    def __init__(self, ApplicationName, _TL, GM):
        self.application = ApplicationName          ## name A name of the application
        self.TR          = _TL                      ## Trace Level used
        self.LNodeType   = None                     ## Access to the LNodeType dictionary
        self.GM          = GM                       ## The Global Data Model of the SCL used
        self.FileId      = None                     ## File ID of the output file
        self.IED_ID      = None                     ## IED name + AcccessPoint Name

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
        if DA.daName is '':
            name = DA.doName
        else:
            name = DA.daName
        dataName = LD + '_'+ LN + '_' + name
        if DA.fc in FC_ACSI:
            self.FileId.write("\t\tdef GetACSI_"+ dataName + "(  IED_ID, mmsAdr, DA )\n")
            self.FileId.write("\t\t\tvalue=ReadDataACSI( IED_ID + mmsAdr + )\n")
        else:
            self.FileId.write("\t\tdef GetData_"+ mode + '_' + dataName + "( IED_ID, mmsAdr, DA, RCB )\n")
            if mode == "RPT":
                self.FileId.write('\t\t\tvalue=VS[ "REPORT/" + ' + ' IED_ID ' +  '+ mmsAdr ]\n')
            else:
                self.FileId.write('\t\t\tvalue=VS[ "GOOSE/+" + ' + ' IED_ID ' +  '+ mmsAdr ]\n')

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
    # \b FindLD: find an instance of a LD , from a giben LD name
    #
    # @param    GM                :  global DAtaModel
    # @param    LDinst            :  The GOOSE subsScripteur instance LD inst  [Several]
    #

    def FindLD(self, GM, LDinst):
        # Browse IED
        for ied in GM.tIED:

            # Browse AccessPoint
            for i in range(len(ied.tAccessPoint)):
                if ied.name + ied.tAccessPoint[i].name == self.IED_ID:
                    continue

                # Browse Server
                for j in range(len(ied.tAccessPoint[i].tServer)):
                    NbLdevice = len(ied.tAccessPoint[i].tServer[j].tLDevice)

                    # Browse LD
                    for k in range(NbLdevice):  # Browsing all LDevice of one IED
                        LD = ied.tAccessPoint[i].tServer[j].tLDevice[k]
                        if LDinst==LD.inst:
                            return LD

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
        CB     = Ref[1]                     # Control Block (GS ou RPT= GSEname ou  RPT
        CBname = CB.split('.')[1]

        X        = IED_LD.split('_')
        IED_name = X[1] + '_' + X[2] + '_' + X[3]    # Name of the source IED
        LD_name  = X[4] #LD + '_' + X[5]             # Name of the source LD
        self.FileId.write("# xxx Data from IED: "+ IED_name + " Source: " + Txt + '..' + LD_name + " ) \n")

        for ied in self.GM.tIED:
            if ied.name == IED_name:
                # Extract GOOSE DATA
                if '_GSE_' in CBname:
                    self.FileId.write("# xxx Data from IED: "+ IED_name + " Source: " + Txt + '..' + LD_name + " ) \n")
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
                                        mmsAdr = da.ldInst + SEP + da.prefix + da.lnClass + da.lnInst + da.fc + SEP + da.doName
                                        self.FileId.write(".....DA: " + mmsAdr + "\n")
                                        if da.fc not in FC_ACSI:  # Ne pas compter les FC DC et SV
                                            nbDA = nbDA+1

                                        self.CreateReadData("GSE", self.IED_ID, mmsAdr, da)
                    continue

                if '_RPT_' in CBname:
                    RPT = 'ied.tAccessPoint[0].tServer[0].'+LD_name +'.LLN0.tRptCtrl'
                    tRPT = eval(RPT)
                    print('WWWWWWWWWWWWWWWWWWW')
                    continue

                if '_SMV_' in CBname:
                    self.FileId.write("# xxx Data from IED: "+ IED_name + " Source: " + Txt + '..' + LD_name + " ) \n")
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
                                    X1 = len(iDS.tFCDA)
                                    self.FileId.write("#     SMV DataSet:" + dsName + "nb DO in FCDA: " + str(X1))
                                    for da in iDS.tFCDA:
                                        mmsAdr = da.ldInst + SEP + da.prefix + da.lnClass + da.lnInst + SEP + '[' + da.fc + ']' + da.doName + '.' + da.daName
                                        self.FileId.write(".....DA: " + mmsAdr + '\t' + Txt + "\n")
                    continue

                print("xxxxxxxxxxxxxxx")

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
        for k in range(0, len(LN.tDataSet)):
            if LN.tDataSet[k].name == DSName:
                self.FileId.write('# DataSet number of DA: ' + str(len(LN.tDataSet[k].tFCDA)) + '\n')

                tDA = LN.tDataSet[k].tFCDA
                for l in range(len(tDA)):
                    DA = tDA[l]
                    mmsAdr = DA.ldInst + SEP + DA.prefix + DA.lnClass + DA.lnInst

                    if DA.fc not in FC_ACSI:     # Ne pas compter les FC DC et SV
                        nbDA=nbDA +1

                    if DA.daName == '':
                        mmsAdr = mmsAdr + SEP + DA.doName + SEP + '[' + DA.fc + ']'
                    else:
                        mmsAdr = '"' + mmsAdr + SEP + DA.daName + SEP + '[' + DA.fc + ']' + '"'

                    out = "Read_" + DA.prefix + DA.lnClass + DA.lnInst + '_' + DA.doName + '_' + DA.fc
                    if type == "GSE":
                        self.CreateReadData("GSE", self.IED_ID, mmsAdr, DA)
                    elif type == "SMV":
                        self.FileId.write('\t\t' + out + '\t\t =get_SVControl( IED_name, "' + mmsAdr + '" , value)' + "\n")
                        nbSMVflux=nbSMVflux+1 # Count flux not DA.
                    elif type == "RPT":
                        self.CreateReadData("RPT",self.IED_ID, mmsAdr, DA)

        return nbDA, nbSMVflux

    ##
    # \b GetGooseSubscriber: for a given LDinst, return the list of Subscribers
    #
    # @param LDinst     : Logical Device Name

    def GetGooseSubscriber(self, LDinst):
        LD = self.FindLD(self.GM, LDinst) # Looking for the LD / Basename
        tGSE = LD.LLN0.tGSECtrl
        self.GetSubscriberList(tGSE, '# Goose Subscriber:')

    ##
    # \b GetSMVSubscriber: for a given LDinst, return the list of SV Subscribers
    #
    # @param LDinst     : Logical Device Name
    def GetSMVSubscriber(self, LDinst):
        LD = self.FindLD(self.GM, LDinst)  # Looking for the LD / Basename
        tSVC = LD.LLN0.tSVCtrl
        self.GetSubscriberList(tSVC, '# SV Subscriber')

    ##
    # \b GetSubscriberList: Create a list of subscrinbers for GOOSE and SV
    #
    # @param tGSE_SVC   : Table of Goose or SV Control Block
    # @param txt        : 'Goose Subscriber' or 'SV Subscriber'
    def GetSubscriberList(self, tGSE_SVC, txt):
        if len(tGSE_SVC)>0:
            idx = 0
            while idx < len(tGSE_SVC):
                iGSE_SVC = tGSE_SVC[idx]
                idx = idx + 1

                idxIED = 0
                while idxIED < len(iGSE_SVC.tIED):
                    iIED   = iGSE_SVC.tIED[idxIED]
                    idxIED = idxIED + 1
                    self.FileId.write('#\t\t ' + txt + 'IED client: ' + self.IED_ID + ' LD' + iIED.ldInst + '\n' )


    ## For each function analyse the input and outp of the function (=LD)

    ##
    # \b Parse_LN0: for a given LD create the list of subscribers for GOOSE and SV and the list of published DATA
    #
    # @param LD         : Instance of a LD
    # @param LN         : Instance of a LN
    # @param txtLN      : txtLN LN_prefix+LN_T

    def Parse_LN0(self, LD, LN, txtLN):
        self.TR.Trace((" Browsing LD:" + self.IED_ID + LD.inst + "Desc:" + LD.desc + " LN:" + txtLN), TL.GENERAL)
        nbFlux = 0
        nbSV   = 0
        LDinst = LD.inst
        if (LDinst.startswith("IEDTEST")):
            return

        ## Create a Python file for each LD
        fName = 'FctTemplate/Fct_'+LD.inst+'.py'
        self.FileId = open(fName, "w")
        self.TR.Trace(("Create file"+fName),TL.GENERAL)

    ## First analyse extract the data being pubished via Report, Goose and dSV
        self.FileId.write("# Output data for LD:" + LD.inst + "\n" )

    # Aspect Report PUBLISHER :
        nbDAPublished = 0
        NbRCB = len(LN.tRptCtrl)
        for i in range(0, NbRCB):
            NbClient = len(LN.tRptCtrl[i].RptEnable.tClientLN)
            for j in range(0, NbClient):
                iClient = LN.tRptCtrl[i].RptEnable.tClientLN[j]
                self.FileId.write("# Client: " + str(j) + " iedName:" + iClient.iedName + " ldInst: " + iClient.ldInst + "\n")

            iClient = LN.tRptCtrl[i].RptEnable.tClientLN[0]
            DSName  = LN.tRptCtrl[i].dataset

            if '_RPT_' in DSName:
                self.FileId.write("# Report published with data set:" + DSName + " for Client:"  + iClient.iedName + "\n")
                nbDA, nbSV =self.DataSetRead(LN, DSName,"RPT")
                nbDAPublished = nbDAPublished + nbDA
                nbFlux        = nbFlux + nbSV

    ## Goose Published
        for i in range(0, len(LN.tGSECtrl)):
            DSName = LN.tGSECtrl[i].datSet
            if '_GSE_' in DSName:
                self.FileId.write("# yy GOOSE published with data set:" + DSName + "\n")
                self.GetGooseSubscriber(LDinst) # Look for Subscriber to this LD.
                nbDA, nbSV = self.DataSetRead(LN, DSName,"GSE")
                nbDAPublished = nbDAPublished + nbDA
                nbFlux        = nbFlux + nbSV

     ## Sample Value Published
        for i in range(0, len(LN.tSVCtrl)):
            DSName = LN.tSVCtrl[i].datSet
            if '_SMV_' in DSName:
                self.FileId.write("# xx Sample Value Published\n")
                self.GetSMVSubscriber(LDinst) # Look for Subscriber to this LD.
                self.DataSetRead(LN, DSName, "SMV")
                nbDAPublished = nbDAPublished + nbDA
                nbFlux        = nbFlux + nbSV
    ## TOTAL
        self.FileId.write('# ....\n')
        self.FileId.write('# LD' + LD.inst + ' Total number of DA published ' + str(nbDAPublished) + '\n')
        self.FileId.write('# ....\n')
    ##
    ## Input data for the LD.
    ##
        nbDASubscribed = 0
        nbSVSubscribed = 0
        self.FileId.write("\n\n # INPUT data for LD:" + LD.inst + '( ' + LD.desc + " )\n")

        # Aspect SubScriber / Receiver:
        LNType =  self.LNodeType.getIEC_LNodeType(LN.lnType)
        if LNType is None:
            self.TR.Trace(("Missing LNOTYPE: "+LN.lnType),TL.ERROR)
        else:
            ## The Data Objects 'InRefxx' are used to defined external data (ie. input Data)
            for do in LNType.tDO:
                if do.DOname.startswith("InRef"):
                    DOType = self.DOType.getIEC_DoType(do.type)

                    for da in DOType.tDA:
                        if da.name.startswith('set'):
                            try:
                                refCB = 'LD.LLN0.' + do.name + '.' + da.name + '.value'
                                CB = eval(refCB)

                                CBname = CB.split('.')[1]
                                print("CBName:" + CBname )

                                nbDA, nbSV = self.GetInputData(CB, do.name)
                                nbDASubscribed = nbDASubscribed + nbDA
                                nbSVSubscribed = nbSVSubscribed + nbSV

                            except (AttributeError, NameError) as e:
                                print(e)
                                pass
            ## Analysis of <Inputs>/ExtRef>
            self.FileId.write('# External data based on ExRef / Inputs \n')
            try:
                RefInputs= LD.LLN0.tInputs
                if len(RefInputs.tExtRef)>0:
                    for ExRf in RefInputs.tExtRef:
                        self.FileId.write('\t\t ' + ExRf.iedName + '.' + ExRf.srcLDInst + '.' + ExRf.lnClass  + '.' +
                                    ExRf.pDO     + '.' + ExRf.pDA +       '.' + ExRf.srcCBName + '\n')
                        nbDASubscribed = nbDASubscribed + 1
            # The potantially 'expected' exception is AttributeError:, usually bad FileName, ClassName or FunctionName
            except AttributeError as e:
                print('tInputs or tExtRef is empty')
            except:
                print("Unexpected error:", sys.exc_info()[0])
                pass

            self.FileId.close()

        return nbDAPublished, nbDASubscribed, nbSVSubscribed

    # Each LD is parsed only once.
    def CheckLD(self, tLD, LDinst):
        for i in range (len(tLD)):
            (name , nbInstance) = tLD[i]
            if name == LDinst:
                tLD[i] = (name, nbInstance+1)
                return tLD, False
        tLD.append((LDinst,1))
        return tLD , True

    def ParcoursDataModel(self, IEDinstance, tLD, fGlobal):
        for i in range (len(IEDinstance.tAccessPoint)):
            IED_Name = IEDinstance.name

            self.IED_ID =   IED_Name + '/' + IEDinstance.tAccessPoint[i].name + '/'
            for j in range (len(IEDinstance.tAccessPoint[i].tServer)):

                NbLdevice = len(IEDinstance.tAccessPoint[i].tServer[j].tLDevice)
                for k in range(NbLdevice):                              # Browsing all LDevice of one IED

                    LD = IEDinstance.tAccessPoint[i].tServer[j].tLDevice[k]
                    name = LD.inst
                    tLD, Result = self.CheckLD(tLD, name)
                    if Result == False:
                        continue

                    for m in range(len(LD.LN)):  # Browsing LN du LDEVICE
                        LN = LD.LN[m]
                        _txtLN = LD.LN[m].lnPrefix + LD.LN[m].lnClass + LD.LN[m].lnInst

                        LNodeType = GM.LNode.getIEC_LNodeType(LN.lnType)  # Look-up for LNType
                        # TODO traiter le cas ou on le trouve pas !!!
                        if LN.lnClass == 'LLN0':
                            nbDAPub,nbDASub,nbSV =  self.Parse_LN0(LD, LN, _txtLN)
                            fGlobal.write( LD.inst + ' published: ' +str(nbDAPub) + " ,subscrided: " + str(nbDASub) + ' ,Flux SV: ' + str(nbSV) + '\n')

        return


if __name__ == '__main__':

#    TX = Trace.Console(TL.GENERAL)
    TX = Trace(TL.DETAIL,"Trace_FctTst.txt")
    tIEDfull=[]
    myCpt = 0

    for file in FL.lstSystem:
        GM = globalDataModel(TX,FL.root + file, None)
        CG = CodeGeneration("CodeGeneration", TX, GM)

        CG.LNodeType = GM.LNode
        CG.DOType    = GM.DOType

        indIED = 0
        T0  = time.time()
        tLD = []

        ## Create a Python file for each LD
        fNameGlobal = 'FctTemplate/' + file + '_Total.txt'
        fIdglobal   = open(fNameGlobal, "w")

        for ied in GM.tIED:

            t0 = time.time()
            myCpt = CG.ParcoursDataModel(ied,tLD,fIdglobal)
            TX.Trace(("Counter:"+str(myCpt)),TL.DETAIL)

        fIdglobal.close()

    T1 = time.time()
    TempsTotal = str(T1 - T0)
    TX.Trace(("Total execution time:" + file + ':' + TempsTotal),TL.GENERAL)

    TX.Close()

    print("*** FINISHED ")
