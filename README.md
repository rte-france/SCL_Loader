# SCL_Loader

The SCL loader software parse and load in memory IEC61850 SCL files (system and/ied levem)

Basically all IEC61850 classes from a SCL files (SCD, ICD, CID, IID) are mapped into 
Python Class, with table of classes when needed.

There is a generic way to deal with Private class, hence private can be dealt with and still remains
private (based on dynamic class loading).

Most likely there are still some issues depending on complex the SCL.
It has been tested with several files, but those cannot be published.

This is still at an early stage. The current actual "application" is to automtically generate:
- Table of all MMS adresses data object,including the expected value (from date type definition, and from DAI / DAI /SDI...)
- Generate scripts to verify that a given IED has actually correctly loaded the initial value.







