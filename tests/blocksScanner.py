#!/usr/bin/env python3
# -*- coding: utf_8 -*-

import sys
sys.path.append("/usr/src/mytosctrl/")
from mypylib.mypylib import bcolors, Sleep
from mytoscore import MyTosCore, TosBlocksScanner

def NewBlockReaction(block):
	print(f"{bcolors.green} block: {bcolors.endc} {block}")
#end define

def NewTransReaction(trans):
	print(f"{bcolors.magenta} trans: {bcolors.endc} {trans}")
#end define

def NewMessageReaction(message):
	print(f"{bcolors.yellow} message: {bcolors.endc} {message}")
#end define


tos = MyTosCore()
scanner = TosBlocksScanner(tos, nbr=NewBlockReaction, ntr=NewTransReaction, nmr=NewMessageReaction)
scanner.Run()
Sleep()
