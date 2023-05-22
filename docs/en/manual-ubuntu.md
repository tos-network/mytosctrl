# How to become a validator with mytosctrl (v0.2, OS Ubuntu)

### 1. Install mytosctrl:
1. Download the installation script. We recommend to install the tool under your local user account, not as Root. In our example a local user account is used:

```sh
wget https://raw.githubusercontent.com/tos-network/mytosctrl/master/scripts/install.sh
```

2. Run the installation script as administrator:

```sh
sudo bash install.sh -m full
```


### 2. Operability test:
1. Run **mytosctrl** from local user account used for installation at step 1:

```sh
mytosctrl
```

2. Check **mytosctrl** statuses, in particular the following:

* **mytoscore status**: should be green.
* **Local validator status**: should be green.
* **Local validator out of sync**. First a big number displays. Once the newly created validator contacts other validators, the number is around 250k. As synchronization goes on, the number decreases. When it falls below 20, the validator is synchronized.

3. Look at the list of available wallets. In our example the **validator_wallet_001** wallet was created at **mytosctrl** installation:

### 3. Send the required number of coins to the wallet and activate it:

* The `vas` command displays the history of transfers
* The `aw` command activates the wallet

### 4. Now your validator is good to go
**mytoscore** automatically joins the elections. It divides the wallet balance into two parts and uses them as a bet to participate in the elections. You can also manually set the stake size:

`set stake 50000` — set the stake size to 50k coins. If the bet is accepted and our node becomes a validator, the bet can only be withdrawn at the second election (according to the rules of the electorate).

Feel free to command help.

To check **mytoscrl** logs, open `~/.local/share/mytoscore/mytoscore.log` for a local user or `/usr/local/bin/mytoscore/mytoscore.log` for Root.
