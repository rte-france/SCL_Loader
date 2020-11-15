

class IEC:
    def __init__(self):

        self.IEC = dict()
        self.IEC["SubStation"]          = ("name", "desc")
        self.IEC["EquipmentContainer"]  = ('name', 'desc')
        self.IEC["VoltageLevel"]        = ('name', 'desc')
        self.IEC["Voltage"]             = ('unit', 'multiplier', 'value')
        self.IEC["PowerTransformer"]    = ('name', 'desc', 'type', 'virtual')
        self.IEC["Function"]            = ("name", "desc")
        self.IEC["ConductingEquipment"] = ("name", "desc", "virtual", "sx_y", "sx_x", "sx_dir")
        self.IEC["LNode"]               = ("lnInst","lnClass","iedName","ldInst","prefix","lnType")
        self.IEC["Bay"]                 = ("name", "desc", "sxy_x", "sxy_y")
        self.IEC["SubEquipement"]       = ("name", "desc", "phase", "virtual")
        self.IEC["Terminal"]            = ("name", "desc", "conNode", "subName", "vName", "bayName", "cNodeName","lineName", "neutralPoint")
        self.IEC["ConnectivityNode"]    = ("name", "desc", "pathName", "sx_y", "sx_x")
        self.IEC["GeneralEquipment"]    = ("name", "type", "use")
        self.IEC["Communication"]       = ("SubNetwork")
        self.IEC["SubNetwork"]          = ("name", "type", "desc", "text", "bitRate", "ConnectedAP")
        self.IEC["BitRate"]             = ("unit", "value")
        self.IEC["ConnectedAP"]         = ("iedName", "apName", "desc", "redProt")
        self.IEC["GSE"]                 = ("ldInst", "cbName", "desc")
        self.IEC["MinTime"]             = ("unit", "min", "mul")
        self.IEC["MaxTime"]             = ("unit", "max", "mul")
        self.IEC["SMV"]                 = ("ldInst","cbName", "desc")
        self.IEC["PhysConn"]            = ("type", "PhysAddress")
        self.IEC["PType"]               = ("type", "value")
        self.IEC["IED"]                 = ("name", "desc", "type", "originalSclVersion", "originalSclRevision", "configVersion", "manufacturer",
                                           "engRight", "owner")
        self.IEC["AccessPoint"]         = ("name", "desc", "router", "clock")
        self.IEC["Server"]              = ("desc", "timeout")
        self.IEC["Authentication"]      = ("none", "password", "weak", "strong", "certificate")
        self.IEC["LDevice"]             = ("inst", "ldName", "desc")
        self.IEC["LN"]                  = ("prefix", "lnType", "inst", "lnClass", "desc")
        self.IEC["LogControl"]          = ("name", "desc", "datSet", "intgPd", "ldInst", "logName","prefix","lnClass","lnInst", "logEna", "reasonCode")
        self.IEC["ReportControl"]       = ("name","desc","datSet","intgPd", "rptID","confRev","buffered","bufTime","indexed")
        self.IEC["OptFields"]           = ("seqNum","timeStamp","dataSet","reasonCode","dataRef","entryID","configRef","bufOvfl")
        self.IEC["RptEnabled"]          = ("max")
        self.IEC["ClientLN"]            = ("iedName", "ldInst", "lnPrefix", "lnClass", "lnInst", "desc", "apRef")
        self.IEC["TrgOps"]              = ("qchg", "dchg", "dupd", "period", "gi ")
        self.IEC["Inputs"]              = ("tRef")
        self.IEC["ExtRef"]              = ("iedName", "ldInst", "prefix", "lnClass", "lnInst", "doName", "daName", "intAddr", "desc", "service", \
                                           "srcLDInst", "srcPrefix", "srcLNClass", "srcLNInst", "srcCBName", "pDO", "pLN", "_pDA", "pServT")
        self.IEC["SampledValueControl"] = ("name", "desc", "datSet", "confRev", "smvID", "multicast", "smpRate", "nofASDU",  "smpMod", "securityEnabled")
        self.IEC["IEDSVCSub"]           = ("apRef", "ldInst", "lnClass", "iedName")
        self.IEC["smvOption"]           = ("refreshTime","sampleSynchronized", "sampleRate", "dataSet", "security", "synchSourceId","timeStamp")
        self.IEC["SettingControlBlock"] = ("desc", "numOfSGs", "actSG", "resvTms")
        self.IEC["GSEControl"]          = ("name","desc","datSet","confRev","type","appID","fixedOffs","securityEnabled")
        self.IEC["IEDGSESub"]           = ("apRef", "ldInst", "lnClass", "iedName")
        self.IEC["DOI"]                 = ("name", "type", "accessControl", "transient", "ix", "desc")
        self.IEC["DAI"]                 = ("desc","name","fc","bType","type","count","valKind","valImp","value") #,"do"sdo")
        self.IEC["SDI"]                 = ("desc", "name", "ix","sAddr ")  # ", "tSDI")
        self.IEC["IEC_90_2"]            = ("externalScl","iedName", "ldInst", "prefix","lnClass","lnInst","doName")
        self.IEC["IEC104"]              = ("casdu", "ioa", "ti", "usedBy", "inverted")
        self.IEC["DataSet"]             = ( "name", "desc")
        self.IEC["FCDA"]                = ("ldInst","prefix","lnClass","lnInst","doName","daName","fc","ix")
        self.IEC["DataTypeTemplates"]   = ("")
        self.IEC["LNodeType"]           = ("id", "desc", "iedType", "lnClass", "tDO")
        self.IEC["DOType"]              = ("id", "iedType", "cdc", "desc", "tDA")
        self.IEC["DAType"]              = ("id", "desc", "protNs", "iedType")
        self.IEC["BDA"]                 = ("name", "type", "bType", "valKind", "value")
        self.IEC["ProtNs"]              = ("type")
        self.IEC["EnumType"]            = ("id", "desc")
        self.IEC["EnumVal"]             = ("ord", "strValue", "desc")
#
# The following  ones are 'useful', but are not directly related to the SCL
#

        self.IEC["FC"]                  = ('ST', 'MX', 'CF', 'DC', 'SP', 'SV', 'SG', 'SE', 'SR', 'OR', 'BL', 'EX', 'CO')
## 'Enum' need to be treated as specific type.
# 'Struct' need to be treated as specific type.
        self.IEC["bType"]               = ("BOOLEAN", "INT8"   ,"INT16" ,"INT24" , "INT32" , "INT64", "INT8U","INT16U","INT24U", "INT32U", \
                                           "FLOAT32", "FLOAT64","Dbpos" , "Tcmd", "Quality", "Timestamp",
                                           "VisString32","VisString64", "VisString65", "VisString129","VisString255","Unicode255",
                                           "Octet64", "EntryTime", "Check"  , "ObjRef",
                                           "Currency",
                                           "PhyComAddr", "TrgOps", "OptFlds", "SvOptFlds","LogOptFlds",
                                           "EntryID",
                                           "Octet6", "Octet16")          # Edition 2.1
        self.IEC["String"]              = ("BOOLEAN","VisString64","VisString129","VisString255","Unicode255","ObjRef", "Quality", "Timestamp","Tcmd")
        self.IEC["Number"]              = ("Check", "INT8U","INT16U","INT32U","INT8","INT16","INT32","INT64","FLOAT32","Octet64")
        self.IEC["Quality"]             = ("Validity", "Overflow", "OutofRange", "BadReference", "Oscillatory",
                                           "Failure",  "OldData", "Inconsistent", "Inaccurate", "Source", "Test" "OperatorBlocked")
        self.IEC["TimeQuality"]         = ("Leap", "Failure", "NotSync" "Precision")

        self.IEC["Timestamp"]           = (("SecondSinceEpoch","FractionOfSecond","TimeQuality"))
        self.IEC["PhyComAddr"]          = ("Addr", "PRIORITY", "VID", "APPID")
        self.IEC["GooseMessage"]        = ("DatSetRef", "GoID", "GoCBRef", "T", "StNum", "SqNum" ,"Simulation", "ConfRev", "NdsComn", "DatSet", "mode")


if __name__ == '__main__':

        iecDict = IEC()

        for entry in iecDict.IEC:
            print(entry + ': ' , end='')
            items = iecDict.IEC[entry]
            for x in items:
                print(x + ', ',end='')
            print('#')






