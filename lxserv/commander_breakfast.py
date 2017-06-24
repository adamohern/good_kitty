import lx, modo, good_kitty

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(good_kitty.CommanderClass):

    def commander_arguments(self):
        return [
            {
                'name': 'dish1',
                'datatype': 'string',
                'default': 'bacon',
                'values_list_type': 'popup',
                'values_list': ['bacon', 'quinoa']
            }, {
                'name': 'dish2',
                'datatype': 'string',
                'default': 'eggs',
                'values_list_type': 'sPresetText',
                'values_list': ['eggs', 'kale']
            }
        ]

    def commander_execute(self, msg, flags):
        dish1 = self.commander_arg_value(0)
        dish2 = self.commander_arg_value(1)

        modo.dialogs.alert("breakfast", ' and '.join([dish1, dish2]))


lx.bless(CommandClass, 'good_kitty.breakfast')
