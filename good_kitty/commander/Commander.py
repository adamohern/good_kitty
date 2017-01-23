import lx, lxu, traceback
from lxifc import UIValueHints, Visitor
from operator import ior

ARG_NAME = 'name'
ARG_LABEL = 'label'
ARG_VALUE = 'default'
ARG_DATATYPE = 'datatype'
ARG_FLAGS = 'flags'

ARG_VALUES_LIST_TYPE = 'values_list_type'
ARG_VALUES_LIST = 'values_list'
LIST_TYPE_sPresetText = 'sPresetText'
LIST_TYPE_POPUP = 'popup'
LIST_TYPE_FCL = 'fcl'

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

sTYPE_STRINGs = [
        'date',
        'datetime',
        'filepath',
        'string',
        'vertmapname'
    ]

sTYPE_STRING_vectors = [
        'angle3',
        'color',
        'float3',
        'percent3'
    ]

sTYPE_INTEGERs = [
        'integer'
    ]

sTYPE_BOOLEANs = [
        'boolean'
    ]


class CommanderClass(lxu.command.BasicCommand):
    _commander_default_values = []

    def __init__(self):
        lxu.command.BasicCommand.__init__(self)

        for n, argument in enumerate(self.commander_arguments()):

            if not argument.get(ARG_DATATYPE):
                return lx.symbol.e_FAILED

            if not argument.get(ARG_NAME):
                return lx.symbol.e_FAILED

            datatype = getattr(lx.symbol, 'sTYPE_' + argument[ARG_DATATYPE].upper())
            if not datatype:
                return lx.symbol.e_FAILED

            self.dyna_Add(argument[ARG_NAME], datatype)
            self._commander_default_values.append(argument.get(ARG_VALUE))

            flags = []
            for flag in argument.get(ARG_FLAGS, []):
                flags.append(getattr(lx.symbol, 'fCMDARG_' + flag.upper()))
            if flags:
                self.basic_SetFlags(n, reduce(ior, flags))

        self.not_svc = lx.service.NotifySys()

        self.notifiers = []
        self.notifier_tuples = tuple([i for i in self.commander_notifiers()])
        for i in self.notifier_tuples:
            self.notifiers.append(None)

    def commander_arguments(self):
        return []

    def commander_notifiers(self):
        return []

    def commander_arg_value(self, index, default=None):
        if not self.dyna_IsSet(index):
            return default

        if self.commander_arguments()[index][ARG_DATATYPE].lower() in sTYPE_STRINGs:
            return self.dyna_String(index)

        elif self.commander_arguments()[index][ARG_DATATYPE].lower() in sTYPE_STRING_vectors:
            return [float(i) for i in self.dyna_String(index).split(" ")]

        elif self.commander_arguments()[index][ARG_DATATYPE].lower() in sTYPE_INTEGERs:
            return self.dyna_Int(index)

        elif self.commander_arguments()[index][ARG_DATATYPE].lower in sTYPE_FLOATs:
            return self.dyna_Float(index)

        elif self.commander_arguments()[index][ARG_DATATYPE].lower() in sTYPE_BOOLEANs:
            return self.dyna_Bool(index)

        return default

    def commander_args(self):
        args = {}
        for i in range(len(self.commander_arguments())):
            name = self.commander_arguments()[i][ARG_NAME]
            value = self.commander_arg_value(i)
            args[name] = value
        return args

    def cmd_NotifyAddClient(self, argument, object):
        for i, tup in enumerate(self.notifier_tuples):
            if self.notifiers[i] is None:
                self.notifiers[i] = self.not_svc.Spawn (self.notifier_tuples[i][0], self.notifier_tuples[i][1])

            self.notifiers[i].AddClient(object)

    def cmd_NotifyRemoveClient(self, object):
        for i, tup in enumerate(self.notifier_tuples):
            if self.notifiers[i] is not None:
                self.notifiers[i].RemoveClient(object)

    def cmd_Flags(self):
        return lx.symbol.fCMD_POSTCMD | lx.symbol.fCMD_MODEL | lx.symbol.fCMD_UNDO

    def arg_UIHints(self, index, hints):
        args = self.commander_arguments()
        if index < len(args):
            label = args[index].get(ARG_LABEL)

            if not label:
                label = args[index].get(ARG_NAME)

            elif hasattr(label, '__call__'):
                label = label()

            hints.Label(label)

            if args[index].get(ARG_VALUES_LIST_TYPE) == LIST_TYPE_sPresetText:
                hints.Class("sPresetText")

    def arg_UIValueHints(self, index):
        args = self.commander_arguments()
        if index < len(args):
            arg = args[index]
            arg_data = None

            if arg.get(ARG_VALUES_LIST) is not None:
                arg_data = arg.get(ARG_VALUES_LIST)

            if not arg_data:
                return

            if isinstance(arg_data, (list, tuple)):
                values = arg_data
            elif hasattr(arg_data, '__call__'):
                values = arg_data()
            elif issubclass(arg_data, UIValueHints):
                return arg_data()

            if not values:
                values = []

            if args[index].get(ARG_VALUES_LIST_TYPE) == LIST_TYPE_POPUP:
                return PopupClass(values)

            elif args[index].get(ARG_VALUES_LIST_TYPE) == LIST_TYPE_sPresetText:
                return PopupClass(values)

            elif args[index].get(ARG_VALUES_LIST_TYPE) == LIST_TYPE_FCL:
                return FormCommandListClass(values)

    def cmd_DialogInit(self):
        for n, argument in enumerate(self.commander_arguments()):

            if self.dyna_IsSet(n) and self.dyna_String(n):
                continue

            if self.commander_arguments()[n].get(ARG_VALUE) == None:
                continue

            datatype = argument.get(ARG_DATATYPE, '').lower()
            default_value = self._commander_default_values[n]

            if datatype in sTYPE_STRINGs:
                self.attr_SetString(n, str(default_value))

            elif datatype in sTYPE_STRING_vectors:
                self.attr_SetString(n, str(default_value))

            elif datatype in sTYPE_INTEGERs:
                self.attr_SetInt(n, int(default_value))

            elif datatype in sTYPE_BOOLEANs:
                self.attr_SetInt(n, int(default_value))

            elif datatype in sTYPE_FLOATs:
                self.attr_SetFlt(n, float(default_value))

    def commander_execute(self, msg, flags):
        pass

    def basic_Execute(self, msg, flags):
        for n, argument in enumerate(self.commander_arguments()):
            self._commander_default_values[n] = self.commander_arg_value(n)

        try:
            self.commander_execute(msg, flags)
        except:
            lx.out(traceback.format_exc())

    def cmd_Query(self,index,vaQuery):
        va = lx.object.ValueArray()
        va.set(vaQuery)

        args = self.commander_arguments()

        if index < len(args):
            is_query = 'query' in args[index].get(ARG_FLAGS, [])
            is_not_fcl = args[index].get(ARG_VALUES_LIST_TYPE) != LIST_TYPE_FCL
            has_recent_value = self._commander_default_values[index]

            if is_query and is_not_fcl and has_recent_value:
                va.AddString(has_recent_value)

        return lx.result.OK

class FormCommandListClass(UIValueHints):
    def __init__(self, items):
        self._items = items

    def uiv_Flags(self):
        return lx.symbol.fVALHINT_FORM_COMMAND_LIST

    def uiv_FormCommandListCount(self):
        return len(self._items)

    def uiv_FormCommandListByIndex(self,index):
        return self._items[index]

class PopupClass(UIValueHints):
    def __init__(self, items):
        if not items or not isinstance(items, (list, tuple)):
            self._user = []
            self._internal = []

        elif isinstance(items[0], (list, tuple)):
            self._user = [str(i[1]) for i in items]
            self._internal = [str(i[0]) for i in items]

        else:
            self._user = [str(i) for i in items]
            self._internal = [str(i) for i in items]

    def uiv_Flags(self):
        return lx.symbol.fVALHINT_POPUPS

    def uiv_PopCount(self):
        return len(self._internal)

    def uiv_PopUserName(self,index):
        return self._user[index]

    def uiv_PopInternalName(self,index):
        return self._internal[index]
