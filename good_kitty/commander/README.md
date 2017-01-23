# commander #
### `lxu.command.BasicCommand` wrapper for typical MODO commands ###

Commander is a clean, simple wrapper for writing MODO commands with common UI elements like popup lists and string fields with popup hints (i.e. ``'sPresetText'``). The wrapper reduces clutter, redundant code, and common mistakes.

To implement a command, just include the commander module and, when creating your command class, extend `commander.CommanderClass` instead of `lxu.command.BasicCommand` as you normally would.

*IMPORTANT* commander has been implemented inside a sub-module within good_kitty. So if you're using good_kitty to implement commander, you'll need to implement your command classes using `good_kitty.CommanderClass` rather than `commander.CommanderClass` as shown below, replacing the string `good_kitty` with the name of your kit. This is to ensure that different versions of commander in different kits do not conflict with one another.

```python
import commander

class CommandClass(commander.CommanderClass):
  _commander_default_values = []

  def commander_execute(self, msg, flags):
    lx.out(' and '.join(['bacon', 'eggs']))

lx.bless(CommandClass, 'breakfast')
```

Hooray! You now have a first-class MODO command. Type `breakfast` into the MODO command line, and read your delicious result.

The only slightly weird bit is that you have to include the `_commander_default_values` definition in your class, otherwise things will go sideways as soon as you use the class more than once. Just trust me on that one.

But it really gets nice when you want to ask the user for something.

```python
import commander

class CommandClass(commander.CommanderClass):
  _commander_default_values = []

  def commander_arguments(self):
    return [
      {
        'name': 'dish1',
        'datatype': 'string'
      }, {
        'name': 'dish2',
        'datatype': 'string'
      }
    ]

  def commander_execute(self, msg, flags):
    dish1 = self.commander_arg_value(0)
    dish2 = self.commander_arg_value(1)

    lx.out(' and '.join([dish1, dish2]))

lx.bless(CommandClass, 'breakfast')
```

The above isn't a big advantage over the traditional `lxu.basic.BasicCommand` import, but that's because it's simplistic.

Usually you want to include fancy stuff like popup menus for limiting your user's options, or `'sPresetText'` fields for suggesting possible values while allowing for arbitrary choices. Those take quite a lot of extra legwork with `BasicCommand`, but not with `commander`:

```python
import commander

class CommandClass(commander.CommanderClass):
  _commander_default_values = []

  def commander_arguments(self):
    return [
      {
        'name': 'dish1',
        'datatype': 'string',
        'label': 'First Dish',
        'default': 'bacon',
        'values_list_type': 'popup',
        'values_list': ['bacon', 'quinoa']
      }, {
        'name': 'dish2',
        'datatype': 'string',
        'label': 'Second Dish',
        'default': 'eggs',
        'values_list_type': 'sPresetText'
        'values_list': ['eggs', 'kale']
      }
    ]

  def commander_execute(self, msg, flags):
    dish1 = self.commander_arg_value(0)
    dish2 = self.commander_arg_value(1)

    lx.out(' and '.join([dish1, dish2]))

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
    _commander_default_values = []

    def commander_arguments(self):
        return [
                {
                    'name': 'myGreatQuery',
                    'label': 'Query This',
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

The above example lists the buttons `'render'`, `'render'`, and `'render'` all in a row in your form. Money. (If you've ever done this before manually, you are very happy right now.)

Okay, I'm getting silly now.

Sigh. Why can't life always be this easy?

Enjoy.
Adam
