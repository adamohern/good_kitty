# Python

NAME = 'name'
LABEL = 'label'
VALUE = 'default'
DATATYPE = 'datatype'
FLAGS = 'flags'

VALUES_LIST_TYPE = 'values_list_type'
VALUES_LIST = 'values_list'
sPresetText = 'sPresetText'
POPUP = 'popup'
FCL = 'fcl'

# These datatypes will be treated as Float values
sTYPE_FLOATs = [
        'acceleration',
        'angle',
        'axis',
        'color1',
        'float',
        'force',
        'light',
        'mass',
        'percent',
        'speed',
        'time',
        'uvcoord'
    ]

# Treated as Str values
sTYPE_STRINGs = [
        'date',
        'datetime',
        'filepath',
        'string',
        'vertmapname'
    ]

# Treated as Str values in the MODO UI,
# but parsed into [Float, Float, Float] for use in the commander_execute()
sTYPE_STRING_vectors = [
        'angle3',
        'color',
        'float3',
        'percent3'
    ]

# Treated as Int values
sTYPE_INTEGERs = [
        'integer'
    ]

# Treated as Bool values
sTYPE_BOOLEANs = [
        'boolean'
    ]

DATATYPES = sTYPE_FLOATs + sTYPE_STRINGs + sTYPE_STRING_vectors + sTYPE_INTEGERs + sTYPE_BOOLEANs
