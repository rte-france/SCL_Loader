from VsUtils import variables as VS
from utest.ATL import *

from IEC_ACSI_Services import ACSI
from IEC_ACSI_Services import API_Test


class demo_template:
    def __init__(self):
        IEC_mgr = API_Test("Test interface multiple", '10.0.254.1', None)
        self.ACSI = IEC_mgr.getAPI_TXT("DUMMY")

    # Output data for LD:LDDJ
    # Client: 0 iedName:GTW1A_SITE_1 ldInst: LDGW
    # Client: 1 iedName:PO_SITE_1 ldInst: LDPO
    # Report published with data set:RTE_LLN0_DS_RPT_DQCHG_EXT for Client:GTW1A_SITE_1
    # DataSet number of DA: 33
    def GetData_RPT_LDDJ_CSWI0_Beh(IED_ID, mmsAdr, DA, RCB)

        # L'IED_ID n'est pas requis, il est dans l'identifiant de la connection..
        value = VS["REPORT/" + IED_ID + mmsAdr]
        value = ACSI.ReadDataReport(mmsAdr)
        return value

    def GetACSI_LDDJ_CSWI0_Beh(IED_ID, mmsAdr, DA):
        value = ACSI.ReadDataACSI(IED_ID + mmsAdr)
        return value


if __name__ == '__main__':
    demo = demo_template()

    demo.GetData_RPT_LDDJ_CSWI0_Beh("PX", 'LDDJ.CSWI0.Beh','' )