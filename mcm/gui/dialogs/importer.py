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

import gtk
import mcm.common.connections
from mcm.common import constants

class ImportProgressDialog(object):

    def __init__(self, uri):
        self.uri = uri
        self.connections = mcm.common.connections.ConnectionStore()
        self.connections.load()
        
        self.dialog = gtk.Dialog(constants.connections_manager, 
             None, gtk.DIALOG_MODAL,
             ( gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
               gtk.STOCK_SAVE, gtk.RESPONSE_OK ))
        self.dialog.set_default_response(gtk.RESPONSE_CLOSE)
        self.dialog.connect('response', self.dialog_response_event)
        self.dialog.set_size_request(500, 300)
        
        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        self.results = gtk.TextView()
        self.results.set_visible(True)
        self.results.set_editable(False)
        self.results.set_wrap_mode(gtk.WRAP_WORD)
        self.results.set_cursor_visible(False)
        self.results.set_accepts_tab(False)
        self.scroll.add(self.results)
        self.scroll.show_all()
        
        self.total_progress = gtk.ProgressBar()
        self.total_progress.show()
        
        self.dialog.get_content_area().pack_start(self.scroll, True, True, 0)
        self.dialog.get_content_area().pack_start(self.total_progress, False, True, 1)

    def run(self):
        self._import_connections()
        self.dialog.run()

    def close_event(self, widget=None):
        self.dialog.destroy()
        
    def dialog_response_event(self, this, response_id):
        if response_id == gtk.RESPONSE_OK:
            self.response = gtk.RESPONSE_OK
            self.connections.save()
        self.dialog.destroy()
        
    def _import_connections(self, pattern="alias"):
        """Returns a list with a dict"""
        import csv
        import_count = 0
        existing_aliases = self.connections.get_aliases()
        with open(self.uri, 'rb') as csv_file:
            csvreader = csv.DictReader(csv_file, fieldnames=mcm.common.connections.fields, dialect='mcm')
            for row in csvreader:
                cx = mcm.common.connections.mapped_connections_factory(row)
                if cx:
                    if cx.alias not in existing_aliases:
                        self.connections.add(cx.alias, cx)
                        import_count += 1
                        self.write_result(constants.import_saving % cx)
                    else:
                        self.write_result(constants.import_not_saving % cx.alias)
                else:
                    self.write_result("Failed to import line %s" % csvreader.line_num)
                self.total_progress.set_text("Imported %s/%s" % (import_count, csvreader.line_num))
                self.total_progress.pulse()
            self.total_progress.set_fraction(1.0)
        
    def write_result(self, text):
        buf = self.results.get_buffer()
        if buf == None:
            buf = gtk.TextBuffer()
            self.results.set_buffer(buf)
        buf.insert_at_cursor(text)