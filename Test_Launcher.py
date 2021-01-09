from lxml import etree
import os

class LoadCampaign:
    def __init__(self,fname):
        self.fname=fname

    def __enter__(self):
        HERE = os.path.abspath(os.path.dirname(__file__))
        filepath = os.path.join(HERE, self.fname)
        self.file = open(filepath)

        return self.file.read()

    def __exit__(self,  exc_type, exc_val, exc_tb):
        print("SCL loaded with success")

class IEDtest:
    def __init__(self,  _bayName:str, _bayTest, _iedName:str, _iedMode:str, _iedTest:bool):
        self.bayName   = _bayName
        self.bayTest   = _bayTest
        self.iedName   = _iedName
        self.iedMode   = _iedMode
        self.iedTest   = _iedTest
        self.tLD       = []


class TestLauncher:

    def __init__(self, _filename:str):
        self.fname = _filename

    def SelectCampaign(self):
        with LoadCampaign(self.fname) as (self.file):  # , self.T_LoadSCL):
            root  = etree.fromstring(self.file)

        tIED=[]
        for bay in root.getchildren():
            bayName = bay.attrib['name']
            bayTest = bay.attrib['test']  # Même si la tranche n'est pas testée on a besoin des IEDs (simulés ou réel)

            for ied in bay.getchildren():
                iedTest  = ied.attrib['test']
                iedName  = ied.attrib['name']
                iedMode  = ied.attrib['mode']

                iIED = IEDtest(bayName, bayTest, iedName, iedMode, iedTest)
                tIED.append(iIED)
                if iedTest.lower() == "no":
                    continue

                for iLD in ied.getchildren():
                    ldTest = iLD.attrib['test']
                    if ldTest.lower() == "no":
                        continue
                    inst = iLD.attrib['inst']
                    print('Testing Bay:', bayName, 'IED:', iedName, ' LD: ', inst)
                    iIED.tLD.append(iLD)




    def LoadCampaign(self):
        print('xx')

if __name__ == '__main__':
    X = TestLauncher('..\TestCampaign\CampagneExemple.xml')
    X.SelectCampaign()






