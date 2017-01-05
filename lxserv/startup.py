import lx, modo, commander

class StartupCommandClass(commander.CommanderClass):
    _commander_default_values = []

    def commander_execute(self, msg, flags):
        lx.out("kitty_kit_initialize",lx.eval('user.value kitty_kit_initialize ?'))
        if lx.eval('user.value kitty_kit_initialize ?') == 0:
            lx.eval('good_kitty.setup')
        elif lx.eval('user.value kitty_kit_initialize ?') == 1:
            lx.eval('good_kitty.getting_started')
        else:
            pass

lx.bless(StartupCommandClass, 'good_kitty.startup')
