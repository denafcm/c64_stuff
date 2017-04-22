#!/usr/local/bin/python
# All programming and design by Deadman / SID Lovin' Criminals

import array

version = '1.1 [25-May-2009]'

def _outputrle(byte, count, cbytes):
	if count == 1:
		if byte not in cbytes:
			#print "out %02x" % byte
			return (byte,)
		else:
			if byte == cbytes[0]:
				#print "out %02x %02x [cb1 occured]" % (cbytes[0], 0x10)
				return (cbytes[0], 0x10)
			if byte == cbytes[1]:
				#print "out %02x %02x [cb2 occured]" % (cbytes[1], 0x01)
				return (cbytes[1], 0x01)
			raise("gotcha! unknown controlbyte ?!")

	if count <= 16 and byte < 16:
		#print "out %02x %02x [shortcode]" % (cbytes[0], (count&15) << 4 | byte&15)
		return (cbytes[0], (count&15) << 4 | byte&15)

	# This part is somewhat confusing, but it's how the original Lejonpacker worked.
	# If it's a control-byte, we just do the wedge trick two times!
	# I know it's bad, but it shouldn't really add many extra bytes to the output.

	if count == 2:
		if byte not in cbytes:
			#print "out %02x %02x [two bytes]" % (byte, byte)
			return (byte, byte)
		else:
			if byte == cbytes[0]:
				return (cbytes[0], 0x10, cbytes[0], 0x10)
			if byte == cbytes[1]:
				return (cbytes[1], 0x01, cbytes[1], 0x01)
			raise("gotcha! what controlbyte ?!")

	#print "out %02x %02x %02x" % (cbytes[1], count&255, byte)
	return (cbytes[1], count&255, byte)

	raise("gotcha! what's up ?!")
		

def crunch(data, cbytes):
	out = array.array("B")
	state = 0
	inskip = 1
	count = 0
	for i in range(0, len(data)):
		if state == 1:
			if (data[i] == byt) and (count < 256):
				count = count + 1
			else:
				state = 0
				#print "%04X: end of run %02X, count %d" % (i, byt, count)
				chunk = _outputrle(byt, count, cbytes)
				for outb in chunk:
					out.append(outb)

		if state == 0:
			byt = data[i]
			#print "%04X: new byte %02X" % (i, byt)
			count = 1
			state = 1


	#print "%04X: last end of run %02X, count %d" % (i, byt, count)

	# Update 25.05.2009: Due to the optimized routine in the decruncher,
	# we have to add an additional "trailer" byte to the output.
	# This byte cannot be a control-byte, though, because that would
	# cause the decruncher to read 1 or 2 more bytes!!
	
	chunk = _outputrle(byt, count, cbytes)
	for outb in chunk:
		out.append(outb)

	for i in (byt, 0x00, 0x55, 0xaa, 0xff):
		if i not in cbytes:
			print "Appending trailer byte $%02X" % (i)
			out.append(i)
			break

	
	return out

def controlbytes(data):

	h = range(0, 256)

	for b in data:
		h[b] = h[b] + 0x0100

	h.sort()
	cb1 = h[0]
	cb2 = h[1]

#	cb1 = min(h)
#
#	def smallestout(x):
#		if x != min(h):
#			return True
#	h = filter(smallestout, h)
#	cb2 = min(h)

	return (cb1&255, cb2&255)

if __name__ == '__main__':
	import sys

	#f = open("/pcc/TEMP/c64/flame.o", "rb")
	f = open("strangeloop.mem", "rb")
	f.seek(2)
	mem = array.array('B')
	mem.fromstring(f.read())

	(cb1, cb2) = controlbytes(mem)

	print "Controlbytes $%02X and $%02X" % (cb1, cb2)

	w = open("out", "wb")
	w.write(crunch(mem, (cb1, cb2)))
	w.close()

