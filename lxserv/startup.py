import lx, modo, good_kitty

class StartupCommandClass(good_kitty.CommanderClass):
    _commander_default_values = []

    def commander_execute(self, msg, flags):
        if lx.eval('user.value kitty_kit_initialize ?') == 0:
            lx.eval('good_kitty.setup')
        elif lx.eval('user.value kitty_kit_initialize ?') == 1:
            lx.eval('good_kitty.getting_started')
        else:
            pass

lx.bless(StartupCommandClass, 'good_kitty.startup')
