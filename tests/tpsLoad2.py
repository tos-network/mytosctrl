#!/usr/bin/env python3
# -*- coding: utf_8 -*-l

from sys import path
path.append("/usr/src/mytosctrl/")
from mytoscore import *

Local = MyPyClass(__file__)
tos = MyTosCore()


def Init():
	wallets = list()
	Local.buffer["wallets"] = wallets
	walletsNameList = tos.GetWalletsNameList()
	
	# Create tests wallet
	testsWalletName = "tests_hwallet"
	testsWallet = tos.CreateHighWallet(testsWalletName)

	# Check tests wallet balance
	account = tos.GetAccount(testsWallet.addr)
	local.AddLog("wallet: {addr}, status: {status}, balance: {balance}".format(addr=testsWallet.addr, status=account.status, balance=account.balance))
	if account.balance == 0:
		raise Exception(testsWallet.name + " wallet balance is empty.")
	if account.status == "uninit":
		tos.SendFile(testsWallet.bocFilePath, testsWallet)

	# Create wallets
	for i in range(load):
		walletName = testsWalletName
		if walletName not in walletsNameList:
			wallet = tos.CreateHighWallet(walletName, i)
		else:
			wallet = tos.GetLocalWallet(walletName, "hw", i)
		wallets.append(wallet)
	#end for

	# Fill up wallets
	buff_wallet = None
	buff_seqno = None
	destList = list()
	for wallet in wallets:
		wallet.account = tos.GetAccount(wallet.addr)
		need = 20 - wallet.account.balance
		if need > 10:
			destList.append([wallet.addr_init, need])
		elif need < -10:
			need = need * -1
			buff_wallet = wallet
			buff_wallet.oldseqno = tos.GetSeqno(wallet)
			tos.MoveGramsFromHW(wallet, [[testsWallet.addr, need]], wait=False)
			Local.AddLog(testsWallet.name + " <<< " + str(wallet.subwallet))
	if buff_wallet:
		tos.WaitTransaction(buff_wallet)
	#end for

	# Move grams from highload wallet
	tos.MoveGramsFromHW(testsWallet, destList)

	# Activate wallets
	for wallet in wallets:
		if wallet.account.status == "uninit":
			wallet.oldseqno = tos.GetSeqno(wallet)
			tos.SendFile(wallet.bocFilePath)
		Local.AddLog(str(wallet.subwallet) + " - OK")
	tos.WaitTransaction(wallets[-1])
#end define

def Work():
	wallets = Local.buffer["wallets"]
	destList = list()
	for i in range(load):
		destList.append([wallets[i].addr, 0.1])
	for wallet in wallets:
		wallet.oldseqno = tos.GetSeqno(wallet)
		tos.MoveGramsFromHW(wallet, destList, wait=False)
		Local.AddLog(str(wallet.subwallet) + " " + wallet.addr + " >>> ")
	tos.WaitTransaction(wallets[-1])
#end define

def General():
	Init()
	while True:
		time.sleep(1)
		Work()
		Local.AddLog("Work - OK")
	#end while
#end define



###
### Start test
###
Local = MyPyClass(__file__)
Local.db["config"]["logLevel"] = "info"
Local.Run()

tos = MyTosCore()
local.db["config"]["logLevel"] = "info"
load = 10

Local.StartCycle(General, sec=1)
while True:
	time.sleep(60)
	hour_str = time.strftime("%H")
	hour = int(hour_str)
	load = hour * 4
#end while
