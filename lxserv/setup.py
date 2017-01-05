import lx, modo, commander, os


class StartupCommandClass(commander.CommanderClass):
    _commander_default_values = []

    def commander_execute(self, msg, flags):
        if not lx.eval('user.value good_kitty_initialized ?'):
            lx.eval('good_kitty.setup')


lx.bless(StartupCommandClass, 'good_kitty.startup')


class CommandClass(commander.CommanderClass):
    _commander_default_values = []

    def commander_arguments(self):
        return [
            {
                'name': 'pretty',
                'datatype': 'string',
                'label': 'Pretty Name',
                'default': 'Good Kitty'
            }, {
                'name': 'internal',
                'datatype': 'string',
                'label': 'Internal Name',
                'default': 'good_kitty'
            }
        ]

    def commander_execute(self, msg, flags):
        pretty_name = self.commander_arg_value(0)
        internal_name = self.commander_arg_value(1)

        if modo.dialogs.yesNo("Are you sure?", "Customizing good_kitty requires MODO to restart. Are you sure?") == 'no':
            return

        kitpath = lx.eval("query platformservice alias ? {kit_good_kitty:}")

        lx.out("os.rename(%s, %s)" % (kitpath, os.path.join(os.path.dirname(kitpath), internal_name)))
        # os.rename(kitpath, os.join(os.dirname(kitpath), internal_name))

        pathiter = (os.path.join(root, filename)
            for root, _, filenames in os.walk(kitpath)
            for filename in filenames
        )
        for path in pathiter:
            newname =  path.replace('good_kitty', 'internal_name')
            if newname != path:
                lx.out("os.rename(%s,%s)" % (path,newname))
                # os.rename(path,newname)

        # find and replace in text files

        # delete setup.py
        # delete startup.cfg
        # remove startup user value

        # open folder in file browser

        # alert with help info

        lx.eval('layout.createOrClose EventLog "Event Log_layout" title:@macros.layouts@EventLog@ width:600 height:600 persistent:true open:true')

        # lx.eval('user.value good_kitty_initialized 1')


lx.bless(CommandClass, 'good_kitty.setup')
