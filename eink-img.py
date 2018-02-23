#!/usr/bin/python3

#******************************************************************************
# Name        : Image loader for E-Ink display GDEW027Z22 2,7" R/B/W
# 
# Description : This is a image loader to E-Ink display from Good-Display. 
#               The e-ink screen have 3 colors:
#               Black/Red/White - while it can be only red or black 
#               (the red have priority over black).
#               Image file HAVE TO exactly: 176x264pixels and be in 24bit RGB
#               so no transparency, and should have only 3 colors that display 
#               is using (red/black/white) - other colors (and variation
#               of those 3 colors might result in white color).
#               Display resolution is 264x176, and the "pixel" have layout 
#               of honeycomb.
# 
# Date        : 2018-02-23
# Author      : Przemyslaw W [saper_2]
# License     : Beerware (rv.42) - Google for it.
# 
# Changelog   :
#               - 0.1 - Initial version
#******************************************************************************

import time
import spidev
import sys
import GDEW027Z22
import os.path


print("E-INK GDEW027Z22 (2.7\" Red/Black/White) image loader.")
print("Author: saper_2 (2018-02-23)")
print(" ")

# check for 2nd argument or print usage and quit
if (len(sys.argv) < 2):
	print("Usage: {} [image_file]".format(sys.argv[0]))
	print("\033[33;1m" "Warning:\033[0m" + "\033[33m" + " Image file\033[91m have to\033[33m size: 176 x 264 px\033[0m")
	sys.exit(1)

# 2nd arg is "0" for clearing display ?
onlyclear=0
try:
	if (sys.argv[1] == "0"):
		onlyclear=1
except:
	pass

# if 2nd arg is not "0" but path to the file then check it
if (os.path.isfile(sys.argv[1]) == False and onlyclear==0):
	print("\033[33m" + "Selected file: {} does not exists or is not a file!".format(sys.argv[1]) + "\033[0m")
	sys.exit(2)

# display connections
print("E-INK pinout:")
print("RPi       = E-INK")
print("spi0.mode = 0")
print("spi0.clk  = CLK")
print("spi0.mosi = DATA")
print("spi0.cs0  = /CS")
print("BCM_IO.25 = D/C")
print("BCM_IO.18 = /Reset")
print("BCM_IO.23 = Busy")
# spi0: mosi=DTA, clk=CLK, cs0=cs, io25=dc, io18=rst, io23=busy, spi_f_clk= ~8MHz
eink = GDEW027Z22.GDEW027Z22(spiBus=0, spiCs=0,spiClockHz=8000000, dcPin=25, rstPin=18, bsyPin=23)
print("E-INK init done.")
print(" ")
print(" ")
try:
	print("Clear B/W...")
	eink.clear_bw(0x00)
	print("done.")
	
	print("Clear Red/W...")
	eink.clear_rw(0x00)
	print("done.")
	
	
	if (onlyclear == 0):
		print("Loading file: \033[94m{}\033[0m".format(sys.argv[1]))
		eink.fb_load(sys.argv[1])
		print("Updating display...")
		eink.fb_update()
		print("done.")
	else:
		print("Display update...")
		eink.update()
		print("done.")
	
	print("done.")
except Exception as ex:
	print("\033[31m" + "Error occured...\033[91m")
	print(ex)
	print("\033[0m")
	sys.exit(3)

print("Power down display...")
eink.shutdown()
print("Shutdown: ok, deep sleep...")
eink.deep_sleep()
print("deep sleep: ok")

print("*** END. ***")

