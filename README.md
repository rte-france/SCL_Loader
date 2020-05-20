# SCL_Loader

The SCL loader software parse and load in memory IEC61850 SCL files (system and/ied levem)

Basically all IEC61850 classes from a SCL files (SCD, ICD, CID, IID) are mapped into 
Python Class, with table of classes when needed.

There is a generic way to deal with Private class, hence private can be dealt with and still remains
private (based on dynamic class loading).

Most likely there are still some issues depending on the complexity of the SCL.
It has been tested with several files, but those cannot be published, if anyone reading this can share SCL files to help the validation...

This is still at an early stage. The current actual "application" is to automtically generate:
- Table of all MMS adresses data object,including the expected value (from date type definition, and from DAI / DAI /SDI...)
- Generate scripts to verify that a given IED has actually correctly loaded the initial value.

Most of python modules can be launched individually.

Nearly of the python modules are now documented with 'doxygen' comments. The 'Doxygen_folders.7z' should be extracted and then the documentation is accessible at ./html/index.html at least IEC61850 part should be interesting.

There are more information in the README in WORD format






