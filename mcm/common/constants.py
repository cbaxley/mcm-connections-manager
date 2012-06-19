# - coding: utf-8 -
#
# Copyright (C) 2009 Alejandro Ayuso
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
File that contains all constants so it's easier to reuse, change and translate
str values.
'''

import os
import sys
import gettext
import locale
from xdg.BaseDirectory import xdg_config_home, xdg_data_home

version = '1.0'
app_name = "mcm connections manager"

home = os.getenv("HOME")
mcm_config_dir = os.path.join(xdg_config_home, 'mcm')
mcm_data_dir = os.path.join(xdg_data_home, 'mcm')
glade_home = os.path.realpath(os.path.dirname(sys.argv[0]))
icon_file = os.path.join(glade_home, "internet-network-preferences-tools-icone-5174-32.png")
tips_file = os.path.join(mcm_data_dir, "tips.json")
conf_file = os.path.join(mcm_config_dir, "mcm.conf")
cxs_json = os.path.join(mcm_data_dir, "mcm.json")
error_dialog = os.path.join(glade_home, "error.py")

# New Glade Files for GtkBuilder
glade_home = os.path.join(glade_home, "glade")
glade_main = os.path.join(glade_home, "main.glade")
glade_file_utils = os.path.join(glade_home, "file_utils_dialogs.glade")
glade_http = os.path.join(glade_home, "http.glade")
glade_preferences = os.path.join(glade_home, "preferences.glade")
glade_new_cx = os.path.join(glade_home, "new_connection.glade")
glade_edit_cx = os.path.join(glade_home, "edit_connections.glade")
glade_import = os.path.join(glade_home, "import_progress.glade")
glade_tips = os.path.join(glade_home, "tips.glade")

# ----------------------------------------------------------------------
# i18n stuff
# ----------------------------------------------------------------------

def get_languages():
    _langs = []
    lc, encd = locale.getdefaultlocale()
    if lc:
        _langs = [lc]

    language = os.environ.get('LANG', None)
    if language:
        _langs += language.split(":")

    _langs += ["en", "es"]
    return _langs

local_path = "%s/../i18n/locale/" % os.path.realpath(os.path.dirname(sys.argv[0]))
gettext.install('mcm', local_path)
gettext.bindtextdomain('mcm', local_path)
gettext.textdomain('mcm')
langs = get_languages()

lang = gettext.translation('mcm', local_path, languages=langs, fallback=True)
_ = lang.ugettext

# ----------------------------------------------------------------------
# i18n stuff
# ----------------------------------------------------------------------

window_title = "MCM - %s"

send_world = _("Send to the World")
google_docs_disclaimer = _("""If you select the option to send \
to the world, your tip will be sent to a Google Docs Spreadsheet \
using an online form. No personal information is sent, only \
the one you fill on the previous dialog.\n\nThis Form is \
online, and the results spreadsheet is public for everyone \
to see. Check the documentation for the links.\n\nIf you \
still feel the need to check on this go to the \
file \"common/utils.py\" and there is a class \
called \"GoogleForm\" where all this process happens.""")

io_error = _("Can\'t Access file %s")

google_search_url = "http://www.google.com/search?q=%s"

mcm_help_url = "http://sites.google.com/site/monocaffe/home/mcm/help"
tips_url = "http://launchpad.net/mcm/trunk/mcm/+download/tips.json"

tip_error = _("Not a Tip Object")

deleting_connection_warning = _("Deleting Connection %s")
are_you_sure = _("Are you sure?")

copy = _("Copy")
paste = _("Paste")
google_search = _("Google Search")
set_title = _("Set as Title")

press_enter_to_save = _("Press Enter to Save changes")

export_csv = _("Export to CSV done")
export_html = _("Export to HTML done")
saved_file = _("Saved file %s")

update_tips_error_1 = _("Unable to update tips file")
update_tips_error_2 = _("An error occurred, please check the log files for more information")
update_tips_success_1 = _("Tips Update Success")
update_tips_success_2 = _("The tips file has been updated successfully using %s. A backup file has been created.")

alias_error = _("This alias is already used")
alias_tooltip = _("The alias for the new connection. Must be unique.")

import_not_saving = _("Not saving %s\n")
import_saving = _("Saved %s\n")
cluster_checkbox_tooltip = _("Set For Clustered Commands")

quit_warning = _("Quitting MCM")

connection_error = _("An error has occurred, please check the output on the terminal for more information")

screenshot_info = _("Screenshot saved to:")
screenshot = _("Screenshot")
disconnect = _("Disconnect")
tools = _("Tools")
all_connections_filter_name = _("All")

# Column Titles
col_title_alias = _("Alias")
col_title_group = _("Group")
col_title_type = _("Type")
col_title_pwd = _("Password")
col_title_delete = _("Delete")
col_title_desc = _("Description")
col_title_host = _("Host")
col_title_port = _("Port")
col_title_user = _("Username")
col_title_opts = _("Options")

# color palettes
color_palletes = {
                  'Default':None,
                  'rxvt': '#cdcd00000000:#000000000000:#0000cdcd0000:#cdcdcdcd0000:#00000000cdcd:#cdcd0000cdcd:#0000cdcdcdcd:#fafaebebd7d7:#404040404040:#ffff00000000:#0000ffff0000:#ffffffff0000:#00000000ffff:#ffff0000ffff:#0000ffffffff:#ffffffffffff',
                  'xterm': '#cdcb00000000:#000000000000:#0000cdcb0000:#cdcbcdcb0000:#1e1a908fffff:#cdcb0000cdcb:#0000cdcbcdcb:#e5e2e5e2e5e2:#4ccc4ccc4ccc:#ffff00000000:#0000ffff0000:#ffffffff0000:#46458281b4ae:#ffff0000ffff:#0000ffffffff:#ffffffffffff',
                  'Tango' : '#cccc00000000:#000000000000:#4e4e9a9a0606:#c4c4a0a00000:#34346565a4a4:#757550507b7b:#060698209a9a:#d3d3d7d7cfcf:#555557575353:#efef29292929:#8a8ae2e23434:#fcfce9e94f4f:#72729f9fcfcf:#adad7f7fa8a8:#3434e2e2e2e2:#eeeeeeeeecec',
                  'Xubuntu Light': '#404040404040:#cececececece:#4e4e9a9a0606:#c4c4a0a00000:#34346565a4a4:#757550507b7b:#060698209a9a:#d3d3d7d7cfcf:#555557575353:#efef29292929:#8a8ae2e23434:#fcfce9e94f4f:#72729f9fcfcf:#adad7f7fa8a8:#3434e2e2e2e2:#eeeeeeeeecec', 
                  'Xubuntu Dark': '#cececececece:#404040404040:#4e4e9a9a0606:#c4c4a0a00000:#34346565a4a4:#757550507b7b:#060698209a9a:#d3d3d7d7cfcf:#555557575353:#efef29292929:#8a8ae2e23434:#fcfce9e94f4f:#72729f9fcfcf:#adad7f7fa8a8:#3434e2e2e2e2:#eeeeeeeeecec', 
                  'Zenburn': '#CCCC93939393:#3F3F3F3F3F3F:#7F7F9F9F7F7F:#E3E3CECEABAB:#DFDFAFAF8F8F:#CCCC93939393:#8C8CD0D0D3D3:#DCDCDCDCCCCC:#3F3F3F3F3F3F:#CCCC93939393:#7F7F9F9F7F7F:#E3E3CECEABAB:#DFDFAFAF8F8F:#CCCC93939393:#8C8CD0D0D3D3:#DCDCDCDCCCCC'
                  }
#palette_xubuntu_light =     ['#404040404040:#cececececece:#4e4e9a9a0606:#c4c4a0a00000:#34346565a4a4:#757550507b7b:#060698209a9a:#d3d3d7d7cfcf:#555557575353:#efef29292929:#8a8ae2e23434:#fcfce9e94f4f:#72729f9fcfcf:#adad7f7fa8a8:#3434e2e2e2e2:#eeeeeeeeecec']
#palette_xubuntu_dark =      ['#cececececece:#404040404040:#4e4e9a9a0606:#c4c4a0a00000:#34346565a4a4:#757550507b7b:#060698209a9a:#d3d3d7d7cfcf:#555557575353:#efef29292929:#8a8ae2e23434:#fcfce9e94f4f:#72729f9fcfcf:#adad7f7fa8a8:#3434e2e2e2e2:#eeeeeeeeecec']
#palette_zenburn =           ['#CCCC93939393:#3F3F3F3F3F3F:#7F7F9F9F7F7F:#E3E3CECEABAB:#DFDFAFAF8F8F:#CCCC93939393:#8C8CD0D0D3D3:#DCDCDCDCCCCC:#3F3F3F3F3F3F:#CCCC93939393:#7F7F9F9F7F7F:#E3E3CECEABAB:#DFDFAFAF8F8F:#CCCC93939393:#8C8CD0D0D3D3:#DCDCDCDCCCCC']
#palette_rxvt =              ['#000000000000:#cdcd00000000:#0000cdcd0000:#cdcdcdcd0000:#00000000cdcd:#cdcd0000cdcd:#0000cdcdcdcd:#fafaebebd7d7:#404040404040:#ffff00000000:#0000ffff0000:#ffffffff0000:#00000000ffff:#ffff0000ffff:#0000ffffffff:#ffffffffffff']
#palette_xterm =             ['#000000000000:#cdcb00000000:#0000cdcb0000:#cdcbcdcb0000:#1e1a908fffff:#cdcb0000cdcb:#0000cdcbcdcb:#e5e2e5e2e5e2:#4ccc4ccc4ccc:#ffff00000000:#0000ffff0000:#ffffffff0000:#46458281b4ae:#ffff0000ffff:#0000ffffffff:#ffffffffffff']
#palette_tango =             ['#000000000000:#cccc00000000:#4e4e9a9a0606:#c4c4a0a00000:#34346565a4a4:#757550507b7b:#060698209a9a:#d3d3d7d7cfcf:#555557575353:#efef29292929:#8a8ae2e23434:#fcfce9e94f4f:#72729f9fcfcf:#adad7f7fa8a8:#3434e2e2e2e2:#eeeeeeeeecec',]
