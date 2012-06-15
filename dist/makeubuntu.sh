#!/bin/bash
#
# Uploads a PPA package to Launchpad

tmp_ppa_dir="/tmp/ppa"
artefact="mcm_0.9.4"

if [ -d ${tmp_ppa_dir} ]; then
    rm -rf /tmp/ppa
    mkdir -p ${tmp_ppa_dir}/${artefact}
fi

cp -R ../* ${tmp_ppa_dir}/${artefact}

cd ${tmp_ppa_dir}/${artefact}

mv dist/debian debian

tar -czf ../${artefact}.orig.tar.gz 

# generate the needed files

debuild -S -sd

# upload

cd ../

dput monocaffe-ppa ${artefact}-0ubuntu1_source.changes 
