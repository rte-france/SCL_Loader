
    def ParcoursDataModel_LD(self, GM, tIEC_adresse, IEDName, LD):
            for j in range(len(LD.LN)):                         # Browsing LN du LDEVICE
                LN = LD.LN[j]
                txtLN = LD.LN[j].lnPrefix + LD.LN[j].lnClass + LD.LN[j].lnInst
                LNodeType    = GM.LNode.getIEC_LNodeType(LN.lnType)   # Look-up for LNType
                if (LNodeType.lnClass=='LLN0'):
                    self.TR.Trace(("Browsing LD:" + LD.inst + " LN:" + txtLN), TL.GENERAL)
                    print("Fonction:" + LD.inst)
                    inputs1 = LN.tInputs
                    try:
                        X = inputs1.tExtRef
                    except AttributeError:
                        print('No ExtRef table')
                        continue
                    else:
                        for extRef in inputs1.tExtRef:
                            print('INPUT, pLN: '  + extRef.pLN + ' pServT:' + extRef.pServT + " pDO:" + extRef.pDO + " Srv: " + extRef.desc)

                    NbRCB = len(LN.tRptCtrl)
                    for i in range(0,NbRCB):
                        NbClient = len(LN.tRptCtrl[i].RptEnable.tClientLN)

                        for j in range(0, NbClient):
                            iClient = LN.tRptCtrl[i].RptEnable.tClientLN[j]
                            ClientAdresse = (iClient.iedName, iClient.apRef , iClient.ldInst, iClient.lnPrefix, iClient.lnClass, iClient.lnInst)


#                        " GET SMV ADRESSE FROM 'RTE_LLN0_CB_SMV_INT'
                    # InReport Control Get the list Client LN
                    # The ReportControl contains the data Set.
                    # ==> On peut mettre à jour les données relatives aux clients. Et mettre ces informations en données d'entrées / par LD.
            return
