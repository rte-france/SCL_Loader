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

import xml.dom.minidom as dom
import time
from IEC_FileListe import FileListe
from IEC_LNodeType import Parse_LNodeType
from IEC_DOType    import Parse_DOType
from IEC_Trace import Trace
from IEC_Trace import Level    as TL
from IEC_TypeSimpleCheck    import Check


from IEC_ParcoursDataModel import globalDataModel

global SEP
SEP   = '/'         # Separator in MMS adress (U-Test)

import sys

class CodeGeneration():

    def __init__(self, ApplicationName, _TL, GM):
        self.application = ApplicationName
        self.TR          = _TL
        self.LNodeType   = None
        self.GM          = GM   # GlobalDataModel

    class IEDfull:
        def __init__(self, _IEDcomm, _IEDmmsadresse):
            self.IEDcomm        = _IEDcomm
            self.IEDmmsadresse  = _IEDmmsadresse

# Analyse des DO InRef
    # GM: global DAtaModel
    # LDinst:  The GOOSE subsScripteur instance LD inst  [Several]
    # publisherBaseName : IedName+ApName of goose publisher
    def FindLD(self, GM, LDinst, publisherBaseName):

        for ied in GM.tIED:
            for i in range(len(ied.tAccessPoint)):
                if ied.name + ied.tAccessPoint[i].name == publisherBaseName:
                    continue

                for j in range(len(ied.tAccessPoint[i].tServer)):

                    NbLdevice = len(ied.tAccessPoint[i].tServer[j].tLDevice)
                    for k in range(NbLdevice):  # Browsing all LDevice of one IED
                        LD = ied.tAccessPoint[i].tServer[j].tLDevice[k]
                        if LDinst==LD.inst:
                            return LD


    def GetInputData(self, FileId, CB, Txt):

        CtrlBlock = CB.split(',')
        nbDA  = 0 # or DO...
        nbSV  = 0 # Counting the number of flux not the DA.

        for i in range(0, len(CtrlBlock)):
            Ref = CtrlBlock[i].split('/')
            IED_LD = Ref[0]  # IED + LD Name
            try:
                CB = Ref[1]  # Control Block (GS ou RPT= GSEname ou  RPT
            except IndexError:      # No actual value ('None','None','None')
                return

            CBname   = CB.split('.')[1]
            X        = IED_LD.split('_')
            IED_name = X[1] + '_' + X[2] + '_' + X[3]    # Name of the source IED
            LD_name  = X[4] #LD + '_' + X[5]             # Name of the source LD

##            FileId.write("# xxx Data from IED: "+ IED_name + " Source: " + Txt + '..' + LD_name + " ) \n")

            for ied in self.GM.tIED:
                if ied.name == IED_name:
                    # Extract GOOSE DATA

                    if '_GSE_' in CBname:
                        FileId.write("# xxx Data from IED: "+ IED_name + " Source: " + Txt + '..' + LD_name + " ) \n")
                        GSE = 'ied.tAccessPoint[0].tServer[0].'+LD_name+'.LLN0.tGSECtrl'
                        tGSE = eval(GSE)
                        for iGSE in tGSE:
                            if iGSE.name == CBname:
                                dsName = iGSE.datSet
                                DS = 'ied.tAccessPoint[0].tServer[0].'+LD_name+'.LLN0.tDataSet'
                                tDS = eval(DS)
                                for iDS in tDS:
                                    if iDS.name == dsName:
                                        FileId.write("#     DataSet:"+dsName + "\n")
                                        for da in iDS.tFCDA:
                                            # AA1J1Q02A1/MON/CMMXU1/A/phsA/cVal[MX]/mag/f"]
                                            mmsAdr = da.ldInst + SEP + da.prefix + da.lnClass + da.lnInst + da.fc + SEP + da.doName
                                            FileId.write(".....DA: " + mmsAdr + "\n")
                                            if not (da.fc == 'DC' or da.fc == 'SV' or da.fc == 'MX'):  # Ne pas compter les FC DC et SV
                                                nbDA = nbDA+1

                    if '_RPT_' in CBname:
                        RPT = 'ied.tAccessPoint[0].tServer[0].'+LD_name +'.LLN0.tRptCtrl'
                        tRPT = eval(RPT)
                        print('WWWWWWWWWWWWWWWWWWW')

                    if '_SMV_' in CBname:
                        FileId.write("# xxx Data from IED: "+ IED_name + " Source: " + Txt + '..' + LD_name + " ) \n")
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
                                        FileId.write("#     SMV DataSet:" + dsName + "nb DO in FCDA: " + str(X1))
                                        for da in iDS.tFCDA:
                                            mmsAdr = da.ldInst + SEP + da.prefix + da.lnClass + da.lnInst + SEP + '[' + da.fc + ']' + da.doName + '.' + da.daName
                                            FileId.write(".....DA: " + mmsAdr + '\t' + Txt + "\n")
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


## ==> lien vers le GSE control et le dataset
    ## List the DO/DA of a given Data Set
    #
    def DataSetRead(self, FileId, LN, DSName, type):
        nbDA      = 0
        nbSMVflux = 0
        for k in range(0, len(LN.tDataSet)):
            if LN.tDataSet[k].name == DSName:
                FileId.write('# DataSet number of DA: ' + str(len(LN.tDataSet[k].tFCDA)) + '\n')

                tDA = LN.tDataSet[k].tFCDA
                for l in range(len(tDA)):
                    DA = tDA[l]
                    mmsAdr = DA.ldInst + SEP + DA.prefix + DA.lnClass + DA.lnInst

                    if not (DA.fc == 'DC' or DA.fc == 'SV' or DA.fc == 'MX'):     # Ne pas compter les FC DC et SV
                        nbDA=nbDA +1

                    if DA.daName == '':
                        mmsAdr = mmsAdr + SEP + DA.doName + SEP + '[' + DA.fc + ']'
                    else:
                        mmsAdr = '"' + mmsAdr + SEP + DA.daName + SEP + '[' + DA.fc + ']' + '"'

                    out = "Read_" + DA.prefix + DA.lnClass + DA.lnInst + '_' + DA.doName + '_' + DA.fc
                    if type == "GSE":
                        FileId.write('\t\t' + out + '\t\t =get_GooseData( IED_name, "' + mmsAdr + '" , value )' + "\n")
                    elif type == "SMV":
                        FileId.write('\t\t' + out + '\t\t =get_SVControl( IED_name, "' + mmsAdr + '" , value)' + "\n")
                        nbSMVflux=nbSMVflux+1 # Count flux not DA.
                    elif type == "RPT":
                        FileId.write('\t\t' + out + '\t\t =get_ReportData( IED_name, "' + mmsAdr + '" , value)' + "\n")
        return nbDA, nbSMVflux

## Parcours des IEDs . LDinst + LN0 + Inputs + ExtRef
    def GetGooseSubscriber(self, FileId, BaseName, LDinst, i):
        LD = self.FindLD(self.GM, LDinst, BaseName) # Looking for the LD / Basename
        tGSE = LD.LLN0.tGSECtrl
        self.GetSubscriberList(FileId, tGSE, 'Goose Subscriber')

    def GetSMVSubscriber(self, FileId, BaseName, LDinst, i):
        LD = self.FindLD(self.GM, LDinst, BaseName)  # Looking for the LD / Basename
        tSVC = LD.LLN0.tSVCtrl
        self.GetSubscriberList(FileId, tSVC, 'SV Subscriber')

    def GetSubscriberList(self, FileId, tGSE_SVC, txt):
        if len(tGSE_SVC)>0:
            idx = 0
            while idx < len(tGSE_SVC):
                iGSE_SVC = tGSE_SVC[idx]
                idx = idx + 1

                idxIED = 0
                while idxIED < len(iGSE_SVC.tIED):
                    iIED   = iGSE_SVC.tIED[idxIED]
                    idxIED = idxIED + 1
                    FileId.write('\t\t ' + txt + 'IED client: ' + ', name:' + iIED.iedName + ' AP:' + iIED.apRef + ' LD' + iIED.ldInst + ' LN' + iIED.lnClass +'\n' )


    ## For each function analyse the input and outp of the function (=LD)

    def Parse_LN0(self,BaseName, LD, LN, txtLN):
        self.TR.Trace(("xxxxxxxx Browsing LD:" + BaseName + LD.inst + "Desc:" + LD.desc + " LN:" + txtLN), TL.GENERAL)
        nbFlux = 0
        nbSV = 0
        LDinst = LD.inst
        if (LDinst.startswith("IEDTEST")):
            return

        ## Create a Python file for each LD
        fName = 'FctTemplate/Fct_'+LD.inst+'.py'
        FileId = open(fName, "w")
        self.TR.Trace(("Create file"+fName),TL.GENERAL)

    ## First analyse extract the data being pubished via Report, Goose and dSV

        FileId.write("# Output data for LD:" + LD.inst + "\n" )

    # Aspect Report PUBLISHER :
        nbDAPublished = 0
        NbRCB = len(LN.tRptCtrl)
        for i in range(0, NbRCB):
            NbClient = len(LN.tRptCtrl[i].RptEnable.tClientLN)
            for j in range(0, NbClient):
                iClient = LN.tRptCtrl[i].RptEnable.tClientLN[j]
                FileId.write("# Client: " + str(j) + " iedName:" + iClient.iedName + " ldInst: " + iClient.ldInst + "\n")

            iClient = LN.tRptCtrl[i].RptEnable.tClientLN[0]
            DSName  = LN.tRptCtrl[i].dataset

            if '_RPT_' in DSName:
                FileId.write("# Report published with data set:" + DSName + " for Client:"  + iClient.iedName + "\n")
                nbDA, nbSV =self.DataSetRead(FileId, LN, DSName,"RPT")
                nbDAPublished = nbDAPublished + nbDA
                nbFlux        = nbFlux + nbSV

    ## Goose Published
        for i in range(0, len(LN.tGSECtrl)):
            DSName = LN.tGSECtrl[i].datSet
            if '_GSE_' in DSName:
                FileId.write("# GOOSE published with data set:" + DSName + "\n")
                self.GetGooseSubscriber(FileId, BaseName, LDinst,i) # Look for Subscriber to this LD.
                self.GetSMVSubscriber(FileId, BaseName, LDinst,i) # Look for Subscriber to this LD.
                nbDA, nbSV = self.DataSetRead(FileId, LN, DSName,"GSE")
                nbDAPublished = nbDAPublished + nbDA
                nbFlux        = nbFlux + nbSV

     ## Sample Value Published
        for i in range(0, len(LN.tSVCtrl)):
            DSName = LN.tSVCtrl[i].datSet
            if '_SMV_' in DSName:
                FileId.write("# Sample Value Published\n")
                self.DataSetRead(FileId, LN, DSName, "SMV")

    ## TOTAL

        FileId.write('# ....\n')
        FileId.write('# LD' + LD.inst + ' Total number of DA published ' + str(nbDAPublished) + '\n')
        FileId.write('# ....\n')

    ##
    ## Input data for the LD.
    ##
        nbDASubscribed = 0
        nbSVSubscribed = 0
        FileId.write("\n\n # INPUT data for LD:" + LD.inst + '( ' + LD.desc + " )\n")

        # Aspect SubScriber / Receiver:
        LNType =  self.LNodeType.getIEC_LNodeType(LN.lnType)
        if LNType is None:
            self.TR.Trace(("Missing LNOTYPE: "+LN.lnType),TL.ERROR)
        else:
            ## The Data Objects 'InRefxx' are used to defined external data (ie. input Data)
            for do in LNType.tDO:
                if do.name.startswith("InRef"):
                    DOType = self.DOType.getIEC_DoType(do.type)

                    for da in DOType.tDA:
                        if da.name.startswith('set'):
                            try:
                                refCB = 'LD.LLN0.' + do.name + '.' + da.name + '.value'
                                CB = eval(refCB)
                                nbDA, nbSV = self.GetInputData(FileId, CB, do.name)
                                nbDASubscribed = nbDASubscribed + nbDA
                                nbSVSubscribed = nbSVSubscribed + nbSV

                            except (AttributeError, NameError) as e:
#                                print(e)
                                pass
## Analysis of <Inputs>/ExtRef>
            FileId.write('# External data based on ExRef / Inputs \n')
            try:
                RefInputs= LD.LLN0.tInputs
                if len(RefInputs.tExtRef)>0:
                    for ExRf in RefInputs.tExtRef:
                        FileId.write('\t\t ' + ExRf.iedName + '.' + ExRf.srcLDInst + '.' + ExRf.lnClass  + '.' +
                                    ExRf.pDO     + '.' + ExRf.pDA +       '.' + ExRf.srcCBName + '\n')
                        nbDASubscribed = nbDASubscribed + 1
            except AttributeError:  # The potantial exception should be ImportErrot:, usually bad FileName, ClassName or FunctionName
#                print('tInputs or tExtRef is empty')
                pass

            FileId.close()

        return nbDAPublished, nbDASubscribed, nbSV

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

            BaseName  =   IED_Name + '.' + IEDinstance.tAccessPoint[i].name
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
                            nbDAPub,nbDASub,nbSV =  self.Parse_LN0(BaseName, LD, LN, _txtLN)
                            fGlobal.write( LD.inst + ' published: ' +str(nbDAPub) + " and subscrided: " + str(nbDASub) + '\n')

        return


if __name__ == '__main__':

#    TX = Trace.Console(TL.GENERAL)
    TX = Trace.File(TL.DETAIL,"Trace_FctTst.txt")
    tIEDfull=[]


    myCpt = 0

    for file in FileListe.lstSystem:

        GM = globalDataModel(TX,'SCL_files/' + file, None)
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
