#!/usr/bin/env python3
# -*- coding: utf_8 -*-

from mypylib.mypylib import *
from mypyconsole.mypyconsole import *
from mytoscore import *
import sys, getopt, os

local = MyPyClass(__file__)
console = MyPyConsole()
tos = MyTosCore()

def Init(argv):
	# Load translate table
	local.InitTranslator(local.buffer.get("myDir") + "translate.json")

	# Create user console
	console.name = "MyTosCtrl"
	console.startFunction = PreUp

	console.AddItem("update", Update, local.Translate("update_cmd"))
	console.AddItem("upgrade", Upgrade, local.Translate("upgrade_cmd"))
	console.AddItem("installer", Installer, local.Translate("installer_cmd"))
	console.AddItem("status", PrintStatus, local.Translate("status_cmd"))
	console.AddItem("seqno", Seqno, local.Translate("seqno_cmd"))
	console.AddItem("getconfig", GetConfig, local.Translate("getconfig_cmd"))

	console.AddItem("nw", CreatNewWallet, local.Translate("nw_cmd"))
	console.AddItem("aw", ActivateWallet, local.Translate("aw_cmd"))
	console.AddItem("wl", PrintWalletsList, local.Translate("wl_cmd"))
	console.AddItem("iw", ImportWallet, local.Translate("iw_cmd"))
	console.AddItem("swv", SetWalletVersion, local.Translate("swv_cmd"))
	console.AddItem("ew", ExportWallet, local.Translate("ex_cmd"))
	console.AddItem("dw", DeleteWallet, local.Translate("dw_cmd"))

	console.AddItem("vas", ViewAccountStatus, local.Translate("vas_cmd"))
	console.AddItem("vah", ViewAccountHistory, local.Translate("vah_cmd"))
	console.AddItem("mg", MoveCoins, local.Translate("mg_cmd"))
	console.AddItem("mgtp", MoveCoinsThroughProxy, local.Translate("mgtp_cmd"))

	console.AddItem("nb", CreatNewBookmark, local.Translate("nb_cmd"))
	console.AddItem("bl", PrintBookmarksList, local.Translate("bl_cmd"))
	console.AddItem("db", DeleteBookmark, local.Translate("db_cmd"))

	console.AddItem("nd", NewDomain, local.Translate("nd_cmd"))
	console.AddItem("dl", PrintDomainsList, local.Translate("dl_cmd"))
	console.AddItem("vds", ViewDomainStatus, local.Translate("vds_cmd"))
	console.AddItem("dd", DeleteDomain, local.Translate("dd_cmd"))

	console.AddItem("ol", PrintOffersList, local.Translate("ol_cmd"))
	console.AddItem("vo", VoteOffer, local.Translate("vo_cmd"))
	console.AddItem("od", OfferDiff, local.Translate("od_cmd"))

	console.AddItem("el", PrintElectionEntriesList, local.Translate("el_cmd"))
	console.AddItem("ve", VoteElectionEntry, local.Translate("ve_cmd"))
	console.AddItem("vl", PrintValidatorList, local.Translate("vl_cmd"))
	console.AddItem("cl", PrintComplaintsList, local.Translate("cl_cmd"))
	console.AddItem("vc", VoteComplaint, local.Translate("vc_cmd"))

	console.AddItem("get", GetSettings, local.Translate("get_cmd"))
	console.AddItem("set", SetSettings, local.Translate("set_cmd"))
	console.AddItem("xrestart", Xrestart, local.Translate("xrestart_cmd"))
	console.AddItem("xlist", Xlist, local.Translate("xlist_cmd"))

	console.AddItem("new_pool", NewPool, local.Translate("new_pool_cmd"))
	console.AddItem("pools_list", PrintPoolsList, local.Translate("pools_list_cmd"))
	console.AddItem("get_pool_data", GetPoolData, local.Translate("get_pool_data_cmd"))
	console.AddItem("activate_pool", ActivatePool, local.Translate("activate_pool_cmd"))
	console.AddItem("deposit_to_pool", DepositToPool, local.Translate("deposit_to_pool_cmd"))
	console.AddItem("withdraw_from_pool", WithdrawFromPool, local.Translate("withdraw_from_pool_cmd"))
	console.AddItem("delete_pool", DeletePool, local.Translate("delete_pool_cmd"))

	# Process input parameters
	opts, args = getopt.getopt(argv,"hc:w:",["config=","wallets="])
	for opt, arg in opts:
		if opt == '-h':
			print ('mytosctrl.py -c <configfile> -w <wallets>')
			sys.exit()
		elif opt in ("-c", "--config"):
			configfile = arg
			if not os.access(configfile, os.R_OK):
				print ("Configuration file " + configfile + " could not be opened")
				sys.exit()

			tos.dbFile = configfile
			tos.Refresh()
		elif opt in ("-w", "--wallets"):
			wallets = arg
			if not os.access(wallets, os.R_OK):
				print ("Wallets path " + wallets  + " could not be opened")
				sys.exit()
			elif not os.path.isdir(wallets):
				print ("Wallets path " + wallets  + " is not a directory")
				sys.exit()
			tos.walletsDir = wallets
	#end for

	local.db["config"]["logLevel"] = "debug"
	local.db["config"]["isLocaldbSaving"] = True
	local.Run()
#end define

def PreUp():
	CheckMytosctrlUpdate()
	# CheckTosUpdate()
#end define

def Installer(args):
	args = ["python3", "/usr/src/mytosctrl/mytosinstaller.py"]
	subprocess.run(args)
#end define

def GetItemFromList(data, index):
	try:
		return data[index]
	except: pass
#end define

def GetAuthorRepoBranchFromArgs(args):
	data = dict()
	arg1 = GetItemFromList(args, 0)
	arg2 = GetItemFromList(args, 1)
	if arg1:
		if "https://" in arg1:
			buff = arg1[8:].split('/')
			print(f"buff: {buff}")
			data["author"] = buff[1]
			data["repo"] = buff[2]
			tree = GetItemFromList(buff, 3)
			if tree:
				data["branch"] = GetItemFromList(buff, 4)
		else:
			data["branch"] = arg1
	if arg2:
		data["branch"] = arg2
	return data
#end define

def Update(args):
	# add safe directory to git
	gitPath = "/usr/src/mytosctrl"
	subprocess.run(["git", "config", "--global", "--add", "safe.directory", gitPath])

	# Get author, repo, branch
	author, repo = GetGitAuthorAndRepo(gitPath)
	branch = GetGitBranch(gitPath)
	
	# Set author, repo, branch
	data = GetAuthorRepoBranchFromArgs(args)
	author = data.get("author", author)
	repo = data.get("repo", repo)
	branch = data.get("branch", branch)

	# Run script
	runArgs = ["bash", "/usr/src/mytosctrl/scripts/update.sh", "-a", author, "-r", repo, "-b", branch]
	exitCode = RunAsRoot(runArgs)
	if exitCode == 0:
		text = "Update - {green}OK{endc}"
	else:
		text = "Update - {red}Error{endc}"
	ColorPrint(text)
	local.Exit()
#end define

def Upgrade(args):
	# add safe directory to git
	gitPath = "/usr/src/tos"
	subprocess.run(["git", "config", "--global", "--add", "safe.directory", gitPath])

	# Get author, repo, branch
	author, repo = GetGitAuthorAndRepo(gitPath)
	branch = GetGitBranch(gitPath)
	
	# Set author, repo, branch
	data = GetAuthorRepoBranchFromArgs(args)
	author = data.get("author", author)
	repo = data.get("repo", repo)
	branch = data.get("branch", branch)

	# Run script
	runArgs = ["bash", "/usr/src/mytosctrl/scripts/upgrade.sh", "-a", author, "-r", repo, "-b", branch]
	exitCode = RunAsRoot(runArgs)
	if exitCode == 0:
		text = "Upgrade - {green}OK{endc}"
	else:
		text = "Upgrade - {red}Error{endc}"
	ColorPrint(text)
#end define

def CheckMytosctrlUpdate():
	gitPath = local.buffer.get("myDir")
	result = CheckGitUpdate(gitPath)
	if result is True:
		ColorPrint(local.Translate("mytosctrl_update_available"))
#end define

def CheckTosUpdate():
	gitPath = "/usr/src/tos"
	result = CheckGitUpdate(gitPath)
	if result is True:
		ColorPrint(local.Translate("tos_update_available"))
#end define

def PrintTest(args):
	print(json.dumps(local.buffer, indent=2))
#end define

def sl(args):
	Slashing(tos)
#end define

def PrintStatus(args):
	opt = None
	if len(args) == 1:
		opt = args[0]
	adnlAddr = tos.GetAdnlAddr()
	rootWorkchainEnabledTime_int = tos.GetRootWorkchainEnabledTime()
	config34 = tos.GetConfig34()
	config36 = tos.GetConfig36()
	totalValidators = config34["totalValidators"]
	onlineValidators = None
	validatorEfficiency = None
	if opt != "fast":
		onlineValidators = tos.GetOnlineValidators()
		validatorEfficiency = tos.GetValidatorEfficiency()
	if onlineValidators:
		onlineValidators = len(onlineValidators)
	oldStartWorkTime = config36.get("startWorkTime")
	if oldStartWorkTime is None:
		oldStartWorkTime = config34.get("startWorkTime")
	shardsNumber = tos.GetShardsNumber()
	validatorStatus = tos.GetValidatorStatus()
	config15 = tos.GetConfig15()
	config17 = tos.GetConfig17()
	fullConfigAddr = tos.GetFullConfigAddr()
	fullElectorAddr = tos.GetFullElectorAddr()
	startWorkTime = tos.GetActiveElectionId(fullElectorAddr)
	validatorIndex = tos.GetValidatorIndex()
	validatorWallet = tos.GetValidatorWallet()
	dbSize = tos.GetDbSize()
	dbUsage = tos.GetDbUsage()
	memoryInfo = GetMemoryInfo()
	swapInfo = GetSwapInfo()
	offersNumber = tos.GetOffersNumber()
	complaintsNumber = tos.GetComplaintsNumber()
	statistics = tos.GetSettings("statistics")
	tpsAvg = tos.GetStatistics("tpsAvg", statistics)
	netLoadAvg = tos.GetStatistics("netLoadAvg", statistics)
	disksLoadAvg = tos.GetStatistics("disksLoadAvg", statistics)
	disksLoadPercentAvg = tos.GetStatistics("disksLoadPercentAvg", statistics)
	if validatorWallet is not None:
		validatorAccount = tos.GetAccount(validatorWallet.addrB64)
	else:
		validatorAccount = None
	PrintTosStatus(startWorkTime, totalValidators, onlineValidators, shardsNumber, offersNumber, complaintsNumber, tpsAvg)
	PrintLocalStatus(adnlAddr, validatorIndex, validatorEfficiency, validatorWallet, validatorAccount, validatorStatus, dbSize, dbUsage, memoryInfo, swapInfo, netLoadAvg, disksLoadAvg, disksLoadPercentAvg)
	PrintTosConfig(fullConfigAddr, fullElectorAddr, config15, config17)
	PrintTimes(rootWorkchainEnabledTime_int, startWorkTime, oldStartWorkTime, config15)
#end define

def PrintTosStatus(startWorkTime, totalValidators, onlineValidators, shardsNumber, offersNumber, complaintsNumber, tpsAvg):
	tps1 = tpsAvg[0]
	tps5 = tpsAvg[1]
	tps15 = tpsAvg[2]
	allValidators = totalValidators
	newOffers = offersNumber.get("new")
	allOffers = offersNumber.get("all")
	newComplaints = complaintsNumber.get("new")
	allComplaints = complaintsNumber.get("all")
	tps1_text = bcolors.Green(tps1)
	tps5_text = bcolors.Green(tps5)
	tps15_text = bcolors.Green(tps15)
	tps_text = local.Translate("tos_status_tps").format(tps1_text, tps5_text, tps15_text)
	onlineValidators_text = GetColorInt(onlineValidators, border=allValidators*2/3, logic="more")
	allValidators_text = bcolors.Yellow(allValidators)
	validators_text = local.Translate("tos_status_validators").format(onlineValidators_text, allValidators_text)
	shards_text = local.Translate("tos_status_shards").format(bcolors.Green(shardsNumber))
	newOffers_text = bcolors.Green(newOffers)
	allOffers_text = bcolors.Yellow(allOffers)
	offers_text = local.Translate("tos_status_offers").format(newOffers_text, allOffers_text)
	newComplaints_text = bcolors.Green(newComplaints)
	allComplaints_text = bcolors.Yellow(allComplaints)
	complaints_text = local.Translate("tos_status_complaints").format(newComplaints_text, allComplaints_text)

	if startWorkTime == 0:
		election_text = bcolors.Yellow("closed")
	else:
		election_text = bcolors.Green("open")
	election_text = local.Translate("tos_status_election").format(election_text)

	ColorPrint(local.Translate("tos_status_head"))
	print(tps_text)
	print(validators_text)
	print(shards_text)
	print(offers_text)
	print(complaints_text)
	print(election_text)
	print()
#end define

def PrintLocalStatus(adnlAddr, validatorIndex, validatorEfficiency, validatorWallet, validatorAccount, validatorStatus, dbSize, dbUsage, memoryInfo, swapInfo, netLoadAvg, disksLoadAvg, disksLoadPercentAvg):
	if validatorWallet is None:
		return
	walletAddr = validatorWallet.addrB64
	walletBalance = validatorAccount.balance
	cpuNumber = psutil.cpu_count()
	loadavg = GetLoadAvg()
	cpuLoad1 = loadavg[0]
	cpuLoad5 = loadavg[1]
	cpuLoad15 = loadavg[2]
	netLoad1 = netLoadAvg[0]
	netLoad5 = netLoadAvg[1]
	netLoad15 = netLoadAvg[2]
	validatorOutOfSync = validatorStatus.get("outOfSync")

	validatorIndex_text = GetColorInt(validatorIndex, 0, logic="more")
	validatorIndex_text = local.Translate("local_status_validator_index").format(validatorIndex_text)
	validatorEfficiency_text = GetColorInt(validatorEfficiency, 10, logic="more", ending=" %")
	validatorEfficiency_text = local.Translate("local_status_validator_efficiency").format(validatorEfficiency_text)
	adnlAddr_text = local.Translate("local_status_adnl_addr").format(bcolors.Yellow(adnlAddr))
	walletAddr_text = local.Translate("local_status_wallet_addr").format(bcolors.Yellow(walletAddr))
	walletBalance_text = local.Translate("local_status_wallet_balance").format(bcolors.Green(walletBalance))

	# CPU status
	cpuNumber_text = bcolors.Yellow(cpuNumber)
	cpuLoad1_text = GetColorInt(cpuLoad1, cpuNumber, logic="less")
	cpuLoad5_text = GetColorInt(cpuLoad5, cpuNumber, logic="less")
	cpuLoad15_text = GetColorInt(cpuLoad15, cpuNumber, logic="less")
	cpuLoad_text = local.Translate("local_status_cpu_load").format(cpuNumber_text, cpuLoad1_text, cpuLoad5_text, cpuLoad15_text)

	# Memory status
	ramUsage = memoryInfo.get("usage")
	ramUsagePercent = memoryInfo.get("usagePercent")
	swapUsage = swapInfo.get("usage")
	swapUsagePercent = swapInfo.get("usagePercent")
	ramUsage_text = GetColorInt(ramUsage, 100, logic="less", ending=" Gb")
	ramUsagePercent_text = GetColorInt(ramUsagePercent, 90, logic="less", ending="%")
	swapUsage_text = GetColorInt(swapUsage, 100, logic="less", ending=" Gb")
	swapUsagePercent_text = GetColorInt(swapUsagePercent, 90, logic="less", ending="%")
	ramLoad_text = "{cyan}ram:[{default}{data}, {percent}{cyan}]{endc}"
	ramLoad_text = ramLoad_text.format(cyan=bcolors.cyan, default=bcolors.default, endc=bcolors.endc, data=ramUsage_text, percent=ramUsagePercent_text)
	swapLoad_text = "{cyan}swap:[{default}{data}, {percent}{cyan}]{endc}"
	swapLoad_text = swapLoad_text.format(cyan=bcolors.cyan, default=bcolors.default, endc=bcolors.endc, data=swapUsage_text, percent=swapUsagePercent_text)
	memoryLoad_text = local.Translate("local_status_memory").format(ramLoad_text, swapLoad_text)

	# Network status
	netLoad1_text = GetColorInt(netLoad1, 300, logic="less")
	netLoad5_text = GetColorInt(netLoad5, 300, logic="less")
	netLoad15_text = GetColorInt(netLoad15, 300, logic="less")
	netLoad_text = local.Translate("local_status_net_load").format(netLoad1_text, netLoad5_text, netLoad15_text)

	# Disks status
	disksLoad_data = list()
	for key, item in disksLoadAvg.items():
		diskLoad1_text = bcolors.Green(item[0])
		diskLoad5_text = bcolors.Green(item[1])
		diskLoad15_text = bcolors.Green(item[2])
		diskLoadPercent1_text = GetColorInt(disksLoadPercentAvg[key][0], 80, logic="less", ending="%")
		diskLoadPercent5_text = GetColorInt(disksLoadPercentAvg[key][1], 80, logic="less", ending="%")
		diskLoadPercent15_text = GetColorInt(disksLoadPercentAvg[key][2], 80, logic="less", ending="%")
		buff = "{}, {}"
		buff = "{}{}:[{}{}{}]{}".format(bcolors.cyan, key, bcolors.default, buff, bcolors.cyan, bcolors.endc)
		disksLoad_buff = buff.format(diskLoad15_text, diskLoadPercent15_text)
		disksLoad_data.append(disksLoad_buff)
	disksLoad_data = ", ".join(disksLoad_data)
	disksLoad_text = local.Translate("local_status_disks_load").format(disksLoad_data)

	# Thread status
	mytoscoreStatus_bool = GetServiceStatus("mytoscore")
	validatorStatus_bool = GetServiceStatus("validator")
	mytoscoreUptime = GetServiceUptime("mytoscore")
	validatorUptime = GetServiceUptime("validator")
	mytoscoreUptime_text = bcolors.Green(time2human(mytoscoreUptime))
	validatorUptime_text = bcolors.Green(time2human(validatorUptime))
	mytoscoreStatus = GetColorStatus(mytoscoreStatus_bool)
	validatorStatus = GetColorStatus(validatorStatus_bool)
	mytoscoreStatus_text = local.Translate("local_status_mytoscore_status").format(mytoscoreStatus, mytoscoreUptime_text)
	validatorStatus_text = local.Translate("local_status_validator_status").format(validatorStatus, validatorUptime_text)
	validatorOutOfSync_text = local.Translate("local_status_validator_out_of_sync").format(GetColorInt(validatorOutOfSync, 20, logic="less", ending=" s"))
	dbSize_text = GetColorInt(dbSize, 1000, logic="less", ending=" Gb")
	dbUsage_text = GetColorInt(dbUsage, 80, logic="less", ending="%")
	dbStatus_text = local.Translate("local_status_db").format(dbSize_text, dbUsage_text)
	
	# Mytosctrl and validator git hash
	mtcGitPath = "/usr/src/mytosctrl"
	validatorGitPath = "/usr/src/tos"
	mtcGitHash = GetGitHash(mtcGitPath, short=True)
	validatorGitHash = GetGitHash(validatorGitPath, short=True)
	mtcGitBranch = GetGitBranch(mtcGitPath)
	validatorGitBranch = GetGitBranch(validatorGitPath)
	mtcGitHash_text = bcolors.Yellow(mtcGitHash)
	validatorGitHash_text = bcolors.Yellow(validatorGitHash)
	mtcGitBranch_text = bcolors.Yellow(mtcGitBranch)
	validatorGitBranch_text = bcolors.Yellow(validatorGitBranch)
	mtcVersion_text = local.Translate("local_status_version_mtc").format(mtcGitHash_text, mtcGitBranch_text)
	validatorVersion_text = local.Translate("local_status_version_validator").format(validatorGitHash_text, validatorGitBranch_text)

	ColorPrint(local.Translate("local_status_head"))
	print(validatorIndex_text)
	print(validatorEfficiency_text)
	print(adnlAddr_text)
	print(walletAddr_text)
	print(walletBalance_text)
	print(cpuLoad_text)
	print(netLoad_text)
	print(memoryLoad_text)
	
	print(disksLoad_text)
	print(mytoscoreStatus_text)
	print(validatorStatus_text)
	print(validatorOutOfSync_text)
	print(dbStatus_text)
	print(mtcVersion_text)
	print(validatorVersion_text)
	print()
#end define

def GetColorInt(data, border, logic, ending=None):
	if data is None:
		result = bcolors.Green("n/a")
	elif logic == "more":
		if data >= border:
			result = bcolors.Green(data, ending)
		else:
			result = bcolors.Red(data, ending)
	elif logic == "less":
		if data <= border:
			result = bcolors.Green(data, ending)
		else:
			result = bcolors.Red(data, ending)
	return result
#end define

def GetColorStatus(input):
	if input == True:
		result = bcolors.Green("working")
	else:
		result = bcolors.Red("not working")
	return result
#end define

def PrintTosConfig(fullConfigAddr, fullElectorAddr, config15, config17):
	validatorsElectedFor = config15["validatorsElectedFor"]
	electionsStartBefore = config15["electionsStartBefore"]
	electionsEndBefore = config15["electionsEndBefore"]
	stakeHeldFor = config15["stakeHeldFor"]
	minStake = config17["minStake"]
	maxStake = config17["maxStake"]

	fullConfigAddr_text = local.Translate("tos_config_configurator_addr").format(bcolors.Yellow(fullConfigAddr))
	fullElectorAddr_text = local.Translate("tos_config_elector_addr").format(bcolors.Yellow(fullElectorAddr))
	validatorsElectedFor_text = bcolors.Yellow(validatorsElectedFor)
	electionsStartBefore_text = bcolors.Yellow(electionsStartBefore)
	electionsEndBefore_text = bcolors.Yellow(electionsEndBefore)
	stakeHeldFor_text = bcolors.Yellow(stakeHeldFor)
	elections_text = local.Translate("tos_config_elections").format(validatorsElectedFor_text, electionsStartBefore_text, electionsEndBefore_text, stakeHeldFor_text)
	minStake_text = bcolors.Yellow(minStake)
	maxStake_text = bcolors.Yellow(maxStake)
	stake_text = local.Translate("tos_config_stake").format(minStake_text, maxStake_text)

	ColorPrint(local.Translate("tos_config_head"))
	print(fullConfigAddr_text)
	print(fullElectorAddr_text)
	print(elections_text)
	print(stake_text)
	print()
#end define

def PrintTimes(rootWorkchainEnabledTime_int, startWorkTime, oldStartWorkTime, config15):
	validatorsElectedFor = config15["validatorsElectedFor"]
	electionsStartBefore = config15["electionsStartBefore"]
	electionsEndBefore = config15["electionsEndBefore"]

	if startWorkTime == 0:
		startWorkTime = oldStartWorkTime
	#end if

	# Calculate time
	startValidation = startWorkTime
	endValidation = startWorkTime + validatorsElectedFor
	startElection = startWorkTime - electionsStartBefore
	endElection = startWorkTime - electionsEndBefore
	startNextElection = startElection + validatorsElectedFor

	# timestamp to datetime
	rootWorkchainEnabledTime = Timestamp2Datetime(rootWorkchainEnabledTime_int)
	startValidationTime = Timestamp2Datetime(startValidation)
	endValidationTime = Timestamp2Datetime(endValidation)
	startElectionTime = Timestamp2Datetime(startElection)
	endElectionTime = Timestamp2Datetime(endElection)
	startNextElectionTime = Timestamp2Datetime(startNextElection)

	# datetime to color text
	rootWorkchainEnabledTime_text = local.Translate("times_root_workchain_enabled_time").format(bcolors.Yellow(rootWorkchainEnabledTime))
	startValidationTime_text = local.Translate("times_start_validation_time").format(GetColorTime(startValidationTime, startValidation))
	endValidationTime_text = local.Translate("times_end_validation_time").format(GetColorTime(endValidationTime, endValidation))
	startElectionTime_text = local.Translate("times_start_election_time").format(GetColorTime(startElectionTime, startElection))
	endElectionTime_text = local.Translate("times_end_election_time").format(GetColorTime(endElectionTime, endElection))
	startNextElectionTime_text = local.Translate("times_start_next_election_time").format(GetColorTime(startNextElectionTime, startNextElection))

	ColorPrint(local.Translate("times_head"))
	print(rootWorkchainEnabledTime_text)
	print(startValidationTime_text)
	print(endValidationTime_text)
	print(startElectionTime_text)
	print(endElectionTime_text)
	print(startNextElectionTime_text)
#end define

def GetColorTime(datetime, timestamp):
	newTimestamp = GetTimestamp()
	if timestamp > newTimestamp:
		result = bcolors.Green(datetime)
	else:
		result = bcolors.Yellow(datetime)
	return result
#end define

def Seqno(args):
	try:
		walletName = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} seqno <wallet-name>")
		return
	wallet = tos.GetLocalWallet(walletName)
	seqno = tos.GetSeqno(wallet)
	print(walletName, "seqno:", seqno)
#end define

def CreatNewWallet(args):
	version = "v1"
	try:
		if len(args) == 0:
			walletName = tos.GenerateWalletName()
			workchain = 0
		else:
			workchain = int(args[0])
			walletName = args[1]
		if len(args) > 2:
			version = args[2]
		if len(args) == 4:
			subwallet = int(args[3])
		else:
			subwallet = 300897706 + workchain # 0x11EF55AA + workchain
	except:
		ColorPrint("{red}Bad args. Usage:{endc} nw <workchain-id> <wallet-name> [<version> <subwallet>]")
		return
	wallet = tos.CreateWallet(walletName, workchain, version, subwallet=subwallet)
	table = list()
	table += [["Name", "Workchain", "Address"]]
	table += [[wallet.name, wallet.workchain, wallet.addrB64_init]]
	PrintTable(table)
#end define

def ActivateWallet(args):
	try:
		walletName = args[0]
	except Exception as err:
		walletName = "all"
	if walletName == "all":
		tos.WalletsCheck()
	else:
		wallet = tos.GetLocalWallet(walletName)
		if not os.path.isfile(wallet.bocFilePath):
			local.AddLog("Wallet {walletName} already activated".format(walletName=walletName), "warning")
			return
		tos.ActivateWallet(wallet)
	ColorPrint("ActivateWallet - {green}OK{endc}")
#end define

def PrintWalletsList(args):
	table = list()
	table += [["Name", "Status", "Balance", "Ver", "Wch", "Address"]]
	data = tos.GetWallets()
	if (data is None or len(data) == 0):
		print("No data")
		return
	for wallet in data:
		account = tos.GetAccount(wallet.addrB64)
		if account.status != "active":
			wallet.addrB64 = wallet.addrB64_init
		table += [[wallet.name, account.status, account.balance, wallet.version, wallet.workchain, wallet.addrB64]]
	PrintTable(table)
#end define

def ImportWalletFromFile(args):
	try:
		filePath = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} iw <wallet-path>")
		return
	if (".addr" in filePath):
		filePath = filePath.replace(".addr", '')
	if (".pk" in filePath):
		filePath = filePath.replace(".pk", '')
	if os.path.isfile(filePath + ".addr") == False:
		local.AddLog("ImportWalletFromFile error: Address file not found: " + filePath, "error")
		return
	if os.path.isfile(filePath + ".pk") == False:
		local.AddLog("ImportWalletFromFile error: Private key not found: " + filePath, "error")
		return
	if '/' in filePath:
		walletName = filePath[filePath.rfind('/')+1:]
	else:
		walletName = filePath
	copyfile(filePath + ".addr", tos.walletsDir + walletName + ".addr")
	copyfile(filePath + ".pk", tos.walletsDir + walletName + ".pk")
	ColorPrint("ImportWalletFromFile - {green}OK{endc}")
#end define

def ImportWallet(args):
	try:
		addr = args[0]
		key = args[1]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} iw <wallet-addr> <wallet-secret-key>")
		return
	name = tos.ImportWallet(addr, key)
	print("Wallet name:", name)
#end define

def SetWalletVersion(args):
	try:
		addr = args[0]
		version = args[1]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} swv <wallet-addr> <wallet-version>")
		return
	tos.SetWalletVersion(addr, version)
	ColorPrint("SetWalletVersion - {green}OK{endc}")
#end define

def ExportWallet(args):
	try:
		name = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} ew <wallet-name>")
		return
	addr, key = tos.ExportWallet(name)
	print("Wallet name:", name)
	print("Address:", addr)
	print("Secret key:", key)
#end define

def DeleteWallet(args):
	try:
		walletName = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} dw <wallet-name>")
		return
	wallet = tos.GetLocalWallet(walletName)
	wallet.Delete()
	ColorPrint("DeleteWallet - {green}OK{endc}")
#end define

def ViewAccountStatus(args):
	try:
		addrB64 = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} vas <account-addr>")
		return
	addrB64 = tos.GetDestinationAddr(addrB64)
	account = tos.GetAccount(addrB64)
	version = tos.GetWalletVersionFromHash(account.codeHash)
	statusTable = list()
	statusTable += [["Address", "Status", "Version", "Balance"]]
	statusTable += [[addrB64, account.status, version, account.balance]]
	historyTable = GetHistoryTable(addrB64, 10)
	PrintTable(statusTable)
	print()
	PrintTable(historyTable)
#end define

def ViewAccountHistory(args):
	try:
		addr = args[0]
		limit = int(args[1])
	except:
		ColorPrint("{red}Bad args. Usage:{endc} vah <account-addr> <limit>")
		return
	table = GetHistoryTable(addr, limit)
	PrintTable(table)
#end define

def GetHistoryTable(addr, limit):
	addr = tos.GetDestinationAddr(addr)
	account = tos.GetAccount(addr)
	history = tos.GetAccountHistory(account, limit)
	table = list()
	typeText = ColorText("{red}{bold}{endc}")
	table += [["Time", typeText, "Coins", "From/To"]]
	for message in history:
		if message.srcAddr is None:
			continue
		srcAddrFull = f"{message.srcWorkchain}:{message.srcAddr}"
		destAddFull = f"{message.destWorkchain}:{message.destAddr}"
		if srcAddrFull == account.addrFull:
			type = ColorText("{red}{bold}>>>{endc}")
			fromto = destAddFull
		else:
			type = ColorText("{blue}{bold}<<<{endc}")
			fromto = srcAddrFull
		fromto = tos.AddrFull2AddrB64(fromto)
		#datetime = Timestamp2Datetime(message.time, "%Y.%m.%d %H:%M:%S")
		datetime = timeago(message.time)
		table += [[datetime, type, message.value, fromto]]
	return table
#end define

def MoveCoins(args):
	try:
		walletName = args[0]
		destination = args[1]
		amount = args[2]
		flags = args[3:]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} mg <wallet-name> <account-addr | bookmark-name> <amount>")
		return
	wallet = tos.GetLocalWallet(walletName)
	destination = tos.GetDestinationAddr(destination)
	tos.MoveCoins(wallet, destination, amount, flags=flags)
	ColorPrint("MoveCoins - {green}OK{endc}")
#end define

def MoveCoinsThroughProxy(args):
	try:
		walletName = args[0]
		destination = args[1]
		amount = args[2]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} mgtp <wallet-name> <account-addr | bookmark-name> <amount>")
		return
	wallet = tos.GetLocalWallet(walletName)
	destination = tos.GetDestinationAddr(destination)
	tos.MoveCoinsThroughProxy(wallet, destination, amount)
	ColorPrint("MoveCoinsThroughProxy - {green}OK{endc}")
#end define

def CreatNewBookmark(args):
	try:
		name = args[0]
		addr = args[1]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} nb <bookmark-name> <account-addr | domain-name>")
		return
	if tos.IsAddr(addr):
		type = "account"
	else:
		type = "domain"
	#end if

	bookmark = dict()
	bookmark["name"] = name
	bookmark["type"] = type
	bookmark["addr"] = addr
	tos.AddBookmark(bookmark)
	ColorPrint("CreatNewBookmark - {green}OK{endc}")
#end define

def PrintBookmarksList(args):
	data = tos.GetBookmarks()
	if (data is None or len(data) == 0):
		print("No data")
		return
	table = list()
	table += [["Name", "Type", "Address / Domain", "Balance / Exp. date"]]
	for item in data:
		name = item.get("name")
		type = item.get("type")
		addr = item.get("addr")
		data = item.get("data")
		table += [[name, type, addr, data]]
	PrintTable(table)
#end define

def DeleteBookmark(args):
	try:
		name = args[0]
		type = args[1]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} db <bookmark-name> <bookmark-type>")
		return
	tos.DeleteBookmark(name, type)
	ColorPrint("DeleteBookmark - {green}OK{endc}")
#end define

def PrintOffersList(args):
	offers = tos.GetOffers()
	if "--json" in args:
		text = json.dumps(offers, indent=2)
		print(text)
	else:
		table = list()
		table += [["Hash", "Votes", "W/L", "Approved", "Is passed"]]
		for item in offers:
			hash = item.get("hash")
			votedValidators = len(item.get("votedValidators"))
			wins = item.get("wins")
			losses = item.get("losses")
			wl = "{0}/{1}".format(wins, losses)
			approvedPercent = item.get("approvedPercent")
			approvedPercent_text = "{0}%".format(approvedPercent)
			isPassed = item.get("isPassed")
			if "hash" not in args:
				hash = Reduct(hash)
			if isPassed == True:
				isPassed = bcolors.Green("true")
			if isPassed == False:
				isPassed = bcolors.Red("false")
			table += [[hash, votedValidators, wl, approvedPercent_text, isPassed]]
		PrintTable(table)
#end define

def VoteOffer(args):
	if len(args) == 0:
		ColorPrint("{red}Bad args. Usage:{endc} vo <offer-hash>")
		return
	for offerHash in args:
		tos.VoteOffer(offerHash)
	ColorPrint("VoteOffer - {green}OK{endc}")
#end define

def OfferDiff(args):
	try:
		offerHash = args[0]
		offerHash = offerHash
	except:
		ColorPrint("{red}Bad args. Usage:{endc} od <offer-hash>")
		return
	tos.GetOfferDiff(offerHash)
#end define

def GetConfig(args):
	try:
		configId = args[0]
		configId = int(configId)
	except:
		ColorPrint("{red}Bad args. Usage:{endc} gc <config-id>")
		return
	data = tos.GetConfig(configId)
	text = json.dumps(data, indent=2)
	print(text)
#end define

def PrintComplaintsList(args):
	past = "past" in args
	complaints = tos.GetComplaints(past=past)
	if "--json" in args:
		text = json.dumps(complaints, indent=2)
		print(text)
	else:
		table = list()
		table += [["Election id", "ADNL", "Fine (part)", "Votes", "Approved", "Is passed"]]
		for key, item in complaints.items():
			electionId = item.get("electionId")
			adnl = item.get("adnl")
			suggestedFine = item.get("suggestedFine")
			suggestedFinePart = item.get("suggestedFinePart")
			Fine_text = "{0} ({1})".format(suggestedFine, suggestedFinePart)
			votedValidators = len(item.get("votedValidators"))
			approvedPercent = item.get("approvedPercent")
			approvedPercent_text = "{0}%".format(approvedPercent)
			isPassed = item.get("isPassed")
			if "adnl" not in args:
				adnl = Reduct(adnl)
			if isPassed == True:
				isPassed = bcolors.Green("true")
			if isPassed == False:
				isPassed = bcolors.Red("false")
			table += [[electionId, adnl, Fine_text, votedValidators, approvedPercent_text, isPassed]]
		PrintTable(table)
#end define

def VoteComplaint(args):
	try:
		electionId = args[0]
		complaintHash = args[1]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} vc <election-id> <complaint-hash>")
		return
	tos.VoteComplaint(electionId, complaintHash)
	ColorPrint("VoteComplaint - {green}OK{endc}")
#end define

def NewDomain(args):
	try:
		domainName = args[0]
		walletName = args[1]
		adnlAddr = args[2]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} nd <domain-name> <wallet-name> <site-adnl-addr>")
		return
	domain = dict()
	domain["name"] = domainName
	domain["adnlAddr"] = adnlAddr
	domain["walletName"] = walletName
	tos.NewDomain(domain)
	ColorPrint("NewDomain - {green}OK{endc}")
#end define

def PrintDomainsList(args):
	data = tos.GetDomains()
	if (data is None or len(data) == 0):
		print("No data")
		return
	table = list()
	table += [["Domain", "Wallet", "Expiration date", "ADNL address"]]
	for item in data:
		domainName = item.get("name")
		walletName = item.get("walletName")
		endTime = item.get("endTime")
		endTime = Timestamp2Datetime(endTime, "%d.%m.%Y")
		adnlAddr = item.get("adnlAddr")
		table += [[domainName, walletName, endTime, adnlAddr]]
	PrintTable(table)
#end define

def ViewDomainStatus(args):
	try:
		domainName = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} vds <domain-name>")
		return
	domain = tos.GetDomain(domainName)
	endTime = domain.get("endTime")
	endTime = Timestamp2Datetime(endTime, "%d.%m.%Y")
	adnlAddr = domain.get("adnlAddr")
	table = list()
	table += [["Domain", "Expiration date", "ADNL address"]]
	table += [[domainName, endTime, adnlAddr]]
	PrintTable(table)
#end define

def DeleteDomain(args):
	try:
		domainName = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} dd <domain-name>")
		return
	tos.DeleteDomain(domainName)
	ColorPrint("DeleteDomain - {green}OK{endc}")
#end define

def PrintElectionEntriesList(args):
	past = "past" in args
	entries = tos.GetElectionEntries(past=past)
	if "--json" in args:
		text = json.dumps(entries, indent=2)
		print(text)
	else:
		table = list()
		table += [["ADNL", "Pubkey", "Wallet", "Stake", "Max-factor"]]
		for key, item in entries.items():
			adnl = item.get("adnlAddr")
			pubkey = item.get("pubkey")
			walletAddr = item.get("walletAddr")
			stake = item.get("stake")
			maxFactor = item.get("maxFactor")
			if "adnl" not in args:
				adnl = Reduct(adnl)
			if "pubkey" not in args:
				pubkey = Reduct(pubkey)
			if "wallet" not in args:
				walletAddr = Reduct(walletAddr)
			table += [[adnl, pubkey, walletAddr, stake, maxFactor]]
		PrintTable(table)
#end define

def VoteElectionEntry(args):
	Elections(tos)
	ColorPrint("VoteElectionEntry - {green}OK{endc}")
#end define

def PrintValidatorList(args):
	past = "past" in args
	validators = tos.GetValidatorsList(past=past)
	if "--json" in args:
		text = json.dumps(validators, indent=2)
		print(text)
	else:
		table = list()
		table += [["ADNL", "Pubkey", "Wallet", "Efficiency", "Online"]]
		for item in validators:
			adnl = item.get("adnlAddr")
			pubkey = item.get("pubkey")
			walletAddr = item.get("walletAddr")
			efficiency = item.get("efficiency")
			online = item.get("online")
			if "adnl" not in args:
				adnl = Reduct(adnl)
			if "pubkey" not in args:
				pubkey = Reduct(pubkey)
			if "wallet" not in args:
				walletAddr = Reduct(walletAddr)
			if "offline" in args and online != False:
				continue
			if online == True:
				online = bcolors.Green("true")
			if online == False:
				online = bcolors.Red("false")
			table += [[adnl, pubkey, walletAddr, efficiency, online]]
		PrintTable(table)
#end define

def Reduct(item):
	item = str(item)
	if item is None:
		result = None
	else:
		end = len(item)
		result = item[0:6] + "..." + item[end-6:end]
	return result
#end define

def GetSettings(args):
	try:
		name = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} get <settings-name>")
		return
	result = tos.GetSettings(name)
	print(json.dumps(result, indent=2))
#end define

def SetSettings(args):
	try:
		name = args[0]
		value = args[1]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} set <settings-name> <settings-value>")
		return
	result = tos.SetSettings(name, value)
	ColorPrint("SetSettings - {green}OK{endc}")
#end define

def Xrestart(inputArgs):
	if len(inputArgs) < 2:
		ColorPrint("{red}Bad args. Usage:{endc} xrestart <timestamp> <args>")
		return
	args = ["python3", "/usr/src/mytosctrl/scripts/xrestart.py"]
	args += inputArgs
	exitCode = RunAsRoot(args)
	if exitCode == 0:
		text = "Xrestart - {green}OK{endc}"
	else:
		text = "Xrestart - {red}Error{endc}"
	ColorPrint(text)
#end define

def Xlist(args):
	ColorPrint("Xlist - {green}OK{endc}")
#end define

def NewPool(args):
	try:
		poolName = args[0]
		validatorRewardSharePercent = float(args[1])
		maxNominatorsCount = int(args[2])
		minValidatorStake = int(args[3])
		minNominatorStake = int(args[4])
	except:
		ColorPrint("{red}Bad args. Usage:{endc} new_pool <pool-name> <validator-reward-share-percent> <max-nominators-count> <min-validator-stake> <min-nominator-stake>")
		return
	tos.CreatePool(poolName, validatorRewardSharePercent, maxNominatorsCount, minValidatorStake, minNominatorStake)
	ColorPrint("NewPool - {green}OK{endc}")
#end define

def ActivatePool(args):
	try:
		poolName = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} activate_pool <pool-name>")
		return
	pool = tos.GetLocalPool(poolName)
	if not os.path.isfile(pool.bocFilePath):
		local.AddLog(f"Pool {poolName} already activated", "warning")
		return
	tos.ActivatePool(pool)
	ColorPrint("ActivatePool - {green}OK{endc}")
#end define

def PrintPoolsList(args):
	table = list()
	table += [["Name", "Status", "Balance", "Address"]]
	data = tos.GetPools()
	if (data is None or len(data) == 0):
		print("No data")
		return
	for pool in data:
		account = tos.GetAccount(pool.addrB64)
		if account.status != "active":
			pool.addrB64 = pool.addrB64_init
		table += [[pool.name, account.status, account.balance, pool.addrB64]]
	PrintTable(table)
#end define

def GetPoolData(args):
	try:
		poolName = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} get_pool_data <pool-name | pool-addr>")
		return
	if tos.IsAddr(poolName):
		poolAddr = poolName
	else:
		pool = tos.GetLocalPool(poolName)
		poolAddr = pool.addrB64
	poolData = tos.GetPoolData(poolAddr)
	print(json.dumps(poolData, indent=4))
#end define

def DepositToPool(args):
	try:
		walletName = args[0]
		pollAddr = args[1]
		amount = float(args[2])
	except:
		ColorPrint("{red}Bad args. Usage:{endc} deposit_to_pool <wallet-name> <pool-addr> <amount>")
		return
	tos.DepositToPool(walletName, pollAddr, amount)
	ColorPrint("DepositToPool - {green}OK{endc}")
#end define

def WithdrawFromPool(args):
	try:
		walletName = args[0]
		poolAddr = args[1]
		amount = float(args[2])
	except:
		ColorPrint("{red}Bad args. Usage:{endc} withdraw_from_pool <wallet-name> <pool-addr> <amount>")
		return
	poolAddr = tos.GetDestinationAddr(poolAddr)
	tos.WithdrawFromPool(walletName, poolAddr, amount)
	ColorPrint("WithdrawFromPool - {green}OK{endc}")
#end define

def DeletePool(args):
	try:
		poolName = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} delete_pool <pool-name>")
		return
	pool = tos.GetLocalPool(poolName)
	pool.Delete()
	ColorPrint("DeletePool - {green}OK{endc}")
#end define

def UpdateValidatorSet(args):
	try:
		poolAddr = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} update_validator_set <pool-addr>")
		return
	wallet = self.GetValidatorWallet()
	self.PoolUpdateValidatorSet(poolAddr, wallet)
	ColorPrint("DeletePool - {green}OK{endc}")
#end define


###
### Start of the program
###

if __name__ == "__main__":
	Init(sys.argv[1:])
	console.Run()
#end if
