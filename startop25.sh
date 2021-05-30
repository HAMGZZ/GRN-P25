#!/bin/sh

rm /tmp/ramdisk/*
./rx.py --args 'rtl' -N 'LNA:45' -S 97600 -x 2 -f 416.2875e6 -o 17e3 -d -200 -2 -T trunk.tsv -V -U -w 2> stderr-stream0.2 > /dev/null 
