import lx, modo, good_kitty, os, shutil, glob, datetime

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
    paths_list = (os.path.join(root, path)
        for root, directories, filenames in os.walk(directory)
        for path in filenames + directories
    )

    paths_list = [path for path in paths_list if (os.sep + '.git' + os.sep) not in path]

    for path in paths_list:
        newname = os.path.basename(path).replace(find, replace)
        newname = os.path.join(os.path.dirname(path), newname)
        if newname != path:
            shutil.move(path,newname)


class CommandClass(good_kitty.CommanderClass):
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
            }, {
                'name': 'modesTail',
                'datatype': 'boolean',
                'label': 'Include Modes Tail Form',
                'default': True
            }, {
                'name': 'presets',
                'datatype': 'boolean',
                'label': 'Include Presets Directory',
                'default': True
            }, {
                'name': 'InputRemapping',
                'datatype': 'boolean',
                'label': 'Extract Input Remapping',
                'default': True
            }, {
                'name': 'DirBrowser',
                'datatype': 'boolean',
                'label': 'Extract Preset Browser State',
                'default': True
            }, {
                'name': 'Preferences',
                'datatype': 'boolean',
                'label': 'Extract Preferences',
                'default': True
            }, {
                'name': 'AppGlobal',
                'datatype': 'boolean',
                'label': 'Extract Global Settings',
                'default': True
            }, {
                'name': 'ToolPresetLists',
                'datatype': 'boolean',
                'label': 'Extract Tool Presets',
                'default': True
            }, {
                'name': 'ToolSnapSettings',
                'datatype': 'boolean',
                'label': 'Extract Snapping Presets',
                'default': True
            }, {
                'name': 'UIElements',
                'datatype': 'boolean',
                'label': 'Extract Color Schemes',
                'default': True
            }, {
                'name': 'UserValues',
                'datatype': 'boolean',
                'label': 'Extract User Values',
                'default': False
            }
        ]

    def commander_execute(self, msg, flags):
        pretty_name = self.commander_arg_value(0)
        internal_name = self.commander_arg_value(1)

        modesTail = self.commander_arg_value(2)
        presets = self.commander_arg_value(3)

        InputRemapping = "InputRemapping" if self.commander_arg_value(4) else ""
        DirBrowser = "DirBrowser" if self.commander_arg_value(5) else ""
        Preferences = "Preferences" if self.commander_arg_value(6) else ""
        AppGlobal = "AppGlobal" if self.commander_arg_value(7) else ""
        ToolPresetLists = "ToolPresetLists" if self.commander_arg_value(8) else ""
        ToolSnapSettings = "ToolSnapSettings" if self.commander_arg_value(9) else ""
        UIElements = "UIElements" if self.commander_arg_value(10) else ""
        UserValues = "UserValues" if self.commander_arg_value(11) else ""

        if modo.dialogs.yesNo("Are you sure?", "Customizing good_kitty requires MODO to quit when finished. Are you sure?") == 'no':
            return

        kitpath = lx.eval("query platformservice alias ? {kit_good_kitty:}")
        new_kitpath = os.path.join(os.path.dirname(kitpath), internal_name)

        # rename the kit directory
        shutil.move(kitpath, new_kitpath)

        # rename any files containing 'good_kitty'
        replace_in_filenames(new_kitpath, 'good_kitty', internal_name)

        # find and replace in text files
        replace_in_files(new_kitpath, 'good_kitty', internal_name, (".cfg", ".py", ".html", ".css"))
        replace_in_files(new_kitpath, 'Good Kitty', pretty_name, (".cfg", ".py", ".html", ".css"))

        # delete pyc files
        for f in glob.glob(new_kitpath + "/*/*.pyc"):
            try:
                os.remove(f)
            except:
                continue

        # delete modes tail if necessary
        if not modesTail:
            os.remove(os.path.join(new_kitpath, 'Configs', 'forms_modes_tail.cfg'))

        # delete presets directory mapping if necessary
        if not presets:
            os.remove(os.path.join(new_kitpath, 'Configs', 'presets.cfg'))

        # delete installation-related files
        os.remove(os.path.join(new_kitpath, 'lxserv', 'setup.py'))
        os.remove(os.path.join(new_kitpath, 'README.md'))
        os.remove(os.path.join(new_kitpath, '.gitignore'))
        shutil.rmtree(os.path.join(new_kitpath, '.git'), True)

        # leave ourselves some temp information for after the restart
        configs_to_extract = ";".join((
                InputRemapping,
                DirBrowser,
                Preferences,
                AppGlobal,
                ToolPresetLists,
                ToolSnapSettings,
                UIElements,
                UserValues
            ))

        with open(os.path.join(new_kitpath, "tmp.xml"), 'w+') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n\n')
            f.write('<!-- Created by good_kitty on %s -->\n' % datetime.datetime.now().strftime("%d-%M-%y at %H:%M"))
            f.write('<!-- This file should self-destruct during the good_kitty setup process. If you\'re reading this, something has gone wrong.-->\n\n')
            f.write("<data>\n")
            f.write('  <element key="initialize">1</element>\n')
            f.write('  <element key="configs_to_extract">%s</element>\n' % configs_to_extract)
            f.write("</data>")


        # NOTE: For some reason app.restart was corrupting the user config file.
        # My workaround is to simply use app.quit and rely on the user to run
        # MODO again.

        # alert with help info
        modo.dialogs.alert("Quitting MODO", "MODO will now quit. Changes will take effect next time MODO runs.")

        # open folder in file browser
        lx.eval('file.open {%s}' % new_kitpath)
        lx.eval('app.quit')

lx.bless(CommandClass, 'good_kitty.setup')
