#!/bin/sh


./rx.py --args 'rtl' -N 'LNA:47' -S 57600 -x 2 -f 416.2875e6 -o 17e3 -d -200 -2 -T trunk.tsv -V -U -w -v 5 2> stderr-stream0.2 > /dev/null 
