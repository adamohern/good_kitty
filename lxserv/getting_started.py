import lx, modo, commander, os

class CommandClass(commander.CommanderClass):
    _commander_default_values = []

    def commander_execute(self, msg, flags):
        kitname = lx.eval('user.value kitty_kit_new_name ?')
        new_kitpath = lx.eval("query platformservice alias ? {%s:}" % kitname)

        os.remove(os.path.join(new_kitpath, 'Configs', 'startup.cfg'))
        os.remove(os.path.join(new_kitpath, 'lxserv', 'getting_started.py'))
        os.remove(os.path.join(new_kitpath, 'lxserv', 'startup.py'))

        modo.dialogs.alert("Kit Initialized", "Your new kit is working. Have fun.")
        lx.eval('user.value kitty_kit_initialize 0')

lx.bless(CommandClass, 'good_kitty.getting_started')
