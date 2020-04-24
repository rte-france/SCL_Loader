import xml.dom.minidom as dom

from IEC_Trace      import IEC_Console  as TConsole
from IEC_Trace      import TraceLevel as TL
from IEC_FileListe  import FileListe

# Class to be tested
from IEC_DAType         import Test_DAType
from IEC_DOType         import Test_DOType
from IEC_EnumType       import Test_EnumType
from IEC_LNodeType      import Test_LNodeType
from IEC_Substation     import Test_Substation
from IEC_Communication  import Test_Communication
from IEC_Services       import Test_Services
from IEC_LN             import Test_LN
from IEC_IED_Server     import Test_IED_Server
from IEC_TypeSimpleCheck    import Test_TypeSimpleCheck
#from IEC_Rte_private        import Test_Rte_private        # TODO
#from IEC_ParcoursDataModel  import Test_ParcoursDataModel  # TODO

class Test_Project:
    def __init__(self):
        self.TRX = TConsole(TL.GENERAL)

    def TestSet(self, directory, file):
        scl = dom.parse(directory + file)               # Loading the SCL
        Test_EnumType.main(directory, file, scl)        # Checking the DataTypeTemplate/EnumType part
        Test_DAType.main(directory, file, scl)          # Checking the DataTypeTemplate/DoType part
        Test_DOType.main(directory, file, scl)          # Checking the DataTypeTemplate/DaType part
        Test_LNodeType.main(directory, file, scl)       # Checking the DataTypeTemplate/LnodeType part
        Test_Substation.main(directory, file, scl)      # Checking the substation section (Partial implementation)
        Test_Communication.main(directory, file, scl)   # Checking the Communication section
        Test_Services.main(directory, file, scl)        # Checking the Services section(Partial implementation)
        Test_LN.main(directory, file, scl)              # Checking the IED Data Model part
        Test_IED_Server.main(directory, file, scl)      # Checking the IED / AccessPoint /Server part

    def SystemTest(self):
        self.TRX.Trace(" === START IED PART ====",TL.GENERAL)
        for file in FileListe.lstIED:
            self.TestSet('SCL_files/' , file)
        self.TRX.Trace(" === END IED PART ====",TL.GENERAL)

        self.TRX.Trace(" === START SYSTEM PART ====",TL.GENERAL)
        for file in FileListe.lstSystem:
            self.TestSet('SCL_files/'  ,file)
        self.TRX.Trace(" === END SYSTEM PART ====",TL.GENERAL)

        Test_TypeSimpleCheck.main(self.TRX)

if __name__ == '__main__':
    SysTest = Test_Project()
    SysTest.SystemTest()






