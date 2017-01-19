# python

import lx, os, modo, datetime
import xml.etree.ElementTree as ET

destination_path = modo.dialogs.customFile('fileSave', 'Save File', ('config',), ('MODO Config File',), ext=('cfg',))

keepers = [
    "ModifierKeys",
    "DirBrowser",
    "Preferences",
    "AppGlobal",
    "UserValues"
]

config_file_path = lx.eval("query platformservice path.path ? configname")

tree = ET.parse(config_file_path)
root = tree.getroot()
kids = root.getchildren()

trees = dict()
for kid in kids:
    try:
        tagType = kid.attrib["type"]
    except:
        continue

    if tagType in keepers:
        print "keeping:", kid.tag, tagType

        split = os.path.splitext(destination_path)
        final_path = "%s_%s%s" % (split[0], tagType, split[1])

        with open(final_path, 'wb') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('\n<!-- extracted by good_kitty on %s -->\n\n' % datetime.datetime.now().strftime("%d-%M-%y at %H:%M"))
            f.write("<configuration>\n\n  ")
            f.write(ET.tostring(kid))
            f.write("\n</configuration>")
