# python

import lx, os, modo, datetime, re, sys
import xml.etree.ElementTree as ET

args = lx.args()

if len(args) > 0:
    destination_path = args[0].translate(None, "{}")
else:
    destination_path = modo.dialogs.customFile('fileSave', 'Save File', ('config',), ('MODO Config File',), ext=('cfg',))

if len(args) > 1:
    keepers = args[1].split(";")
    keepers = [i.translate(None, "{}") for i in keepers if i]
else:
    keepers = [
        "InputRemapping",
        "DirBrowser",
        "Preferences",
        "AppGlobal",
        "ToolPresetLists",
        "ToolSnapSettings",
        "UIElements",
        "UserValues"
    ]

config_file_path = lx.eval("query platformservice path.path ? configname")

try:
    with open(config_file_path, "r") as fp:
        root = ET.fromstring(unicode(fp.read(), errors='ignore'))
except:
    modo.dialogs.alert("Failed", "Could not open config file.")
    sys.exit()

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
