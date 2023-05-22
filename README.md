## What is MyTosCtrl?
This console is a wrapper over `fift`,`lite-client` and `validator-engine-console`. It was created to facilitate wallet, domain and validator management on Ubuntu OS.

## Functionality
- [x] Show TOS network status
- [x] Management of local wallets
	- [x] Create local wallet
	- [x] Activate local wallet
	- [x] Show local wallets
	- [x] Import wallet from file (.pk)
	- [x] Save wallet address to file (.addr)
	- [x] Delete local wallet
- [x] Show account status
	- [x] Show account balance
	- [x] Show account history
	- [x] Show account status from bookmarks
- [x] Transferring funds to the wallet
	- [x] Transfer of a fixed amount
	- [x] Transfer of the entire amount (all)
	- [x] Transfer of the entire amount with wallet deactivation (alld)
	- [x] Transferring funds to the wallet from bookmarks
	- [x] Transferring funds to a wallet through a chain of self-deleting wallets
- [x] Manage bookmarks
	- [x] Add account to bookmarks
	- [x] Show bookmarks
	- [x] Delete bookmark
- [x] Offer management
	- [x] Show offers
	- [x] Vote for the proposal
	- [x] Automatic voting for previously voted proposals
- [x] Domain management
	- [x] Rent a new domain
	- [x] Show rented domains
	- [x] Show domain status
	- [x] Delete domain
	- [ ] Automatic domain renewal
- [x] Controlling the validator
	- [x] Participate in the election of a validator
	- [x] Return bet + reward
	- [x] Autostart validator on abnormal termination (systemd)

## List of tested operating systems
```
Ubuntu 22.04.2 LTS (Jammy Jellyfish) - OK
```

## Installation scripts overview
- `tosinstaller.sh`: clones `TOS` and` mytosctrl` sources to `/usr/src/tos` and`/usr/src/mytosctrl` folders, compiles programs from sources and writes them to `/usr/bin/`.
- `mytosinstaller.py`: configures the validator and `mytosctrl`; generates validator connection keys.

## Installation modes
There are two installation modes: `lite` and` full`. They both **compile** and install `TOS` components. However the `lite` version does not configure or run the node/validator.

## Installation for Ubuntu
1. Download and execute the `install.sh` script in the desired installation mode. During installation the script prompts you for the superuser password several times.
```sh
wget https://raw.githubusercontent.com/tos-network/mytosctrl/master/scripts/install.sh
sudo bash install.sh -m <mode>
```

2. Done. You can try to run the `mytosctrl` console now.
```sh
mytosctrl
```

## Web admin panel
To control the node/validator through the browser, you need to install an additional module:
`mytosctrl` -> `installer` -> `enable JR`

Next, you need to create a password for connection:
`mytosctrl` -> `installer` -> `setwebpass`


## Licenses
This tool is based on the work of @igroman787, licensed under the GNU General Public License v3.0
