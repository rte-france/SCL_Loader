#
# Code Sample for 'XXX' private tag
#
# This is not an open source file
#

# Implementation of XXX PrivateClass:

# IEC_RTE_Private.py for examples

from IEC_Trace  import Trace
from IEC_Trace  import Level as TL

##
# \b Private_XXX:
# @brief
#   Template to implement Private TAG for company 'XXX'
#
#   The function from this class are called after loading 'dynamically' the class.
class Private_XXX:
    ##
    # \b XXX_Private:
    #
    #  @param   _type        - the type of the private: '[Private type="RTE-BAP" ]'
    #  @param   _pSCL        - the pointer to the SCL, where the tag was found
    #  @param   _pDataModel  - the pointer to the global model, where the data related to the private tag can be stored typically by dynamically creating data in it.
    def __init__(self, _type, _pSCL, _pDataModel):
        ## type  - the private TAG
        self.type        = _type
        ## pSCL - the pointer to the SCL, where the tag was found
        self.pSCL        = _pSCL
        ## pDataModel - the pointer to the data model
        self.pDataModel  = _pDataModel
        ## TR - the initialized trace service.
        self.TR          = Trace.Console(TL.GENERAL)

    ##
    # \b XXX_Generic
    #
    # This method is invoked for generic tags 'XXX-' (Based on a pattern specific to a given manufacturer...
    #
    #  @param   type         - the type of the private: [Private type="RTE-BAP"]
    #  @param   pSCL        - the pointer to the SCL, where the tag was found
    #  @param   pDataModel  - the pointer to the global model, where the data related to the private tag can be stored typically by dynamically creating data in it.
    def XXX_Generic(self, type, pSCL, pDataModel):
        self.TR(("XXX Generic", type),TL.GENERAL)

    ##
    # \b XXX_Generic
    #
    # This method is invoked for a specific private TAG 'myTag_Specific'.
    #
    #  @param   type       - the type of the private: [Private type="RTE-BAP"]
    #  @param   pSCL        - the pointer to the SCL, where the tag was found
    #  @param   pDataModel  - the pointer to the global model, where the data related to the private tag can be stored typically by dynamically creating data in it.
    def myTag_Specific(self, type, pSCL, pDataModel):
        self.TR(("myTag_Specific", type),TL.GENERAL)
