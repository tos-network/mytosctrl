#!/bin/bash
set -e

# check sudo
if [ "$(id -u)" != "0" ]; then
	echo "Please run script as root"
	exit 1
fi

# Get arguments
while getopts u: flag
do
	case "${flag}" in
		u) user=${OPTARG};;
	esac
done

# Colors
COLOR='\033[92m'
ENDC='\033[0m'

# Install python3 components
echo -e "${COLOR}[1/4]${ENDC} Installing required packages"
pip3 install pipenv==2022.3.28

# Clone repositories from github.com
echo -e "${COLOR}[2/4]${ENDC} Cloning github repository"
cd /usr/src
rm -rf pytosv3
git clone https://github.com/tomisetsu/pytosv3

# Installing the module
cd /usr/src/pytosv3
python3 setup.py install

# Compile the missing binary
cd /usr/bin/tos && make toslibjson

# Register autoload
echo -e "${COLOR}[3/4]${ENDC} Add to startup"
cmd="from sys import path; path.append('/usr/src/mytosctrl/'); from mypylib.mypylib import *; Add2Systemd(name='pytosv3', user='${user}', workdir='/usr/src/pytosv3', start='/usr/bin/python3 -m pyTOS --liteserverconfig /usr/bin/tos/local.config.json --libtoslibjson /usr/bin/tos/toslib/libtoslibjson.so')"
python3 -c "${cmd}"
systemctl restart pytosv3

# End
echo -e "${COLOR}[4/4]${ENDC} pyTOSv3 installation complete"
exit 0
