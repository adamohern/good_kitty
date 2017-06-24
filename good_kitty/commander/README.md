# commander #
### `lxu.command.BasicCommand` wrapper for typical MODO commands ###

Commander is a clean, simple wrapper for writing MODO commands with common UI elements like popup lists and string fields with popup hints (i.e. ``'sPresetText'``). The wrapper reduces clutter, redundant code, and common mistakes.

To implement a command, just include the commander module and, when creating your command class, extend `commander.CommanderClass` instead of `lxu.command.BasicCommand` as you normally would.

```python
import commander

class CommandClass(commander.CommanderClass):
  def commander_execute(self, msg, flags):
    lx.out('%s and %s' % ('bacon', 'eggs'))

lx.bless(CommandClass, 'breakfast')
```

Hooray! You now have a first-class MODO command. Type `breakfast` into the MODO command line, and read your delicious result.

```python
import commander

class CommandClass(commander.CommanderClass):
  def commander_arguments(self):
    return [
      {
        'name': 'dish_1',
        'datatype': 'string'
      }, {
        'name': 'dish_2',
        'datatype': 'string'
      }
    ]

  def commander_execute(self, msg, flags):
    dishes = self.commander_args()
    lx.out('%s and %s' % (dishes['dish_1'], dishes['dish_2']))

lx.bless(CommandClass, 'breakfast')
```

This asks the user for two strings in a command dialog. Easy enough.

Usually you want to include fancy stuff like popup menus for limiting your user's options, or `'sPresetText'` fields for suggesting possible values while allowing for arbitrary choices. Those take quite a lot of extra legwork with `BasicCommand`, but not with `commander`:

```python
import commander

class CommandClass(commander.CommanderClass):
  def commander_arguments(self):
    return [
      {
        'name': 'dish_1',
        'datatype': 'string',
        'default': 'bacon',
        'values_list_type': 'popup',
        'values_list': ['bacon', 'quinoa']
      }, {
        'name': 'dish_2',
        'datatype': 'string',
        'default': 'eggs',
        'values_list_type': 'sPresetText'
        'values_list': ['eggs', 'kale']
      }
    ]

  def commander_execute(self, msg, flags):
    dishes = self.commander_args()
    lx.out('%s and %s' % (dishes['dish_1'], dishes['dish_2']))

lx.bless(CommandClass, 'breakfast')
```

There are two kinds of popup arguments in commander: `'popup'` and `'sPresetText'`. The former is a straightforward popup menu with fixed values. The latter is a popup list with an editable text field. An argument may have one or the other of these fields, but not both.

The only required fields for each argument are `'name'` and `'datatype'`. `'name'` is an arbitrary alphanumeric string. `'datatype'` can be any of the following:

- `'acceleration'`
- `'angle'`
- `'angle3'`
- `'axis'`
- `'boolean'`
- `'color'`
- `'color1'`
- `'date'`
- `'datetime'`
- `'filepath'`
- `'float'`
- `'float3'`
- `'force'`
- `'integer'`
- `'light'`
- `'mass'`
- `'percent'`
- `'percent3'`
- `'speed'`
- `'string'`
- `'time'`
- `'uvcoord'`
- `'vertmapname'`

Arguments may also have a list of flags for special functionality, most commonly `'query'`, `'optional'`, and sometimes `'hidden'`. Valid flags include:

- `'can_query_when_disabled'`
- `'changed'`
- `'dialog_always_sets'`
- `'dialog_divider_after_arg'`
- `'dynamichints'`
- `'dynamic_defaults'`
- `'hidden'`
- `'init_only'`
- `'optional'`
- `'query'`
- `'readonly'`
- `'reqforvariable'`
- `'reqforvar_set'`
- `'state_only'`
- `'value_set'`
- `'variable'`

Include any of the above datatype strings, and `commander` will handle the rest, insuring that you always grab the correct python datatype for a given argument type. (No more accidentally trying to grab an sTYPE_STRING from an integer field or vise-verse.)

And yes, `commander` will even parse your vectors so that a `'color'` field returns the list `[0.0, 0.0, 0.0]` instead of the raw string `"0.0 0.0 0.0"`, saving you that trouble.

`commander` also bubble wraps your entire `commander_execute()` command in a nice, safe `try/except` statement with traceback for debugging.

You can also add notifiers to update your popup queries when other things happen in the app.

```python
def commander_notifiers(self):
    return [("select.event", "polygon +ldt"),("select.event", "item +ldt")]
```

The above listens for changes to polygon and/or item selection and updates form elements accordingly. If you're familiar with notifiers in MODO, you'll know how maniacally I laugh every time I implement this.

You can even build Form Command Lists (a list of programmatically-generated buttons in a form) by setting the `'values_list_type'` to `'fcl'`. Note that the argument must have the `'query'` flag, and each value in `'values_list'` list must be a valid MODO command.

```python
class CommandClass(commander.CommanderClass):
    def commander_arguments(self):
        return [
                {
                    'name': 'myGreatQuery',
                    'datatype': 'integer',
                    'default': '',
                    'values_list_type': 'fcl'
                    'values_list': ['render', 'render', 'render'],
                    'flags': ['query'],
                }
            ]

    def commander_notifiers(self):
        return [("select.event", "polygon +ldt"),("select.event", "item +ldt")]

lx.bless(CommandClass, CMD_NAME)
```

Speaking of the `query` flag, you can of course use it to query data within a command.

A common use-case would be a toggle button. The cleanest way is to have two separate arguments: one for the toggle mode, and another to query a boolean. You'll need to store a persistent state, of course, so we use a class variable.

Observe.

```python
class CommandClass(commander.CommanderClass):

    # This class variable stores our current toggle state.
    _state = False

    # Define two separate arguments: one for what we want to do when the command
    # is clicked in a toolbar, and the second is a query for displaying the current
    # toggle state.
    def commander_arguments(self):
        return [
                {
                    'name': 'mode',
                    'datatype': 'integer',
                    'default': 'toggle',
                    'values_list_type': 'popup'
                    'values_list': ['toggle', 'on', 'off']
                }, {
                    'name': 'query_me',
                    'datatype': 'boolean',
                    'default': 0,
                    'flags': ['query', 'optional']
                }
            ]

    # If you're not familiar with the @classmethod decorator and how it relates
    # to class variables, it'd be worth your time to do some reading.
    # In this case, we set the _state variable not just for the current object,
    # but for all objects of the current class.
    @classmethod
    def set_state(cls, value):
        cls._state = value

    def commander_execute(self):
        # In addition to `commander_args()`, we can get a specific arg value
        # by index using `commander_arg_value(index)`. Just for funsies.
        mode = self.commander_arg_value(0)

        if mode == 'on':
            # If on, toggle True
            self.set_state(True)

        elif mode == 'off':
            # If off, toggle False
            self.set_state(False)

        else:
            # Otherwise toggle the value
            state = False if self._state else True
            self.set_state(state)

    def commander_query(self, arg_index):
        # This just returns the query value based on the index of the argument
        # being queried. Our query arg is the second one in the list, so:
        if arg_index == 1:
            return self._state

lx.bless(CommandClass, CMD_NAME)
```

## Nuances

First, it can be a good idea to use constants rather than string literals for
key values in your dictionaries, as below. (I don't do this in the examples above
for readability, and I personally like it that way. But be warned: Joe will
send you angry emoji if you use string literals.)

```python
commander.NAME = 'name'
commander.LABEL = 'label'
commander.VALUE = 'default'
commander.DATATYPE = 'datatype'
commander.FLAGS = 'flags'
commander.VALUES_LIST_TYPE = 'values_list_type'
commander.VALUES_LIST = 'values_list'
```

Second, if your argument names are in ``"decent_underscore_style_english"``, the arg
labels will be generated automatically by replacing underscores with spaces and
capitalizing words. (e.g. "Decent Underscore Style English")

Third, in many cases, your popups may contain dynamic information, like a list of
polygon tags. For performance reasons, it's important that the function or method
that generates this list be passed into commander, not its result.

Finally, note that you can override any of the normal `lxu.command.BasicCommand`
methods as you normally would for adding a `basic_ButtonName` or `basic_Icon`, etc.

For example:

```python
import commander

class CommandClass(commander.CommanderClass):
  def commander_arguments(self):
    return [
      {
        # Since I'm not providing a label, "First Number" will be used.
        commander.NAME: 'first_number',
        commander.DATATYPE: 'float',
        commander.VALUE: 1.0,
        commander.VALUES_LIST_TYPE: 'popup',

        # Be sure not to put the parenthesis after the method name,
        # i.e. self.generate_list - NOT self.generate_list()
        commander.VALUES_LIST: self.generate_list
      }, {
        commander.NAME: 'second_number',
        commander.DATATYPE: 'float',
        commander.VALUE: 2.0,
        commander.VALUES_LIST_TYPE: 'sPresetText'
        commander.VALUES_LIST: self.generate_list
      }
    ]

  def commander_execute(self, msg, flags):
    numbers = self.commander_args()
    lx.out(numbers['first_number'] + numbers['second_number'])

  # If you generate dynamic values for a popup list, be sure to pass it
  # the actual method itself (see above).
  def generate_list(self):
    return float(i) for i in range(10)

  # You can override any of the normal lxu.command.BasicCommand stuff.
  def basic_ButtonName(self):
    return "Add Two Numbers..."


lx.bless(CommandClass, 'breakfast')
```

Enjoy.
Adam
