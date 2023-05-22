#!/bin/bash
set -e

# Check sudo
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
COLOR='\033[95m'
ENDC='\033[0m'

# Install python3 components
echo -e "${COLOR}[1/4]${ENDC} Installing required packages"
pip3 install Werkzeug json-rpc cloudscraper pyotp

# Clone repositories from github.com
echo -e "${COLOR}[2/4]${ENDC} Cloning github repository"
cd /usr/src/
rm -rf mtc-jsonrpc
git clone --recursive https://github.com/tomisetsu/mtc-jsonrpc.git

# Register autoload
echo -e "${COLOR}[3/4]${ENDC} Add to startup"
cmd="from sys import path; path.append('/usr/src/mytosctrl/'); from mypylib.mypylib import *; Add2Systemd(name='mtc-jsonrpc', user='${user}', start='/usr/bin/python3 /usr/src/mtc-jsonrpc/mtc-jsonrpc.py')"
python3 -c "${cmd}"
systemctl restart mtc-jsonrpc

# Exit the program
echo -e "${COLOR}[4/4]${ENDC} JsonRPC installation complete"
exit 0
