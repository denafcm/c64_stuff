; LEJON PACKER UNPACKER ROUTINE BY DEADMAN 1995, 2009

; Let DASM calculate offsets into the decruncher code
; where by the packer to fill in the proper new values

	.echo "PAGECNT.B  ", (cp1 - 1) - $0801
	.echo "LASTPAGE.W ", (cp1 + 1) - $0801
	.echo "LOWMEM.W   ",  decrunch - $0801
	.echo "--"
	.echo "LADDR.W    ", ((stal   + 1) - $FD) + reloc
	.echo "CB1.B      ", ((main   + 3) - $FD) + reloc
	.echo "CB1.B      ", ((false1 + 1) - $FD) + reloc
	.echo "CB2.B      ", ((main   + 7) - $FD) + reloc
	.echo "CB2.B      ", ((false2 + 1) - $FD) + reloc
	.echo "ROMSTAT.B  ", ((exx + 1) - $FD) + reloc
	.echo "IRQSTAT.B  ", ((exx + 4) - $FD) + reloc
	.echo "SYSENT.W   ", ((exx + 6) - $FD) + reloc
	.echo "--"
	
; Control bytes
CB1 = $b8
CB2 = $b2
; Page count for initial copy to highmem, make it: ceil(PackedLength>>8)
PAGECNT = ((dataend-databeg)/256)+1
; Lowmem after initial copy, its just $10000-PackedLength.
LOWMEM = $10000-(dataend-databeg)
; Destination address for the unpacked data.
LADDR = $0801
; Decruncher exit and program start conditions.
ROMSTAT = $37
IRQSTAT = $58	; CLI
SYSENT = $0817


	processor 6502

	.org $0801

	ldy #$00
	sei
	inc $01
	ldx #PAGECNT
cp1	lda dataend-256,y
cp2	sta $ff00,y
	iny
	bne cp1
	dec cp1+2
	dec cp2+2
	dex
	bne cp1
	ldx #(databeg-decrunch)
nada	lda decrunch-1,x
	.byte $9d
	.word $fb-1
	dex
	bne nada
	jmp entry

decrunch
	.word LOWMEM
reloc = * - $0801
	.rorg $00fd

stal	sta LADDR
	inc $fe
	bne *+4
	inc $ff
	dex
	bne stal
	;beq main

entry	ldy #$00
main	lda ($fb),y
	cmp #CB1
	beq contr1
	cmp #CB2
	beq contr2

	iny
	ldx #$01

; Entries: Y=source add. X=run length. A=value to run 
isrc	inc $fb
	bne *+4
	inc $fc
	beq exx
	dey
	bne isrc

	;here was stal
	beq stal


exx	lda #ROMSTAT
	sta $01
	.byte IRQSTAT
	jmp SYSENT

contr1	iny
	lda ($fb),y
	cmp #$10
	beq false1
	pha
;;	and #$f0	; optimized out 10/2014
	lsr
	lsr
	lsr
	lsr
	bne *+4
	lda #$10
	tax
	pla
	and #$0f
_cn1	ldy #$02
	bne isrc
false1	lda #CB1
	ldx #$01
	ldy #$02
	bne isrc

contr2	iny
	lda ($fb),y
	cmp #$01
	beq false2
	tax
	iny
	lda ($fb),y
_cn2	ldy #$03
	bne isrc
false2	lda #CB2
	ldx #$01
	ldy #$02
	bne isrc

	.rend

databeg
	.dc "PUT SOME DATA HERE"
dataend

