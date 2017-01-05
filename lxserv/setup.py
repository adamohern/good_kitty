import lx, modo, commander, os

def replace_in_files(directory, find, replace, list_of_extensions):
    for path, dirs, files in os.walk(os.path.abspath(directory)):
        if filename.endswith(list_of_extensions):
            filepath = os.path.join(path, filename)
            with open(filepath) as f:
                s = f.read()
            s = s.replace(find, replace)
            with open(filepath, "w") as f:
                f.write(s)

def replace_in_filenames(directory, find, replace):
    paths_list = (os.path.join(root, filename)
        for root, _, filenames in os.walk(kitpath)
        for filename in filenames
    )

    paths_list = [path for path in paths_list if (os.sep + '.git' + os.sep) not in path]

    for path in paths_list:
        newname = os.path.basename(path).replace(find, replace)
        newname = os.path.join(os.path.dirname(path), newname)
        if newname != path:
            os.rename(path,newname)


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
        new_kitpath = os.path.join(os.path.dirname(kitpath), internal_name)

        # rename the kit directory
        os.rename(kitpath, new_kitpath)

        # rename any files containing 'good_kitty'
        replace_in_filenames(new_kitpath, 'good_kitty', internal_name)

        # find and replace in text files
        replace_in_files(new_kitpath, 'good_kitty', internal_name, (".cfg", ".py", ".md", ".html", ".css"))

        # delete setup.py
        os.remove(os.path.join(new_kitpath, 'lxserv', 'setup.py'))

        # delete startup.cfg
        os.remove(os.path.join(new_kitpath, 'Configs', 'startup.cfg'))

        # open folder in file browser
        lx.eval('file.open {%s}' % new_kitpath)

        # alert with help info
        modo.dialogs.alert("Restarting", "good_kitty has been customized. Restarting MODO.")
        lx.eval('app.restart')


lx.bless(CommandClass, 'good_kitty.setup')
