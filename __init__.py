# python

""" Allows you to write typical MODO commands with much less boilerplate,
less redundant code, and fewer common mistakes. The following is a
blessed modo command using Commander:

class CommandClass(tagger.Commander):
    _commander_last_used = []

    def commander_arguments(self):
        return [
                {
                    'name': 'myGreatString',
                    'label': 'Input String Here',
                    'datatype': 'string',
                    'value': "default string goes here",
                    'popup': function_that_returns_list_of_possible_strings(),
                    'flags': [],
                    'sPresetText': True
                }, {
                    'name': 'greeting',
                    'datatype': 'string',
                    'value': 'hello',
                    'popup': ['hello', 'greetings', 'how ya doin\'?'],
                    'flags': ['optional']
                }
            ]

    def commander_execute(self, msg, flags):
        myGreatString = self.commander_arg_value(0)
        greeting = self.commander_arg_value(1)

        lx.out("%s, %s" (greeting, myGreatString))
"""

__version__ = "0.13"
__author__ = "Adam"

import lx, lxu, traceback
from lxifc import UIValueHints
from operator import ior

ARG_NAME = 'name'
ARG_LABEL = 'label'
ARG_VALUE = 'value'
ARG_DATATYPE = 'datatype'
ARG_POPUP = 'popup'
ARG_FCL = 'fcl'
ARG_FLAGS = 'flags'
ARG_sPresetText = 'sPresetText'

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


class Commander(lxu.command.BasicCommand):
    _commander_last_used = []

    def __init__(self):
        lxu.command.BasicCommand.__init__(self)

        for n, argument in enumerate(self.commander_arguments()):
            if ARG_DATATYPE not in argument or ARG_NAME not in argument:
                continue

            datatype = getattr(lx.symbol, 'sTYPE_' + argument[ARG_DATATYPE].upper())
            self.dyna_Add(argument[ARG_NAME], datatype)

            if ARG_VALUE in argument:
                self._commander_last_used.append(argument[ARG_VALUE])
            else:
                self._commander_last_used.append(None)

            if ARG_FLAGS in argument:
                flags = []
                for flag in argument[ARG_FLAGS]:
                    flags.append(getattr(lx.symbol, 'fCMDARG_' + flag.upper()))
                if flags:
                    self.basic_SetFlags(n, reduce(ior, flags))

        self.notifiers = []
        self.notifier_tuples = tuple([i for i in self.commander_notifiers()])
        self.not_svc = lx.service.NotifySys()

        for i in self.notifier_tuples:
            self.notifiers.append(None)

    def commander_arguments(self):
        return []

    def commander_arg_value(self, index):
        if self.dyna_IsSet(index):
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

        return None

    def commander_args_count(self):
        return len(self._arguments)

    def commander_notifiers(self):
        return []

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
        for n, argument in enumerate(self.commander_arguments()):
            if index == n:
                if ARG_LABEL in argument:
                    label = argument[ARG_LABEL]
                else:
                    label = argument[ARG_NAME]

                if ARG_sPresetText in argument:
                    if argument[ARG_sPresetText]:
                        hints.Class("sPresetText")

    def arg_UIValueHints(self, index):
        for n, argument in enumerate(self.commander_arguments()):
            if ARG_POPUP in argument:
                if index == n:
                    return PopupClass(argument[ARG_POPUP])
            if ARG_FCL in argument:
                if index == n:
                    return FormCommandListClass(argument[ARG_FCL])

    def cmd_DialogInit(self):
        for n, argument in enumerate(self.commander_arguments()):
            if self._commander_last_used[n] != None and ARG_DATATYPE in argument:

                if argument[ARG_DATATYPE].lower() in sTYPE_STRINGs:
                    self.attr_SetString(n, str(self._commander_last_used[n]))

                elif argument[ARG_DATATYPE].lower() in sTYPE_STRING_vectors:
                    self.attr_SetString(n, str(self._commander_last_used[n]))

                elif argument[ARG_DATATYPE].lower() in sTYPE_INTEGERs:
                    self.attr_SetInt(n, int(self._commander_last_used[n]))

                elif argument[ARG_DATATYPE].lower() in sTYPE_BOOLEANs:
                    self.attr_SetInt(n, int(self._commander_last_used[n]))

                elif argument[ARG_DATATYPE].lower in sTYPE_FLOATs:
                    self.attr_SetFlt(n, float(self._commander_last_used[n]))

    @classmethod
    def set_commander_last_used(cls, key, value):
        cls._commander_last_used[key] = value

    @classmethod
    def set_argument(cls, key, value):
        cls._arguments[key] = value

    def commander_execute(self, msg, flags):
        pass

    def basic_Execute(self, msg, flags):
        try:
            for n, argument in enumerate(self.commander_arguments()):

                if self.dyna_IsSet(n):
                    self.set_commander_last_used(n, self.commander_arg_value(n))

            self.commander_execute(msg, flags)

        except:
            lx.out(traceback.format_exc())

    def cmd_Query(self,index,vaQuery):
        va = lx.object.ValueArray()
        va.set(vaQuery)
        for n, argument in enumerate(self.commander_arguments()):
            if ARG_FLAGS in argument:
                if 'query' not in argument[ARG_FLAGS]:
                    continue
                if ARG_FCL in argument:
                    if argument[ARG_FCL]:
                        continue
                if index == n and self._commander_last_used[n]:
                    va.AddString(str(self._commander_last_used[n]))
        return lx.result.OK
