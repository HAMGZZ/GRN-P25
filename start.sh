#!/bin/bash
sudo mkdir /tmp/ramdisk
sudo chmod 777 /tmp/ramdisk
sudo mount -t tmpfs -o size=10m ramdisk /tmp/ramdisk
touch /tmp/ramdisk/p25Data.gzz
touch /tmp/ramdisk/p25DataSrc.gzz
python3 P25-Control.py