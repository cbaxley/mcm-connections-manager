#!/bin/sh
#
# Install Script for MCM Connections Manager
# Please run as root
#
# This script is based on the one of pyjama.
#

# Clever way of testing for root
userpriv=$(test -w \/ && echo "ok")
if [ -z $userpriv ]
    then echo "Please run this script as root / sudo"
    exit 1
fi

install_dir="/usr/share/apps/mcm-connections-manager"
mcm_shell="${install_dir}/bin/mcm"

echo "1/3 Copying files to ${install_dir}"
mkdir -p ${install_dir} 2>/dev/null
cp -R * ${install_dir} 2>/dev/null

echo "2/3 Creating symlinks"
ln -s ${mcm_shell}  /usr/bin/mcm
ln -s ${mcm_shell}  /usr/bin/mcm-gtk

echo "3/3 Creating menu-entry for MCM Connections Manager"
cp ${install_dir}/mcm/gui/internet-network-preferences-tools-icone-5174.ico /usr/share/pixmaps/
cp ${install_dir}/docs/mcm.desktop /usr/share/applications/

echo "Done. MCM Connections Manager is ready"

exit 0
