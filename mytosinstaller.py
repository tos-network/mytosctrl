#!/usr/bin/env python3
# -*- coding: utf_8 -*-

import pwd
import random
import requests
from mypylib.mypylib import *
from mypyconsole.mypyconsole import *

local = MyPyClass(__file__)
console = MyPyConsole()
defaultLocalConfigPath = "/usr/bin/tos/local.config.json"


def Init():
	local.db["config"]["isStartOnlyOneProcess"] = False
	local.db["config"]["logLevel"] = "debug"
	local.db["config"]["isIgnorLogWarning"] = True # disable warning
	local.Run()
	local.db["config"]["isIgnorLogWarning"] = False # enable warning


	# create variables
	user = os.environ.get("USER", "root")
	local.buffer["user"] = user
	local.buffer["vuser"] = "validator"
	local.buffer["cport"] = random.randint(2000, 65000)
	local.buffer["lport"] = random.randint(2000, 65000)

	# Create user console
	console.name = "MyTosInstaller"
	console.color = console.RED
	console.AddItem("status", Status, "Print TOS component status")
	console.AddItem("enable", Enable, "Enable some function: 'FN' - Full node, 'VC' - Validator console, 'LS' - Liteserver, 'DS' - DHT-Server, 'JR' - jsonrpc, 'PT' - pyTOSv3. Example: 'enable FN'")
	console.AddItem("update", Enable, "Update some function: 'JR' - jsonrpc.  Example: 'update JR'") 
	console.AddItem("plsc", PrintLiteServerConfig, "Print LiteServer config")
	console.AddItem("clcf", CreateLocalConfigFile, "CreateLocalConfigFile")
	console.AddItem("drvcf", DRVCF, "Dangerous recovery validator config file")
	console.AddItem("setwebpass", SetWebPassword, "Set a password for the web admin interface")

	Refresh()
#end define

def Refresh():
	user = local.buffer["user"]
	local.buffer["mconfigPath"] = "/home/{user}/.local/share/mytoscore/mytoscore.db".format(user=user)
	if user == 'root':
		local.buffer["mconfigPath"] = "/usr/local/bin/mytoscore/mytoscore.db"
	#end if

	# create variables
	binDir = "/usr/bin/"
	srcDir = "/usr/src/"
	tosWorkDir = "/var/tos-work/"
	tosBinDir = binDir + "tos/"
	tosSrcDir = srcDir + "tos/"
	local.buffer["binDir"] = binDir
	local.buffer["srcDir"] = srcDir
	local.buffer["tosWorkDir"] = tosWorkDir
	local.buffer["tosBinDir"] = tosBinDir
	local.buffer["tosSrcDir"] = tosSrcDir
	tosDbDir = tosWorkDir + "db/"
	keysDir = tosWorkDir + "keys/"
	local.buffer["tosDbDir"] = tosDbDir
	local.buffer["keysDir"] = keysDir
	local.buffer["tosLogPath"] = tosWorkDir + "log"
	local.buffer["validatorAppPath"] = tosBinDir + "validator-engine/validator-engine"
	local.buffer["globalConfigPath"] = tosBinDir + "global-config.json"
	local.buffer["vconfigPath"] = tosDbDir + "config.json"
#end define

def Status(args):
	vconfigPath = local.buffer["vconfigPath"]

	user = local.buffer["user"]
	mconfigPath = local.buffer["mconfigPath"]

	tosBinDir = local.buffer["tosBinDir"]
	keysDir = local.buffer["keysDir"]
	server_key = keysDir + "server"
	client_key = keysDir + "client"
	liteserver_key = keysDir + "liteserver"
	liteserver_pubkey = liteserver_key + ".pub"


	fnStatus = os.path.isfile(vconfigPath)
	mtcStatus = os.path.isfile(mconfigPath)
	vcStatus = os.path.isfile(server_key) or os.path.isfile(client_key)
	lsStatus = os.path.isfile(liteserver_pubkey)

	print("Full node status:", fnStatus)
	print("Mytoscore status:", mtcStatus)
	print("V.console status:", vcStatus)
	print("Liteserver status:", lsStatus)
#end define

def Enable(args):
	name = args[0]
	user = local.buffer["user"]
	if name == "PT":
		CreateLocalConfigFile(args)
	args = ["python3", local.buffer["myPath"], "-u", user, "-e", "enable{name}".format(name=name)]
	RunAsRoot(args)
#end define

def DRVCF(args):
	user = local.buffer["user"]
	args = ["python3", local.buffer["myPath"], "-u", user, "-e", "drvcf"]
	RunAsRoot(args)
#end define

def GetLiteServerConfig():
	keysDir = local.buffer["keysDir"]
	liteserver_key = keysDir + "liteserver"
	liteserver_pubkey = liteserver_key + ".pub"
	result = dict()
	file = open(liteserver_pubkey, 'rb')
	data = file.read()
	file.close()
	key = base64.b64encode(data[4:])
	ip = requests.get("https://ifconfig.me").text
	mconfigPath = local.buffer["mconfigPath"]
	mconfig = GetConfig(path=mconfigPath)
	liteClient = mconfig.get("liteClient")
	liteServer = liteClient.get("liteServer")
	result["ip"] = ip2int(ip)
	result["port"] = liteServer.get("port")
	result["id"] = dict()
	result["id"]["@type"]= "pub.ed25519"
	result["id"]["key"]= key.decode()
	return result
#end define

def GetInitBlock():
	from mytoscore import MyTosCore
	tos = MyTosCore()
	initBlock = tos.GetInitBlock()
	return initBlock
#end define

def CreateLocalConfig(initBlock, localConfigPath=defaultLocalConfigPath):
	# dirty hack, but GetInitBlock() function uses the same technique
	from mytoscore import hex2base64

	# read global config file
	file = open("/usr/bin/tos/global-config.json", 'rt')
	text = file.read()
	data = json.loads(text)
	file.close()

	# edit config
	liteServerConfig = GetLiteServerConfig()
	data["liteservers"] = [liteServerConfig]
	data["validator"]["init_block"]["seqno"] = initBlock["seqno"]
	data["validator"]["init_block"]["root_hash"] = hex2base64(initBlock["rootHash"])
	data["validator"]["init_block"]["file_hash"] = hex2base64(initBlock["fileHash"])
	text = json.dumps(data, indent=4)

	# write local config file
	file = open(localConfigPath, 'wt')
	file.write(text)
	file.close()

	# chown
	user = local.buffer["user"]
	args = ["chown", "-R", user + ':' + user, localConfigPath]

	print("Local config file created:", localConfigPath)
#end define

def PrintLiteServerConfig(args):
	liteServerConfig = GetLiteServerConfig()
	text = json.dumps(liteServerConfig, indent=4)
	print(text)
#end define

def CreateLocalConfigFile(args):
	initBlock = GetInitBlock()
	initBlock_b64 = dict2b64(initBlock)
	user = local.buffer["user"]
	args = ["python3", local.buffer["myPath"], "-u", user, "-e", "clc", "-i", initBlock_b64]
	RunAsRoot(args)
#end define

def Event(name):
	if name == "enableFN":
		FirstNodeSettings()
	if name == "enableVC":
		EnableValidatorConsole()
	if name == "enableLS":
		EnableLiteServer()
	if name == "enableDS":
		EnableDhtServer()
	if name == "drvcf":
		DangerousRecoveryValidatorConfigFile()
	if name == "enableJR":
		EnableJsonRpc()
	if name == "enablePT":
		EnablePytosv3()
	if name == "clc":
		ix = sys.argv.index("-i")
		initBlock_b64 = sys.argv[ix+1]
		initBlock = b642dict(initBlock_b64)
		CreateLocalConfig(initBlock)
#end define

def General():
	if "-u" in sys.argv:
		ux = sys.argv.index("-u")
		user = sys.argv[ux+1]
		local.buffer["user"] = user
		Refresh()
	if "-e" in sys.argv:
		ex = sys.argv.index("-e")
		name = sys.argv[ex+1]
		Event(name)
	if "-m" in sys.argv:
		mx = sys.argv.index("-m")
		mode = sys.argv[mx+1]
	if "-t" in sys.argv:
		mx = sys.argv.index("-t")
		telemetry = sys.argv[mx+1]
		local.buffer["telemetry"] = Str2Bool(telemetry)
	if "--dump" in sys.argv:
		mx = sys.argv.index("--dump")
		dump = sys.argv[mx+1]
		local.buffer["dump"] = Str2Bool(dump)
	#end if

		# Create settings for mytoscore.py
		FirstMytoscoreSettings()

		if mode == "full":
			FirstNodeSettings()
			EnableValidatorConsole()
			EnableLiteServer()
			BackupVconfig()
			BackupMconfig()
		#end if

    # Create symbolic links
		CreateSymlinks()
	#end if
#end define

def Str2Bool(str):
	if str == "true":
		return True
	return False
#end define

def FirstNodeSettings():
	local.AddLog("start FirstNodeSettings fuction", "debug")

  # Create variables
	user = local.buffer["user"]
	vuser = local.buffer["vuser"]
	tosWorkDir = local.buffer["tosWorkDir"]
	tosDbDir = local.buffer["tosDbDir"]
	keysDir = local.buffer["keysDir"]
	tosLogPath = local.buffer["tosLogPath"]
	validatorAppPath = local.buffer["validatorAppPath"]
	globalConfigPath = local.buffer["globalConfigPath"]
	vconfigPath = local.buffer["vconfigPath"]

  # Check configuration
	if os.path.isfile(vconfigPath):
		local.AddLog("Validators config.json already exist. Break FirstNodeSettings fuction", "warning")
		return
	#end if

  # Create user
	file = open("/etc/passwd", 'rt')
	text = file.read()
	file.close()
	if vuser not in text:
		local.AddLog("Creating new user: " + vuser, "debug")
		args = ["/usr/sbin/useradd", "-d", "/dev/null", "-s", "/dev/null", vuser]
		subprocess.run(args)
	#end if

  # Prepare validator folders
	os.makedirs(tosDbDir, exist_ok=True)
	os.makedirs(keysDir, exist_ok=True)

  # Register autoload
	cpus = psutil.cpu_count() - 1
	cmd = "{validatorAppPath} --threads {cpus} --daemonize --global-config {globalConfigPath} --db {tosDbDir} --logname {tosLogPath} --state-ttl 604800 --verbosity 1"
	cmd = cmd.format(validatorAppPath=validatorAppPath, globalConfigPath=globalConfigPath, tosDbDir=tosDbDir, tosLogPath=tosLogPath, cpus=cpus)
	Add2Systemd(name="validator", user=vuser, start=cmd) # post="/usr/bin/python3 /usr/src/mytosctrl/mytoscore.py -e \"validator down\""

	# Get external ip address
	ip = requests.get("https://ifconfig.me").text
	vport = random.randint(2000, 65000)
	addr = "{ip}:{vport}".format(ip=ip, vport=vport)
	local.AddLog("Use addr: " + addr, "debug")

	# First start
	local.AddLog("First start validator - create config.json", "debug")
	args = [validatorAppPath, "--global-config", globalConfigPath, "--db", tosDbDir, "--ip", addr, "--logname", tosLogPath]
	subprocess.run(args)

	# Download dump
	DownloadDump()

	# chown 1
	local.AddLog("Chown tos-work dir", "debug")
	args = ["chown", "-R", vuser + ':' + vuser, tosWorkDir]
	subprocess.run(args)

	# start validator
	StartValidator()
#end define

def DownloadDump():
	dump = local.buffer["dump"]
	if dump == False:
		return
	#end if

	local.AddLog("start DownloadDump fuction", "debug")
	url = "https://dump.tos.org"
	dumpSize = requests.get(url + "/dumps/latest.size.archive.txt").text
	print("dumpSize:", dumpSize)
	needSpace = int(dumpSize) * 3
	diskSpace = psutil.disk_usage("/var")
	if needSpace > diskSpace.free:
		return
	#end if

	# apt install
	cmd = "apt install plzip pv -y"
	os.system(cmd)

	# download dump
	cmd = "curl -s {url}/dumps/latest.tar.lz | pv | plzip -d -n8 | tar -xC /var/tos-work/db".format(url=url)
	os.system(cmd)
#end define

def FirstMytoscoreSettings():
	local.AddLog("start FirstMytoscoreSettings fuction", "debug")
	user = local.buffer["user"]

	# Add mytoscore.py to autoload
	Add2Systemd(name="mytoscore", user=user, start="/usr/bin/python3 /usr/src/mytosctrl/mytoscore.py")

	# Check Configuration
	path = "/home/{user}/.local/share/mytoscore/mytoscore.db".format(user=user)
	path2 = "/usr/local/bin/mytoscore/mytoscore.db"
	if os.path.isfile(path) or os.path.isfile(path2):
		local.AddLog("mytoscore.db already exist. Break FirstMytoscoreSettings fuction", "warning")
		return
	#end if

	# amazon bugfix
	path1 = "/home/{user}/.local/".format(user=user)
	path2 = path1 + "share/"
	chownOwner = "{user}:{user}".format(user=user)
	os.makedirs(path1, exist_ok=True)
	os.makedirs(path2, exist_ok=True)
	args = ["chown", chownOwner, path1, path2]
	subprocess.run(args)

	# Prepare mytoscore folder
	mconfigPath = local.buffer["mconfigPath"]
	mconfigDir = GetDirFromPath(mconfigPath)
	os.makedirs(mconfigDir, exist_ok=True)

	# create variables
	srcDir = local.buffer["srcDir"]
	tosBinDir = local.buffer["tosBinDir"]
	tosSrcDir = local.buffer["tosSrcDir"]

	# general config
	mconfig = dict()
	mconfig["config"] = dict()
	mconfig["config"]["logLevel"] = "debug"
	mconfig["config"]["isLocaldbSaving"] = True

	# fift
	fift = dict()
	fift["appPath"] = tosBinDir + "crypto/fift"
	fift["libsPath"] = tosSrcDir + "crypto/fift/lib"
	fift["smartcontsPath"] = tosSrcDir + "crypto/smartcont"
	mconfig["fift"] = fift

	# lite-client
	liteClient = dict()
	liteClient["appPath"] = tosBinDir + "lite-client/lite-client"
	liteClient["configPath"] = tosBinDir + "global-config.json"
	mconfig["liteClient"] = liteClient

	# miner
	miner = dict()
	miner["appPath"] = tosBinDir + "crypto/pow-miner"
	mconfig["miner"] = miner

	# Telemetry
	mconfig["sendTelemetry"] = local.buffer["telemetry"]

	# Write settings to file
	SetConfig(path=mconfigPath, data=mconfig)

	# chown 1
	args = ["chown", user + ':' + user, mconfigDir, mconfigPath]
	subprocess.run(args)

	# start mytoscore
	StartMytoscore()
#end define

def EnableValidatorConsole():
	local.AddLog("start EnableValidatorConsole function", "debug")

	# Create variables
	user = local.buffer["user"]
	vuser = local.buffer["vuser"]
	cport = local.buffer["cport"]
	srcDir = local.buffer["srcDir"]
	tosDbDir = local.buffer["tosDbDir"]
	tosBinDir = local.buffer["tosBinDir"]
	vconfigPath = local.buffer["vconfigPath"]
	generate_random_id = tosBinDir + "utils/generate-random-id"
	keysDir = local.buffer["keysDir"]
	client_key = keysDir + "client"
	server_key = keysDir + "server"
	client_pubkey = client_key + ".pub"
	server_pubkey = server_key + ".pub"

	# Check if key exist
	if os.path.isfile(server_key) or os.path.isfile(client_key):
		local.AddLog("Server or client key already exist. Break EnableValidatorConsole fuction", "warning")
		return
	#end if

	# generate server key
	args = [generate_random_id, "--mode", "keys", "--name", server_key]
	process = subprocess.run(args, stdout=subprocess.PIPE)
	output = process.stdout.decode("utf-8")
	output_arr = output.split(' ')
	server_key_hex = output_arr[0]
	server_key_b64 = output_arr[1].replace('\n', '')

	# move key
	newKeyPath = tosDbDir + "/keyring/" + server_key_hex
	args = ["mv", server_key, newKeyPath]
	subprocess.run(args)

	# generate client key
	args = [generate_random_id, "--mode", "keys", "--name", client_key]
	process = subprocess.run(args, stdout=subprocess.PIPE)
	output = process.stdout.decode("utf-8")
	output_arr = output.split(' ')
	client_key_hex = output_arr[0]
	client_key_b64 = output_arr[1].replace('\n', '')

	# chown 1
	args = ["chown", vuser + ':' + vuser, newKeyPath]
	subprocess.run(args)

	# chown 2
	args = ["chown", user + ':' + user, server_pubkey, client_key, client_pubkey]
	subprocess.run(args)

	# read vconfig
	vconfig = GetConfig(path=vconfigPath)

	# prepare config
	control = dict()
	control["id"] = server_key_b64
	control["port"] = cport
	allowed = dict()
	allowed["id"] = client_key_b64
	allowed["permissions"] = 15
	control["allowed"] = [allowed] # fix me
	vconfig["control"].append(control)

	# write vconfig
	SetConfig(path=vconfigPath, data=vconfig)

	# restart validator
	StartValidator()

	# read mconfig
	mconfigPath = local.buffer["mconfigPath"]
	mconfig = GetConfig(path=mconfigPath)

	# edit mytoscore config file
	validatorConsole = dict()
	validatorConsole["appPath"] = tosBinDir + "validator-engine-console/validator-engine-console"
	validatorConsole["privKeyPath"] = client_key
	validatorConsole["pubKeyPath"] = server_pubkey
	validatorConsole["addr"] = "127.0.0.1:{cport}".format(cport=cport)
	mconfig["validatorConsole"] = validatorConsole

	# write mconfig
	SetConfig(path=mconfigPath, data=mconfig)

	# Pull event in mytoscore.py
	cmd = "python3 {srcDir}mytosctrl/mytoscore.py -e \"enableVC\"".format(srcDir=srcDir)
	args = ["su", "-l", user, "-c", cmd]
	subprocess.run(args)

	# restart mytoscore
	StartMytoscore()
#end define

def EnableLiteServer():
	local.AddLog("start EnableLiteServer function", "debug")

	# Create variables
	user = local.buffer["user"]
	vuser = local.buffer["vuser"]
	lport = local.buffer["lport"]
	srcDir = local.buffer["srcDir"]
	tosDbDir = local.buffer["tosDbDir"]
	keysDir = local.buffer["keysDir"]
	tosBinDir = local.buffer["tosBinDir"]
	vconfigPath = local.buffer["vconfigPath"]
	generate_random_id = tosBinDir + "utils/generate-random-id"
	liteserver_key = keysDir + "liteserver"
	liteserver_pubkey = liteserver_key + ".pub"

	# Check if key exist
	if os.path.isfile(liteserver_pubkey):
		local.AddLog("Liteserver key already exist. Break EnableLiteServer fuction", "warning")
		return
	#end if

	# generate liteserver key
	local.AddLog("generate liteserver key", "debug")
	args = [generate_random_id, "--mode", "keys", "--name", liteserver_key]
	process = subprocess.run(args, stdout=subprocess.PIPE)
	output = process.stdout.decode("utf-8")
	output_arr = output.split(' ')
	liteserver_key_hex = output_arr[0]
	liteserver_key_b64 = output_arr[1].replace('\n', '')

	# move key
	local.AddLog("move key", "debug")
	newKeyPath = tosDbDir + "/keyring/" + liteserver_key_hex
	args = ["mv", liteserver_key, newKeyPath]
	subprocess.run(args)

	# chown 1
	local.AddLog("chown 1", "debug")
	args = ["chown", vuser + ':' + vuser, newKeyPath]
	subprocess.run(args)

	# chown 2
	local.AddLog("chown 2", "debug")
	args = ["chown", user + ':' + user, liteserver_pubkey]
	subprocess.run(args)

	# read vconfig
	local.AddLog("read vconfig", "debug")
	vconfig = GetConfig(path=vconfigPath)

	# prepare vconfig
	local.AddLog("prepare vconfig", "debug")
	liteserver = dict()
	liteserver["id"] = liteserver_key_b64
	liteserver["port"] = lport
	vconfig["liteservers"].append(liteserver)

	# write vconfig
	local.AddLog("write vconfig", "debug")
	SetConfig(path=vconfigPath, data=vconfig)

	# restart validator
	StartValidator()

	# edit mytoscore config file
	# read mconfig
	local.AddLog("read mconfig", "debug")
	mconfigPath = local.buffer["mconfigPath"]
	mconfig = GetConfig(path=mconfigPath)

	# edit mytoscore config file
	local.AddLog("edit mytoscore config file", "debug")
	liteServer = dict()
	liteServer["pubkeyPath"] = liteserver_pubkey
	liteServer["ip"] = "127.0.0.1"
	liteServer["port"] = lport
	mconfig["liteClient"]["liteServer"] = liteServer

	# write mconfig
	local.AddLog("write mconfig", "debug")
	SetConfig(path=mconfigPath, data=mconfig)

	# restart mytoscore
	StartMytoscore()
#end define

def StartValidator():
	# restart validator
	local.AddLog("Start/restart validator service", "debug")
	args = ["systemctl", "restart", "validator"]
	subprocess.run(args)

	# sleep 10 sec
	local.AddLog("sleep 10 sec", "debug")
	time.sleep(10)
#end define

def StartMytoscore():
	# restart mytoscore
	local.AddLog("Start/restart mytoscore service", "debug")
	args = ["systemctl", "restart", "mytoscore"]
	subprocess.run(args)
#end define

def GetConfig(**kwargs):
	path = kwargs.get("path")
	file = open(path, 'rt')
	text = file.read()
	file.close()
	config = json.loads(text)
	return config
#end define

def SetConfig(**kwargs):
	path = kwargs.get("path")
	data = kwargs.get("data")

	# write config
	text = json.dumps(data, indent=4)
	file = open(path, 'wt')
	file.write(text)
	file.close()
#end define

def BackupVconfig():
	local.AddLog("Backup validator config file 'config.json' to 'config.json.backup'", "debug")
	vconfigPath = local.buffer["vconfigPath"]
	backupPath = vconfigPath + ".backup"
	args = ["cp", vconfigPath, backupPath]
	subprocess.run(args)
#end define

def BackupMconfig():
	local.AddLog("Backup mytoscore config file 'mytoscore.db' to 'mytoscore.db.backup'", "debug")
	mconfigPath = local.buffer["mconfigPath"]
	backupPath = mconfigPath + ".backup"
	args = ["cp", mconfigPath, backupPath]
	subprocess.run(args)
#end define

def GetPortsFromVconfig():
	vconfigPath = local.buffer["vconfigPath"]

	# read vconfig
	local.AddLog("read vconfig", "debug")
	vconfig = GetConfig(path=vconfigPath)

	# read mconfig
	local.AddLog("read mconfig", "debug")
	mconfigPath = local.buffer["mconfigPath"]
	mconfig = GetConfig(path=mconfigPath)

	# edit mytoscore config file
	local.AddLog("edit mytoscore config file", "debug")
	mconfig["liteClient"]["liteServer"]["port"] = mconfig["liteservers"][0]["port"]
	mconfig["validatorConsole"]["addr"] = "127.0.0.1:{}".format(mconfig["control"][0]["port"])

	# write mconfig
	local.AddLog("write mconfig", "debug")
	SetConfig(path=mconfigPath, data=mconfig)

	# restart mytoscore
	StartMytoscore()
#end define

def DangerousRecoveryValidatorConfigFile():
	local.AddLog("start DangerousRecoveryValidatorConfigFile function", "info")

	# install and import cryptography library
	args = ["pip3", "install", "cryptography"]
	subprocess.run(args)
	from cryptography.hazmat.primitives import serialization
	from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

	# Get keys from keyring
	keys = list()
	keyringDir = "/var/tos-work/db/keyring/"
	keyring = os.listdir(keyringDir)
	os.chdir(keyringDir)
	sorted(keyring, key=os.path.getmtime)
	for item in keyring:
		b64String = hex2b64(item)
		keys.append(b64String)
	#end for

	# Create config object
	vconfig = dict()
	vconfig["@type"] = "engine.validator.config"
	vconfig["out_port"] = 3278

	# Create addrs object
	buffer = dict()
	buffer["@type"] = "engine.addr"
	buffer["ip"] = ip2int(requests.get("https://ifconfig.me").text)
	buffer["port"] = None
	buffer["categories"] = [0, 1, 2, 3]
	buffer["priority_categories"] = []
	vconfig["addrs"] = [buffer]

	# Get liteserver fragment
	mconfigPath = local.buffer["mconfigPath"]
	mconfig = GetConfig(path=mconfigPath)
	lkey = mconfig["liteClient"]["liteServer"]["pubkeyPath"]
	lport = mconfig["liteClient"]["liteServer"]["port"]

	# Read lite server pubkey
	file = open(lkey, 'rb')
	data = file.read()
	file.close()
	lsPubkey = data[4:]

	# Search lite server priv key
	for item in keyring:
		path = keyringDir + item
		file = open(path, 'rb')
		data = file.read()
		file.close()
		peivkey = data[4:]
		privkeyObject = Ed25519PrivateKey.from_private_bytes(peivkey)
		pubkeyObject = privkeyObject.public_key()
		pubkey = pubkeyObject.public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
		if pubkey == lsPubkey:
			lsId = hex2b64(item)
			keys.remove(lsId)
	#end for

	# Create LS object
	buffer = dict()
	buffer["@type"] = "engine.liteServer"
	buffer["id"] = lsId
	buffer["port"] = lport
	vconfig["liteservers"] = [buffer]

	# Get validator-console fragment
	ckey = mconfig["validatorConsole"]["pubKeyPath"]
	addr = mconfig["validatorConsole"]["addr"]
	buff = addr.split(':')
	cport = int(buff[1])

	# Read validator-console pubkey
	file = open(ckey, 'rb')
	data = file.read()
	file.close()
	vPubkey = data[4:]

	# Search validator-console priv key
	for item in keyring:
		path = keyringDir + item
		file = open(path, 'rb')
		data = file.read()
		file.close()
		peivkey = data[4:]
		privkeyObject = Ed25519PrivateKey.from_private_bytes(peivkey)
		pubkeyObject = privkeyObject.public_key()
		pubkey = pubkeyObject.public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
		if pubkey == vPubkey:
			vcId = hex2b64(item)
			keys.remove(vcId)
	#end for

	# Create VC object
	buffer = dict()
	buffer2 = dict()
	buffer["@type"] = "engine.controlInterface"
	buffer["id"] = vcId
	buffer["port"] = cport
	buffer2["@type"] = "engine.controlProcess"
	buffer2["id"] = None
	buffer2["permissions"] = 15
	buffer["allowed"] = buffer2
	vconfig["control"] = [buffer]

	# Get dht fragment
	files = os.listdir("/var/tos-work/db")
	for item in files:
		if item[:3] == "dht":
			dhtS = item[4:]
			dhtS = dhtS.replace('_', '/')
			dhtS = dhtS.replace('-', '+')
			break
	#end for

	# Get ght from keys
	for item in keys:
		if dhtS in item:
			dhtId = item
			keys.remove(dhtId)
	#end for

	# Create dht object
	buffer = dict()
	buffer["@type"] = "engine.dht"
	buffer["id"] = dhtId
	vconfig["dht"] = [buffer]

	# Create adnl object
	adnl2 = dict()
	adnl2["@type"] = "engine.adnl"
	adnl2["id"] = dhtId
	adnl2["category"] = 0

	# Create adnl object
	adnlId = hex2b64(mconfig["adnlAddr"])
	keys.remove(adnlId)
	adnl3 = dict()
	adnl3["@type"] = "engine.adnl"
	adnl3["id"] = adnlId
	adnl3["category"] = 0

	# Create adnl object
	adnl1 = dict()
	adnl1["@type"] = "engine.adnl"
	adnl1["id"] = keys.pop(0)
	adnl1["category"] = 1

	vconfig["adnl"] = [adnl1, adnl2, adnl3]

	# Get dumps from tmp
	dumps = list()
	dumpsDir = "/tmp/mytoscore/"
	dumpsList = os.listdir(dumpsDir)
	os.chdir(dumpsDir)
	sorted(dumpsList, key=os.path.getmtime)
	for item in dumpsList:
		if "ElectionEntry.json" in item:
			dumps.append(item)
	#end for

	# Create validators object
	validators = list()

	# Read dump file
	while len(keys) > 0:
		dumpPath = dumps.pop()
		file = open(dumpPath, 'rt')
		data = file.read()
		file.close()
		dump = json.loads(data)
		vkey = hex2b64(dump["validatorKey"])
		temp_key = dict()
		temp_key["@type"] = "engine.validatorTempKey"
		temp_key["key"] = vkey
		temp_key["expire_at"] = dump["endWorkTime"]
		adnl_addr = dict()
		adnl_addr["@type"] = "engine.validatorAdnlAddress"
		adnl_addr["id"] = adnlId
		adnl_addr["expire_at"] = dump["endWorkTime"]

		# Create validator object
		validator = dict()
		validator["@type"] = "engine.validator"
		validator["id"] = vkey
		validator["temp_keys"] = [temp_key]
		validator["adnl_addrs"] = [adnl_addr]
		validator["election_date"] = dump["startWorkTime"]
		validator["expire_at"] = dump["endWorkTime"]
		if vkey in keys:
			validators.append(validator)
			keys.remove(vkey)
		#end if
	#end while

	# Add validators object to vconfig
	vconfig["validators"] = validators


	print("vconfig:", json.dumps(vconfig, indent=4))
	print("keys:", keys)
#end define

def hex2b64(input):
	hexBytes = bytes.fromhex(input)
	b64Bytes = base64.b64encode(hexBytes)
	b64String = b64Bytes.decode()
	return b64String
#end define

def b642hex(input):
	b64Bytes = input.encode()
	hexBytes = base64.b64decode(b64Bytes)
	hexString = hexBytes.hex()
	return hexString
#end define

def CreateSymlinks():
	local.AddLog("start CreateSymlinks fuction", "debug")
	cport = local.buffer["cport"]

	mytosctrl_file = "/usr/bin/mytosctrl"
	fift_file = "/usr/bin/fift"
	liteclient_file = "/usr/bin/lite-client"
	validator_console_file = "/usr/bin/validator-console"
	env_file = "/etc/environment"
	file = open(mytosctrl_file, 'wt')
	file.write("/usr/bin/python3 /usr/src/mytosctrl/mytosctrl.py $@")
	file.close()
	file = open(fift_file, 'wt')
	file.write("/usr/bin/tos/crypto/fift $@")
	file.close()
	file = open(liteclient_file, 'wt')
	file.write("/usr/bin/tos/lite-client/lite-client -C /usr/bin/tos/global-config.json $@")
	file.close()
	if cport:
		file = open(validator_console_file, 'wt')
		file.write("/usr/bin/tos/validator-engine-console/validator-engine-console -k /var/tos-work/keys/client -p /var/tos-work/keys/server.pub -a 127.0.0.1:" + str(cport) + " $@")
		file.close()
		args = ["chmod", "+x", validator_console_file]
		subprocess.run(args)
	args = ["chmod", "+x", mytosctrl_file, fift_file, liteclient_file]
	subprocess.run(args)

	# env
	fiftpath = "export FIFTPATH=/usr/src/tos/crypto/fift/lib/:/usr/src/tos/crypto/smartcont/"
	file = open(env_file, 'rt+')
	text = file.read()
	if fiftpath not in text:
		file.write(fiftpath + '\n')
	file.close()
#end define

def EnableDhtServer():
	local.AddLog("start EnableDhtServer function", "debug")
	vuser = local.buffer["vuser"]
	tosBinDir = local.buffer["tosBinDir"]
	globalConfigPath = local.buffer["globalConfigPath"]
	dht_server = tosBinDir + "dht-server/dht-server"
	generate_random_id = tosBinDir + "utils/generate-random-id"
	tosDhtServerDir = "/var/tos-dht-server/"
	tosDhtKeyringDir = tosDhtServerDir + "keyring/"

	# Check Configuration
	if os.path.isfile("/var/tos-dht-server/config.json"):
		local.AddLog("DHT-Server config.json already exist. Break EnableDhtServer fuction", "warning")
		return
	#end if

	# Prepare folder
	os.makedirs(tosDhtServerDir, exist_ok=True)

	# Register autoload
	cmd = "{dht_server} -C {globalConfigPath} -D {tosDhtServerDir}"
	cmd = cmd.format(dht_server=dht_server, globalConfigPath=globalConfigPath, tosDhtServerDir=tosDhtServerDir)
	Add2Systemd(name="dht-server", user=vuser, start=cmd)

	# Get external ip address
	ip = requests.get("https://ifconfig.me").text
	port = random.randint(2000, 65000)
	addr = "{ip}:{port}".format(ip=ip, port=port)

	# First start
	args = [dht_server, "-C", globalConfigPath, "-D", tosDhtServerDir, "-I", addr]
	subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

	# Get config output
	key = os.listdir(tosDhtKeyringDir)[0]
	ip = ip2int(ip)
	text = '{"@type": "adnl.addressList", "addrs": [{"@type": "adnl.address.udp", "ip": ' + str(ip) + ', "port": ' + str(port) + '}], "version": 0, "reinit_date": 0, "priority": 0, "expire_at": 0}'
	args = [generate_random_id, "-m", "dht", "-k", tosDhtKeyringDir + key, "-a", text]
	process = subprocess.run(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=3)
	output = process.stdout.decode("utf-8")
	err = process.stderr.decode("utf-8")
	if len(err) > 0:
		raise Exeption(err)
	#end if

	data = json.loads(output)
	text = json.dumps(data, indent=4)
	print(text)

	# chown 1
	args = ["chown", "-R", vuser + ':' + vuser, tosDhtServerDir]
	subprocess.run(args)

	# start DHT-Server
	args = ["systemctl", "restart", "dht-server"]
	subprocess.run(args)
#end define

def SetWebPassword(args):
	args = ["python3", "/usr/src/mtc-jsonrpc/mtc-jsonrpc.py", "-p"]
	subprocess.run(args)
#end define

def EnableJsonRpc():
	local.AddLog("start EnableJsonRpc function", "debug")
	user = local.buffer["user"]
	exitCode = RunAsRoot(["bash", "/usr/src/mytosctrl/scripts/jsonrpcinstaller.sh", "-u", user])
	if exitCode == 0:
		text = "EnableJsonRpc - {green}OK{endc}"
	else:
		text = "EnableJsonRpc - {red}Error{endc}"
	ColorPrint(text)
#end define

def EnablePytosv3():
	local.AddLog("start EnablePytosv3 function", "debug")
	user = local.buffer["user"]
	exitCode = RunAsRoot(["bash", "/usr/src/mytosctrl/scripts/pytosv3installer.sh", "-u", user])
	if exitCode == 0:
		text = "EnablePytosv3 - {green}OK{endc}"
	else:
		text = "EnablePytosv3 - {red}Error{endc}"
	ColorPrint(text)
#end define

def str2b64(s):
	b = s.encode("utf-8")
	b64 = base64.b64encode(b)
	b64 = b64.decode("utf-8")
	return b64
#end define

def b642str(b64):
	b64 = b64.encode("utf-8")
	b = base64.b64decode(b64)
	s = b.decode("utf-8")
	return s
#end define

def dict2b64(d):
	s = json.dumps(d)
	b64 = str2b64(s)
	return b64
#end define

def b642dict(b64):
	s = b642str(b64)
	d = json.loads(s)
	return d
#end define



###
### Start of the program
###

if __name__ == "__main__":
	Init()
	if len(sys.argv) > 1:
		General()
	else:
		console.Run()
	local.Exit()
#end if
