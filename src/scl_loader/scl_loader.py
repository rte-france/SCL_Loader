#!/usr/bin/env python3
# Copyright RTE - 2020

import os
import logging
import re
import weakref
from copy import deepcopy
from lxml import etree
from enum import Enum, unique

HERE = os.path.abspath(os.path.dirname(__file__))
XSD_PATH = os.path.join(HERE, 'resources', 'SCL_Schema', 'SCL.xsd')
LOGGER = logging.getLogger(__name__)
NS = {'rte': 'http://www.rte-france.com', 'iec61850': 'http://www.iec.ch/61850/2003/SCL'}
SCL_NAMESPACE = r'{http://www.iec.ch/61850/2003/SCL}'
MAX_VALIDATION_SIZE = 500  # taille en Mo
REG_DA = r'(?:\{.+\})?[BS]?DA'
REG_DO = r'(?:\{.+\})?S?DO'
REG_SDI = r'(?:\{.+\})?S?D[OA]?I'
REG_ARRAY_TAGS = r'(?:\{.+\})?(?:FCDA|ClientLN|IEDName|FIP|BAP|ExtRef|Terminal|P|DataSet|GSE' \
                 r'|GSEControl|ReportControl|VoltageLevel)'  # |Server)'
REG_DT_NODE = r'(?:.*\})?((?:[BS]?D[AO])|(?:LN0?))'
REF_SCL_NODES = r'(?:\{.+\})?(?:Header|Substation|Private|Communication)'
DEFAULT_AP = 'PROCESS_AP'
SEP1 = '$'          # Standard MMS separator.
SEP2 = '/'          # MMS Separator for system testing

FORCE_ITER_MODE = False

NODES_ATTRS = {
    'IED': [
        'Server',
        'name',
        'desc',
        'type',
        'originalSclVersion',
        'originalSclRevision',
        'configVersion',
        'manufacturer',
        'engRight',
        'owner',
        'IP'
    ],
    'LD': [
        'inst',
        'desc',
        'ldName'
    ],
    'LN0': [],  # Inherited from LN
    'LN': [
        'id',
        'desc',
        'iedType',
        'lnClass',
        'lnInst',
        'iedName',
        'ldInst',
        'prefix',
        'lnType',
        'lnPrefix',
        'lnDesc'
    ],
    'DO': [
        'id',
        'desc',
        'iedType',
        'cdc',
        'type',
        'accessControl',
        'transient',
        'ix',
        'value'
    ],
    'DA': [
        'id',
        'desc',
        'iedType',
        'protNs',
        'name',
        'fc',
        'dchg',
        'qchg',
        'dupd',
        'sAddr',
        'bType',
        'type',
        'count',
        'valKind',
        'valImport',
        'SDO',
        'value',
    ],
    'BDA': [
        'name',
        'SDO',
        'type',
        'bType',
        'valKind',
        'value'
    ],
    'FCDA': [
        'ldInst',
        'prefix',
        'lnClass',
        'lnInst',
        'doName',
        'daName',
        'fc',
        'ix'
    ],
    'DataSet': [
        'name'
    ]
}


@unique
class ServiceType(str, Enum):
    Poll = 'Poll'
    Report = 'Report'
    GOOSE = 'GOOSE'
    SMV = 'SMV'


def _safe_convert_value(value: str) -> any:
    """
        Convert a string value in typed value une valeur string en valeur typée.

        Parameters
        ----------
        value
            La string contenant la valeur à convertir

        Returns
        -------
        any
            la valeur convertie
    """
    if value is None:
        return None

    p_num = re.compile(r'^-?([0-9]+)(\.[0-9]+)?$')
    value = value.strip()
    low_val = str.lower(value)
    if low_val == 'false':
        return False
    elif low_val == 'true':
        return True
    elif p_num.match(value) is not None:
        if p_num.match(value).group(2):
            return float(value)
        else:
            return int(value)
    else:
        val = value.strip()
        if len(val) > 0:
            return val
        return None


def _get_tag_without_ns(nstag: str) -> str:
    """
        Get the xml tag without namespace

        Parameters
        ----------
        nstag
           The xml element tag

        Returns
        -------
        str
            the tag without namespace
    """
    tag_reg = r'(?:{.+})?(\w+)'
    result = re.match(tag_reg, nstag)
    if result:
        return result.group(1)


def _get_node_name(node: etree.Element):
    name = None
    tag = _get_tag_without_ns(node.tag)

    name = node.get('name')
    if not name:
        if tag in ['LN', 'LN0']:
            lnClass = node.get('lnClass')
            inst = node.get('inst')
            prefix = node.get('prefix') or ''
            name = prefix + lnClass + str(inst)
        elif tag == 'LDevice':
            name = node.get('inst')
        elif tag == 'Private':
            name = node.get('type')
        elif tag == 'ConnectedAP':
            name = node.get('iedName')
        else:
            name = tag

    if name is not None:
        name = re.sub('[-:]', '_', name)  # in to handle: RTE-FIP, RTE-BAP, rte:BAP and rte:FIP

    return name


class DataTypeTemplates:
    """
        Utility class to fast retrieve datatypes elements
    """
    def __init__(self, xml_path: str):
        """
            Constructeur de l'outil de gestion des datatypes

            Parameters
                ----------
                xml_path
                    chemin du fichier SCD/SCL contenant les datatypes
        """
        context = etree.iterparse(xml_path, events=("end",), tag='{}DataTypeTemplates'.format(SCL_NAMESPACE), remove_comments=True)
        _, self._datatypes_root = next(context)

    def get_type_by_id(self, id: str) -> etree.Element:
        """
            Retrouve un Datatype avec son id

            Parameters
                ----------
                id
                    L'identifiant du datatype à récupérer

                Returns
                -------
                etree.Element
                    L'élément etree (xml) du datatype
        """
        item_xpath = 'child::*[@id="{}"]'.format(id)
        return self._datatypes_root.xpath(item_xpath, namespaces=NS)[0]

    def get_Data_Type_Definitions(self) -> dict:

        """
            Create a table of all Data Types definitions (LNodeType, DOType, DAType ad EnumType)

            Returns

            -------

            `dict`

                A dictionnary of the DataTypes definitions grouped by tag
        """
        tags = {'LNodeType': [], 'DOType': [], 'DAType': [], 'EnumType': []}

        for tag_key in tags.keys():
            item_xpath = 'child::iec61850:{}'.format(tag_key)
            tags[tag_key] = self._datatypes_root.xpath(item_xpath, namespaces=NS)

        return tags


class SCDNode:
    """
        Basic class to compute SCD nodes
    """
    @property
    def children(self):
        return self.get_children()

    def __init__(self, datatypes: DataTypeTemplates, node_elem: etree.Element = None, fullattrs: bool = False, **kwargs: dict):
        """
            Constructor

            Parameters
            ----------
            `datatypes`
                Instance of the DataTypeTemplates object from the SCD/SCL file.

            `node_elem` (optional)
                etree.Element element from the SCD/SCL file to build the node object.

            `fullattrs` (optional)
                If True, all the possible attributes for the SCD objects will be created
                even if they are not described in the SCD/SCL file.

            `kwargs` (optional)
                Dictionary of the node attributes.

            /!\\ At least one of node_elem or kwargs must be provided /!\\
        """

        if not isinstance(datatypes, DataTypeTemplates):
            msg = 'datatype is not a valid instance of DatatypeTemplates class'
            LOGGER.error(msg)
            raise AttributeError(msg)

        if node_elem is not None and not isinstance(node_elem, etree._Element):
            msg = 'node_elem is not a valid instance of etree.Element class'
            LOGGER.error(msg)
            raise AttributeError(msg)

        if not hasattr(self, '_all_attributes'):
            self._all_attributes = ['name', 'desc']

        if fullattrs:
            self.__dict__.update(dict.fromkeys(self._all_attributes, None))

        self._node_elem = node_elem
        self._datatypes = datatypes
        self.name = ''
        self.tag = None
        self.parent = None
        self._fullattrs = fullattrs

        if node_elem is not None:
            self.tag = _get_tag_without_ns(node_elem.tag)

        if node_elem is None and not kwargs:
            msg = 'Please enter a xml Element and/or attributes (kwargs)'
            LOGGER.error(msg)
            raise AttributeError(msg)

        self._create_node(node_elem, **kwargs)

        self.name = self.name or self.tag

        self.name = str(self.name)

        if len(self.name) == 0:
            raise AttributeError('Name cannot be set')

    def add_subnode_by_elem(self, elem: etree.Element):
        """
            Add a child node to the current node from an xml node

            Parameters
            ----------
            `elem`
                The xml node to add as a child

            Returns
            -------
            `SCDNode`
                The new subnode
        """

        new_node = None
        attributes = {}
        attributes.update(elem.attrib)
        _tag = _get_tag_without_ns(elem.tag)

        if elem.text:
            val = elem.text.strip()
            if val is not None and len(val) > 0:
                attributes['Val'] = val

        if _tag == 'Val' and 'Val' in attributes:
            setattr(self, 'Val', _safe_convert_value(attributes['Val']) or '')
            return
        elif re.fullmatch(REG_DA, elem.tag):
            new_node = DA(self._datatypes, elem, self._fullattrs, **attributes)
        elif re.fullmatch(REG_DO, elem.tag):
            new_node = DO(self._datatypes, elem, self._fullattrs, **attributes)
        elif _get_tag_without_ns(elem.tag) == 'LN':
            new_node = LN(self._datatypes, elem, self._fullattrs, **attributes)
        elif _get_tag_without_ns(elem.tag) == 'LN0':
            new_node = LN0(self._datatypes, elem, self._fullattrs, **attributes)
        elif _get_tag_without_ns(elem.tag) == 'LDevice':
            new_node = LD(self._datatypes, elem, self._fullattrs, **attributes)
        elif _get_tag_without_ns(elem.tag) == 'DataSet':
            new_node = DataSet(self._datatypes, elem, self._fullattrs, **attributes)
        else:
            new_node = SCDNode(self._datatypes, elem, self._fullattrs, **attributes)

        new_node.parent = weakref.ref(self)

        if re.fullmatch(REG_ARRAY_TAGS, _tag):
            if not hasattr(self, _tag):
                setattr(self, _tag, [])
            getattr(self, _tag).append(new_node)
        else:
            setattr(self, new_node.name, new_node)

        return new_node

    def get_DA_leaf_nodes(self) -> dict:
        """
            Recursively retrieve the leaf DA nodes of the current node.

            Returns
            -------
            `array`
                Return an dictionnary of found children SCDNodes : int_addr: SCDNode
                (int_addr is the path build with the names of the ancestors starting at the SCDNode)
        """

        leaves = {}
        self._collect_DA_leaf_nodes(self, leaves)
        return leaves

    def get_DO_nodes(self) -> dict:
        """
            Recursively retrieve the leaf DO of the current node.

            Returns
            -------
            `array`
                Return an dictionnary of found children SCDNodes : int_addr: SCDNode
                (int_addr is the path build with the names of the ancestors starting at the SCDNode)
        """
        do_nodes = {}
        if isinstance(self, (DA, DO)):
            node = self
            while node.parent is not None:
                if isinstance(node.parent(), LN):
                    do_nodes[node.get_path_from_ld()] = node
                node = node.parent()
        else:
            self._collect_DO_nodes(self, do_nodes)

        return do_nodes

    def get_children(self, tag: str = None) -> list:
        """
            Retrieve the children nodes of the current node.
            (not recursive)

            Parameters
            ----------
            `tag`
                Optionnel : si un tag est précisé, ne retourne que les enfants avec ce tag.

            Returns
            -------
            `[SCDNode]`
                Return an array of found children SCDNodes (can be subclasses of SCDNodes)
        """

        results = []
        for key, item in self.__dict__.items():
            if isinstance(item, SCDNode):
                if tag is None:
                    results.append(item)
                elif item.tag == tag:
                    results.append(item)
            elif isinstance(item, list) and re.fullmatch(REG_ARRAY_TAGS, key):
                if tag is None:
                    results += item
                elif key == tag:
                    results += item
        return results

    def get_name_subtree(self, fc_filter: str = None):
        """
            get_name_subtree

            Parameters
            ----------
            `fc_filter` (optional)
                Functional constraint string

            Return
            ----------
            `i_obj_path`
                Tree of 2-tuple elements (name, [subelem])
        """
        tree = {}
        node_depth = len(self.get_path_from_ld().split("."))

        for leaf_path, leaf_node in self.get_DA_leaf_nodes().items():
            if fc_filter is None or leaf_node.get_associated_fc() == fc_filter:
                node = tree
                for level in leaf_path.split(".")[node_depth-1:]:
                    node = node.setdefault(level, dict())
        tree_as_tuples = self._recursive_dict_to_tuple(tree)
        return tree_as_tuples[0]

    def _recursive_dict_to_tuple(self, i_dict):
        """
            /!\\ PRIVATE : do not use /!\\

            Recursive reshaping dict tree in list of
            2-tuple: ('name of the node', list of 2-tuple children)

            Parameters
            ----------
            `i_dict` (optional)
                dict to reshape
        """
        return [(k, self._recursive_dict_to_tuple(v)) for k, v in i_dict.items()] if i_dict else []

    def _create_node(self, node_elem: etree.Element, **kwargs):
        """
            /!\\ PRIVATE : do not use /!\\

            Create a SCDNode node from a xml node of the SCD/SCL or from a arguments dictionary

            Parameters
            ----------
            `node_elem` (optional)
                A source etree.Element node

            `kwargs`(optional)
                Arguments dictionnary
        """

        dtype_id = None

        if kwargs.get('bType') != 'Enum':
            dtype_id = kwargs.get('id') or kwargs.get('type') or kwargs.get('lnType')

        if node_elem is not None:
            self._create_from_etree_element(node_elem)
        elif dtype_id:
            dt_node_elem = self._datatypes.get_type_by_id(dtype_id)
            self._create_from_etree_element(dt_node_elem)

        for key, value in kwargs.items():
            setattr(self, key, _safe_convert_value(value))

    def _create_from_etree_element(self, node_elem: etree.Element):
        """
            /!\\ PRIVATE : do not use /!\\

            Create a SCDNode from a etree.Element

            Parameters
            ----------
            `node_elem`
                The etree.Element to compute
        """

        dtype_struct = None
        bType = node_elem.get('bType')
        if bType == 'Struct':
            dtype_struct = node_elem.get('type')

        dtype_id = self._get_dtid_of_elem(node_elem) or dtype_struct

        if not dtype_id:
            self._create_by_node_elem(node_elem)
        else:  # If the node has a datatype id, we create the datatype structure
            dt_node_elem = self._datatypes.get_type_by_id(dtype_id)
            self._create_by_node_elem(dt_node_elem)

    def _is_leaf(self, node) -> bool:
        """
            /!\\ PRIVATE : do not use /!\\

            Check if a SCDNode is leaf

            Parameters
            ----------
            `node`
                The SCDNode to check

            Returns
            -------
            `bool`
                Return True if the node is leaf.
        """

        return len(node.get_children()) == 0 and isinstance(node, DA) and hasattr(node, 'parent')

    def _collect_DA_leaf_nodes(self, node, leaves: dict) -> dict:
        """
            /!\\ PRIVATE : do not use /!\\

            Retrieve DA leaves

            Parameters
            ----------
            `node`
                SCDNode to compute

            `leaves`
                The found leaves dictionnary

            Returns
            -------
            `{int_addr : node}`
                The found leaves dictionnary.
        """
        if node is not None:
            if self._is_leaf(node):
                leaves[node.get_path_from_ld()] = node

            else:
                children = node.get_children()
                for child in children:
                    self._collect_DA_leaf_nodes(child, leaves)

    def _collect_DO_nodes(self, node, do_nodes: dict) -> dict:
        """
            /!\\ PRIVATE : do not use /!\\

            Retrieve DO nodes

            Parameters
            ----------
            `node`
                SCDNode to compute

            `do`
                The found do

            Returns
            -------
            `{int_addr : node}`
                The found leaves dictionnary.
        """
        if node is not None:
            if isinstance(node, DO):
                do_nodes[node.get_path_from_ld()] = node

            else:
                children = node.get_children()
                for child in children:
                    self._collect_DO_nodes(child, do_nodes)

    def get_path_from_ld(self) -> str:
        """
            Get int adr of SCDNode

            Parameters
            ----------
            `node`
                The SCDNode to check

            Returns
            -------
            `str`
                Return the path of the node from LD (format LD.LN.DO.DA)
        """
        assert isinstance(self, (LD, LN, DO, DA)), "Invalid SCDNode level, expect LD, LN, DO or DA"
        path = self.name
        if isinstance(self, LD):
            return path
        if self.parent is None:
            logging.debug(f'SCDNode::get_path_from_ld: parent node of node: {self.name} is None, cannot build path')
            return None
        ancestor = self.parent()
        while ancestor is not None:
            path = ancestor.name + '.' + path
            if ancestor.parent is not None and ancestor.tag != 'LDevice':
                ancestor = ancestor.parent()
            else:
                ancestor = None
        return path

    def get_object_reference(self) -> str:
        """
            Get object reference as defined by IEC61850-8-1, section 8.1.3.2.3

            Returns
            -------
            `str`
                Return the object reference of the node
        """
        assert isinstance(self, (LD, LN, DO, DA, DataSet)), "Invalid SCDNode level, expects LD, LN, DO, DA or DataSet"
        if isinstance(self, LD):
            if hasattr(self, 'ldName'):
                return self.ldName
            else:  # ldName is optional, if absent, use <IEDName><LDInst>
                if self.parent is None:
                    logging.debug(f'SCDNode::_get_object_reference: parent object not found for LD {self.name}')
                    return None
                return self.parent().parent().name + self.name

        else:
            if self.parent is None:
                logging.debug(f'SCDNode::_get_object_reference: parent node not found '
                              f'to build object reference for node with name {self.name}')
                return None
            sep = '/' if isinstance(self.parent(), LD) else '.'
            return self.parent().get_object_reference() + sep + self.name

    def get_GOCB_reference(self) -> str:
        """
            Get GOOSE Control block Reference, with format ldName/lnName$GO$CBName
                NOTE: If a class GSEControl is created, this should belong to it

            Returns
            -------
            `str`
                Return the reference of the GOOSE Control Block
        """
        assert self.tag == 'GSEControl', "Invalid SCDNode, expects tag GSEControl"
        ied = self.get_parent_with_class(IED)
        ld = self.get_parent_with_class(LD)
        ln = self.get_parent_with_class(LN)  # expected is LLN0
        if ied and ld and ln:
            return f'{ied.name}{ld.name}/{ln.name}$GO${self.name}'


    def get_parent_with_class(self, parent_class: type):
        """
            Get parent node with input Class (e.g. IED, LD, LN, DO, DA)

            Returns
            -------
            `SCDNode`
                Return the first node matching request, else None
        """
        p = self
        while True:
            if p.parent is None:
                return None
            p = p.parent()
            if isinstance(p, parent_class):
                return p

    def _create_by_node_elem(self, node: etree.Element):
        """
            /!\\ PRIVATE : do not use /!\\

            Create a SCDNode from a etree.Element

            Parameters
            ----------
            `node`
                The source etree.Element node
        """

        self._set_attributes_from_elem(node)

        # Creation of child nodes
        for elem in node.getchildren():
            self.add_subnode_by_elem(elem)

    def _set_attributes_from_elem(self, node: etree.Element):
        """
            /!\\ PRIVATE : do not use /!\\

            Set the attributes of the SCDNode from a etree.Element

            Parameters
            ----------
            `node`
                The source etree.Element node
        """

        for key, value in node.attrib.items():
            setattr(self, key, _safe_convert_value(value))

        if node.text and len(node.text.strip()) > 0:
            setattr(self, 'Val', _safe_convert_value(node.text))

        self.name = str(self.name)

        if len(self.name) == 0:
            self.name = _get_node_name(node)

    def _get_dtid_of_elem(self, node: etree.Element) -> str:
        """
            /!\\ PRIVATE : do not use /!\\

            Get the datatype id from a etree.Element

            Parameters
            ----------
            `node`
                The etree.Element node

            Returns
            -------
            `str`
                the datatype id found or None if not found
        """

        result = None
        if re.fullmatch(REG_DT_NODE, node.tag) and node.get('bType') != 'Enum':
            result = node.get('id') or node.get('type') or node.get('lnType')
        return result

    def _set_instances(self, elem: etree.Element):
        """
            /!\\ PRIVATE : do not use /!\\

            Manage the instances (DOI, SDI, DAI, ...)

            Parameters
            ----------
            `elem`
                The etree.Element instance node to create
        """

        children = elem.getchildren()

        for elem in children:
            if not elem.get('id'):  # No instances in datatypes
                tag = _get_tag_without_ns(elem.tag)
                if tag == 'Val' and elem.text:
                    setattr(self, 'Val', _safe_convert_value(elem.text))
                elif re.fullmatch(REG_SDI, tag):
                    self._manage_SDI(elem)
                else:
                    self.add_subnode_by_elem(elem)

    def _manage_SDI(self, inst_node: etree.Element, current_node: bool = None):
        """
            /!\\ PRIVATE : do not use /!\\

            Manage the SDI nodes to build the instances

            Parameters
            ----------
            `inst_node`
                The etree.Element instance node to create

            `current_node`
                The current SCDNode parent of the inst_node
        """

        if current_node is None:
            current_node = self

        upd_node = None
        if hasattr(current_node, inst_node.get('name')):
            upd_node = getattr(current_node, inst_node.get('name'))
            if isinstance(upd_node, SCDNode):
                if _get_tag_without_ns(inst_node.tag) == 'DAI':
                    upd_node._set_attributes_from_elem(inst_node)

                upd_node._set_instances(inst_node)


class DA(SCDNode):
    """
        Class to manage a DA / SDA / DAI
    """
    def __init__(self, datatypes: DataTypeTemplates, node_elem: etree.Element = None, fullattrs: bool = False, **kwargs: dict):
        """
            Constructor

            Parameters
            ----------
            `datatypes`
                Instance of the DataTypeTemplates object from the SCD/SCL file.

            `node_elem` (optional)
                etree.Element element from the SCD/SCL file to build the node object.

            `fullattrs` (optional)
                If True, all the possible attributes for the SCD objects will be created
                even if they are not described in the SCD/SCL file.

            `kwargs` (optional)
                Dictionary of the node attributes.

            /!\\ At least one of node_elem or kwargs must be provided /!\\
        """
        self._all_attributes = NODES_ATTRS['DA']
        super().__init__(datatypes, node_elem, fullattrs, **kwargs)

    def get_associated_fc(self):
        """
            Returns the Functional Constraint associated with DA. If absent (SDA case), climb the hierarchy

            Returns
            -------
            `fc`
                Return an the value of the 'fc' field of the DA
        """
        if hasattr(self, "fc"):
            return self.fc
        else:
            if isinstance(self.parent(), DA):
                return self.parent().get_associated_fc()
            else:
                err = f'SCD not valid: No FC found for DA "{self.name}"'
                LOGGER.error(err)
                raise AttributeError(err)

    def get_mms_var_name(self) -> str:
        """
            Get MMS variable name as defined by IEC61850-8-1, section 7.3.4 (including domain name)

            Returns
            -------
            `str`
                Return the MMS variable name of the node
        """
        obj_ref = self.get_object_reference()
        if not obj_ref:
            raise AttributeError('DO::get_mms_var_name: invalid object reference')
        obj_ref_parts = obj_ref.split(".")
        obj_ref_parts.insert(1, self.get_associated_fc())
        return "$".join(obj_ref_parts)


class DO(SCDNode):
    """
        Class to manage a DO / SDO / DOI
    """
    def __init__(self, datatypes: DataTypeTemplates, node_elem: etree.Element = None, fullattrs: bool = False, **kwargs: dict):
        """
            Constructor

            Parameters
            ----------
            `datatypes`
                Instance of the DataTypeTemplates object from the SCD/SCL file.

            `node_elem` (optional)
                etree.Element element from the SCD/SCL file to build the node object.

            `fullattrs` (optional)
                If True, all the possible attributes for the SCD objects will be created
                even if they are not described in the SCD/SCL file.

            `kwargs` (optional)
                Dictionary of the node attributes.

            /!\\ At least one of node_elem or kwargs must be provided /!\\
        """
        self._all_attributes = NODES_ATTRS['DO']
        super().__init__(datatypes, node_elem, fullattrs, **kwargs)

    def get_mms_var_name(self, fc: str) -> str:
        """
            Get MMS variable name as defined by IEC61850-8-1, section 7.3.3 (including domain name)

            Parameter
            -------
            `fc`
                Functional constraint string to include in the variable name

            Returns
            -------
            `str`
                Return the MMS variable name of the node
        """
        obj_ref = self.get_object_reference()
        if not obj_ref:
            raise AttributeError('DO::get_mms_var_name: invalid object reference')
        obj_ref_parts = obj_ref.split(".")
        obj_ref_parts[0] += '$' + fc
        return "$".join(obj_ref_parts)

class LN(SCDNode):
    """
        Class to manage a LN
    """
    def __init__(self, datatypes: DataTypeTemplates, node_elem: etree.Element = None, fullattrs: bool = False, **kwargs: dict):
        """
            Constructor

            Parameters
            ----------
            `datatypes`
                Instance of the DataTypeTemplates object from the SCD/SCL file.

            `node_elem` (optional)
                etree.Element element from the SCD/SCL file to build the node object.

            `fullattrs` (optional)
                If True, all the possible attributes for the SCD objects will be created
                even if they are not described in the SCD/SCL file.

            `kwargs` (optional)
                Dictionary of the node attributes.

            /!\\ At least one of node_elem or kwargs must be provided /!\\
        """
        self._all_attributes = []
        self._all_attributes.extend(NODES_ATTRS['LN'])

        if node_elem is not None:
            kwargs['name'] = _get_node_name(node_elem)
        else:
            lnClass = kwargs.get('lnClass')
            inst = kwargs.get('inst')
            kwargs.update({'name': lnClass + str(inst)})

        super().__init__(datatypes, node_elem, fullattrs, **kwargs)

        # Managing instances
        if self._node_elem is not None:
            self._set_instances(self._node_elem)


class LN0(LN):
    """
        Class to manage a LN0
    """
    def __init__(self, datatypes: DataTypeTemplates, node_elem: etree.Element = None, fullattrs: bool = False, **kwargs: dict):
        """
            Constructor

            Parameters
            ----------
            `datatypes`
                Instance of the DataTypeTemplates object from the SCD/SCL file.

            `node_elem` (optional)
                etree.Element element from the SCD/SCL file to build the node object.

            `fullattrs` (optional)
                If True, all the possible attributes for the SCD objects will be created
                even if they are not described in the SCD/SCL file.

            `kwargs` (optional)
                Dictionary of the node attributes.

            /!\\ At least one of node_elem or kwargs must be provided /!\\
        """
        self._all_attributes = []
        self._all_attributes.extend(NODES_ATTRS['LN0'])
        super().__init__(datatypes, node_elem, fullattrs, **kwargs)


class DataSet(SCDNode):
    """
        Class to manage a DataSet
    """
    _data_tree = None

    def __init__(self, datatypes: DataTypeTemplates, node_elem: etree.Element = None, fullattrs: bool = False, **kwargs: dict):
        """
            Constructor

            Parameters
            ----------
            `datatypes`
                Instance of the DataTypeTemplates object from the SCD/SCL file.

            `node_elem` (optional)
                etree.Element element from the SCD/SCL file to build the node object.

            `fullattrs` (optional)
                If True, all the possible attributes for the SCD objects will be created
                even if they are not described in the SCD/SCL file.

            `kwargs` (optional)
                Dictionary of the node attributes.

            /!\\ At least one of node_elem or kwargs must be provided /!\\
        """
        super().__init__(datatypes, node_elem, fullattrs, **kwargs)
        self._all_attributes = NODES_ATTRS['DataSet']

    def as_tree(self) -> dict:
        """
            Get the DataSet elements as a tree matching the structure of data sent in control blocks
            Root node of Dataset is named 'root', e.g.:
                 ('root', [
                    ('pathuntilSDA1', [
                        ('DA1', []),
                        ('DA2', [
                            ('SDA21', []),
                            ('SDA22', [])
                        ])
                    ]),
                    ('pathuntilSDA2', [
                       ('DA1', []),
                       ('DA2', [])
                    ])
                ])

            Returns
            -------
            `()`
                DataSet element as a tree of DO and DA.
        """
        if self._data_tree is not None:
            return self._data_tree

        self._data_tree = ('root', [])  # tree starting with root, then object ref until node, then subsequent nodes
        ld = self.parent().parent()  # DataSet is located in LD.LLN0

        for fcda in self.FCDA:
            fcda_fc = fcda.fc
            fcda_doName = fcda.doName
            fcda_prefix = fcda.prefix if hasattr(fcda, "prefix") else ""
            fcda_daName = fcda.daName if hasattr(fcda, "daName") else ""
            fcda_lnClass = fcda.lnClass
            fcda_lnInst = "" if fcda_lnClass == "LLN0" else fcda.lnInst
            fcda_ln_full_name = fcda_prefix + fcda_lnClass + str(fcda_lnInst)
            fcda_dataref = f"{ld.name}.{fcda_ln_full_name}.{fcda_doName}{'.' + fcda_daName if fcda_daName else ''}"

            path_to_fcda_node = fcda_dataref.split(".")
            node = ld.get_LN_by_name(fcda_ln_full_name)
            for i in range(1, len(path_to_fcda_node)):
                if hasattr(node, path_to_fcda_node[i]):
                    node = getattr(node, path_to_fcda_node[i])

            self._data_tree[1].append((fcda_dataref, node.get_name_subtree(fc_filter=fcda_fc)[1]))

        return self._data_tree

    def as_list(self) -> list:
        """
            Get the array of DA path present in a dataset

            Returns
            -------
            `[]`
                List of DA in DataSet
        """
        dataset_path_list = self._tree_to_list(self.as_tree())
        return [".".join(da_path[1:]) for da_path in dataset_path_list]  # skip 'root' element

    def get_path_in_dataset(self, da_path: str) -> list:
        """
            Convert a DA path into a list of keys corresponding to tree nodes

            Parameters
            ----------
            `da_path`
                DA path (LD.LN.DO[.SDO].DA[.SDA])

            Returns
            -------
            `[]`
                list of keys to reach DA in Dataset tree
        """
        seq = [path_list for path_list in self._tree_to_list(self.as_tree()) if ".".join(path_list[1:]) == da_path]
        if len(seq) == 0:
            raise AttributeError(f"get_path_in_dataset: DA '{da_path}' not found in DataSet '{self.name}'")
        return seq[0]

    def _tree_to_list(self, n):
        if len(n[1]):
            l = []
            for next_n in n[1]:
                for e in self._tree_to_list(next_n):
                    l.append([n[0]] + e)
            return l
        else:
            return [[n[0]]]


class LD(SCDNode):
    """
        Class to manage a LD
    """
    def __init__(self, datatypes: DataTypeTemplates, node_elem: etree.Element = None, fullattrs: bool = False, **kwargs: dict):
        """
            Constructor

            Parameters
            ----------
            `datatypes`
                Instance of the DataTypeTemplates object from the SCD/SCL file.

            `node_elem` (optional)
                etree.Element element from the SCD/SCL file to build the node object.

            `fullattrs` (optional)
                If True, all the possible attributes for the SCD objects will be created
                even if they are not described in the SCD/SCL file.

            `kwargs` (optional)
                Dictionary of the node attributes.

            /!\\ At least one of node_elem or kwargs must be provided /!\\
        """
        self._all_attributes = []
        self._all_attributes.extend(NODES_ATTRS['LD'])

        if node_elem is not None:
            kwargs['name'] = _get_node_name(node_elem)
        else:
            inst = kwargs.get('inst')
            kwargs.update({'name': inst})
        super().__init__(datatypes, node_elem, fullattrs, **kwargs)

    def get_inputs_extrefs(self, service_type: ServiceType = None) -> list:
        """
            Get the input extRefs list

            Returns
            -------
            `[]`
                An array of objects containing the extRefs attributes
        """
        service_type_str = f'[@serviceType="{service_type.value}"]' if service_type else ''
        XPATH_INPUTS_EXTREFS = f'./iec61850:LN0/iec61850:Inputs/iec61850:ExtRef{service_type_str}'
        extrefs = []

        xpath_result = self._node_elem.xpath(XPATH_INPUTS_EXTREFS, namespaces=NS)

        for item in xpath_result:
            itm = deepcopy(item.attrib)
            extrefs.append(itm)

        return extrefs

    def get_inputs_goose_extrefs(self) -> list:
        """
            Get the GOOSE input extRefs list

            Returns
            -------
            `[]`
                An array of objects containing the GOOSE extRefs attributes
        """
        return self.get_inputs_extrefs(ServiceType.GOOSE)

    def get_datasets(self) -> list:
        """
            Get the GSEControl list

            Returns
            -------
            `[]`
                An array of objects containing the GSEControl attributes
        """
        return self.LLN0.DataSet if hasattr(self.LLN0, "DataSet") else []

    def get_dataset_by_name(self, name: str) -> DataSet:
        """
            Get the DataSet

            Returns
            -------
            `node`
                GSEControl with input name, None if not found
        """
        filtered_dataset = [d for d in self.get_datasets() if d.name == name]
        return filtered_dataset[0] if len(filtered_dataset) == 1 else None

    def get_gsecontrols(self) -> list:
        """
            Get the GSEControl list

            Returns
            -------
            `[]`
                An array of objects containing the GSEControl attributes
        """
        return self.LLN0.GSEControl if hasattr(self.LLN0, "GSEControl") else []

    def get_gsecontrol_by_name(self, name: str) -> SCDNode:
        """
            Get the GSEControl

            Returns
            -------
            `node`
                GSEControl with input name, None if not found
        """
        filtered_gsecontrol = [g for g in self.get_gsecontrols() if g.name == name]
        return filtered_gsecontrol[0] if len(filtered_gsecontrol) == 1 else None

    def get_reportcontrols(self) -> list:
        """
            Get the ReportControl list

            Returns
            -------
            `[]`
                An array of objects containing the ReportControl attributes
        """
        return self.LLN0.ReportControl if hasattr(self.LLN0, "ReportControl") else []

    def get_reportcontrol_by_name(self, name: str) -> SCDNode:
        """
            Get the ReportControl

            Returns
            -------
            `node``
                ReportControl with input name, None if not found
        """
        filtered_reportcontrol = [r for r in self.get_reportcontrols() if r.name == name]
        return filtered_reportcontrol[0] if len(filtered_reportcontrol) == 1 else None

    def get_LN_by_name(self, ln_Name: str) -> LN:
        if hasattr(self, ln_Name):
            return getattr(self, ln_Name)




class IED(SCDNode):
    """
        Class to manage an IED
    """
    DEFAULT_AP = 'PROCESS_AP'

    def __init__(self, datatypes: DataTypeTemplates, node_elem: etree.Element = None, fullattrs: bool = False, **kwargs: dict):
        """
            Constructor

            Parameters
            ----------
            `datatypes`
                Instance of the DataTypeTemplates object from the SCD/SCL file.

            `node_elem` (optional)
                etree.Element element from the SCD/SCL file to build the node object.

            `fullattrs` (optional)
                If True, all the possible attributes for the SCD objects will be created
                even if they are not described in the SCD/SCL file.

            `kwargs` (optional)
                Dictionary of the node attributes.

            /!\\ At least one of node_elem or kwargs must be provided /!\\
        """
        self._all_attributes = []
        self._all_attributes.extend(NODES_ATTRS['IED'])
        self._LDs = {}
        super().__init__(datatypes, node_elem, fullattrs, **kwargs)

    def get_inputs_extrefs(self, service_type: ServiceType = None) -> list:
        """
            Get the input extRefs list

            Returns
            -------
            `[]`
                An array of objects containing the extRefs attributes
        """
        return [e for ld in self.get_children_LDs() for e in ld.get_inputs_extrefs(service_type)]

    def get_inputs_goose_extrefs(self) -> list:
        """
            Get the GOOSE input extRefs list

            Returns
            -------
            `[]`
                An array of objects containing the GOOSE extRefs attributes
        """
        return self.get_inputs_extrefs(ServiceType.GOOSE)

    def get_children_LDs(self, ap_name: str = DEFAULT_AP) -> list:
        ap = self._get_ap_by_name(ap_name)
        if ap:
            return ap.Server.get_children('LDevice')

    def get_LD_by_inst(self, ld_inst: str, ap_name: str = DEFAULT_AP) -> LD:
        if hasattr(self._LDs, ld_inst):
            return self._LDs[ld_inst]

        ap = self._get_ap_by_name(ap_name)
        if ap and hasattr(ap.Server, ld_inst):
            result = getattr(ap.Server, ld_inst)
            self._LDs[ld_inst] = result
            return self._LDs[ld_inst]

    def get_LN_by_name(self, ld_inst: str, ln_Name: str, ap_name: str = DEFAULT_AP) -> LN:
        ld = self.get_LD_by_inst(ld_inst, ap_name)
        ln = ld.get_LN_by_name(ln_Name)
        return ln

    def get_node_by_path(self, data_ref: str, ap_name: str = DEFAULT_AP) -> SCDNode:
        f"""
            Get a SCDNode from its reference

            Parameters
            ----------
            `data_ref`
                reference in the format 'LD.LN.DO[.SDO(s)].DA[.SDA(s)]'

            `ap_name` (optional)
                Access point name (default = {DEFAULT_AP})

            Returns
            -------
            `node`
                SCDNode
        """
        data_path = data_ref.replace("/", ".").split(".")
        node = self
        if len(data_path) > 0 and data_path[0] == self.name:
            data_path.pop(0)  # remove IED name if present
        if len(data_path) > 0:
            node = self.get_LD_by_inst(data_path.pop(0), ap_name)
        if len(data_path) > 0:
            node = node.get_LN_by_name(data_path.pop(0))
        while len(data_path) > 0:
            node = getattr(node, data_path.pop(0))
        if node is None:
            err = f'Could not reach data node with reference {data_ref} in IED {self.name}'
            LOGGER.error(err)
            raise AttributeError(err)
        return node

    def _get_ap_by_name(self, ap_name):
        if hasattr(self, ap_name):
            return getattr(self, ap_name)



class SCD_handler():
    """
        Class to handle a SCD/SCL file
    """
    def __init__(self, scd_path: str, fullattrs: bool = False):
        """
            Constructor of the SCD_handler class

            Parameters
            ----------
            `scd_path`
                The full path of the SCD/SCL file to manage

            `fullattrs` (optional)
                If True, all the possible attributes for the SCD objects will be created
                even if they are not described in the SCD/SCL file.
        """
        self._scl_root = None
        self._scd_path = scd_path
        schema_doc = etree.parse(XSD_PATH)
        self._schema = etree.XMLSchema(schema_doc)
        self._fullattrs = fullattrs
        self._IEDs = {}

        is_valid, error = self._check_scd_file()
        if not is_valid:
            err = 'SCL/SCD not valid at line {}: {}'.format(error.line, error.message)
            LOGGER.error(err)
            raise AttributeError(err)

        self.datatypes = DataTypeTemplates(self._scd_path)
        self.Substation = []
        scl_children = self._get_SCL_elems()
        for elem in scl_children:
            if _get_tag_without_ns(elem.tag) == 'Substation':
                self.Substation.append(SCDNode(self.datatypes, elem, self._fullattrs))
            else:
                elem_name = _get_node_name(elem)
                setattr(self, elem_name, SCDNode(self.datatypes, elem, self._fullattrs))

    def extract_sub_SCD(self, ied_name_list: list) -> str:
        """
            Extract a smaller SCD containing only the IED from the IED_list

            Parameters
            ----------
            `ied_name_list`
                List of the ied names to keep

            Returns
            -------
            `str`
                The full path of the new reduced scd file
        """
        newroot = None
        path, ext = os.path.splitext(self._scd_path)
        dest_path = '{}-reduced{}'.format(path, ext)

        ctx = etree.iterparse(self._scd_path, events=("start",), tag='{}SCL'.format(SCL_NAMESPACE), remove_comments=True)
        for _, root in ctx:
            newroot = etree.Element(root.tag, nsmap=root.nsmap, attrib=root.attrib)
            break

        scl_children = self._get_SCL_elems()
        for child in scl_children:
            newroot.append(deepcopy(child))

        # Clean not needed ConnectedAP
        connected_aps = newroot.xpath('child::iec61850:Communication/*/iec61850:ConnectedAP', namespaces=NS)
        connected_aps = [itm for itm in connected_aps if itm.get('iedName') not in ied_name_list]
        for c_ap in connected_aps:
            c_ap.getparent().remove(c_ap)

        ieds = self._get_IED_elems_by_names(ied_name_list)
        for ied in ieds:
            newroot.append(deepcopy(ied))

        newroot.append(deepcopy(self.datatypes._datatypes_root))

        et = etree.ElementTree(newroot)
        et.write(dest_path, encoding="utf-8", xml_declaration=True)

        return dest_path

    def get_all_IEDs(self) -> list:
        """
            Load all the IEDs from the SCD/SCL file

            Returns
            -------
            `[IED]`
                An array of the loaded IED objects
        """

        ied_names = self.get_IED_names_list()

        tIED = []
        for ied_name in ied_names:
            if ied_name not in self._IEDs.keys():
                self._IEDs[ied_name] = self.get_IED_by_name(ied_name)
            tIED.append(self._IEDs[ied_name])

        return tIED

    def get_IED_by_name(self, ied_name: str) -> IED:
        """
            Load an IED from the SCD/SCL file by name

            Parameters
            ----------
            `ied_name`
                Name of the IED to find

            Returns
            -------
            `IED`
                The loaded IED object
        """
        if ied_name in self._IEDs:
            return self._IEDs[ied_name]

        ied_elems = self._get_IED_elems_by_names([ied_name])
        if len(ied_elems) > 0:
            self._IEDs[ied_name] = IED(self.datatypes, ied_elems[0], self._fullattrs)
            return self._IEDs[ied_name]

    def get_IED_by_type(self, ied_type: str) -> list:
        """
            Load an IED from the SCD/SCL file by type

            Parameters
            ----------
            `ied_type`
                Type of the IED to find

            Returns
            -------
            `IED`
                The loaded IED object
        """

        ied_elems = self._get_IED_elems_by_types([ied_type])
        result = []
        for ied_elem in ied_elems:
            ied_name = ied_elem.get('name')
            if ied_name not in self._IEDs:
                self._IEDs[ied_name] = IED(self.datatypes, ied_elem, self._fullattrs)

            result.append(self._IEDs[ied_name])

        return result

    def get_IED_names_list(self) -> list:
        """
            Load an IED from the SCD/SCL file by name

            Returns
            -------
            `[str]`
                The found IED names
        """
        result = []
        if self._scl_root is not None:
            ieds = self._scl_root.xpath('child::iec61850:IED', namespaces=NS)
            for ied in ieds:
                result.append(ied.get('name'))
        else:
            result = self._iter_get_IED_names_list()

        return result

    def get_IP_Adr(self, ied_name: str):
        """
            Get IP address from GSE for an IED

            Returns
            -------
            `str`
                IP of the IED
        """
        for iComm in self.Communication.get_children('SubNetwork'):  # browse all iED SubNetWork
            if iComm.type != "8-MMS":  # IP can be found only in MMS access point '.
                continue
            for iCnxAP in iComm.get_children('ConnectedAP'):  # browse all Access Point(s) of the iED
                if iCnxAP.iedName == ied_name:  # and iCnxAP.apName == apNAme:
                    for iAdr in iCnxAP.get_children('Address'):

                        for iP in iAdr.P:
                            if iP.type == "IP":  # Look for IP address
                                if iP.Val is not None:
                                    return iP.Val, iCnxAP.apName
            return None, None    # Not found

    def get_GSEs(self, ied_name: str) -> list:
        """
            List the GSE SCDNodes of the IED

            Returns
            -------
            `[]`
                List of GSEs
        """
        for subnet in self.Communication.get_children('SubNetwork'):  # browse all iED SubNetWork
            if subnet.type != "8-MMS":
                continue
            for conn_ap in subnet.get_children('ConnectedAP'):  # browse all Access Point(s) of the iED
                if conn_ap.iedName == ied_name:
                    return conn_ap.GSE if hasattr(conn_ap, "GSE") else []
        return []

    def _check_scd_file(self) -> tuple:
        """
            /!\\ PRIVATE : do not use /!\\

            Check if the input SCD/SCL file is valid.

            If the size of the xml is over MAX_VALIDATION_SIZE,
            the validation is skipped to prevent memory overflow

            Returns
            -------
            `(bool, str)`
                A tuple of boolean and string.
                The boolean is True if the xml is valid
                If the xml is not valid the str is the error message
        """
        file_size = os.path.getsize(self._scd_path) // (1024 * 1024)
        if file_size < MAX_VALIDATION_SIZE:
            tree = etree.parse(self._scd_path, parser=etree.XMLParser(remove_comments=True))
            is_valid = self._schema.validate(tree)
            if not FORCE_ITER_MODE:
                self._scl_root = tree.getroot()
            return (is_valid, self._schema.error_log.last_error)
        else:
            LOGGER.warning('XSD validation skipped due to file size over {} Mo' % MAX_VALIDATION_SIZE)
            return True

    def _get_IED_elems_by_names(self, ied_names_list: list) -> list:
        """
            /!\\ PRIVATE : do not use /!\\

            Retrieve the IED elements by name

            Parameters
            ----------
            `ied_names_list`
                List of ied names to retrieve

            Returns
            -------
            `[etree.Element]`
                Array of found etree.Element elements
        """
        result = []
        if self._scl_root is not None:
            result = self._scl_root.xpath('child::iec61850:IED', namespaces=NS)
            result = [ied for ied in result if ied.get('name') in ied_names_list]
        else:
            result = self._iter_get_IED_elems_by_names(ied_names_list)

        return result

    def _get_IED_elems_by_types(self, ied_types_list: list) -> list:
        """
            /!\\ PRIVATE : do not use /!\\

            Retrieve the IED elements by type

            Parameters
            ----------
            `ied_types_list`
                List of ied types to retrieve

            Returns
            -------
            `[etree.Element]`
                Array of found etree.Element elements
        """
        result = []
        if self._scl_root is not None:
            result = self._scl_root.xpath('child::iec61850:IED', namespaces=NS)
            result = [ied for ied in result if ied.get('type') in ied_types_list]
        else:
            result = self._iter_get_IED_elems_by_types(ied_types_list)

        return result

    def _get_SCL_elems(self) -> list:
        """
            /!\\ PRIVATE : do not use /!\\

            Retrieve the SCL node direct children
            Header, Communication, Substation, Private nodes

            Returns
            -------
            `[etree.Element]`
                Array of found etree.Element elements
        """
        tags = ['Header', 'Communication', 'Substation', 'Private']

        xpath_tags = ''
        for tag in tags:
            xpath_tags = '{} or self::iec61850:{}'.format(xpath_tags, tag)

        xpath_tags = xpath_tags[3:]

        result = []
        if self._scl_root is not None:
            result = self._scl_root.xpath('child::*[{}]'.format(xpath_tags), namespaces=NS)
        else:
            result = self._iter_get_SCL_elems(tags)

        return result

    def _get_all_elem_by_tag(self, tag: str) -> list:
        """
            /!\\ PRIVATE : do not use /!\\

            Retrieve the SCL elements by tag

            Parameters
            ----------
            `tag`
                the elements tag to search

            Returns
            -------
            `[etree.Element]`
                Array of found etree.Element elements
        """
        elem_list = []
        if self._scl_root is not None:
            elem_list = self._scl_root.xpath('iec61850:{}'.format(tag), namespaces=NS)
        else:
            elem_list = self._iter_get_all_elem_by_tag(tag)

        return elem_list

    def _iter_get_all_elem_by_tag(self, tag: str) -> list:
        """
            /!\\ PRIVATE : do not use /!\\

            Retrieve the SCL elements by tag

            Parameters
            ----------
            `tag`
                the elements tag to search

            Returns
            -------
            `[etree.Element]`
                Array of found etree.Element elements
        """
        context = etree.iterparse(self._scd_path, events=("end",), tag='{}{}'.format(SCL_NAMESPACE, tag), remove_comments=True)

        elem_list = []
        _, elem = next(context)
        while elem:
            elem_list.append(elem)
            _, elem = next(context)

        return elem_list

    def _iter_get_SCL_elems(self, tags: list) -> list:
        """
            /!\\ PRIVATE : do not use /!\\

            Retrieve the SCL node direct children
            Header, Communication, Substation, Private nodes

            Parameters
            ----------
            `tags`
                List of tags to consider

            Returns
            -------
            `[etree.Element]`
                Array of found etree.Element elements
        """
        for idx, tag in enumerate(tags):
            tags[idx] = '{}{}'.format(SCL_NAMESPACE, tag)

        context = etree.iterparse(self._scd_path, events=("end",), tag=tags, remove_comments=True)
        result = []
        for _, elem in context:

            if _get_tag_without_ns(elem.tag) != 'Private':
                result.append(elem)
            elif _get_tag_without_ns(elem.tag) == 'Private' and \
                    (elem.xpath('following-sibling::iec61850:Header', namespaces=NS) or
                     elem.xpath('preceding-sibling::iec61850:Header', namespaces=NS)):
                result.append(elem)
            else:
                elem.clear()

        return result

    def _iter_get_IED_elems_by_names(self, ied_names_list: list) -> list:
        """
            /!\\ PRIVATE : do not use /!\\

            Retrieve the IED elements by name

            Parameters
            ----------
            `ied_names_list`
                List of ied names to retrieve

            Returns
            -------
            `[etree.Element]`
                Array of found etree.Element elements
        """
        context = etree.iterparse(self._scd_path, events=("end",), tag='{}IED'.format(SCL_NAMESPACE), remove_comments=True)
        result = []
        for _, ied in context:
            item_name = ied.get('name')
            if item_name in ied_names_list:
                result.append(ied)
            else:
                ied.clear()

        return result

    def _iter_get_IED_elems_by_types(self, ied_types_list: list) -> list:
        """
            /!\\ PRIVATE : do not use /!\\

            Retrieve the IED elements by type

            Parameters
            ----------
            `ied_types_list`
                List of ied types to retrieve

            Returns
            -------
            `[etree.Element]`
                Array of found etree.Element elements
        """
        context = etree.iterparse(self._scd_path, events=("end",), tag='{}IED'.format(SCL_NAMESPACE), remove_comments=True)
        result = []
        for _, ied in context:
            item_type = ied.get('type')
            if item_type in ied_types_list:
                result.append(ied)
            else:
                ied.clear()

        return result

    def _iter_get_IED_names_list(self) -> list:
        """
            Load an IED from the SCD/SCL file by name

            Returns
            -------
            `[str]`
                The found IED names
        """
        result = []
        context = etree.iterparse(self._scd_path, events=("end",), tag='{}IED'.format(SCL_NAMESPACE), remove_comments=True)
        for _, ied in context:
            result.append(ied.get('name'))
            ied.clear()

        return result

