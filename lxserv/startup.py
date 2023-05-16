import os
import xml.etree.ElementTree as ET

import lx
import good_kitty


class StartupCommandClass(good_kitty.CommanderClass):
    _commander_default_values = []

    def commander_execute(self, msg, flags):
        # retrieve current kit path
        lxserv_path = os.path.dirname(os.path.realpath(__file__))
        new_kitpath = os.path.dirname(lxserv_path)
        tmp_file = os.path.join(new_kitpath, "tmp.xml")

        if not os.path.isfile(tmp_file):
            lx.eval('good_kitty.setup')
            return

        tmp_xml = ET.parse(tmp_file).getroot()
        elements = tmp_xml.getchildren()

        values = dict()
        for element in elements:
            values[element.attrib['key']] = element.text

        if values["initialize"] == "1":
            lx.eval('good_kitty.cleanup')


lx.bless(StartupCommandClass, 'good_kitty.startup')
