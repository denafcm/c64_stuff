#!/usr/local/bin/python
# All programming and design by Deadman / SID Lovin' Criminals
# Written during December 2007 - January 2008. It's free to use by all the
# people in the C64 scene, others probably don't care too much :0

# First complete successful test took place on 22nd-23rd January 2008.
# It looks good so now we can remove some "hardcode" and extra debugging

# 05/2009 Fixed a I/O bug on Windows; must open binary files with 'rb'
# 07/2013 Load address > $7FFF bug fixed; unpack h => H
# 09/2015 Option to save linked but unpacked data to a file. Exceptions fix

import sys
import struct
import getopt
import array
import string

import lejon
from lejon import packer
from lejon import depacker

bot_addr = 0xffff
top_addr = 0x0000 
mem = array.array("B", "\0" * 65536)
#mem = array.array("B", (0, ) * 65536)


def loadmem(filename, loadaddr):

	f = open(filename, 'rb')

	(la, ) = struct.unpack("<H", f.read(2))

	data = f.read()

	o = 0

	if loadaddr:
		la = loadaddr

	for b in data:
		mem[la+o] = ord(b)
		o = o + 1

	return (la, la + o)


# ------------------ #
# -- MAIN PROGRAM -- #
# ------------------ #

# ---- GETOPTS ---- #

longopts = [ "romstatus=", "irqstatus=", "sysaddr=", "output=",
             "linked=" ]

opt_romstat = 0x37
opt_irqstat = 0x58
opt_sysaddr = 0xe386
opt_output = 'a.out'
opt_link = False

try:
	opts, args = getopt.getopt(sys.argv[1:], "r:i:j:s:o:O:", longopts)
	for o,v in opts:
		if o in ('-r', '--romstat', '--romstatus'):
			opt_romstat = int(v, 16)
		if o in ('-i', '--irqstat', '--irqstatus'):
			if v in ('sei', 'Sei', 'S', 'SEI', '78'):
				opt_irqstat = 0x78
			if v in ('cli', 'Cli', 'C', 'CLI', '58'):
				opt_irqstat = 0x58
		if o in ('-s', '--sysaddr', '--jmpaddr'):
			opt_sysaddr = int(v, 16)
		if o in ('-o', '--output'):
			opt_output = v
		if o in ('-O', '--linked'):
			opt_link = v

except getopt.GetoptError, error_message:
	print "Error: ", error_message
	print "Usage: %s [-options] [-o OUTFILE] FILE,xxxx [FILE,xxxx] ..." % \
		sys.argv[0]
	print "   -r, --romstat=BYTE       ROM status byte ($01 register)"
	print "   -i, --irqstat=CLI/SEI    IRQ flag, SEI or CLI"
	print "   -s, --sysaddr=ADDR       Program JMP start address"
	print "   -o, --output=FILE        Save packed 'n linked data to FILE"
	print "   -O, --linked=FILE        Save only linked data to FILE"
	sys.exit(1)

print "LEJON PACKER/LINKER, V1.2 BY DEADMAN"
print "COPYRIGHT 1995,2009,2015 SID LOVIN' CRIMINALS"
print "PACKER VERSION %s" % packer.version
print "DEPACKER VERS. %s" % depacker.version

if args == []: 
	raise SystemExit("No input files")

print ""

print "ROM status  : ", hex(opt_romstat)
print "IRQ status  : ", hex(opt_irqstat)
print "SYS address : ", hex(opt_sysaddr)
print "Output file : ", opt_output

print ""
print "Loading..."
 
# ---- FILE LOADING ---- #

for p in range(0, len(args)):
	fileparams = string.split(args[p], ",")

	filename = fileparams[0]
	try:
		force_la = int(fileparams[1], 16)
	except ValueError:
		force_la = 0
	except IndexError:
		force_la = 0

	(low, high) = loadmem(filename, force_la)

	if low < bot_addr:
		bot_addr = low
	if high > top_addr:
		top_addr = high

	print "%-30s loaded at $%04X-$%04X" % (filename, low, high)

if bot_addr < 0x0200:
	raise ValueError("Low memory address $%04X too low" % bot_addr)

# ---- CRUNCHING ---- #

print ""
print "Packing memory $%04X-$%04X (%d blocks)..." % (bot_addr, top_addr, (top_addr-bot_addr)>>8)

controlbytes = packer.controlbytes(mem[bot_addr:top_addr])
print "Control bytes $%02X and $%02X" % (controlbytes[0], controlbytes[1])

packdata = packer.crunch(mem[bot_addr:top_addr], controlbytes)
print "Packed length $%04X (saved $%04X), Compression ratio %f" % \
	(len(packdata), (top_addr - bot_addr) - len(packdata), len(packdata) * 1.000/(top_addr - bot_addr))

# ---- SAVING ---- #

depack = depacker.makedepacker((
		('CNTRLBY1', controlbytes[0]),
		('CNTRLBY2', controlbytes[1]),
		('LOADADDR', bot_addr),
		('ROMSTAT',  opt_romstat),
		('CLI/SEI',  opt_irqstat),
		('SYSADDR',  opt_sysaddr)), len(packdata))

print "Depacker length $%04X" % len(depack)

print ""

print "Saving %s ..." % opt_output

w = open(opt_output, 'wb')
try:
	w.write(struct.pack("<h", 0x0801))
	w.write(depack)
	w.write(packdata)
except IOError, ioerror:
	raise IOError("Saving I/O error", ioerror)

w.close()

if opt_link:
	print "Saving unpacked'n'linked data to %s ..." % opt_link
	w = open(opt_link, 'wb')
	try:
		w.write(struct.pack("<h", bot_addr))
		w.write(mem[bot_addr:top_addr])
	except IOError, ioerror:
		raise IOError("Saving I/O error"), ioerror

greetz = (
	'E.C.A.',
	'MATCHAM/NETWORK',
	'ONEWAY',
	'1001 CREW',
	'GALLEON/SPHINX',
	'DINO/FAIRLIGHT',
	'TCD/TRIANGLE'
) 
import random
print "Goodbye, hope you enjoyed your time! Random greeting to %s!" % \
	(random.choice(greetz))


