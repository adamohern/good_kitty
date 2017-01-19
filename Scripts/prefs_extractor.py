# python

import lx, os
import xml.etree.ElementTree as ElementTree

destination_path = "E:\Users\Adam\Desktop"

keepers = [
    "ModifierKeys",
    "DirBrowser",
    "Preferences",
    "AppGlobal",
    "UserValues"
]

config_file_path = lx.eval("query platformservice path.path ? configname")
#lx.eval("file.open {%s}" % config_file_path)

tree = ElementTree.parse(config_file_path)
root = tree.getroot()
kids = root.getchildren()

for kid in kids:
    try:
        tagType = kid.attrib["type"]
    except:
        root.remove(kid)
        continue


    if tagType in keepers:
        print "keep:", kid.tag, tagType
        continue
    else:
        print "remove:", kid.tag, tagType
        root.remove(kid)
        continue

tree.write(os.path.join(destination_path, "extracted_prefs.cfg"))
