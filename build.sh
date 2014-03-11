#!/bin/sh

rst=$1

if [ "$rst" = "" ]; then
    echo "Usage: ./build.sh rst-file"
    exit
fi

rst2html --stylesheet wypy.css --embed-stylesheet $rst > templates/index.html
