#!/usr/bin/python3

#******************************************************************************
# Name        : Driver for E-INK GDEW027Z22 2,7" R/B/W (using software SPI)
# 
# Description : Display from Good-Display. This e-ink screen have 3 colors:
#               Black/Red/White - while it can be only red or black 
#               (the red have priority over black).
#               Display resolution 264x176, and the "pixel" have layout 
#               of honeycomb.
#               Controller: EK79652 for 2/3 colors e-ink from [???no idea??].
#               One note, after each byte CS line must be toggled so 
#               the send_cmd2 can't be optimized better :/
#               !!! I have dropped this file after I got spidev working. !!!
# 
# Date        : 2018-02-22
# Author      : Przemyslaw W [saper_2]
# License     : Beerware (rv.42) - Google for it.
# 
# Changelog   :
#               - 0.1 - Initial version
#******************************************************************************

import time
import spidev
import sys
import RPi.GPIO as GPIO

class GDEW027Z22:
	def __init__(self, dtaPin=9, clkPin=11, csPin=8, dcPin=25, rstPin=24, bsyPin=23, halfBitDelay=0.000001):
		#self.spi_bus =
		self.pin_dta = dtaPin
		self.pin_clk = clkPin
		self.pin_dc = dcPin
		self.pin_cs = csPin
		self.pin_rst = rstPin
		self.pin_bsy = bsyPin
		self.hdelay=halfBitDelay
		# some constans
		self.WIDTH=264
		self.HEIGHT=176
		# internal variables
		
		# setup I/O
		GPIO.setmode(GPIO.BCM)
		# data pin
		GPIO.setup(self.pin_dta,GPIO.IN, pull_up_down=GPIO.PUD_UP)
		# clock
		GPIO.setup(self.pin_clk, GPIO.OUT, initial=0)
		# D/C
		GPIO.setup(self.pin_dc, GPIO.OUT, initial=1)
		# CS
		GPIO.setup(self.pin_cs, GPIO.OUT, initial=1)
		# /RST
		GPIO.setup(self.pin_rst, GPIO.OUT, initial=1)
		# /BSY
		GPIO.setup(self.pin_bsy, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		# perform controller reset
		self.pin_rst_lo()
		time.sleep(0.01) # 10ms delay
		self.pin_rst_hi()
		# now init controller
		self.init_ctrl()
		
	# restor GPIO to defaults
	def __del__(self):
		GPIO.cleanup()
		
	# reset pin
	def pin_rst_lo(self):
		GPIO.output(self.pin_rst, 0)
	
	def pin_rst_hi(self):
		GPIO.output(self.pin_rst, 1)

	# busy pin
	def pin_get_bsy(self):
		if GPIO.input(self.pin_bsy):
			return 1
		else:
			return 0

	# clock pin
	def pin_clk_hi(self):
		GPIO.output(self.pin_clk, 1)
	
	def pin_clk_lo(self):
		GPIO.output(self.pin_clk, 0)
	
	# data pin
	def pin_dta_hi(self):
		GPIO.output(self.pin_dta, 1)
	
	def pin_dta_lo(self):
		GPIO.output(self.pin_dta, 0)
	
	def pin_dta_out(self):
		GPIO.setup(self.pin_dta, GPIO.OUT)
	
	def pin_dta_in(self):
		GPIO.setup(self.pin_dta, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	
	def pin_dta_get(self):
		if GPIO.input(self.pin_dta):
			return 1
		else:
			return 0

	
	# d/c pin
	def pin_dc_hi(self):
		GPIO.output(self.pin_dc, 1)
	
	def pin_dc_lo(self):
		GPIO.output(self.pin_dc, 0)
	
	# /cs pin
	def pin_cs_hi(self):
		GPIO.output(self.pin_cs, 1)
	
	def pin_cs_lo(self):
		GPIO.output(self.pin_cs, 0)
	
	#send byte
	def send_byte(self, b):
		self.pin_cs_lo()
		time.sleep(self.hdelay)
		self.pin_dta_out()
		for i in range(0,8):
			if (b & 0x80):
				self.pin_dta_hi()
			else:
				self.pin_dta_lo()
			time.sleep(self.hdelay)
			self.pin_clk_hi()
			time.sleep(self.hdelay)
			self.pin_clk_lo()
			b = b << 1
		time.sleep(self.hdelay)
		self.pin_dta_in()
		self.pin_cs_hi()
	
	#get byte
	def get_byte(self):
		r = 0
		self.pin_cs_lo()
		time.sleep(self.hdelay)
		#self.pin_dta_hi()
		self.pin_dta_in()
		for i in range(0,8):
			time.sleep(self.hdelay)
			self.pin_clk_lo()
			time.sleep(self.hdelay)
			r = r << 1
			if (self.pin_dta_get()):
				r = r | 0x01
			self.pin_clk_hi()
		time.sleep(self.hdelay)
		self.pin_dta_in()
		self.pin_cs_hi()
		self.pin_clk_lo()
		return r
	
	# wait for busy
	def busy_wait(self):
		while self.pin_get_bsy() == 0:
			time.sleep(0.000001)
	
	def send_cmd(self, cmd):
		self.pin_dc_lo()
		self.send_byte(cmd)
		self.pin_dc_hi()
	
	def send_data(self, data):
		self.pin_dc_hi()
		self.send_byte(data)
	
	def send_cmd2(self, cmd, pcnt, parm):
		self.pin_dc_lo()
		self.send_byte(cmd)
		self.pin_dc_hi()
		for i in range(0, pcnt):
			time.sleep(0.000001)
			self.send_byte(parm[i])
			# every 100 writed do a longer pause for OS to do things
			if ((i%100)==99):
				time.sleep(0.001)
	
	def send_cmd_read1(self, cmd):
		rr = 0;
		self.pin_dc_lo()
		time.sleep(0.000001)
		self.send_byte(cmd)
		self.pin_dc_hi()
		time.sleep(0.000001)
		rr = self.get_byte()
		time.sleep(0.000001)
		
		return rr
	
	# Write Black/White pixels data. display_data must have exactly 5808 bytes length.
	# Function return 0 on success, 1 if data is not equal 5808 bytes, 2 if data is malformed (wrong type/etc.)
	def write_bw(self, display_data):
		try:
			if (len(display_data) != 5808):
				return 1
			
			# B/W Data: CMD_DTM1[0x10]
			self.send_cmd2(0x10, 5808, display_data)
		except:
			return 2
		return 0
	
	# Write Red/White pixels data. display_data must have exactly 5808 bytes length.
	# Function return 0 on success, 1 if data is not equal 5808 bytes, 2 if data is malformed (wrong type/etc.)
	def write_rw(self, display_data):
		try:
			if (len(display_data) != 5808):
				return 1
			
			# B/W Data: CMD_DTM2[0x13]
			self.send_cmd2(0x13, 5808, display_data)
		except:
			return 2
		return 0
	
	# clear B/W to white (or to pattern[byte])
	def clear_bw(self, pattern=0x00):
		pattern = pattern & 0x00ff
		self.send_cmd(0x10)
		for i in range(0,5808):
			self.send_data(pattern)
	
	# clear R/W to white (or pattern[byte])
	def clear_rw(self, pattern=0x00):
		pattern = pattern & 0x00ff
		self.send_cmd(0x13)
		for i in range(0,5808):
			self.send_data(pattern)
	
	# send Data transmission end to the controller and start display refresh (wait for busy to be released!) (set noWait to 1 to skip busy wait)
	# retrun 0x80 if whole display buffer(s) were filled, or 0x00 if not.
	def update(self, noWait=0):
		r = self.send_cmd_read1(0x11)
		if (noWait==0):
			self.busy_wait()
		return r
	
	# init controller
	def init_ctrl(self):
		#LUT_VCOMDC_LEN=44
		lut_vcomdc = [
			0x00	,0x00,
			0x00	,0x1A	,0x1A	,0x00	,0x00	,0x01,
			0x00	,0x0A	,0x0A	,0x00	,0x00	,0x08,
			0x00	,0x0E	,0x01	,0x0E	,0x01	,0x10,
			0x00	,0x0A	,0x0A	,0x00	,0x00	,0x08,
			0x00	,0x04	,0x10	,0x00	,0x00	,0x05,
			0x00	,0x03	,0x0E	,0x00	,0x00	,0x0A,
			0x00	,0x23	,0x00	,0x00	,0x00	,0x01
		]
		#LUT_WW_LEN=42
		lut_ww = [
			0x90	,0x1A	,0x1A	,0x00	,0x00	,0x01,
			0x40	,0x0A	,0x0A	,0x00	,0x00	,0x08,
			0x84	,0x0E	,0x01	,0x0E	,0x01	,0x10,
			0x80	,0x0A	,0x0A	,0x00	,0x00	,0x08,
			0x00	,0x04	,0x10	,0x00	,0x00	,0x05,
			0x00	,0x03	,0x0E	,0x00	,0x00	,0x0A,
			0x00	,0x23	,0x00	,0x00	,0x00	,0x01
		]
		#LUT_BW_LEN=42
		lut_bw = [
			0xA0	,0x1A	,0x1A	,0x00	,0x00	,0x01,
			0x00	,0x0A	,0x0A	,0x00	,0x00	,0x08,
			0x84	,0x0E	,0x01	,0x0E	,0x01	,0x10,
			0x90	,0x0A	,0x0A	,0x00	,0x00	,0x08,
			0xB0	,0x04	,0x10	,0x00	,0x00	,0x05,
			0xB0	,0x03	,0x0E	,0x00	,0x00	,0x0A,
			0xC0	,0x23	,0x00	,0x00	,0x00	,0x01
		]
		#LUT_WB_LEN=42
		lut_wb = [
			0x90	,0x1A	,0x1A	,0x00	,0x00	,0x01,
			0x40	,0x0A	,0x0A	,0x00	,0x00	,0x08,
			0x84	,0x0E	,0x01	,0x0E	,0x01	,0x10,
			0x80	,0x0A	,0x0A	,0x00	,0x00	,0x08,
			0x00	,0x04	,0x10	,0x00	,0x00	,0x05,
			0x00	,0x03	,0x0E	,0x00	,0x00	,0x0A,
			0x00	,0x23	,0x00	,0x00	,0x00	,0x01
		]
		#LUT_BB_LEN=42
		lut_bb = [
			0x90	,0x1A	,0x1A	,0x00	,0x00	,0x01,
			0x20	,0x0A	,0x0A	,0x00	,0x00	,0x08,
			0x84	,0x0E	,0x01	,0x0E	,0x01	,0x10,
			0x10	,0x0A	,0x0A	,0x00	,0x00	,0x08,
			0x00	,0x04	,0x10	,0x00	,0x00	,0x05,
			0x00	,0x03	,0x0E	,0x00	,0x00	,0x0A,
			0x00	,0x23	,0x00	,0x00	,0x00	,0x01
		]
		# power settings
		# REG_POWER[0x01] 
		#     P0=VDS_INT[0x02] | VDG_INT[0x01] 
		#     P1=VCOM_with_VCOMDC[0x00] | VGL_16V[0x00] 
		#     P2=VDH_11V[0x2b]
		#     P3=VDL_11V[0x2b]
		#     P4=VDHR_4.2V[0x09]
		self.send_cmd2(0x01, 5, [0x03, 0x00, 0x2b, 0x2b, 0x09])
		
		# setup booster
		# CMD_BTST[0x06]
		#     P0=BTPHA_10ms[0x00] | BTPHA_S1[0x00] | BTPHA_OFF6.58us[0x07]
		#     P1=BTPHB_10ms[0x00] | BTPHB_S1[0x00] | BTPHB_OFF6.58us[0x07]
		#     P2=BTPHC_S3[0x10] | BTPHC_OFF6.58us[0x07]
		self.send_cmd2(0x06, 3, [0x07, 0x07, 0x17])
		time.sleep(0.005)
		
		# power optimization - no reference in datasheet for command 0xF8!
		self.send_cmd2(0xf8, 2, [0x60, 0xa5])
		self.send_cmd2(0xf8, 2, [0x89, 0xa5])
		self.send_cmd2(0xf8, 2, [0x90, 0x00])
		self.send_cmd2(0xf8, 2, [0x93, 0x2a])
		self.send_cmd2(0xf8, 2, [0x73, 0x41])
		
		# power ON
		# CMD_PON[0x04]
		self.send_cmd(0x04)
		time.sleep(0.00001)
		# display will hold down busy for power-on sequence
		self.busy_wait()
		
		# panel settings
		# CMD_PSR[0x00]
		#       P0=RES_296x160[0x80] | LUT_REG[0x20] | BWR_ON[0x00] | GateScan_UP[0x08] | SourceShift_LEFT[0x00] | BOOSTER_ON[0x02] | NO_RESET[0x01]
		self.send_cmd2(0x00, 1, [0xab])
		
		# pll control
		# CMD_PLL[0x30]
		#      P0=DIV_01[0x20] | PLL_F[0x1a]
		self.send_cmd2(0x30, 1, [0x3a])
		
		# resolution settings
		# CMD_TRES[0x61]
		#      P0=H_RES(bit8)
		#      P1=H_RES(bit7..0) (bit0 alwas 0!)
		#      P2=V_RES(bit8)
		#      P3=V_RES(bit7..0)
		self.send_cmd2(0x61, 4, [ ((self.HEIGHT>>8)&0x01) , (self.HEIGHT&0x00ff), ((self.WIDTH>>8)&0x0001), (self.WIDTH & 0x00ff) ])
		
		# VCM_DC setting
		# CMD_VDCS[0x82]
		#      P0=VDCS_-1.0V[0x12]
		self.send_cmd2(0x82, 1, [ 0x12 ])
		
		# VCOM and data interval
		# CMD_CDI[0x50]
		#      P0=CDI_VBD_10[0x80] | CDI_DDX_10[0x00] | CDI_10hSync-s[0x07]
		self.send_cmd2(0x50, 1, [ 0x87 ])
		
		# *** load LUT tables ***
		# LUTC[0x20]
		self.send_cmd2(0x20, 44, lut_vcomdc)
		# LUTWW[0x21]
		self.send_cmd2(0x21, 42, lut_ww)
		# LUTBW[0x22]
		self.send_cmd2(0x22, 42, lut_bw)
		# LUTWB[x023]
		self.send_cmd2(0x23, 42, lut_wb)
		# LUTBB[0x24]
		self.send_cmd2(0x24, 42, lut_bb)
		
		# end init controller
		
	def shutdown(self):
		self.busy_wait()
		# CMD_CDI[0x50] , P0=CDI_VBD_11[0x80] | DDX_10[0x00] | CDI_10hSyncs[0x07]
		self.send_cmd2(0x50, 1, [0x87]);
		# power off: CMD_POF[0x02]
		self.send_cmd(0x02)
		
	def deep_sleep(self):
		self.busy_wait()
		# CMD_DSLP[0x07] , P0=CHECK_CODE[0xa5]
		self.send_cmd2(0x07, 1, [0xa5]);
		

