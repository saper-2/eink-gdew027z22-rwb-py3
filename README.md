# Driver for E-INK GDEW027Z22 display
GDEW027Z22 is a E-Ink display from "Dalian Good Display Co., Ltd.". The display have 3 colors (compared to most):

* Black
* White
* and 3rd: **Red**

Display resolution is 176x264px (in portrait), and the pixels are layout in honeycomb (different than in LCDs) - this have impact on level of details that display can show - usually 1px line is almost invisible.

Display is using controller with symbol: EK79652 (this seems like a Good-Display own controller).

Controller have built-in DC/DC converter for generating all required voltages for panel. From hardware DC/DC need inductor, few Schottky diodes and bunch of 1-10uF MLCC (ceramic) capacitors rated for 25-35V) - circuit from datasheet *(To get one you have to get in touch with Good-Display)*.

It is possible to add LM75 as temperature sensor for compensating power & panel driver circuits operation.

Controller have 2 RAM block, one per color: black (DTM1) and red (DTM2). 
Each block have length of 5808 bytes ( 176px*264px/8bit=5808 ).

Note: The Red color have priority over the black.

## Some parameters in table

Parameter|Value
-|-
Supply|2,3-3,6V
Current|didn't measured.
Interface|4-wire SPI (bi-direction 8bit DATA)
SPI Mode|Mode 0
SPI clock f_max|10MHz for write\6MHz for read
Panel dimension|70,5 x 45,8 x 1 mm
Active area|57,3 x 38,2 mm
Diagonal|2,7inch
Resolution|274 x 176 px / 117dpi
Controller|EK79652
Connector|FPC 0.5mm 24pin

# Wiring

Simple as stick :grin:

Raspberry Pi|Display
------------|-------
BCM.GPIO18 |/Reset
BCM.GPIO23|Busy
BCM.GPIO25|D/C
BCM.SPI0.CS0|/CS
BCM.SPI0.MOSI|DATA
BCM.SPI0.CLK|CLK
BCM.SPI0.MAX_CLOCK|8MHz

# Driver
There are two files for driver, old (with suffix ```_SOFT```) and new :smile: . New driver use hardware SPI to accelerate data loading to display, while old use bitbanging and can hang up the Pi :evil: , also image loading & processing is only implemented in newer version.

For usage of driver see the code of ```test.py``` and ```eink-img.py``` .

This driver was based on my driver for Atmel AVRs (you can find on Youtube movies with demo of it too).

# Links
* [Video with demo](https://youtu.be/Kffm1Wp5UVM)

# Credits
For me :smile:

# License
Beerware v42 - google for it.

# EOF
```exit(0);```