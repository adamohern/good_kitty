# commander
lxu.command.BasicCommand wrapper for typical MODO commands

Commander is a clean, simple wrapper for writing MODO commands with common UI elements like popup lists and string fields with popup hints (i.e. 'sPresetText'). The wrapper reduces clutter, redundant code, and common mistakes.

To implement a command, just include the commander module and, when creating your command class, extend `commander.Commander` instead of `lxu.command.BasicCommand` as you normally would.
