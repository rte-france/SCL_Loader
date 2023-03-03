#!/usr/bin/env python3
# Copyright RTE - 2020

"""
Module de test du module scd_loader
"""
import os
import logging
import pytest
import hashlib
import cProfile
import pstats
import io
from pstats import SortKey
from lxml import etree

import scl_loader.scl_loader as scdl
from scl_loader import SCD_handler
from scl_loader import IED
from scl_loader import LD
from scl_loader import LN
from scl_loader import LN0
from scl_loader import DO
from scl_loader import DA
from scl_loader import SCDNode
from scl_loader import DataTypeTemplates
from scl_loader import ServiceType

LOGGER = logging.getLogger(__name__)
HERE = os.path.abspath(os.path.dirname(__file__))
SCD_OPEN_NAME = 'SCD_Test.scl'
SCD_OPEN_IOP_NAME = 'IOP_ParserOpenSource_SCD_SITE_20201026_v2.scd'
SCD_WRONG_NAME = 'SCD_WRONG.scd'
SCD_OPEN_PATH = os.path.join(HERE, 'resources', SCD_OPEN_NAME)
SCD_OPEN_IOP_PATH = os.path.join(HERE, 'resources', SCD_OPEN_IOP_NAME)
SCD_WRONG_PATH = os.path.join(HERE, 'resources', SCD_WRONG_NAME)


def hashfile(file):

    # A arbitrary (but fixed) buffer
    # size (change accordingly)
    # 65536 = 65536 bytes = 64 kilobytes
    BUF_SIZE = 65536

    # Initializing the sha256() method
    sha256 = hashlib.sha256()

    # Opening the file provided as
    # the first commandline arguement
    with open(file, 'rb') as f:

        while True:

            # reading data = BUF_SIZE from
            # the file and saving it in a
            # variable
            data = f.read(BUF_SIZE)

            # True if eof = 1
            if not data:
                break

            # Passing that data to that sh256 hash
            # function (updating the function with
            # that data)
            sha256.update(data)

    # sha256.hexdigest() hashes all the input
    # data passed to the sha256() via sha256.update()
    # Acts as a finalize method, after which
    # all the input data gets hashed hexdigest()
    # hashes the data, and returns the output
    # in hexadecimal format
    return sha256.hexdigest()


def _get_node_list_by_tag(scd, tag: str) -> list:
    result = []
    context = etree.iterparse(scd._scd_path, events=("end",), tag=r'{http://www.iec.ch/61850/2003/SCL}' + tag, remove_comments=True)
    for _, ied in context:
        result.append(ied)
    return result


def test_safe_convert_value():
    """
        I should be able to convert a value in
        string format to typed format.
        Typed formats supported : bool, int, float
    """
    assert scdl._safe_convert_value('abc123') == 'abc123'
    assert scdl._safe_convert_value('false') is False
    assert scdl._safe_convert_value('False') is False
    assert scdl._safe_convert_value('true') is True
    assert scdl._safe_convert_value('TRUE') is True
    assert scdl._safe_convert_value('123') == 123
    assert scdl._safe_convert_value('-123') == -123
    assert scdl._safe_convert_value('.123') == '.123'
    assert scdl._safe_convert_value('01.23') == 1.23
    assert scdl._safe_convert_value('-1.23') == -1.23
    assert scdl._safe_convert_value('01b23') == '01b23'
    assert scdl._safe_convert_value('#{~[~]{@^|`@`~\\/') == '#{~[~]{@^|`@`~\\/'


def test_valid_scd():
    assert SCD_handler(SCD_OPEN_PATH)
    with pytest.raises(AttributeError):
        SCD_handler(SCD_WRONG_PATH)


def test_datatypes_get_by_id():
    """
        I should be able to load a Datatype by id
    """
    datatypes = DataTypeTemplates(SCD_OPEN_PATH)
    ln_type = datatypes.get_type_by_id('GAPC')
    assert ln_type.get('lnClass') == 'GAPC'
    do_type = datatypes.get_type_by_id('ENC')
    assert do_type.get('cdc') == 'ENC'


class TestSCD_OPEN():

    def setup_method(self):
        self.scd = SCD_handler(SCD_OPEN_PATH)
        self.tIED = self.scd.get_all_IEDs()

    def teardown_method(self):
        del self.scd
        del self.tIED

    def _start_perfo_stats(self):
        self.pr = cProfile.Profile()
        self.pr.enable()

    def _end_perfo_stats(self):
        self.pr.disable()
        s = io.StringIO()
        ps = pstats.Stats(self.pr, stream=s).sort_stats(SortKey.CUMULATIVE)
        ps.print_stats()
        LOGGER.info(s.getvalue())

    def test_create_scd_object(self):
        """
            I Should be able to create a SCL object with its children (except IEDs and Datatype)
        """
        assert self.scd.Header.toolID == 'ggu'  # pylint: disable=maybe-no-member
        assert self.scd.Communication.Net1.LD_All.GSE[0].Address.P[0].type == 'VLAN-ID'  # pylint: disable=maybe-no-member

    def test_create_DA_by_kwargs(self):
        """
            I should be able to create a DA object with kwargs
        """
        simple_da = {'fc': 'ST', 'dchg': 'false', 'qchg': 'true', 'dupd': 'false', 'name': 'q', 'bType': 'Quality'}
        simple2_da = {'fc': 'DC', 'dchg': 'false', 'qchg': 'false', 'dupd': 'false', 'name': 'd', 'bType': 'VisString255', 'valKind': 'RO', 'valImport': 'false'}
        enum_da = {'fc': 'CF', 'dchg': 'true', 'qchg': 'false', 'dupd': 'false', 'name': 'ctlModel', 'bType': 'Enum', 'valKind': 'RO', 'type': 'CtlModelKind', 'valImport': 'false'}

        with pytest.raises(AttributeError):
            DA(self.scd.datatypes)
        simple_da_inst = DA(self.scd.datatypes, None, None, **simple_da)
        assert getattr(simple_da_inst, 'fc') == 'ST'
        assert getattr(simple_da_inst, 'dchg') is False
        assert getattr(simple_da_inst, 'qchg') is True
        assert getattr(simple_da_inst, 'dupd') is False
        assert getattr(simple_da_inst, 'name') == 'q'
        assert getattr(simple_da_inst, 'bType') == 'Quality'

        simple2_da_inst = DA(self.scd.datatypes, None, None, **simple2_da)
        assert getattr(simple2_da_inst, 'fc') == 'DC'
        assert getattr(simple2_da_inst, 'dchg') is False
        assert getattr(simple2_da_inst, 'qchg') is False
        assert getattr(simple2_da_inst, 'dupd') is False
        assert getattr(simple2_da_inst, 'name') == 'd'
        assert getattr(simple2_da_inst, 'bType') == 'VisString255'
        assert getattr(simple2_da_inst, 'valKind') == 'RO'
        assert getattr(simple2_da_inst, 'valImport') is False

        enum_da_inst = DA(self.scd.datatypes, None, None, **enum_da)
        assert getattr(enum_da_inst, 'fc') == 'CF'
        assert getattr(enum_da_inst, 'dchg') is True
        assert getattr(enum_da_inst, 'qchg') is False
        assert getattr(enum_da_inst, 'dupd') is False
        assert getattr(enum_da_inst, 'name') == 'ctlModel'
        assert getattr(enum_da_inst, 'bType') == 'Enum'
        assert getattr(enum_da_inst, 'valKind') == 'RO'
        assert getattr(enum_da_inst, 'type') == 'CtlModelKind'
        assert getattr(enum_da_inst, 'valImport') is False

    def test_create_struct_DA_by_kwargs(self):
        struct_da = {'name': 'originSrc', 'fc': 'ST', 'bType': 'Struct', 'type': 'Originator'}

        struct_da_inst = DA(self.scd.datatypes, None, **struct_da)
        assert getattr(struct_da_inst, 'fc') == 'ST'
        assert getattr(struct_da_inst, 'name') == 'originSrc'
        assert getattr(struct_da_inst, 'bType') == 'Struct'
        assert getattr(struct_da_inst, 'type') == 'Originator'
        assert struct_da_inst.orCat.tag == 'BDA'             # pylint: disable=maybe-no-member
        assert struct_da_inst.orIdent.bType == 'Octet64'     # pylint: disable=maybe-no-member

    def test_create_DO_by_dtid(self):
        """
            I should be able to create a DO object with datatype id
        """
        input_node = etree.Element('DO')
        input_node.attrib['id'] = 'ENC'
        simple_do_inst = DO(self.scd.datatypes, input_node, **{'name': 'DO_RTE_1'})
        assert getattr(simple_do_inst, 'id') == 'ENC'
        assert getattr(simple_do_inst, 'cdc') == 'ENC'
        assert getattr(simple_do_inst, 'parent') is None
        assert isinstance(getattr(simple_do_inst, 'ctlModel'), DA)
        assert simple_do_inst.ctlModel.type == 'CtlModels'      # pylint: disable=maybe-no-member
        assert isinstance(getattr(simple_do_inst, 'blkEna'), DA)
        assert isinstance(getattr(simple_do_inst, 'ctlNum'), DA)
        assert isinstance(getattr(simple_do_inst, 'd'), DA)
        assert isinstance(getattr(simple_do_inst, 'dU'), DA)
        assert isinstance(getattr(simple_do_inst, 'dataNs'), DA)
        assert isinstance(getattr(simple_do_inst, 'opOk'), DA)
        assert isinstance(getattr(simple_do_inst, 'opRcvd'), DA)
        assert isinstance(getattr(simple_do_inst, 'operTimeout'), DA)
        assert isinstance(getattr(simple_do_inst, 'origin'), DA)
        assert isinstance(getattr(simple_do_inst, 'q'), DA)
        assert isinstance(getattr(simple_do_inst, 'stVal'), DA)
        assert isinstance(getattr(simple_do_inst, 'subEna'), DA)
        assert isinstance(getattr(simple_do_inst, 'subID'), DA)
        assert isinstance(getattr(simple_do_inst, 'subQ'), DA)
        assert isinstance(getattr(simple_do_inst, 'subVal'), DA)
        assert isinstance(getattr(simple_do_inst, 't'), DA)
        assert isinstance(getattr(simple_do_inst, 'tOpOk'), DA)

    def test_create_LN_by_dtid(self):
        """
            I should be able to create a LN object
        """
        kwargs = {'lnClass': 'GAPC', 'inst': '0', 'lnType': 'GAPC', 'desc': 'This is a GAPC'}
        ln_inst = LN(self.scd.datatypes, None, **kwargs)
        assert getattr(ln_inst, 'lnType') == 'GAPC'
        assert getattr(ln_inst, 'lnClass') == 'GAPC'
        assert getattr(ln_inst, 'inst') == 0
        assert getattr(ln_inst, 'name') == 'GAPC0'
        assert getattr(ln_inst, 'desc') == 'This is a GAPC'
        assert isinstance(getattr(ln_inst, 'Alm1'), DO)
        assert isinstance(getattr(ln_inst, 'Auto'), DO)
        assert isinstance(getattr(ln_inst, 'DPCSO1'), DO)
        assert isinstance(getattr(ln_inst, 'ISCSO1'), DO)
        assert isinstance(getattr(ln_inst, 'Ind1'), DO)
        assert isinstance(getattr(ln_inst, 'Loc'), DO)
        assert isinstance(getattr(ln_inst, 'LocKey'), DO)
        assert isinstance(getattr(ln_inst, 'LocSta'), DO)
        assert isinstance(getattr(ln_inst, 'Op1'), DO)
        assert isinstance(getattr(ln_inst, 'OpCntRs'), DO)
        assert isinstance(getattr(ln_inst, 'SPCSO1'), DO)
        assert isinstance(getattr(ln_inst, 'Str1'), DO)
        assert isinstance(getattr(ln_inst, 'StrVal1'), DO)
        assert isinstance(getattr(ln_inst, 'Wrn1'), DO)                                         # pylint: disable=maybe-no-member
        assert ln_inst.LocKey.dU.bType == 'Unicode255'                          # pylint: disable=maybe-no-member
        assert ln_inst.DPCSO1.ctlModel.fc == 'CF'   # pylint: disable=maybe-no-member

    def test_create_LN0_by_dtid(self):
        """
            I should be able to create a LN0 object
        """
        ln0s = _get_node_list_by_tag(self.scd, 'LN0')
        assert len(ln0s) > 0
        ln0 = LN0(self.scd.datatypes, ln0s[0])
        assert getattr(ln0, 'lnClass') == 'LLN0'
        assert getattr(ln0, 'name') == 'LLN0'
        datasets = ln0.DataSet
        assert len(datasets) == 157
        assert datasets[0]
        assert getattr(datasets[0], 'name') == 'DS_LPHD'
        assert isinstance(datasets[0], SCDNode)
        assert len(ln0.get_children('ReportControl')) == 157
        assert len(ln0.get_children('GSEControl')) == 157
        assert len(ln0.get_children('DO')) == 8
        assert len(ln0.get_children()) == 479
        assert isinstance(getattr(ln0, 'Diag'), DO)

    def test_create_LD(self):
        """
            I should be able to create a LD object
        """
        lds = _get_node_list_by_tag(self.scd, 'LDevice')
        ld = LD(self.scd.datatypes, lds[0])
        assert ld.name == 'LD_all'                      # pylint: disable=maybe-no-member
        assert ld.inst == 'LD_all'                      # pylint: disable=maybe-no-member
        assert ld.LLN0                                  # pylint: disable=maybe-no-member
        assert len(ld.get_children('LN')) == 157

    def test_create_IED(self):
        """
            I should be able to create a IED object
        """
        ieds = _get_node_list_by_tag(self.scd, 'IED')
        self._start_perfo_stats()
        ied = IED(self.scd.datatypes, ieds[0])
        assert ied.HVDC_LD_All_1.Server.LD_all.ANCR1.ADetun.blkEna.fc == 'BL'  # pylint: disable=maybe-no-member
        assert ied.name == 'LD_All'                                             # pylint: disable=maybe-no-member
        self._end_perfo_stats()

    def test_get_DA_leaf_nodes(self):
        """
            I should be able to retrieve all DA leaf nodes from a SCD_Node
        """
        ieds = _get_node_list_by_tag(self.scd, 'IED')
        self._start_perfo_stats()
        ied = IED(self.scd.datatypes, ieds[0])
        da_list = ied.get_DA_leaf_nodes()
        assert len(da_list) == 54166
        for da in da_list.values():
            assert da.tag == 'DA' or da.tag == 'BDA'
            assert ied.get_int_addr(da) is not None

        assert da_list['LD_all.LLN0.OpTmh.blkEna'].name == 'blkEna'
        self._end_perfo_stats()

    def test_get_ied_names_list(self):
        """
            I should be able to get the list of the IED names
        """
        result = self.scd.get_IED_names_list()
        assert len(result) == 1
        assert result[0] == 'LD_All'

    def test_get_ied_by_name(self):
        ied = self.scd.get_IED_by_name('LD_All')
        assert isinstance(ied, IED)

    def test_get_all_ied(self):
        ieds = self.scd.get_all_IEDs()
        assert len(ieds) == 1
        assert isinstance(ieds[0], IED)


def test_open_iop():
    scd = SCD_handler(SCD_OPEN_IOP_PATH)
    assert scd
    assert scd.Header.toolID == 'PVR GEN TOOL'  # pylint: disable=maybe-no-member
    assert scd.Communication.RSPACE_PROCESS_NETWORK.AUT1A_SITE_1.GSE[0].Address.P[0].type == 'VLAN-PRIORITY'  # pylint: disable=maybe-no-member
    assert scd.Substation[0].VoltageLevel[0].name == 'SITEP41'  # pylint: disable=maybe-no-member
    del scd


def test_get_Data_Type_Definition():
    scd = SCD_handler(SCD_OPEN_IOP_PATH)
    datatype_defs = scd.datatypes.get_Data_Type_Definitions()
    assert datatype_defs
    assert len(datatype_defs.keys()) == 4
    assert len(datatype_defs['LNodeType']) == 145
    assert len(datatype_defs['DOType']) == 89
    assert len(datatype_defs['DAType']) == 16
    assert len(datatype_defs['EnumType']) == 40


def test_extract_sub_SCD():
    ref_scd2_hash = '4577fb05ea3cc39d637feb699b684cab2a73c216b2bc9bd8f194d3310e66c005'
    scd = SCD_handler(SCD_OPEN_IOP_PATH)
    ied_list = ['AUT1A_SITE_1', 'IEDTEST_SITE_1']

    dest_path = scd.extract_sub_SCD(ied_list)
    assert 'AUT1A_SITE_1' in scd._iter_get_IED_names_list()
    assert os.path.exists(dest_path)
    assert ref_scd2_hash == hashfile(dest_path)


def test_get_IP_Adr():
    scd = SCD_handler(SCD_OPEN_IOP_PATH)
    (ip1, apName1) = scd.get_IP_Adr('AUT1A_SITE_1')
    assert ip1 == '127.0.0.1'
    assert apName1 == "PROCESS_AP"

    (ip2, apName2) = scd.get_IP_Adr('IEDTEST_SITE_1')
    assert ip2 == '127.0.0.1'
    assert apName2 == "PROCESS_AP"


class TestSCD_IOP():
    '''
    !!! SCD_HANDLER set as class attribute because tests are not altering it
    Set back SCD_HANDLER in setup/teadown methods if it is altered by any test
    '''

    SCD_HANDLER = SCD_handler(SCD_OPEN_IOP_PATH)
    def setup_method(self):
        pass
        # self.SCD_HANDLER = SCD_handler(SCD_OPEN_IOP_PATH)

    def teardown_method(self):
        pass
        # del self.SCD_HANDLER

    def test_get_all_GSE(self):
        all_gse = self.SCD_HANDLER.get_GSEs("AUT1A_SITE_1")
        assert (self.SCD_HANDLER.get_GSEs("AUT1A_SITE_1")[0].cbName == "PVR_LLN0_CB_GSE_INT")
        assert (self.SCD_HANDLER.get_GSEs("AUT1A_SITE_1")[0].Address.P[0].type == "VLAN-PRIORITY")
        assert (self.SCD_HANDLER.get_GSEs("AUT1A_SITE_1")[0].Address.P[0].Val == 4)
        assert (len(self.SCD_HANDLER.get_GSEs("AUT1A_SITE_1")) == 11)
        assert (self.SCD_HANDLER.get_GSEs("AUT1A_SITE_666") == [])

    def test_extract_sub_SCD(self):
        ref_scd2_hash = '4577fb05ea3cc39d637feb699b684cab2a73c216b2bc9bd8f194d3310e66c005'
        ied_list = ['AUT1A_SITE_1', 'IEDTEST_SITE_1']

        dest_path = self.SCD_HANDLER.extract_sub_SCD(ied_list)
        assert 'AUT1A_SITE_1' in self.SCD_HANDLER._iter_get_IED_names_list()
        assert os.path.exists(dest_path)
        assert ref_scd2_hash == hashfile(dest_path)

    def test_get_IP_Adr(self):
        (ip1, apName1) = self.SCD_HANDLER.get_IP_Adr('AUT1A_SITE_1')
        assert ip1 == '127.0.0.1'
        assert apName1 == "PROCESS_AP"

        (ip2, apName2) = self.SCD_HANDLER.get_IP_Adr('IEDTEST_SITE_1')
        assert ip2 == '127.0.0.1'
        assert apName2 == "PROCESS_AP"

    def test_IED_get_extrefs(self):
        ied = self.SCD_HANDLER.get_IED_by_name('AUT1A_SITE_1')

        extrefs = ied.get_inputs_extrefs()
        assert len(extrefs) == 535
        assert extrefs[0] == {'iedName': 'IEDTEST_SITE_1', 'ldInst': 'XX_BCU_4LINE2_1_LDCMDSL_1', 'lnClass': 'CSWI', 'lnInst': '0', 'doName': 'Pos', 'intAddr': 'VDF', 'serviceType': 'GOOSE', 'pLN': 'CSWI', 'pDO': 'Pos', 'pServT': 'GOOSE', 'srcLDInst': 'XX_BCU_4LINE2_1_LDCMDSL_1', 'srcCBName': 'PVR_LLN0_CB_GSE_EXT', 'desc': 'DYN_LDASLD_Position filtree sectionneur_5_Dbpos_1_stVal_3'}
        assert extrefs[525] == {'iedName': 'SCU1B_SITE_1', 'ldInst': 'LDITFUA', 'lnClass': 'SBAT', 'lnInst': '2', 'doName': 'BatEF', 'intAddr': 'VDF', 'serviceType': 'GOOSE', 'pLN': 'SBAT', 'pDO': 'BatEF', 'pServT': 'GOOSE', 'srcLDInst': 'LDITFUA', 'srcCBName': 'PVR_LLN0_CB_GSE_INT', 'desc': 'DYN_LDTGSEC_Terre Batterie UA_2_BOOLEAN_1_stVal_2'}

        goose_extrefs = ied.get_goose_inputs_extrefs()
        assert goose_extrefs[0] == {'iedName': 'IEDTEST_SITE_1', 'ldInst': 'XX_BCU_4LINE2_1_LDCMDSL_1', 'lnClass': 'CSWI', 'lnInst': '0', 'doName': 'Pos', 'intAddr': 'VDF', 'serviceType': 'GOOSE', 'pLN': 'CSWI', 'pDO': 'Pos', 'pServT': 'GOOSE', 'srcLDInst': 'XX_BCU_4LINE2_1_LDCMDSL_1', 'srcCBName': 'PVR_LLN0_CB_GSE_EXT', 'desc': 'DYN_LDASLD_Position filtree sectionneur_5_Dbpos_1_stVal_3'}
        assert len(goose_extrefs) == 526

        assert len(ied.get_inputs_extrefs(ServiceType.SMV)) == 0
        assert len(ied.get_inputs_extrefs(ServiceType.Report)) == 0
        assert len(ied.get_inputs_extrefs(ServiceType.Poll)) == 0

    def test_IED_get_lds(self):
        ied = self.SCD_HANDLER.get_IED_by_name('AUT1A_SITE_1')

        result = ied.get_children_LDs()
        assert len(result) == 11
        assert isinstance(result[0], LD)

    def test_IED_get_node_by_ref(self):
        ied = self.SCD_HANDLER.get_IED_by_name('AUT1A_SITE_1')

        assert ied.get_node_by_ref('LDASLD').name == 'LDASLD'
        assert ied.get_node_by_ref('LDASLD.LLN0').name == 'LLN0'
        assert ied.get_node_by_ref('LDASLD.LLN0.Beh').name == 'Beh'
        assert ied.get_node_by_ref('LDASLD/LLN0.Beh').name == 'Beh'
        assert ied.get_node_by_ref('LDASLD.LLN0.Beh.stVal').name == 'stVal'
        assert ied.get_node_by_ref('LDASLD.PTRC3.Beh.subQ').name == 'subQ'
        with pytest.raises(AttributeError):
            ied.get_node_by_ref('toto')
        with pytest.raises(AttributeError):
            ied.get_node_by_ref('')


    def test_DataSet_as_tree(self):
        ied = self.SCD_HANDLER.get_IED_by_name('AUT1A_SITE_1')
        ld = ied.get_children_LDs()[0]

        result = ld.get_dataset_by_name("PVR_LLN0_DS_RPT_DQCHG_EXT").as_tree()
        assert(result == ('root', [('LDASLD.LLN0.Beh', [('q', []), ('stVal', []), ('t', [])]),  ('LDASLD.LLN0.Beh',   [('subEna', []), ('subID', []), ('subQ', []), ('subVal', [])]),  ('LDASLD.LLN0.Health', [('q', []), ('stVal', []), ('t', [])]),  ('LDASLD.LLN0.Health',   [('subEna', []), ('subID', []), ('subQ', []), ('subVal', [])]),  ('LDASLD.LLN0.NamPlt', [('paramRev', []), ('valRev', [])]),  ('LDASLD.PTRC1.Beh', [('q', []), ('stVal', []), ('t', [])]),  ('LDASLD.PTRC1.Beh',   [('subEna', []), ('subID', []), ('subQ', []), ('subVal', [])]),  ('LDASLD.PTRC1.Tr',   [('general', []),    ('neut', []),    ('phsA', []),    ('phsB', []),    ('phsC', []),    ('q', []),    ('t', []),    ('originSrc', [('orCat', []), ('orIdent', [])])]),  ('LDASLD.PTRC2.Beh', [('q', []), ('stVal', []), ('t', [])]),  ('LDASLD.PTRC2.Beh',   [('subEna', []), ('subID', []), ('subQ', []), ('subVal', [])]),  ('LDASLD.PTRC2.Tr',   [('general', []),    ('neut', []),    ('phsA', []),    ('phsB', []),    ('phsC', []),    ('q', []),    ('t', []),    ('originSrc', [('orCat', []), ('orIdent', [])])]),  ('LDASLD.PTRC3.Beh', [('q', []), ('stVal', []), ('t', [])]),  ('LDASLD.PTRC3.Beh',   [('subEna', []), ('subID', []), ('subQ', []), ('subVal', [])]),  ('LDASLD.PTRC3.Tr',   [('general', []),    ('neut', []),    ('phsA', []),    ('phsB', []),    ('phsC', []),    ('q', []),    ('t', []),    ('originSrc', [('orCat', []), ('orIdent', [])])]),  ('LDASLD.RBRF1.Beh', [('q', []), ('stVal', []), ('t', [])]),  ('LDASLD.RBRF1.Beh',   [('subEna', []), ('subID', []), ('subQ', []), ('subVal', [])]),  ('LDASLD.RBRF1.OpEx',   [('general', []),    ('neut', []),    ('phsA', []),    ('phsB', []),    ('phsC', []),    ('q', []),    ('t', []),    ('originSrc', [('orCat', []), ('orIdent', [])])]),  ('LDASLD.RBRF2.Beh', [('q', []), ('stVal', []), ('t', [])]),  ('LDASLD.RBRF2.Beh',   [('subEna', []), ('subID', []), ('subQ', []), ('subVal', [])]),  ('LDASLD.RBRF2.OpEx',   [('general', []),    ('neut', []),    ('phsA', []),    ('phsB', []),    ('phsC', []),    ('q', []),    ('t', []),    ('originSrc', [('orCat', []), ('orIdent', [])])]),  ('LDASLD.RBRF3.Beh', [('q', []), ('stVal', []), ('t', [])]),  ('LDASLD.RBRF3.OpEx',   [('general', []),    ('neut', []), ('phsA', []),    ('phsB', []),    ('phsC', []),    ('q', []),    ('t', []),    ('originSrc', [('orCat', []), ('orIdent', [])])]),  ('LDASLD.LPHD0.NamPlt', [('paramRev', []), ('valRev', [])]),  ('LDASLD.LPHD0.PhyHealth', [('q', []), ('stVal', []), ('t', [])]),  ('LDASLD.LPHD0.PhyHealth',   [('subEna', []), ('subID', []), ('subQ', []), ('subVal', [])]),  ('LDASLD.LPHD0.Proxy', [('q', []), ('stVal', []), ('t', [])]),  ('LDASLD.LPHD0.Proxy',   [('subEna', []), ('subID', []), ('subQ', []), ('subVal', [])]),  ('LDASLD.LLN0.Mod', [('q', []), ('stVal', []), ('t', [])]),  ('LDASLD.LLN0.Mod',   [('subEna', []), ('subID', []), ('subQ', []), ('subVal', [])]),  ('LDASLD.RBRF3.Beh', [('subEna', []), ('subID', []), ('subQ', []), ('subVal', [])])]))

    def test_DataSet_as_list(self):
        ied = self.SCD_HANDLER.get_IED_by_name('AUT1A_SITE_1')
        ld = ied.get_children_LDs()[0]

        result = ld.get_dataset_by_name("PVR_LLN0_DS_RPT_DQCHG_EXT").as_list()
        assert(result == ['LDASLD.LLN0.Beh.q', 'LDASLD.LLN0.Beh.stVal', 'LDASLD.LLN0.Beh.t', 'LDASLD.LLN0.Beh.subEna', 'LDASLD.LLN0.Beh.subID', 'LDASLD.LLN0.Beh.subQ', 'LDASLD.LLN0.Beh.subVal', 'LDASLD.LLN0.Health.q', 'LDASLD.LLN0.Health.stVal', 'LDASLD.LLN0.Health.t', 'LDASLD.LLN0.Health.subEna', 'LDASLD.LLN0.Health.subID', 'LDASLD.LLN0.Health.subQ', 'LDASLD.LLN0.Health.subVal', 'LDASLD.LLN0.NamPlt.paramRev', 'LDASLD.LLN0.NamPlt.valRev', 'LDASLD.PTRC1.Beh.q', 'LDASLD.PTRC1.Beh.stVal', 'LDASLD.PTRC1.Beh.t', 'LDASLD.PTRC1.Beh.subEna', 'LDASLD.PTRC1.Beh.subID', 'LDASLD.PTRC1.Beh.subQ', 'LDASLD.PTRC1.Beh.subVal', 'LDASLD.PTRC1.Tr.general', 'LDASLD.PTRC1.Tr.neut', 'LDASLD.PTRC1.Tr.phsA', 'LDASLD.PTRC1.Tr.phsB', 'LDASLD.PTRC1.Tr.phsC', 'LDASLD.PTRC1.Tr.q', 'LDASLD.PTRC1.Tr.t', 'LDASLD.PTRC1.Tr.originSrc.orCat', 'LDASLD.PTRC1.Tr.originSrc.orIdent', 'LDASLD.PTRC2.Beh.q', 'LDASLD.PTRC2.Beh.stVal', 'LDASLD.PTRC2.Beh.t', 'LDASLD.PTRC2.Beh.subEna', 'LDASLD.PTRC2.Beh.subID', 'LDASLD.PTRC2.Beh.subQ', 'LDASLD.PTRC2.Beh.subVal', 'LDASLD.PTRC2.Tr.general', 'LDASLD.PTRC2.Tr.neut', 'LDASLD.PTRC2.Tr.phsA', 'LDASLD.PTRC2.Tr.phsB', 'LDASLD.PTRC2.Tr.phsC', 'LDASLD.PTRC2.Tr.q', 'LDASLD.PTRC2.Tr.t', 'LDASLD.PTRC2.Tr.originSrc.orCat', 'LDASLD.PTRC2.Tr.originSrc.orIdent', 'LDASLD.PTRC3.Beh.q', 'LDASLD.PTRC3.Beh.stVal', 'LDASLD.PTRC3.Beh.t', 'LDASLD.PTRC3.Beh.subEna', 'LDASLD.PTRC3.Beh.subID', 'LDASLD.PTRC3.Beh.subQ', 'LDASLD.PTRC3.Beh.subVal', 'LDASLD.PTRC3.Tr.general', 'LDASLD.PTRC3.Tr.neut', 'LDASLD.PTRC3.Tr.phsA', 'LDASLD.PTRC3.Tr.phsB', 'LDASLD.PTRC3.Tr.phsC', 'LDASLD.PTRC3.Tr.q', 'LDASLD.PTRC3.Tr.t', 'LDASLD.PTRC3.Tr.originSrc.orCat', 'LDASLD.PTRC3.Tr.originSrc.orIdent', 'LDASLD.RBRF1.Beh.q', 'LDASLD.RBRF1.Beh.stVal', 'LDASLD.RBRF1.Beh.t', 'LDASLD.RBRF1.Beh.subEna', 'LDASLD.RBRF1.Beh.subID', 'LDASLD.RBRF1.Beh.subQ', 'LDASLD.RBRF1.Beh.subVal', 'LDASLD.RBRF1.OpEx.general', 'LDASLD.RBRF1.OpEx.neut', 'LDASLD.RBRF1.OpEx.phsA', 'LDASLD.RBRF1.OpEx.phsB', 'LDASLD.RBRF1.OpEx.phsC', 'LDASLD.RBRF1.OpEx.q', 'LDASLD.RBRF1.OpEx.t', 'LDASLD.RBRF1.OpEx.originSrc.orCat', 'LDASLD.RBRF1.OpEx.originSrc.orIdent', 'LDASLD.RBRF2.Beh.q', 'LDASLD.RBRF2.Beh.stVal', 'LDASLD.RBRF2.Beh.t', 'LDASLD.RBRF2.Beh.subEna', 'LDASLD.RBRF2.Beh.subID', 'LDASLD.RBRF2.Beh.subQ', 'LDASLD.RBRF2.Beh.subVal', 'LDASLD.RBRF2.OpEx.general', 'LDASLD.RBRF2.OpEx.neut', 'LDASLD.RBRF2.OpEx.phsA', 'LDASLD.RBRF2.OpEx.phsB', 'LDASLD.RBRF2.OpEx.phsC', 'LDASLD.RBRF2.OpEx.q', 'LDASLD.RBRF2.OpEx.t', 'LDASLD.RBRF2.OpEx.originSrc.orCat', 'LDASLD.RBRF2.OpEx.originSrc.orIdent', 'LDASLD.RBRF3.Beh.q', 'LDASLD.RBRF3.Beh.stVal', 'LDASLD.RBRF3.Beh.t', 'LDASLD.RBRF3.OpEx.general', 'LDASLD.RBRF3.OpEx.neut', 'LDASLD.RBRF3.OpEx.phsA', 'LDASLD.RBRF3.OpEx.phsB', 'LDASLD.RBRF3.OpEx.phsC', 'LDASLD.RBRF3.OpEx.q', 'LDASLD.RBRF3.OpEx.t', 'LDASLD.RBRF3.OpEx.originSrc.orCat', 'LDASLD.RBRF3.OpEx.originSrc.orIdent', 'LDASLD.LPHD0.NamPlt.paramRev', 'LDASLD.LPHD0.NamPlt.valRev', 'LDASLD.LPHD0.PhyHealth.q', 'LDASLD.LPHD0.PhyHealth.stVal', 'LDASLD.LPHD0.PhyHealth.t', 'LDASLD.LPHD0.PhyHealth.subEna', 'LDASLD.LPHD0.PhyHealth.subID', 'LDASLD.LPHD0.PhyHealth.subQ', 'LDASLD.LPHD0.PhyHealth.subVal', 'LDASLD.LPHD0.Proxy.q', 'LDASLD.LPHD0.Proxy.stVal', 'LDASLD.LPHD0.Proxy.t', 'LDASLD.LPHD0.Proxy.subEna', 'LDASLD.LPHD0.Proxy.subID', 'LDASLD.LPHD0.Proxy.subQ', 'LDASLD.LPHD0.Proxy.subVal', 'LDASLD.LLN0.Mod.q', 'LDASLD.LLN0.Mod.stVal', 'LDASLD.LLN0.Mod.t', 'LDASLD.LLN0.Mod.subEna', 'LDASLD.LLN0.Mod.subID', 'LDASLD.LLN0.Mod.subQ', 'LDASLD.LLN0.Mod.subVal', 'LDASLD.RBRF3.Beh.subEna', 'LDASLD.RBRF3.Beh.subID', 'LDASLD.RBRF3.Beh.subQ', 'LDASLD.RBRF3.Beh.subVal'])

    def test_DataSet_get_path_in_dataset(self):
        ied = self.SCD_HANDLER.get_IED_by_name('AUT1A_SITE_1')
        ld = ied.get_children_LDs()[0]
        ds = ld.get_dataset_by_name("PVR_LLN0_DS_RPT_DQCHG_EXT")
        assert ds.get_path_in_dataset('LDASLD.LLN0.Beh.stVal') == ['root', 'LDASLD.LLN0.Beh', "stVal"]
        with pytest.raises(AttributeError):
            ds.get_path_in_dataset('toto')

    def test_LD_get_extrefs(self):
        ied = self.SCD_HANDLER.get_IED_by_name('BCU_4LINE2_1')
        ld = ied.get_children_LDs()[0]

        extrefs = ld.get_inputs_extrefs()
        assert len(extrefs) == 58
        assert extrefs[0] == {'desc': 'DYN_LDADD_Position filtree du DJ_1_Dbpos_1_stVal_3', 'doName': 'Pos', 'iedName': 'IEDTEST_SITE_1', 'intAddr': 'VDF', 'ldInst': 'XX_BCU_4LINE2_1_LDCMDDJ_1', 'lnClass': 'CSWI', 'lnInst': '1', 'pDO': 'Pos', 'pLN': 'CSWI', 'pServT': 'GOOSE', 'serviceType': 'GOOSE', 'srcCBName': 'PVR_LLN0_CB_GSE_INT', 'srcLDInst': 'XX_BCU_4LINE2_1_LDCMDDJ_1'}

        goose_extrefs = ld.get_goose_inputs_extrefs()
        assert goose_extrefs[0] == {'iedName': 'IEDTEST_SITE_1', 'ldInst': 'XX_BCU_4LINE2_1_LDCMDDJ_1', 'lnClass': 'CSWI', 'lnInst': '1', 'doName': 'Pos', 'intAddr': 'VDF', 'serviceType': 'GOOSE', 'pLN': 'CSWI', 'pDO': 'Pos', 'pServT': 'GOOSE', 'srcLDInst': 'XX_BCU_4LINE2_1_LDCMDDJ_1', 'srcCBName': 'PVR_LLN0_CB_GSE_INT', 'desc': 'DYN_LDADD_Position filtree du DJ_1_Dbpos_1_stVal_3'}
        assert len(goose_extrefs) == 21


    def test_LD_get_gsecontrols(self):
        ied = self.SCD_HANDLER.get_IED_by_name('BCU_4LINE2_1')
        ld = ied.get_children_LDs()[0]

        result = ld.get_gsecontrols()

        assert len(result) == 1
        assert result[0].type == 'GOOSE'
        assert result[0].datSet == 'PVR_LLN0_GSE_EXT'
        assert result[0].name == 'PVR_LLN0_CB_GSE_EXT'

    def test_LD_get_gsecontrol_by_name(self):
        ied = self.SCD_HANDLER.get_IED_by_name('BCU_4LINE2_1')
        ld = ied.get_children_LDs()[0]

        assert ld.get_gsecontrol_by_name("toto") is None
        assert ld.get_gsecontrol_by_name("PVR_LLN0_CB_GSE_EXT").name == "PVR_LLN0_CB_GSE_EXT"
        assert ld.get_gsecontrol_by_name("PVR_LLN0_CB_GSE_EXT").datSet == "PVR_LLN0_GSE_EXT"

    def test_LD_get_reportcontrols(self):
        ied = self.SCD_HANDLER.get_IED_by_name('BCU_4LINE2_1')
        ld = ied.get_children_LDs()[0]

        result = ld.get_reportcontrols()
        assert len(result) == 1
        assert result[0].buffered is True
        assert result[0].datSet == 'PVR_LLN0_DS_RPT_DQCHG_EXT'

    def test_LD_get_reportcontrol_by_name(self):
        ied = self.SCD_HANDLER.get_IED_by_name('BCU_4LINE2_1')
        ld = ied.get_children_LDs()[0]

        assert ld.get_reportcontrol_by_name("toto") is None
        assert ld.get_reportcontrol_by_name("PVR_LLN0_CB_RPT_DQCHG_EXT").buffered is True
        assert ld.get_reportcontrol_by_name("PVR_LLN0_CB_RPT_DQCHG_EXT").datSet == 'PVR_LLN0_DS_RPT_DQCHG_EXT'

    def test_LD_get_datasets(self):
        ied = self.SCD_HANDLER.get_IED_by_name('BCU_4LINE2_1')
        ld = ied.get_children_LDs()[0]

        result = ld.get_datasets()
        assert len(result) == 2
        assert result[0].name == "PVR_LLN0_GSE_EXT"
        assert len(result[0].FCDA) == 2

    def test_LD_get_dataset_by_name(self):
        ied = self.SCD_HANDLER.get_IED_by_name('BCU_4LINE2_1')
        ld = ied.get_children_LDs()[0]

        assert ld.get_dataset_by_name("toto") is None
        assert ld.get_dataset_by_name("PVR_LLN0_GSE_EXT").name == "PVR_LLN0_GSE_EXT"
        assert len(ld.get_dataset_by_name("PVR_LLN0_GSE_EXT").FCDA) == 2

    def test_LD_get_LN_by_name(self):
        ied = self.SCD_HANDLER.get_IED_by_name('AUT1A_SITE_1')
        ld = ied.get_children_LDs()[0]
        ln_name = 'PTRC1'

        result = ld.get_LN_by_name(ln_name)
        assert isinstance(result, LN)
        assert result.name == ln_name

    def test_IED_get_LN_by_name(self):
        ied = self.SCD_HANDLER.get_IED_by_name('AUT1A_SITE_1')
        ld_inst = 'LDASLD'
        ln_name = 'PTRC1'

        result = ied.get_LN_by_name(ld_inst, ln_name)
        assert isinstance(result, LN)
        assert result.name == ln_name

    def test_IED_get_LD_by_inst(self):
        ied = self.SCD_HANDLER.get_IED_by_name('AUT1A_SITE_1')
        ld_inst = 'LDASLD'

        result = ied.get_LD_by_inst(ld_inst)
        assert isinstance(result, LD)
        assert result.name == ld_inst

    def test_get_ieds_by_type(self):
        ieds = self.SCD_HANDLER.get_IED_by_type('TYPE1')
        assert len(ieds) == 2
        assert isinstance(ieds[0], IED)

    def test_get_associated_fc(self):
        ied = self.SCD_HANDLER.get_IED_by_name('AUT1A_SITE_1')
        ln = ied.PROCESS_AP.Server.LDASLD.PTRC2

        assert(ln.Tr.originSrc.orIdent.get_associated_fc() == "ST")
        assert(ln.Tr.d.get_associated_fc() == "DC")
        with pytest.raises(AttributeError):
            ln.get_associated_fc()

    def test_get_name_subtree(self):
        ied = self.SCD_HANDLER.get_IED_by_name('AUT1A_SITE_1')
        ln = ied.PROCESS_AP.Server.LDASLD.PTRC2
        with pytest.raises(AssertionError):
            ied.get_name_subtree()
        assert(ied.PROCESS_AP.Server.LDASLD.get_name_subtree() == ('blkEna', []))
        assert(ln.get_name_subtree() == ('PTRC2', [('Beh',   [('blkEna', []),    ('d', []),    ('q', []),    ('stVal', []),    ('subEna', []),    ('subID', []),    ('subQ', []),    ('subVal', []),    ('t', [])]),  ('Tr',   [('d', []),    ('general', []),    ('neut', []),    ('phsA', []),    ('phsB', []),    ('phsC', []),    ('q', []),    ('t', []),    ('originSrc', [('orCat', []), ('orIdent', [])])])]))
        assert(ln.Tr.d.get_name_subtree() == ('d', []) )
        assert(ln.Tr.get_name_subtree() == ('Tr',   [('d', []),    ('general', []),    ('neut', []),    ('phsA', []),    ('phsB', []),    ('phsC', []),    ('q', []),    ('t', []),    ('originSrc', [('orCat', []), ('orIdent', [])])]))
        assert(ln.Tr.originSrc.get_name_subtree() == ('originSrc', [('orCat', []), ('orIdent', [])]))
        assert(ln.get_name_subtree("ST") == ('PTRC2', [('Beh', [('q', []), ('stVal', []), ('t', [])]), ('Tr', [('general', []), ('neut', []), ('phsA', []), ('phsB', []), ('phsC', []), ('q', []), ('t', []), ('originSrc', [('orCat', []), ('orIdent', [])])])]))

    def test_get_object_reference(self):
        ied = self.SCD_HANDLER.get_IED_by_name('AUT1A_SITE_1')
        ln = ied.PROCESS_AP.Server.LDASLD.PTRC2
        assert ln.get_object_reference() == 'XX_AUT1A_SITE_1_LDASLD_1/PTRC2'
        assert ln.Tr.d.get_object_reference() == 'XX_AUT1A_SITE_1_LDASLD_1/PTRC2.Tr.d'
        assert ln.Tr.get_object_reference() == 'XX_AUT1A_SITE_1_LDASLD_1/PTRC2.Tr'
        assert ln.Tr.originSrc.get_object_reference() == 'XX_AUT1A_SITE_1_LDASLD_1/PTRC2.Tr.originSrc'

    def test_get_DO_nodes(self):
        ied = self.SCD_HANDLER.get_IED_by_name('AUT1A_SITE_1')
        ld = ied.PROCESS_AP.Server.LDASLD

        assert len(ld.get_DO_nodes()) == 27
        assert "LDASLD.PTRC2.Tr" in ld.PTRC2.Tr.get_DO_nodes()
        assert "LDASLD.PTRC2.Tr" in ld.PTRC2.Tr.originSrc.get_DO_nodes()
        assert ld.PTRC2.Tr.originSrc.get_DO_nodes()["LDASLD.PTRC2.Tr"].cdc == 'ACT'

    def test_get_mms_var_name(self):
        ied = self.SCD_HANDLER.get_IED_by_name('AUT1A_SITE_1')
        ln = ied.PROCESS_AP.Server.LDASLD.PTRC2
        assert ln.Tr.d.get_mms_var_name() == 'XX_AUT1A_SITE_1_LDASLD_1/PTRC2$DC$Tr$d'
        assert ln.Tr.get_mms_var_name('DC') == 'XX_AUT1A_SITE_1_LDASLD_1/PTRC2$DC$Tr'
        assert ln.Tr.originSrc.get_mms_var_name() == 'XX_AUT1A_SITE_1_LDASLD_1/PTRC2$ST$Tr$originSrc'

    def test_get_parent_with_class(self):
        ied = self.SCD_HANDLER.get_IED_by_name('AUT1A_SITE_1')
        da = ied.PROCESS_AP.Server.LDASLD.PTRC2.Tr.originSrc
        assert ied.get_parent_with_class(LD) is None
        assert da.get_parent_with_class(DO).name == 'Tr'
        assert da.get_parent_with_class(LN).name == 'PTRC2'
        assert da.get_parent_with_class(LD).name == 'LDASLD'
        assert da.get_parent_with_class(IED).name == 'AUT1A_SITE_1'
        assert da.get_parent_with_class(DA) is None

    def test_get_GOCB_reference(self):
        ied = self.SCD_HANDLER.get_IED_by_name('BCU_4LINE2_1')
        ld = ied.get_children_LDs()[0]
        assert ld.get_gsecontrol_by_name("PVR_LLN0_CB_GSE_EXT").get_GOCB_reference() == "BCU_4LINE2_1LDADD/LLN0$GO$PVR_LLN0_CB_GSE_EXT"
