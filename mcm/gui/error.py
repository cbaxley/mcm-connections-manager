#!/usr/bin/env python
# - coding: utf-8 -
#
# Copyright (C) 2010 Alejandro Ayuso
#
# This file is part of the MCM Connection Manager
#
# MCM Connection Manager is free software: you can redistribute
# it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# MCM Connection Manager is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the MCM Connection Manager. If not, see
# <http://www.gnu.org/licenses/>.
#

'''
A simple error dialog for MCM output. Captures the exit code
of an app and shows a dialog with the error if there was an
abnormal (not 0) exit. Also needs the error string to show.
'''

import sys
import gtk
import pygtk
pygtk.require("2.0")

from widgets import UtilityDialogs

class McmErrorDialog(object):

    def __init__(self, app, err_msg):
        self.err_title = "%s Error" % app.upper()
        self.err_msg = err_msg

    def draw(self):
        dlg = UtilityDialogs()
        dlg.show_error_dialog(self.err_title, self.err_msg)

if __name__ == '__main__':
    exit_code = int(sys.argv[1])
    app = sys.argv[2]
    err_msg = sys.argv[3]
    if app == "ssh":
        if exit_code != 1 and exit_code != 0:
            dlg = McmErrorDialog(app, err_msg)
            dlg.draw()
    elif app == 'vnc':
        if exit_code != 0:
            dlg = McmErrorDialog(app, err_msg)
            dlg.draw()
    elif app == 'ftp':
        if exit_code != 0:
            dlg = McmErrorDialog(app, err_msg)
            dlg.draw()
    elif app == 'rdp':
        if exit_code != 0:
            dlg = McmErrorDialog(app, err_msg)
            dlg.draw()
    elif app == 'telnet':
        if exit_code != 0:
            dlg = McmErrorDialog(app, err_msg)
            dlg.draw()

    else:
        print "unkown %s" % app
        exit(exit_code)
