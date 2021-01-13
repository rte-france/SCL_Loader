#!/usr/bin/env python3
# Copyright RTE - 2020

import os
import logging
import re
import weakref
from lxml import etree

HERE = os.path.abspath(os.path.dirname(__file__))
XSD_PATH = os.path.join(HERE, 'resources', 'SCL_Schema', 'SCL.xsd')
LOGGER = logging.getLogger(__name__)
NS = {'rte': 'http://www.rte-france.com', 'iec61850': 'http://www.iec.ch/61850/2003/SCL'}
SCL_NAMESPACE = r'{http://www.iec.ch/61850/2003/SCL}'
MAX_VALIDATION_SIZE = 500  # taille en Mo
REG_DA = r'(?:\{.+\})?[BS]?DA'
REG_DO = r'(?:\{.+\})?S?DO'
REG_SDI = r'(?:\{.+\})?S?D[OA]?I'
REG_ARRAY_TAGS = r'(?:\{.+\})?(?:FCDA|ClientLN|IEDName|FIP|BAP|ExtRef|Terminal|P)'  # |Server)'
REG_DT_NODE = r'(?:.*\})?((?:[BS]?D[AO])|(?:LN0?))'
REF_SCL_NODES = r'(?:\{.+\})?(?:Header|Substation|Private|Communication)'
SEP1 = '$'          # Standard MMS separator.
SEP2 = '/'          # MMS Separator for system testing

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
}


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


def _get_node_name(node: etree.Element):
    name = None
    tag = node.tag.split('}')[-1]

    name = node.get('name')
    if not name:
        if tag in ['LN', 'LN0']:
            lnClass = node.get('lnClass')
            inst = node.get('inst')
            name = lnClass + str(inst)
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
        context = etree.iterparse(xml_path, events=("end",), tag='{}DataTypeTemplates'.format(SCL_NAMESPACE))
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
        tags = {'LNodeType':[], 'DOType':[], 'DAType':[], 'EnumType':[]}

        for tag_key in tags.keys():
            item_xpath = 'child::iec61850:{}'.format(tag_key)
            tags[tag_key] = self._datatypes_root.xpath(item_xpath, namespaces=NS)

        return tags


# TODO :
# - Manage BAP/FIP
# - Gestion des attributs dont le nom comporte des . ou des -
# - Gestion des noeud étranges (voir SCD de Gilles)
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
            self.tag = node_elem.tag.split('}')[-1]

        if node_elem is None and not kwargs:
            msg = 'Please enter a xml Element and/or attributes (kwargs)'
            LOGGER.error(msg)
            raise AttributeError(msg)

        self._create_node(node_elem, **kwargs)

        self.name = self.name or self.tag

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
        _tag = elem.tag.split('}')[-1]

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
        elif elem.tag.split('}')[-1] == 'LN':
            new_node = LN(self._datatypes, elem, self._fullattrs, **attributes)
        elif elem.tag.split('}')[-1] == 'LN0':
            new_node = LN0(self._datatypes, elem, self._fullattrs, **attributes)
        elif elem.tag.split('}')[-1] == 'LDevice':
            new_node = LD(self._datatypes, elem, self._fullattrs, **attributes)
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
                Return an dictionnary of found children SCDNodes : array[IntAdr] = SCDNode
                (IntAdr is the path build with the names of the ancestors starting at the SCDNode)
        """

        leaves = {}
        mms = False
        if self.tag in ['IED', 'LN', 'LN0', 'LDevice']:
            mms = True
        self._collect_DA_leaf_nodes(self, leaves, mms)
        return leaves

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
        for _, item in self.__dict__.items():
            if isinstance(item, SCDNode):
                if tag is None:
                    results.append(item)
                elif item.tag == tag:
                    results.append(item)
        return results

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

    def _collect_DA_leaf_nodes(self, node, leaves: dict, mms: bool = False) -> dict:
        """
            /!\\ PRIVATE : do not use /!\\

            Retrieve DA leaves

            Parameters
            ----------
            `node`
                SCDNode to compute

            `leaves`
                The found leaves dictionnary

            `mms`
                If True, compute the mms and u_mms adresses

            Returns
            -------
            `{IntAdr : node}`
                The found leaves dictionnary.
        """
        if node is not None:
            if self._is_leaf(node):
                ancestor = node.parent()
                IntAdr = node.name
                while ancestor is not None:
                    IntAdr = ancestor.name + '.' + IntAdr
                    if ancestor.parent is not None and ancestor.tag != 'LDevice':
                        ancestor = ancestor.parent()
                    else:
                        ancestor = None

                mmsAdr = ''
                u_mmsAdr = ''

                if mms:  # mms adresses ok only if the root is a LD
                    for item in IntAdr.split('.'):
                        mmsAdr += SEP1 + item
                        u_mmsAdr += SEP2 + item
                    setattr(node, 'mmsAdr', mmsAdr[1:])
                    setattr(node, 'u_mmsAdr', u_mmsAdr[1:])

                setattr(node, 'IntAdr', IntAdr)
                leaves[IntAdr] = node
            else:
                children = node.get_children()
                for child in children:
                    self._collect_DA_leaf_nodes(child, leaves, mms)

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
                tag = elem.tag.split('}')[-1]
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
                if inst_node.tag.split('}')[-1] == 'DAI':
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


class IED(SCDNode):
    """
        Class to manage an IED
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
        self._all_attributes.extend(NODES_ATTRS['IED'])
        super().__init__(datatypes, node_elem, fullattrs, **kwargs)


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
        self._scd_path = scd_path
        schema_doc = etree.parse(XSD_PATH)
        self._schema = etree.XMLSchema(schema_doc)
        self._fullattrs = fullattrs

        is_valid, error = self._check_scd_file()
        if not is_valid:
            err = 'SCL/SCD not valid at line {}: {}'.format(error.line, error.message)
            LOGGER.error(err)
            raise AttributeError(err)

        self.datatypes = DataTypeTemplates(self._scd_path)
        self.Substation = []
        scl_children = self._iter_get_SCL_elems()
        for elem in scl_children:
            if elem.tag.split('}')[-1] == 'Substation':
                self.Substation.append(SCDNode(self.datatypes, elem, self._fullattrs))
            else:
                elem_name = _get_node_name(elem)
                setattr(self, elem_name, SCDNode(self.datatypes, elem, self._fullattrs))

    def get_all_IEDs(self) -> list:
        """
            Load all the IEDs from the SCD/SCL file

            Returns
            -------
            `[IED]`
                An array of the loaded IED objects
        """
        context = etree.iterparse(self._scd_path, events=("end",), tag='{}IED'.format(SCL_NAMESPACE))
        tIED = []
        for _, ied in context:
            tIED.append(IED(self.datatypes, ied, self._fullattrs))

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
        context = etree.iterparse(self._scd_path, events=("end",), tag='{}IED'.format(SCL_NAMESPACE))
        for _, ied in context:
            item_name = ied.get('name')
            if item_name == ied_name:
                return IED(self.datatypes, ied, self._fullattrs)
            else:
                ied.clear()

    def get_IED_names_list(self) -> list:
        """
            Load an IED from the SCD/SCL file by name

            Returns
            -------
            `[str]`
                The found IED names
        """
        result = []
        context = etree.iterparse(self._scd_path, events=("end",), tag='{}IED'.format(SCL_NAMESPACE))
        for _, ied in context:
            result.append(ied.get('name'))
            ied.clear()

        return result

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
        file_size = os.path.getsize(self._scd_path) // (1024*1024)
        if file_size < MAX_VALIDATION_SIZE:
            tree = etree.parse(self._scd_path)
            is_valid = self._schema.validate(tree)
            tree = None
            return (is_valid, self._schema.error_log.last_error)
        else:
            LOGGER.warn('XSD validation skipped due to file size over {} Mo' % MAX_VALIDATION_SIZE)
            return True

    def _iter_get_SCL_elems(self) -> list:
        """
            /!\\ PRIVATE : do not use /!\\

            Retrieve the SCL node direct children
            Header, Communication, Substation, Private nodes

            Returns
            -------
            `[etree.Element]`
                Array of found etree.Element elements
        """
        tags = [
            '{}Header'.format(SCL_NAMESPACE),
            '{}Communication'.format(SCL_NAMESPACE),
            '{}Substation'.format(SCL_NAMESPACE),
            '{}Private'.format(SCL_NAMESPACE)
        ]
        context = etree.iterparse(self._scd_path, events=("end",), tag=tags)
        result = []
        for _, elem in context:

            if elem.tag.split('}')[-1] != 'Private':
                result.append(elem)
            elif elem.tag.split('}')[-1] == 'Private' \
                                            and (elem.xpath('following-sibling::iec61850:Header', namespaces=NS)
                                            or elem.xpath('preceding-sibling::iec61850:Header', namespaces=NS)):
                result.append(elem)
            else:
                elem.clear()

        return result

    def _iter_get_all_elem_by_tag(self, tag:str) -> list:
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
        context = etree.iterparse(self._scd_path, events=("end",), tag='{}{}'.format(SCL_NAMESPACE, tag))

        elem_list = []
        _, elem = next(context)
        while elem:
            elem_list.append(elem)
            _, elem = next(context)

        return elem_list
