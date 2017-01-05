import lx, modo, commander

class CommandClass(commander.CommanderClass):
    _commander_default_values = []

    def commander_execute(self, msg, flags):
        modo.dialogs.alert("Kit Initialized", "Your new kit is working. Have fun.")
        lx.eval('user.value kitty_kit_initialize 2')

lx.bless(CommandClass, 'good_kitty.getting_started')
