import lx, modo, commander, os, shutil, glob

def replace_in_files(directory, find, replace, list_of_extensions):
    for path, dirs, files in os.walk(os.path.abspath(directory)):
        for filename in files:
            if filename.lower().endswith(list_of_extensions):
                filepath = os.path.join(path, filename)
                with open(filepath) as f:
                    s = f.read()
                s = s.replace(find, replace)
                with open(filepath, "w") as f:
                    f.write(s)

def replace_in_filenames(directory, find, replace):
    paths_list = (os.path.join(root, filename)
        for root, _, filenames in os.walk(directory)
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
                'default': 'My Great Kit'
            }, {
                'name': 'internal',
                'datatype': 'string',
                'label': 'Internal Name',
                'default': 'my_great_kit'
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
        replace_in_files(new_kitpath, 'good_kitty', internal_name, (".cfg", ".py", ".html", ".css"))
        replace_in_files(new_kitpath, 'Good Kitty', pretty_name, (".cfg", ".py", ".html", ".css"))

        # delete unnecessary stuff
        for f in glob.glob(new_kitpath + "/*/*.pyc"):
            try:
                os.remove(f)
            except:
                continue

        os.remove(os.path.join(new_kitpath, 'lxserv', 'setup.py'))
        os.remove(os.path.join(new_kitpath, 'README.md'))
        os.remove(os.path.join(new_kitpath, '.gitignore'))
        shutil.rmtree(os.path.join(new_kitpath, '.git'), True)

        # open folder in file browser
        lx.eval('file.open {%s}' % new_kitpath)

        # tell the user what to do next on restart
        lx.eval('user.value kitty_kit_new_name {kit_%s}' % internal_name)
        lx.eval('user.value kitty_kit_initialize 1')

        # alert with help info
        modo.dialogs.alert("Restarting", "good_kitty has been customized. Restarting MODO.")
        lx.eval('app.restart')


lx.bless(CommandClass, 'good_kitty.setup')
