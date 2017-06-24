# python

import lx, lxu, traceback
from lxifc import UIValueHints, Visitor
from operator import ior
from Var import *

class CommanderClass(lxu.command.BasicCommand):

    """Wrapper for lxu.command.BasicCommand. Improves and simplifies common
    command UI implementations, like popups, sPresetText fields, and
    Form Command Lists. Allows for virtually any type of command.

    See README.md for more examples.

    Example:
    ****************

    # Extend the commander.CommandClass
    class MyGreatCommandClass(commander.CommandClass):

        # Optional method returns any command argument definitions

        commander_arguments(self):
            return[{
                commander.NAME: 'myStringArgument',
                commander.DATATYPE: 'string'
            }]

        # Required method contains the actual command code.
        # Note: traceback is included by default; no need to add.

        commander_execute(self):
            args = commander_args()
            lx.out(args['myStringArgument'])

    # Bless the class as normal.
    lx.bless(MyGreatCommandClass, "myGreatCommand")

    ****************
    """

    def __init__(self):

        # Since we run our own __init__(), we need to explicitly run the
        # base class's __init__() as well.
        lxu.command.BasicCommand.__init__(self)

        # NOTE re: default argument values.

        # When a command is run for the first time, MODO presents the user
        # with a dialog containing blank fields for each argument. After first
        # run, the command will remember the previous values used.

        # In many cases, however, you may want to present a new user with sensible
        # default values for arguments--not the blank fields provided by default.
        # To this end, you can use the cmd_DialogInit() method. Define your
        # defaults there, and MODO will always present the user with those
        # defaults.

        # But there's a problem: you can't have it both ways. Either you use
        # cmd_DialogInit() to set the same default values every time the command
        # is run, or you remember the last values and use those. You can't
        # have a default value for first run, and then remember recent values
        # thereafter.

        # And yes, you sort of can by testing for dyna_IsSet(), but no. You can't.
        # Not for popups. Popups with dynamic contents will always default to
        # blank "...", no matter what you do.

        # The commander workaround is to store our own argument default values
        # in a class variable called _commander_stored_values. We then manually
        # use the stored values in cmd_DialogInit(), and viola! Sensible
        # default values that also remember recently-used values... even for
        # popups menus. Yay.

        # So here we go. If _commander_stored_values hasn't been initilized yet,
        # we need to initialize it. (And no, you can't just put it outside of
        # __init__() just below the class declaration, lest your sublcasses
        # start trying to use each other's default arguments. Trust me.)
        try:
            self._commander_stored_values
        except AttributeError:
            self.commander_default_values_init()

        # Loop through command arguments defined in commander_arguments()
        # and initialize.
        for n, argument in enumerate(self.commander_arguments()):

            # Arguments need a valid name and datatype. Without those, we die.

            if not argument.get(DATATYPE):
                return lx.symbol.e_FAILED

            if not argument.get(NAME):
                return lx.symbol.e_FAILED

            datatype = getattr(lx.symbol, 'sTYPE_' + argument[DATATYPE].upper())
            if not datatype:
                return lx.symbol.e_FAILED

            # Add the argument as normal.
            self.dyna_Add(argument[NAME], datatype)

            # If this is the first time running the command, the class variable
            # _commander_stored_values will be empty. In that case, populate it.
            if n >= len(self._commander_stored_values):
                self.commander_default_values_set(argument.get(VALUE))

            # If a list of flags is included in the argument, set them.
            flags = []
            for flag in argument.get(FLAGS, []):
                flags.append(getattr(lx.symbol, 'fCMDARG_' + flag.upper()))
            if flags:
                self.basic_SetFlags(n, reduce(ior, flags))

        # CommandClass can implement the commander_notifiers() method to update
        # FormCommandLists and Popups. If implemented, add the notifiers.
        self.not_svc = lx.service.NotifySys()
        self.notifiers = []
        self.notifier_tuples = tuple([i for i in self.commander_notifiers()])
        for i in self.notifier_tuples:
            self.notifiers.append(None)

    def commander_arguments(self):
        """To be overridden by subclasses.
        Should return a list of dictionaries, one for each argument."""
        return []

    def commander_notifiers(self):
        """To be overridden by subclasses.
        Should return a list of tuples, e
        [('notifier.editAction',''), ("select.event", "item +ldt"), ("tagger.notifier", "")]"""

        return []

    def commander_execute(self, msg, flags):
        """To be overridden by subclasses.
        This is the main command execution code. It is already wrapped in
        a try/except statement with traceback, so you don't need to add that."""
        pass

    def commander_query(self, arg_index):
        """To be overridden by subclasses.
        Should return a value based on the arg_index being queried. For toggle
        buttons and checkmarks, this should be a boolean. Can also return strings
        or floats as required."""

        return False

    @classmethod
    def commander_default_values_init(cls):
        """Initialize the class variable _commander_stored_values.
        You should never need to touch this."""
        cls._commander_stored_values = []

    @classmethod
    def commander_default_values_set(cls, value):
        """Add an argument to the class variable _commander_stored_values.
        You should never need to touch this."""
        cls._commander_stored_values.append(value)


    def commander_arg_value(self, index, default=None):
        """Return a command argument value by index.
        If no argument value exists, returns the default parameter.

        NOTE: The commander_args() method is simpler to use than this method.
        You should probably use that one unless you have a reason to find a specific
        argument by index.

        :param index: (int) index of argument to retrieve
        :param default: value to return if argument is not set
        :returns: argument value (str, int, float, or boolean as appropriate)"""

        # If no value is set, return the default.
        if not self.dyna_IsSet(index):
            return default

        # If it's a string, use dyna_String to grab it.
        if self.commander_arguments()[index][DATATYPE].lower() in sTYPE_STRINGs:
            return self.dyna_String(index)

        # If the value is a vector, use dyna_String to grab it, then parse it
        # into a list of float vlues.
        elif self.commander_arguments()[index][DATATYPE].lower() in sTYPE_STRING_vectors:
            return [float(i) for i in self.dyna_String(index).split(" ")]

        # If the value is an integer, use dyna_Int to grab it.
        elif self.commander_arguments()[index][DATATYPE].lower() in sTYPE_INTEGERs:
            return self.dyna_Int(index)

        # If the value is a float, use dyna_Float to grab it.
        elif self.commander_arguments()[index][DATATYPE].lower in sTYPE_FLOATs:
            return self.dyna_Float(index)

        # If the value is a boolean, use dyna_Bool to grab it.
        elif self.commander_arguments()[index][DATATYPE].lower() in sTYPE_BOOLEANs:
            return self.dyna_Bool(index)

        # If something bonkers is going on, use the default.
        return default

    def commander_args(self):
        """Returns a dictionary of arguments in name:value pairs."""
        args = {}
        for i in range(len(self.commander_arguments())):
            name = self.commander_arguments()[i][NAME]
            value = self.commander_arg_value(i)
            args[name] = value
        return args

    def cmd_NotifyAddClient(self, argument, object):
        """Add notifier clients as needed.
        You should never need to touch this."""
        for i, tup in enumerate(self.notifier_tuples):
            if self.notifiers[i] is None:
                self.notifiers[i] = self.not_svc.Spawn (self.notifier_tuples[i][0], self.notifier_tuples[i][1])

            self.notifiers[i].AddClient(object)

    def cmd_NotifyRemoveClient(self, object):
        """Remove notifier clients as needed.
        You should never need to touch this."""
        for i, tup in enumerate(self.notifier_tuples):
            if self.notifiers[i] is not None:
                self.notifiers[i].RemoveClient(object)

    def cmd_Flags(self):
        """Set command flags. This method can be overridden if special flags
        are needed."""
        return lx.symbol.fCMD_POSTCMD | lx.symbol.fCMD_MODEL | lx.symbol.fCMD_UNDO

    def arg_UIHints(self, index, hints):
        """Adds pretty labels to arguments in command dialogs. If no label parameter
        is explicitly included, we create a pseudo-label by capitalizing the
        argument name and replacing underscores with spaces.

        Labels can either be literal strings or method/function objects. In the
        latter case, the method or function will be called when needed.

        If any popup fields of type sPresetText are present,
        adds the appropriate hint.

        You should never need to touch this."""

        args = self.commander_arguments()
        if index < len(args):

            # If an explicit label is provided, use it.
            label = args[index].get(LABEL)

            # If not, make a pretty version of the arg name.
            if not label:
                label = args[index].get(NAME).replace("_", " ").title()

            # Labels can be functions. If so, run the function to get the string.
            elif hasattr(label, '__call__'):
                label = label()

            # Apply the label.
            hints.Label(label)

            # If the popup type is sPresetText, apply the appropriate class.
            if args[index].get(VALUES_LIST_TYPE) == sPresetText:
                hints.Class("sPresetText")

    def arg_UIValueHints(self, index):
        """Popups and sPresetText arguments fire this method whenever
        they update. Note that the 'hints' parameter can be a literal list
        or tuple, but can also be a method or function.

        For dynamic lists,
        be sure to pass in the generator method or function object itself,
        not its result. (i.e. pass in 'myGreatFunction', NOT 'myGreatFunction()')

        You should never need to touch this."""

        args = self.commander_arguments()
        if index < len(args):
            arg = args[index]
            arg_data = None

            # Try to grab the values_list for the argument.
            if arg.get(VALUES_LIST) is not None:
                arg_data = arg.get(VALUES_LIST)

            # If our values_list is empty, don't bother.
            if not arg_data:
                return

            # If the values_list is a list/tuple, use it as-is.
            if isinstance(arg_data, (list, tuple)):
                values = arg_data

            # If the values_list is a method/function, fire it and use the result.
            elif hasattr(arg_data, '__call__'):
                values = arg_data()

            # In some rare cases you may want to manually instantiate your own
            # popup class as a subclass of UIValueHints. In those cases, we
            # ignore the below and just use yours.
            elif issubclass(arg_data, UIValueHints):
                return arg_data()

            # If values is None or "" or someother nonsense, return an empty list.
            if not values:
                values = []

            # Argument can be a normal popup, an sPresetText popup, or a
            # Form Command List. We'll need to return a different class
            # depending on the 'values_list_type'.

            if args[index].get(VALUES_LIST_TYPE) == POPUP:
                return PopupClass(values)

            elif args[index].get(VALUES_LIST_TYPE) == sPresetText:
                return PopupClass(values)

            elif args[index].get(VALUES_LIST_TYPE) == FCL:
                return FormCommandListClass(values)

    def cmd_DialogInit(self):
        """Sets default values for arguments in command dialogs as
        explained in __init__() above. If you change this, you run the risk
        of causing the universe to implode on itself.

        You should never need to touch this."""

        for n, argument in enumerate(self.commander_arguments()):

            # If we already have a value, use it.
            # This is especially important when a command is run with args
            # via command line or form button.
            if self.dyna_IsSet(n) and self.dyna_String(n):
                continue

            datatype = argument.get(DATATYPE, '').lower()
            stored_value = self._commander_stored_values[n]
            default_value = self.commander_arguments()[n].get(VALUE)

            # If there's no default and nothing stored, we're done here.
            if default_value == None and not stored_value:
                continue

            # The correct attr_Set... method depends on datatype.

            if datatype in sTYPE_STRINGs + sTYPE_STRING_vectors:
                self.attr_SetString(n, str(stored_value))

            elif datatype in sTYPE_INTEGERs + sTYPE_BOOLEANs:
                self.attr_SetInt(n, int(stored_value))

            elif datatype in sTYPE_FLOATs:
                self.attr_SetFlt(n, float(stored_value))

    def basic_Execute(self, msg, flags):
        """Stores recent command values for next run and wraps commander_execute
        in a try/except statement with traceback.

        Do NOT override this method. Use commander_execute() instead.

        You should never need to touch this."""

        for n, argument in enumerate(self.commander_arguments()):
            self._commander_stored_values[n] = self.commander_arg_value(n)

        try:
            self.commander_execute(msg, flags)
        except:
            lx.out(traceback.format_exc())

    def cmd_Query(self, index, vaQuery):
        """Returns a value when a queriable argument is queried. It's a bit weird
        to use, so commander wraps it up for you. Implement `commander_query` in
        your own sublcass to and return whatever you like based on the arg_index.

        You should never need to touch this."""

        # Create the ValueArray object
        va = lx.object.ValueArray()
        va.set(vaQuery)

        args = self.commander_arguments()

        # If index out of range, bail
        if index > len(args):
            return lx.result.OK

        # If it's not a query, bail
        is_query = 'query' in args[index].get(FLAGS, [])
        if not is_query:
            return lx.result.OK

        # If it's a Form Command List (FCL), bail
        is_fcl = args[index].get(VALUES_LIST_TYPE) == FCL
        if is_fcl:
            return lx.result.OK

        # To keep things simpler for commander users, let them return
        # a value using only an index (no ValueArray nonsense)
        commander_query_result = self.commander_query(index)

        # Need to add the proper datatype based on result from commander_query

        if isinstance(commander_query_result, basestring):
            va.AddString(commander_query_result)

        elif isinstance(commander_query_result, int):
            va.AddInt(commander_query_result)

        elif isinstance(commander_query_result, float):
            va.AddFloat(commander_query_result)

        return lx.result.OK


class FormCommandListClass(UIValueHints):
    """Special class for creating Form Command Lists. This is instantiated
    by CommanderClass objects if an FCL argument provided.

    Expects a list of valid MODO commands to be provided to init.

    NOTE: Any invalid command will crash MODO.

    You should never need to touch this."""

    def __init__(self, items):
        self._items = items

    def uiv_Flags(self):
        return lx.symbol.fVALHINT_FORM_COMMAND_LIST

    def uiv_FormCommandListCount(self):
        return len(self._items)

    def uiv_FormCommandListByIndex(self,index):
        return self._items[index]


class PopupClass(UIValueHints):
    """Special class for creating popups and sPresetText fields. Accepts
    either a simple list of values, or a list of (ugly, pretty) tuples:

    [1, 2, 3]
    or
    [(1, "The Number One"), (2, "The Number Two"), (3, "The Number Three")]

    You should never need to touch this."""

    def __init__(self, items):
        self._internal = []
        self._user = []

        # If we have items to add to the lists, add them.
        if items and isinstance(items, (list, tuple)):
            for item in items:

                # If the list item is a list or tuple, assume the format (ugly, pretty)
                if isinstance(item, (list, tuple)):
                    self._internal.append(str(item[0]))
                    self._user.append(str(item[1]))

                # Otherwise just use the value for both Ugly and Pretty
                else:
                    self._internal.append(str(item))
                    self._user.append(str(item))

    def uiv_Flags(self):
        return lx.symbol.fVALHINT_POPUPS

    def uiv_PopCount(self):
        return len(self._internal)

    def uiv_PopUserName(self,index):
        return self._user[index]

    def uiv_PopInternalName(self,index):
        return self._internal[index]
