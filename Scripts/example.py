import lx, modo

"""Prints a list of all selected items."""

for item in modo.Scene().selected:
    lx.out(item.name)

lx.eval('layout.createOrClose EventLog "Event Log_layout" title:@macros.layouts@EventLog@ width:600 height:600 persistent:true open:true')
