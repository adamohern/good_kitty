# Good Kitty #
### Making kits for MODO has never been easier. ###

good_kitty is a template for building well-structured kits in MODO, complete with icons, commands, configs, and scripts.

It also includes `commander`, a wrapper for MODO's built-in `lxu.command.BasicCommand` API class that makes building first-class MODO commands incredibly easy. See <a href="https://github.com/adamohern/commander">commander</a> on github for more.

To implement a new kit with good_kitty, I recommend the following steps:

1. Download and unzip good_kitty to a folder the MODO kits directory.
2. Start MODO.
3. Input the name and internal name of the new kit.

A setup script will then customize the kit to use the name and internal name you provided, then restart MODO for the changes to take effect.

This should get you to a functioning kit. Peruse the content of the kit for examples of scripts, commands, preferences, command help, icons, html documentation, and more. Once you understand what each file does, feel free to use it as a starting point for your own, or just delete the ones you don't need.

Adam
adam@mechanicalcolor.com
