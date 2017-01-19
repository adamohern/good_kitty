import lx, modo, good_kitty, xml.etree.ElementTree, os, sys

class StartupCommandClass(good_kitty.CommanderClass):
    _commander_default_values = []

    def commander_execute(self, msg, flags):
        # retrieve current kit path
        lxserv_path = os.path.dirname(os.path.realpath(__file__))
        new_kitpath = os.path.dirname(lxserv_path)
        tmp_file = os.path.join(new_kitpath, "tmp.xml")

        if not os.path.isfile(tmp_file):
            lx.out("Unable to find:", tmp_file)
            lx.out("Running setup routine...")
            lx.eval('good_kitty.setup')
            sys.exit()

        tmp_xml = xml.etree.ElementTree.parse(tmp_file).getroot()
        elements = tmp_xml.getchildren()

        values = dict()
        for element in elements:
            values[element.attrib['key']] = element.text

        if values["initialize"] == "1":
            lx.eval('good_kitty.cleanup')

lx.bless(StartupCommandClass, 'good_kitty.startup')
