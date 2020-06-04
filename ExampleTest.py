from utest.ATL import *
from VsUtils import variables as vs
import time
import sys
from utest import IECToolkit
from datetime import datetime

from IEC_ACSI_Services import ACSI
from IEC_ACSI_Services import API_Test

class testSAMUPXISIO_G(ATLTestCase):

    def initialize(self):

        IEC_mgr    = API_Test("Test interface multiple", '10.0.254.1' , None)
        self.ACSI  = IEC_mgr.getAPI_TXT("SYSTEM")

        self.behIED = 'AA1J1Q02A1/LD0/LLN0/Beh/stVal[ST]'
#        pass

    def Read_CMMXU1(self, IedName, Phase):
        return self.ACSI.getDataValues(IedName+'/MON/CMMXU1/A'  + Phase + '/cVal[MX]/mag/f')
    def Write_CMMXU1(self, IedName, Phase, Value):
        self.VS[IedName+'/MON/CMMXU1/A'  + Phase + '/cVal[MX]/mag/f'] = Value

    def Read_VNMMXU1(self, IedName, Phase):
        return self.ACSI.getDataValues(IedName+'/MON/VNMMXU1/PhV/' + Phase + '/cVal[MX]/mag/f')
    def Write_VNMMXU1(self, IedName, Phase, Value):
        self.VS[IedName + '/MON/VNMMXU1/PhV/' + Phase + '/cVal[MX]/mag/f'] = Value

    def finalize(self):

        pass

    def ResetData(self, IEDName):
        self.Write_CMMXU1(IEDName,'phsA', 0.0)
        self.Write_CMMXU1(IEDName,'phsB', 0.0)
        self.Write_CMMXU1(IEDName,'phsC', 0.0)

        self.Write_VNMMXU1(IEDName,'phsA', 0.0)
        self.Write_VNMMXU1(IEDName,'phsB', 0.0)
        self.Write_VNMMXU1(IEDName,'phsC', 0.0)

        self.VS[ IEDName + '/LD0/LLN0/Beh/stVal[ST]'] = 0

        #vs["AA1J1Q02A1/MON/CMMXU1/A/phsA/cVal[MX]/mag/f"] = 0.0
        #vs["AA1J1Q02A1/MON/CMMXU1/A/phsB/cVal[MX]/mag/f"] = 0.0
        #vs["AA1J1Q02A1/MON/CMMXU1/A/phsC/cVal[MX]/mag/f"] = 0.0
        #vs["AA1J1Q02A1/MON/VNMMXU1/PhV/phsA/cVal[MX]/mag/f"] = 0.0
        #vs["AA1J1Q02A1/MON/VNMMXU1/PhV/phsB/cVal[MX]/mag/f"] = 0.0
        #vs["AA1J1Q02A1/MON/VNMMXU1/PhV/phsC/cVal[MX]/mag/f"] = 0.0

    def execute(self):
        i = 1
        while i < 2:
            t0 = time.time()
#           mgr = IECToolkit.Manager('10.0.254.1') ==> Voir initialize

            # get PX ACSI interface
            PX =   self.ACSI.Associate("AA1J1Q02A1"  , "S1")                 #  PX   = mgr.getACSI("AA1J1Q02A1/S1")
            SAMU = self.ACSI.Associate("IEDName"     , "P1")                 #  SAMU = mgr.getACSI("IEDName/P1")
            ISIO = self.ACSI.Associate("ISIO_FM723L" , "P1")                 #  ISIO = mgr.getACSI("ISIO_FM723L/P1")

                                                                                # Etape 10 - verifie que les equipements repondent aux requetes ACSI
                                                                                # PX.getDataValues('AA1J1Q02A1LD0/LLN0.Beh.stVal[ST]')
                                                                                # time.sleep(0.6)
            beh = self.ACSI.ReadDataPoint('AA1J1Q02A1/LD0/LLN0/Beh/stVal[ST]')  # beh = vs['AA1J1Q02A1/LD0/LLN0/Beh/stVal[ST]']

            if beh < 1:
                print("Etape 20 - pas de reponse de la PX ou probleme de mise a jour des variables",
                      vs['AA1J1Q02A1/LD0/LLN0/Beh/stVal[ST]'])
                sys.exit()
            print("la PX repond aux requetes ACSI")

            SAMU.getDataValues('IEDNameCTRL/LLN0.Beh.stVal[ST]')
            time.sleep(0.6)
            beh = vs["IEDName/CTRL/LLN0/Beh/stVal[ST]"]
            if beh < 1:
                print("Etape 20 - pas de reponse de la SAMU ou probleme de mise a jour des variables",
                      vs["IEDName/CTRL/LLN0/Beh/stVal[ST]"])
                sys.exit()
            print("la SAMU repond aux requetes ACSI")

            ISIO.getDataValues('ISIO_FM723LBX/LLN0.Beh.stVal[ST]')
            time.sleep(0.6)
            behISIO = vs["ISIO_FM723L/BX/LLN0/Beh/stVal[ST]"]
            if behISIO < 1:
                print("Etape 20 - pas de reponse de l'ISIO ou probleme de mise a jour des variables",
                      vs["ISIO_FM723L/BX/LLN0/Beh/stVal[ST]"])
                sys.exit()
            print("l'ISIO repond aux requetes ACSI")

            # Etape 11 - Verifie que StateSequencer et la caisse d'injection sont lances
            while (vs["IEDName/E2-InitSS/E2"] != 1):
                if time.time() - t0 > 5:
                    print("Etape 30 - Lancer State Sequencer et la caisse d'injection puis relancer le test ")
                    sys.exit()

            # Etape 12 - verifie que le BCU ne voit pas de valeur (pas d'injection)
            if vs["AA1J1Q02A1/MON/CMMXU1/A/phsA/cVal[MX]/mag/f"] > 2 or vs[
                "AA1J1Q02A1/MON/VNMMXU1/PhV/phsA/cVal[MX]/mag/f"] > 2:
                print("Etape 40 - Incoherence sur les valeurs lues sur le BCU (pas d'injection) A (phA) - V(phA): ",
                      vs["AA1J1Q02A1/MON/CMMXU1/A/phsA/cVal[MX]/mag/f"],
                      vs["AA1J1Q02A1/MON/VNMMXU1/PhV/phsA/cVal[MX]/mag/f"])
                sys.exit()

                # Etape 13 - injection reseau sain
            vs["IEDName/S1-INJ SAIN/S1"] = 1
            print("Etape 10 : lancement injection reseau sain a:"), datetime.now()
            tempo = time.time()

            # Etape14
            controle = (vs["AA1J1Q02A1/MON/CMMXU1/A/phsA/cVal[MX]/mag/f"] > 900) and \
                       (vs["AA1J1Q02A1/MON/CMMXU1/A/phsB/cVal[MX]/mag/f"] > 900) and \
                       (vs["AA1J1Q02A1/MON/CMMXU1/A/phsC/cVal[MX]/mag/f"] > 900) and \
                       (vs["AA1J1Q02A1/MON/VNMMXU1/PhV/phsA/cVal[MX]/mag/f"] > 200000) and \
                       (vs["AA1J1Q02A1/MON/VNMMXU1/PhV/phsB/cVal[MX]/mag/f"] > 200000) and \
                       (vs["AA1J1Q02A1/MON/VNMMXU1/PhV/phsC/cVal[MX]/mag/f"] > 200000)

            while controle != True:
                if time.time() - tempo > 20:
                    print(
                        "Etape 50 :Incoherence sur les valeurs lues sur le BCU (reseau sain) - A (A,B,C) et V (A, B, C) :" \
                        , vs["AA1J1Q02A1/MON/CMMXU1/A/phsA/cVal[MX]/mag/f"],
                        vs["AA1J1Q02A1/MON/CMMXU1/A/phsB/cVal[MX]/mag/f"], \
                        vs["AA1J1Q02A1/MON/CMMXU1/A/phsC/cVal[MX]/mag/f"],
                        vs["AA1J1Q02A1/MON/VNMMXU1/PhV/phsA/cVal[MX]/mag/f"], \
                        vs["AA1J1Q02A1/MON/VNMMXU1/PhV/phsB/cVal[MX]/mag/f"],
                        vs["AA1J1Q02A1/MON/VNMMXU1/PhV/phsC/cVal[MX]/mag/f"])
                    print("Arreter manuellement l'injection et relancer le test")
                    print(time.time() - t0, "s")
                    vs["IEDName/S1-INJ SAIN/S1"] = 0
                    sys.exit()

                controle = (vs["AA1J1Q02A1/MON/CMMXU1/A/phsA/cVal[MX]/mag/f"] > 900) and \
                           (vs["AA1J1Q02A1/MON/CMMXU1/A/phsB/cVal[MX]/mag/f"] > 900) and \
                           (vs["AA1J1Q02A1/MON/CMMXU1/A/phsC/cVal[MX]/mag/f"] > 900) and \
                           (vs["AA1J1Q02A1/MON/VNMMXU1/PhV/phsA/cVal[MX]/mag/f"] > 200000) and \
                           (vs["AA1J1Q02A1/MON/VNMMXU1/PhV/phsB/cVal[MX]/mag/f"] > 200000) and \
                           (vs["AA1J1Q02A1/MON/VNMMXU1/PhV/phsC/cVal[MX]/mag/f"] > 200000)

            print("Injection OK (reseau sain) - A (A,B,C) et V (A, B, C) :",
                  vs["AA1J1Q02A1/MON/CMMXU1/A/phsA/cVal[MX]/mag/f"], vs["AA1J1Q02A1/MON/CMMXU1/A/phsB/cVal[MX]/mag/f"],
                  vs["AA1J1Q02A1/MON/CMMXU1/A/phsC/cVal[MX]/mag/f"],
                  vs["AA1J1Q02A1/MON/VNMMXU1/PhV/phsA/cVal[MX]/mag/f"],
                  vs["AA1J1Q02A1/MON/VNMMXU1/PhV/phsB/cVal[MX]/mag/f"],
                  vs["AA1J1Q02A1/MON/VNMMXU1/PhV/phsC/cVal[MX]/mag/f"])

            # Etape15 - injection defaut phsA
            vs["IEDName/S2-INJ DEF/S2"] = 1
            vs["IEDName/S1-INJ SAIN/S1"] = 0
            tempo = time.time()
            (_, _, t0_TOR_def) = vs.get("IEDName/S2-INJ DEF/S2").r.get()
            print("Etape 12 : lancement injection defaut a l'heure :"), t0_TOR_def

            # Datation injection defaut reelle
            while vs["AA1J1Q02A1/MON/CMMXU1/A/phsA/cVal[MX]/mag/f"] < 1200:
                if time.time() - tempo > 5:
                    print("courant inferieur a 1200 : ", time.time() - tempo, " - arret de l'injection")
                    vs["IEDName/S3-INJ ARRET/S3"] = 1
                    time.sleep(0.2)
                    vs["IEDName/S3-INJ ARRET/S3"] = 0
                    vs["IEDName/S2-INJ DEF/S2"] = 0
                    sys.exit()

            Ts_A_phsA = vs["AA1J1Q02A1/MON/CMMXU1/A/phsA/t[MX]/secondSinceEpoch"]
            Tf_A_phsA = vs["AA1J1Q02A1/MON/CMMXU1/A/phsA/t[MX]/fractionOfSecond"]
            T_A_phsA = str(Ts_A_phsA) + str(Tf_A_phsA)[0:6]
            print
            "passage I sup 1200 A dans GOOSE PX : ", T_A_phsA

            # Reception GOOSE trip
            tempo = time.time()
            while vs["AA1J1Q02A1/ZMF_1/ZMFPTRC1/Op/general[ST]"] != True:
                if time.time() - tempo > 5:
                    print("pas de reception goose PX - arret de l'injection")
                    vs["IEDName/S3-INJ ARRET/S3"] = 1
                    time.sleep(0.2)
                    vs["IEDName/S3-INJ ARRET/S3"] = 0
                    vs["IEDName/S2-INJ DEF/S2"] = 0
                    sys.exit()

            Ts_goose_PX = vs["AA1J1Q02A1/ZMF_1/ZMFPTRC1/Op/t[ST]/secondSinceEpoch"]
            Tf_goose_PX = vs["AA1J1Q02A1/ZMF_1/ZMFPTRC1/Op/t[ST]/fractionOfSecond"]
            T_goose_PX = str(Ts_goose_PX) + str(Tf_goose_PX)[0:6]
            print
            "envoi goose PX a ", T_goose_PX
            print
            "delai etablissement ordre : ", int(T_goose_PX) - int(T_A_phsA)

            if vs["AA1J1Q02A1/ZMF_1/ZMFPDIS1/Op/general[ST]"] == True:
                print
                "dec zone1"
            if vs["AA1J1Q02A1/ZMF_1/ZMFPDIS2/Op/general[ST]"] == True:
                print
                "dec zone 2"
            if vs["AA1J1Q02A1/ZMF_1/ZMFPDIS3/Op/general[ST]"] == True:
                print
                "dec zone 3"
            if vs["AA1J1Q02A1/ZMF_1/ZMFPDIS4/Op/general[ST]"] == True:
                print
                "dec amont"

            # Lit un GOOSE sur l'ISIO - test GOOSE issus de plusieurs IED et test DO quality
            tempo = time.time()
            while vs["ISIO_FM723L/BX/GGIO1/Ind1/stVal[ST]"] != True:
                if time.time() - tempo > 5:
                    print("pas de reception goose ISIO - arret de l'injection")
                    vs["IEDName/S3-INJ ARRET/S3"] = 1
                    time.sleep(0.2)
                    vs["IEDName/S3-INJ ARRET/S3"] = 0
                    vs["IEDName/S2-INJ DEF/S2"] = 0
                    sys.exit()
            Ts_goose_ISIO = vs["ISIO_FM723L/BX/GGIO1/Ind1/t[ST]/secondSinceEpoch"]
            Tf_goose_ISIO = vs["ISIO_FM723L/BX/GGIO1/Ind1/t[ST]/fractionOfSecond"]
            T_goose_ISIO = str(Ts_goose_ISIO) + str(Tf_goose_ISIO)[0:6]

            print
            "reception GOOSE Isio a : ", T_goose_ISIO
            print
            "qualite : detail badreference, operator Blocked, source, test, validity ", vs[
                "ISIO_FM723L/BX/GGIO1/Ind1/q[ST]/detail/badReference"], \
            vs["ISIO_FM723L/BX/GGIO1/Ind1/q[ST]/operatorBlocked"], vs["ISIO_FM723L/BX/GGIO1/Ind1/q[ST]/source"], \
            vs["ISIO_FM723L/BX/GGIO1/Ind1/q[ST]/test"], vs["ISIO_FM723L/BX/GGIO1/Ind1/q[ST]/validity"]

            # Etape16
            while vs["IEDName/E1-TRIP/E1"] != 1:
                #  recordTime.append(time.time())
                if time.time() - tempo > 5:
                    print("Etape 60 : pas de declenchement apres delai de : ", time.time() - tempo,
                          " - arret de l'injection")
                    vs["IEDName/S3-INJ ARRET/S3"] = 1
                    time.sleep(0.2)
                    vs["IEDName/S3-INJ ARRET/S3"] = 0
                    vs["IEDName/S2-INJ DEF/S2"] = 0
                    sys.exit()
            (_, _, t_TOR_dec) = vs.get("IEDName/E1-TRIP/E1").r.get()
            print
            "datation TOR E1-TRIP :", t_TOR_dec

            print('etape 17: temps elimination defaut :', int(t_TOR_dec) - int(t0_TOR_def), "s, fin d'injection")
            print("temps d'execution du test:", time.time() - t0, "s")
            vs["IEDName/S3-INJ ARRET/S3"] = 1
            time.sleep(0.2)
            vs["IEDName/S3-INJ ARRET/S3"] = 0
            vs["IEDName/S2-INJ DEF/S2"] = 0

            print("fin du test - n", i)
            i = i + 1
            time.sleep(5)

