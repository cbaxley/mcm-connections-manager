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
Configuration Loading for file ~/.mcm
'''

import ConfigParser
import os
import pango
import mcm.common.constants as constants


class McmConfig(object):

    def __init__(self):
        self.config = ConfigParser.SafeConfigParser()
        self.cfgfile = constants.conf_file
        self.config.read(self.cfgfile)
        self.configuration = None

    def get_config(self):
        if not self.configuration:
            self.configuration = {}
            for option in self.config.options("mcm"):
                self.configuration[option] = self.config.get("mcm", option)
        return self.configuration

    def save_config(self):
        """Receives a dictionary with the options to be saved"""
        for k, v in self.configuration.items():
            self.config.set("mcm", k, v)
        self.config.write(open(self.cfgfile, 'w'))

    def get_ssh_conf(self):
        conf = self.get_config()
        return (conf['binary-ssh'], conf['default-options-ssh'])
    
    def set_ssh_conf(self, binary, options):
        self.get_config()['binary-ssh'] = binary
        self.get_config()['default-options-ssh'] = options

    def get_vnc_conf(self):
        """Returns a tuple"""
        conf = self.get_config()
        try:
            embedded = self.parse_boolean(conf['embedded-vnc'])
            return (conf['binary-vnc'], conf['default-options-vnc'], embedded)
        except KeyError:
            return (conf['binary-vnc'], conf['default-options-vnc'], False)
        
    def set_vnc_conf(self, binary, options, embedded):
        self.get_config()['binary-vnc'] = binary
        self.get_config()['default-options-vnc'] = options
        self.get_config()['embedded-vnc'] = embedded

    def get_rdp_conf(self):
        conf = self.get_config()
        return (conf['binary-rdp'], conf['default-options-rdp'])
    
    def set_rdp_conf(self, binary, options):
        self.get_config()['binary-rdp'] = binary
        self.get_config()['default-options-rdp'] = options

    def get_telnet_conf(self):
        conf = self.get_config()
        return (conf['binary-telnet'], conf['default-options-telnet'])
    
    def set_telnet_conf(self, binary, options):
        self.get_config()['binary-telnet'] = binary
        self.get_config()['default-options-telnet'] = options

    def get_ftp_conf(self):
        conf = self.get_config()
        return (conf['binary-ftp'], conf['default-options-ftp'])
    
    def set_ftp_conf(self, binary, options):
        self.get_config()['binary-ftp'] = binary
        self.get_config()['default-options-ftp'] = options

    def get_bg_color(self):
        try:
            conf = self.get_config()
            return conf['color-background']
        except KeyError:
            return '#000000000000'

    def get_fg_color(self):
        try:
            conf = self.get_config()
            return conf['color-foreground']
        except KeyError:
            return '#3341ffff0000'
        
    def get_cursor_color(self):
        try:
            conf = self.get_config()
            return conf['color-cursor']
        except KeyError:
            return '#a3d6a3d6a3d6'
        
    def get_selection_color(self):
        try:
            conf = self.get_config()
            return conf['color-selection']
        except KeyError:
            return '#e3d6e3d6e3d6'
        
    def get_tint_color(self):
        try:
            conf = self.get_config()
            return conf['color-tint']
        except KeyError:
            return '#262656568080' # test this color is appropriate!

    def get_bg_image(self):
        """
        Checks if the image file given in the configuration exists and is accessible.
        Returns the path if all conditions are met. Empty string else.
        """
        conf = self.get_config()
        if os.path.isfile(conf['background-image']) and \
        os.access(conf['background-image'], os.R_OK):
            return conf['background-image']
        else:
            return ""

    def get_bg_transparent(self):
        try:
            conf = self.get_config()
            return conf['background-transparent'] == 'True'
        except KeyError:
            return False

    def get_bg_saturation(self):
        """
            If a background image has been set and the saturation value is less than 100, 
            the terminal will adjust the colors of the image before drawing the image. 
            To do so, the terminal will create a copy of the background image 
            (or snapshot of the root window) and modify its pixel values.
            Returns a value between 0 and 100
        """
        try:
            conf = self.get_config()
            return int(conf['background-saturation']) / 100
        except KeyError:
            return 0
        
    def get_bg_opacity(self):
        """
            Sets the opacity of the terminal background, were 0 means 
            completely transparent and 100 means completely opaque. 
        """
        try:
            conf = self.get_config()
            return (int(conf['background-opacity']) * 65535) / 100
        except KeyError:
            return 0
        
    def get_pallete(self):
        """
            Returns a list of 14 colors
        """
        try:
            selected_pallete = self.get_config()['color-palette']
            colors = constants.color_palletes[selected_pallete].split(':')
            return colors
        except Exception:
            print "Failed to get the color palette"
        return None
        
    def get_pallete_name(self):
        try:
            return self.get_config()['color-palette']
        except KeyError:
            return 'DEFAULT'
    
    def set_pallete_name(self, pallete):
        self.get_config()['color-palette'] = pallete

    def get_font(self):
        try:
            conf = self.get_config()
            return pango.FontDescription(conf['font-name'])
        except KeyError:
            return pango.FontDescription("Monospace 10")
        
    def set_font(self, font):
        self.get_config()['font-name'] = font

    def get_word_chars(self):
        try:
            conf = self.get_config()
            return conf['word-chars']
        except KeyError:
            return "-A-Za-z0-9,./?&#:_"
        
    def set_word_chars(self, chars):
        self.get_config()['word-chars'] = chars
        
    def get_cursor_shape(self):
        """
            Returns the name of the cursor shape to be used.
            Default is BLOCK
        """
        try:
            conf = self.get_config()
            return conf['cursor-shape']
        except KeyError:
            return "BLOCK"

    def get_buffer_size(self):
        try:
            conf = self.get_config()
            size = int(conf['buffer-size'])
            if size:
                if size < 500:
                    return 500
                else:
                    return size
            else:
                return 500
        except KeyError:
            return 500
        
    def set_buffer_size(self, size):
        if isinstance(size, float):
            size = str(int(size))
        elif isinstance(size, int):
            size = str(size)
        self.get_config()['buffer-size'] = size
        
    # KeyBindings configurations
    
    def get_kb_tab_switch(self):
        try:
            conf = self.get_config()
            return conf['key-switch']
        except KeyError:
            return "<Alt>"
    
    def get_kb_tab_close(self):
        try:
            conf = self.get_config()
            return conf['key-close']
        except KeyError:
            return "<Shift><Ctrl>w"
    
    def get_kb_copy(self):
        try:
            conf = self.get_config()
            return conf['key-copy']
        except KeyError:
            return "<Shift><Ctrl>c"
    
    def get_kb_paste(self):
        try:
            conf = self.get_config()
            return conf['key-paste']
        except KeyError:
            return "<Shift><Ctrl>v"
    
    def get_kb_home(self):
        try:
            conf = self.get_config()
            return conf['key-home']
        except KeyError:
            return "<Shift><Ctrl>T"
    
    def get_kb_hide(self):
        try:
            conf = self.get_config()
            return conf['key-hide']
        except KeyError:
            return "F2"

    def parse_boolean(self, b):
        if b == False or b == True:
            return b
        b = b.strip()
        if len(b) < 1:
            raise ValueError ('Cannot parse empty string into boolean.')
        b = b[0].lower()
        if b == 't' or b == 'y' or b == '1':
            return True
        if b == 'f' or b == 'n' or b == '0':
            return False
        raise ValueError ('Cannot parse string into boolean.')
