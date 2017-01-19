import lx, modo, good_kitty, os, glob, xml.etree.ElementTree

class CommandClass(good_kitty.CommanderClass):
    _commander_default_values = []

    def commander_execute(self, msg, flags):
        # retrieve new kit name
        lxserv_path = os.path.dirname(os.path.realpath(__file__))
        new_kitpath = os.path.dirname(lxserv_path)

        index_file = os.path.join(new_kitpath, "index.cfg")

        index_xml = xml.etree.ElementTree.parse(index_file).getroot()
        kitname = index_xml.attrib["kit"]


        # remove pyc files
        for f in glob.glob(new_kitpath + "/*/*.pyc"):
            try:
                os.remove(f)
            except:
                continue


        # read configs to extract from temp file
        tmp_file = os.path.join(new_kitpath, "tmp.xml")

        tmp_xml = xml.etree.ElementTree.parse(tmp_file).getroot()
        elements = tmp_xml.getchildren()

        values = dict()
        for element in elements:
            if 'key' in element.attrib:
                values[element.attrib['key']] = element.text

        if "configs_to_extract" in values:
            arg2 = ' "%s"' % values["configs_to_extract"]
        else:
            arg2 = ""

        command_string = '@good_kitty_prefs_extractor.py "%s"%s' % (os.path.join(new_kitpath, 'Configs', 'Extracted.cfg'), arg2)
        lx.eval(command_string)


        # remove cruft
        os.remove(os.path.join(new_kitpath, 'tmp.xml'))
        os.remove(os.path.join(new_kitpath, 'Scripts', 'good_kitty_prefs_extractor.py'))
        os.remove(os.path.join(new_kitpath, 'Configs', 'startup.cfg'))
        os.remove(os.path.join(new_kitpath, 'lxserv', 'cleanup.py'))
        os.remove(os.path.join(new_kitpath, 'lxserv', 'startup.py'))


        # celebrate
        modo.dialogs.alert("Kit Initialized", "Your new kit is working. Have fun.")


lx.bless(CommandClass, 'good_kitty.cleanup')
