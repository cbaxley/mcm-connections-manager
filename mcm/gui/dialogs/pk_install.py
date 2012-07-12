# - coding: utf-8 -
#
# Copyright (C) 2009 Alejandro Ayuso 
#
# This file is part of the MCM Connection Manager
#
# MCM Connection Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MCM Connection Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with the MCM Connection Manager.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import gtk

from mcm.common import constants

class InstallPublicKeyDialog(object):
    
    def __init__(self):
        self.dialog = gtk.Dialog(constants.installing_pk, None, 0, (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        self.dialog.set_default_response(gtk.RESPONSE_CLOSE)
        self.dialog.connect("response", self.hide)
        
    def install(self, username, server):
        vbox = self.dialog.get_child()
        pk_path = os.path.expanduser("~") + '/.ssh/id_rsa.pub'
        
        if os.path.exists(pk_path):
            import vte
            scroll = gtk.ScrolledWindow()
            scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
            v = vte.Terminal()
            scroll.add(v)
            vbox.add(scroll)
            cx = '%s@%s' % (username, server)
            cmd = ['/usr/bin/ssh-copy-id', cx]
            v.fork_command(cmd[0], cmd, None, None, False, False, False)
            self.dialog.resize(600, 400)
        else:
            label = gtk.Label()
            label.set_text(constants.public_key_rsa_not_found)
            vbox.add(label)
        self.dialog.show_all()
        
    def hide(self, dialog, response_id):
        self.dialog.hide()