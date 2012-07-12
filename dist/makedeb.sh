#!/bin/bash
#
# Creates the Structure for a deb

rm -rf /tmp/pack
mkdir -p /tmp/pack/usr/share/apps/mcm-connections-manager
mkdir -p /tmp/pack/DEBIAN
cp -R ../* /tmp/pack/usr/share/apps/mcm-connections-manager
cp debian/* /tmp/pack/DEBIAN/

cd /tmp/
dpkg -b pack mcm-1.1_all.deb
