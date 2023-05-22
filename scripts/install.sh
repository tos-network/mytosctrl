#!/bin/bash
set -e

# Check sudo
if [ "$(id -u)" != "0" ]; then
	echo "Please run script as root"
	exit 1
fi

show_help_and_exit() {
    echo 'Supported argumets:'
    echo ' -m [lite|full]   Choose installation mode'
    echo ' -c  PATH         Provide custom config for tosinstaller.sh'
    echo ' -t               Disable telemetry'
    echo ' -i               Ignore minimum reqiurements'
    echo ' -d               Use pre-packaged dump. Reduces duration of initial synchronization.'
    echo ' -h               Show this help'
    exit
}

if [[ "${1-}" =~ ^-*h(elp)?$ ]]; then
    show_help_and_exit
fi

# Get arguments
config="https://tos.network/global-config.json"
telemetry=true
ignore=false
dump=false
while getopts m:c:tidh flag
do
	case "${flag}" in
		m) mode=${OPTARG};;
		c) config=${OPTARG};;
		t) telemetry=false;;
		i) ignore=true;;
		d) dump=true;;
        h) show_help_and_exit;;
        *)
            echo "Flag -${flag} is not recognized. Aborting"
            exit 1 ;;
	esac
done


# Checking the installation mode
if [ "${mode}" != "lite" ] && [ "${mode}" != "full" ]; then
	echo "Run script with flag '-m lite' or '-m full'"
	exit 1
fi

# Capacity check
cpus=$(lscpu | grep "CPU(s)" | head -n 1 | awk '{print $2}')
memory=$(grep MemTotal /proc/meminfo | awk '{print $2}')
if [ "${mode}" = "lite" ] && [ "$ignore" = false ] && ([ "${cpus}" -lt 2 ] || [ "${memory}" -lt 2000000 ]); then
	echo "Insufficient resources. Requires a minimum of 2 processors and 2Gb RAM."
	exit 1
fi
if [ "${mode}" = "full" ] && [ "$ignore" = false ] && ([ "${cpus}" -lt 8 ] || [ "${memory}" -lt 8000000 ]); then
	echo "Insufficient resources. Requires a minimum of 8 processors and 8Gb RAM."
	exit 1
fi

# Colors
COLOR='\033[92m'
ENDC='\033[0m'

# Start installing mytosctrl
echo -e "${COLOR}[1/4]${ENDC} Starting installation MyTosCtrl"
mydir=$(pwd)

# On OSX there is no such directory by default, so we create...
SOURCES_DIR=/usr/src
BIN_DIR=/usr/bin
if [[ "$OSTYPE" =~ darwin.* ]]; then
	SOURCES_DIR=/usr/local/src
	BIN_DIR=/usr/local/bin
	mkdir -p ${SOURCES_DIR}
fi

# Check for TOS components
echo -e "${COLOR}[2/4]${ENDC} Checking for required TOS components"
file1=${BIN_DIR}/tos/crypto/fift
file2=${BIN_DIR}/tos/lite-client/lite-client
file3=${BIN_DIR}/tos/validator-engine-console/validator-engine-console
if [ -f "${file1}" ] && [ -f "${file2}" ] && [ -f "${file3}" ]; then
	echo "TOS exist"
	cd $SOURCES_DIR
	rm -rf $SOURCES_DIR/mytosctrl
	git clone --recursive https://github.com/tos-network/mytosctrl.git
else
	rm -f tosinstaller.sh
	wget https://raw.githubusercontent.com/tos-network/mytosctrl/master/scripts/tosinstaller.sh
	bash tosinstaller.sh -c "${config}"
	rm -f tosinstaller.sh
fi

# Run the installer mytosinstaller.py
echo -e "${COLOR}[3/4]${ENDC} Launching the mytosinstaller.py"
parent_name=$(ps -p $PPID -o comm=)
user=$(whoami)
if [ "$parent_name" = "sudo" ]; then
    user=$(logname)
fi
python3 ${SOURCES_DIR}/mytosctrl/mytosinstaller.py -m ${mode} -u ${user} -t ${telemetry} --dump ${dump}

# Exit the program
echo -e "${COLOR}[4/4]${ENDC} Mytosctrl installation completed"
exit 0
