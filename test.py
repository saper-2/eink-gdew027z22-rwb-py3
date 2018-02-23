#!/usr/bin/python3

import time
import spidev
import sys
import GDEW027Z22
import traceback

# Set test mode:
# -1 - only clear
# 0 - pattern fill test
# 1 - image load (and process pixels colors) and save load result
# 2 - show python3-test image
# 3 - show saper-logo2 image
testmode=-1

try:
	testmode = int(sys.argv[1])
except:
	print("Usage ./test.py [testmode]")
	print("Testmodes:")
	print("-1 - Only clear panel")
	print(" 0 - Pattern fill test")
	print(" 1 - load image 'GDEW027Z22-pyton3-test.png' and save it after processing to test1.png")
	print(" 2 - show image 'GDEW027Z22-pyton3-test.png'")
	print(" 3 - show image 'saper-logo2-GDEW027Z22-rbw.bmp'")
	#print("  - ")
	#print("  - ")
	sys.exit(1)

print("E-INK GDEW027Z22 driver test program...")

# defaults: spi=0, cs=io8, d/c=io25, rst=io24, bsy=io23 dta=miso[io9] , clk=sclk[io11]
# does not apply because I use now SW spi (miso[io9] & mosi[io10] must be connected with 1k resistor)
#dtaPin=9, clkPin=11, csPin=8, dcPin=25, rstPin=24, bsyPin=23
eink = GDEW027Z22.GDEW027Z22(spiBus=0, spiCs=0,spiClockHz=8000000, dcPin=25, rstPin=18, bsyPin=23)
print("Init done.")

print("Selected testmode: {}".format(testmode))

try:
	print("Clear B/W...")
	eink.clear_bw(0x00)
	print("done.")
	
	print("Clear Red/W...")
	eink.clear_rw(0x00)
	print("done.")
	
	if (testmode == -1):
		print(".")
	elif (testmode == 0):
		print("Pattern black 0x36...")
		eink.clear_bw(0x36)
		print("Pattern red 0x18...")
		eink.clear_rw(0x18)
		print("done.")
	elif (testmode == 1):
		print("Loading test image: GDEW027Z22-pyton3-test.png")
		eink.fb_load("GDEW027Z22-pyton3-test.png")
		print("Saving test image load result to file: test1.png")
		eink.fb_save("test1.png")
	elif (testmode == 2):
		print("Loading test image: GDEW027Z22-pyton3-test.png")
		eink.fb_load("GDEW027Z22-pyton3-test.png")
		print("Update display...")
		eink.fb_update()
		print("done.")
	elif (testmode == 3):
		print("Loading test image: saper-logo2-GDEW027Z22-rbw.bmp")
		eink.fb_load("saper-logo2-GDEW027Z22-rbw.bmp")
		print("Update display...")
		eink.fb_update()
		print("done.")
	else:
		print("Unknown testmode: {}".format(testmode))
	
	if (testmode == -1 or testmode == 0 or testmode == 1):
		print("Display update...")
		eink.update()
		print("done.")
	
except:
	print("\033[31m" + "Error occured...")
	traceback.print_exc()
	print("\033[0m")

print("Power down display...")
eink.shutdown()
print("Shutdown: ok, deep sleep...")
eink.deep_sleep()
print("deep sleep: ok")

print("*** PROGRAM END. ***")

