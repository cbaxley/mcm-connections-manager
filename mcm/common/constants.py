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

# New Glade Files for GtkBuilder
glade_home = os.path.join(glade_home, "glade")
glade_main = os.path.join(glade_home, "main.glade")
glade_preferences = os.path.join(glade_home, "preferences.glade")
glade_new_cx = os.path.join(glade_home, "new_connection.glade")
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

io_error = _("Can\'t Access file %s")

google_search_url = "http://www.google.com/search?q=%s"

mcm_help_url = "http://code.google.com/p/mcm-connections-manager/"
tips_url = "http://launchpad.net/mcm/trunk/mcm/+download/tips.json"
tip_error = _("Not a Tip Object")
deleting_connection_warning = _("Deleting Connection %s")
are_you_sure = _("Are you sure?")
copy = _("Copy")
paste = _("Paste")
google_search = _("Google Search")
set_title = _("Set as Title")
install_key = _("Install public key")
press_enter_to_save = _("Press Enter to Save changes")
export_finished = _("Export finished")
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

select_file_to_import = _("Select File to Import")
select_file_to_export = _("Select File to Export")

# color palettes
color_palletes = {
    'Default': None,
    'rxvt': '#000000:#FAEBD7:#FAEBD7:#FAEBD7:#000000:#CD0000:#00CD00:#CDCD00:#0000CD:#CD00CD:#00CDCD:#FAEBD7:#404040:#FF0000:#00FF00:#FFFF00:#0000FF:#FF00FF:#00FFFF:#FFFFFF',
    'xterm': '#000000:#C0C0C0:#C0C0C0:#C0C0C0:#000000:#CD0000:#00CD00:#CDCD00:#1E90FF:#CD00CD:#00CDCD:#E5E5E5:#4C4C4C:#FF0000:#00FF00:#FFFF00:#4682B4:#FF00FF:#00FFFF:#FFFFFF',
    'Tango': '#000000:#C0C0C0:#C0C0C0:#C0C0C0:#000000:#CC0000:#4E9A06:#C4A000:#3465A4:#75507B:#06989A:#D3D7CF:#555753:#EF2929:#8AE234:#FCE94F:#729FCF:#AD7FA8:#34E2E2:#EEEEEC',
    'Greybird': '#CECECE:#404040:#E3E3E3:#A3A3A3:#000000:#660A0A:#006619:#4E2E66:#17344D:#801280:#008080:#3578B3:#999999:#800C0C:#00A629:#9D5CCC:#265680:#CC1ECC:#00AAAA:#5293CC',
    'Zenburn': '#3F3F3F:#DCDCCC:#DCDCCC:#DCDCCC:#3F3F3F:#CC9393:#7F9F7F:#E3CEAB:#DFAF8F:#CC9393:#8CD0D3:#DCDCCC:#3F3F3F:#CC9393:#7F9F7F:#E3CEAB:#DFAF8F:#CC9393:#8CD0D3:#DCDCCC',
    'Solarized Light': '#fdf6e3:#657b83:#657b83:#657b83:#002B36:#DC322F:#859900:#6C71C4:#268BD2:#D33682:#2AA198:#EEE8D5:#002B36:#DC322F:#859900:#6C71C4:#268BD2:#D33682:#2AA198:#EEE8D5',
    'Solarized Dark': '#002B36:#839496:#839496:#839496:#002B36:#DC322F:#859900:#6C71C4:#268BD2:#D33682:#2AA198:#EEE8D5:#002B36:#DC322F:#859900:#6C71C4:#268BD2:#D33682:#2AA198:#EEE8D5'}

default_error_color = "#FFADAD"
public_key_rsa_not_found = _("Please generate your\nPublic Key with ssh-keygen -t rsa")
unexpected_exit_code = _("Unexpected Exit Code")
connection_terminated = _("The connection was terminated with status code %s")
connections_manager = _("Connections Manager")
failed_decrypt_import = _("Failed to decrypt file probably to a wrong password")
