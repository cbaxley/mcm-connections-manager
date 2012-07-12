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

import mcm.common.utils
import mcm.common.connections
import mcm.gui.dialogs.importer
import mcm.gui.widgets

from mcm.common import constants

class MCMCryptoDialog(object):
    
    def __init__(self, out_file_path=None, in_file_path=None):
        self.in_file_path = in_file_path
        self.out_file_path = out_file_path
        self.response = gtk.RESPONSE_CANCEL
        self.dialog = gtk.Dialog(constants.provide_password, 
             None, gtk.DIALOG_MODAL,
             ( gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK ))
        self.dialog.set_default_response(gtk.RESPONSE_CANCEL)
        self.dialog.connect('response', self.dialog_response_event)
        self.pwd_entry = gtk.Entry()
        self.pwd_entry.set_visibility(False)
        self.pwd_entry.show()
        self.dialog.get_content_area().pack_start(self.pwd_entry, True, True, 0)
        
    def run(self):
        self.dialog.run()
        
    def destroy(self):
        pass

    def dialog_response_event(self, this, response_id):
        if response_id == gtk.RESPONSE_OK:
            self.response = gtk.RESPONSE_OK
            if self.in_file_path:
                temp_file = self._decrypt(self.in_file_path)
                if temp_file:
                    dlg = mcm.gui.dialogs.importer.ImportProgressDialog(temp_file)
                    dlg.run()
                    os.remove(temp_file)
                else:
                    mcm.gui.widgets.show_error_dialog(constants.failed_decrypt_import, constants.failed_decrypt_import)
            else:
                temp_file = self._export()
                self._encrypt(temp_file)
        self.dialog.destroy()
        
    def _export(self):
        connections = mcm.common.connections.ConnectionStore()
        connections.load()
        return mcm.common.utils.export_csv(connections)
        
    def _encrypt(self, temp_file):
        import hashlib
        key = hashlib.sha256(self.pwd_entry.get_text()).digest()
        mcm.common.utils.encrypt_file(key, temp_file, self.out_file_path)
        os.remove(temp_file)
        
    def _decrypt(self, in_filename):
        import hashlib
        key = hashlib.sha256(self.pwd_entry.get_text()).digest()
        return mcm.common.utils.decrypt_file(key, in_filename)
