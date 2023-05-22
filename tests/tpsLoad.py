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
		walletName = "w_" + str(i)
		if walletName not in walletsNameList:
			wallet = tos.CreateWallet(walletName)
		else:
			wallet = tos.GetLocalWallet(walletName)
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
			tos.MoveGrams(wallet, testsWallet.addr, need, wait=False)
			Local.AddLog(testsWallet.name + " <<< " + wallet.name)
	if buff_wallet:
		tos.WaitTransaction(buff_wallet, False)
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
	for i in range(load):
		if i + 1 == load:
			i = -1
		#end if
		
		wallet1 = wallets[i]
		wallet2 = wallets[i+1]
		wallet1.oldseqno = tos.GetSeqno(wallet1)
		tos.MoveGrams(wallet1, wallet2.addr, 3.14, wait=False)
		Local.AddLog(wallet1.name + " >>> " + wallet2.name)
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
load = 100

Local.StartCycle(General, sec=1)
Sleep()
