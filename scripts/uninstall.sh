#!/bin/bash

# Check sudo
if [ "$(id -u)" != "0" ]; then
	echo "Please run script as root"
	exit 1
fi

# Colors
COLOR='\033[34m'
ENDC='\033[0m'

# Stop services
systemctl stop validator
systemctl stop mytoscore
systemctl stop dht-server

# variables
str=$(systemctl cat mytoscore | grep User | cut -d '=' -f2)
user=$(echo ${str})

# Removing services
rm -rf /etc/systemd/system/validator.service
rm -rf /etc/systemd/system/mytoscore.service
rm -rf /etc/systemd/system/dht-server.service
systemctl daemon-reload

# Deleting files
rm -rf /usr/src/tos
rm -rf /usr/src/mytosctrl
rm -rf /usr/bin/tos
rm -rf /var/tos-work
rm -rf /var/tos-dht-server
rm -rf /tmp/mytos*
rm -rf /usr/local/bin/mytosinstaller/
rm -rf /usr/local/bin/mytoscore/mytoscore.db
rm -rf /home/${user}/.local/share/mytosctrl
rm -rf /home/${user}/.local/share/mytoscore/mytoscore.db

# Removing links
rm -rf /usr/bin/fift
rm -rf /usr/bin/liteclient
rm -rf /usr/bin/validator-console
rm -rf /usr/bin/mytosctrl

# End
echo -e "${COLOR}Uninstall Complete${ENDC}"
