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
import mcm.gui.widgets
import mcm.common.export
from mcm.common import constants

class ManageConnectionsDialog(object):

    def __init__(self):
        self.response = gtk.RESPONSE_CANCEL
        self.connections = mcm.common.connections.ConnectionStore()
        self.connections.load()
        self.groups = self.connections.get_groups()
        self.types = mcm.common.connections.types.keys()
        self.dialog = gtk.Dialog(constants.connections_manager, 
             None, gtk.DIALOG_MODAL,
             ( gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK ))
        self.dialog.set_default_response(gtk.RESPONSE_CANCEL)
        self.dialog.connect('response', self.dialog_response_event)
        self.dialog.set_size_request(600, 300)
        v_box = self.dialog.get_content_area()
        self.tree_container = gtk.ScrolledWindow()
        self.tree_container.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.draw_tree()
        v_box.pack_start(self.tree_container, True, True, 0)

    def draw_tree(self):
        view = self.connections_view()
        self.tree_container.add(view)
        self.tree_container.show_all()

    def run(self):
        self.dialog.run()
        
    def destroy(self):
        pass

    def dialog_response_event(self, this, response_id):
        if response_id == gtk.RESPONSE_OK:
            self.response = gtk.RESPONSE_OK
            self.connections.save()
        self.dialog.destroy()
    
    def event_export(self, widget):
        dlg = mcm.gui.widgets.FileSelectDialog(True)
        dlg.run()
        if dlg.response == gtk.RESPONSE_OK and dlg.mime == 'html':
            _html = mcm.common.export.Html(constants.version, self.connections)
            _html.export(dlg.get_filename())
            mcm.gui.widgets.show_info_dialog(constants.export_finished, constants.saved_file % dlg.get_filename())
        elif dlg.response == gtk.RESPONSE_OK and dlg.mime == 'csv':
            _csv = mcm.common.utils.export_csv(self.connections, dlg.get_filename())
            mcm.gui.widgets.show_info_dialog(constants.export_finished, constants.saved_file % dlg.get_filename())

    def init_combo(self, items, active_item=None):
        cb = gtk.CellRendererCombo()
        cb_index = self.set_model_from_list(cb, items)
        if active_item:
            active = cb_index[active_item]
            cb.set_active(active)
        return cb

    def set_model_from_list(self, cb, items):
        """Setup a CellRendererCombo based on a list of strings."""           
        model = gtk.ListStore(str)
        index = {}
        j = 0
        for i in items:
            model.append([i])
            index[i] = j
            j += 1
        cb.set_property('model', model)
        cb.set_property('text-column', 0)
        cb.set_property('editable', True)
        cb.set_property('has-entry', False)
        return index

    def type_edited_event(self, widget, path, new_iter, model):
        self.update_combo_cell(widget, path, 1, new_iter, model)
    
    def group_edited_event(self, widget, path, new_iter, model):
        self.update_combo_cell(widget, path, 7, new_iter, model)
    
    def update_cell(self, widget, pos_x, new_value, model):
        pos_y = widget.pos_y
        model[pos_x][pos_y] = new_value
        alias = model[pos_x][0]
        cx = self.connections.get(alias)
        if pos_y is 4:
            cx.user = new_value
        elif pos_y is 2:
            cx.host = new_value
        elif pos_y is 3:
            cx.port = new_value
        elif pos_y is 6:
            cx.options = new_value
        elif pos_y is 5:
            cx.password = new_value
        elif pos_y is 8:
            cx.description = new_value
        
        self.connections.update(alias, cx)
        
    def update_combo_cell(self, widget, pos_x, pos_y, new_iter, model):
        new_value = widget.props.model.get_value(new_iter, 0)
        model[pos_x][pos_y] = new_value
        alias = model[pos_x][0]
        cx = self.connections.get(alias)
        if pos_y is 1:
            cx = mcm.common.connections.connections_factory(new_value, 
                                                             cx.user, 
                                                             cx.host, 
                                                             cx.alias, 
                                                             cx.password, 
                                                             cx.port, 
                                                             cx.group, 
                                                             cx.options, 
                                                             cx.description)
        elif pos_y is 7:
            cx.group = new_value
            
        self.connections.update(alias, cx)

    def cell_click_event(self, widget, event):
        path = widget.get_path_at_pos(int(event.x), int(event.y))
        active_column = path[1]
        col_title = active_column.get_title()
        if col_title == constants.col_title_delete and event.type == gtk.gdk._2BUTTON_PRESS:
            cursor = widget.get_selection()
            (model, a_iter) = cursor.get_selected()
            alias = model.get_value(a_iter, 0)
            response = mcm.gui.widgets.show_question_dialog(constants.deleting_connection_warning % alias, constants.are_you_sure)
            if response == gtk.RESPONSE_OK:
                model.remove(a_iter)
                self.connections.delete(alias)

    def connections_view(self):
        store = self.connections_model()
        view = gtk.TreeView(store)

        for column in self.generate_columns(store):
            view.append_column(column)

        # Configure Tree Properties
        view.set_headers_clickable(True)
        view.set_rules_hint(True)
        view.set_search_column(0)
        view.columns_autosize()
        view.connect('button-press-event', self.cell_click_event)

        return view

    def generate_columns(self, store):
        columns = []
        
        # For each column we need a renderer so we can easily pick the cell value
        alias_renderer = gtk.CellRendererText()

        # We create the CellRendererCombo with the given models and then feed this models to the event
        types_combo_renderer = self.init_combo(self.types)
        types_combo_renderer.connect('changed', self.type_edited_event, store)
        types_combo_renderer.pos_y = 1
        
        groups_combo_renderer = self.init_combo(self.groups)
        groups_combo_renderer.connect('changed', self.group_edited_event, store)
        groups_combo_renderer.pos_y = 7
        
        user_renderer = self.get_new_cell_renderer(True, 4, store)
        host_renderer = self.get_new_cell_renderer(True, 2, store)
        port_renderer = self.get_new_cell_renderer(True, 3, store)
        opts_renderer = self.get_new_cell_renderer(True, 6, store)
        pwd_renderer = self.get_new_cell_renderer(True, 5, store)
        desc_renderer = self.get_new_cell_renderer(True, 8, store)
        
        # Renderer for the delete button
        img_renderer = gtk.CellRendererPixbuf()
        
        # Make the first row sortable
        col = gtk.TreeViewColumn(constants.col_title_alias, alias_renderer, text=0)
        col.set_sort_column_id(0)
        #col.set_resizable(True)
        #col.set_expand(True)
        
        columns.append(col)
        columns.append(self.get_new_column(constants.col_title_type, types_combo_renderer, True))
        columns.append(self.get_new_column(constants.col_title_group, groups_combo_renderer, True))
        columns.append(self.get_new_column(constants.col_title_user, user_renderer, True))
        columns.append(self.get_new_column(constants.col_title_host, host_renderer, True))
        columns.append(self.get_new_column(constants.col_title_port, port_renderer))
        columns.append(self.get_new_column(constants.col_title_opts, opts_renderer))
        columns.append(self.get_new_column(constants.col_title_pwd, pwd_renderer))
        columns.append(self.get_new_column(constants.col_title_desc, desc_renderer, False, True))
        
        # Finally we append the delete button column
        del_col = gtk.TreeViewColumn(constants.col_title_delete, img_renderer, pixbuf=9)
        del_col.set_resizable(False)
        del_col.set_expand(False)
        columns.append(del_col)

        return columns

    def connections_model(self):
        """Creates a ListStore with the Connections data"""
        store = gtk.ListStore(str, str, str, str, str, str, str, str, str, gtk.gdk.Pixbuf)
        img = self.dialog.render_icon(gtk.STOCK_CLEAR, gtk.ICON_SIZE_BUTTON)
        for cx in self.connections.get_all():
            cx_list = cx.to_list()
            cx_list.append(img)
            store.append(cx_list)
        return store
    
    def get_new_column(self, title, renderer, sort=False, expand=False):
        col = gtk.TreeViewColumn(title, renderer, text=renderer.pos_y)
        col.set_resizable(False)
        col.set_expand(expand)
        if sort:
            col.set_sort_column_id(renderer.pos_y)
        return col
    
    def get_new_cell_renderer(self, editable, pos_y, store):
        renderer = gtk.CellRendererText()
        renderer.set_property( 'editable', editable)
        renderer.pos_y = pos_y
        renderer.connect('edited', self.update_cell, store )
        return renderer