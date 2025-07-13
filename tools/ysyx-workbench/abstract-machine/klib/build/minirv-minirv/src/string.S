#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
	.file	"string.c"
	.option nopic
	.text
	.section	.ssbl,"ax",@progbits
	.align	2
	.globl	memcpy
	.hidden	memcpy
	.type	memcpy, @function
memcpy:
	beq	a0,zero,.L2
	li	a5,0
	bne	a1,zero,.L3
	li	a0,0
.L2:
	ret
.L4:
	add	a4,a1,a5
	lbu	a3,0(a4)
	add	a4,a0,a5
	addi	a5,a5,1
	sb	a3,0(a4)
.L3:
	bne	a2,a5,.L4
	ret
	.size	memcpy, .-memcpy
	.section	.text.strlen,"ax",@progbits
	.align	2
	.globl	strlen
	.hidden	strlen
	.type	strlen, @function
strlen:
	mv	a5,a0
	li	a0,0
.L10:
	add	a4,a5,a0
	lbu	a4,0(a4)
	bne	a4,zero,.L11
	ret
.L11:
	addi	a0,a0,1
	j	.L10
	.size	strlen, .-strlen
	.section	.text.strcpy,"ax",@progbits
	.align	2
	.globl	strcpy
	.hidden	strcpy
	.type	strcpy, @function
strcpy:
	beq	a0,zero,.L13
	beq	a1,zero,.L15
	mv	a5,a0
.L14:
	lbu	a4,0(a1)
	addi	a1,a1,1
	addi	a5,a5,1
	sb	a4,-1(a5)
	bne	a4,zero,.L14
	ret
.L15:
	li	a0,0
.L13:
	ret
	.size	strcpy, .-strcpy
	.section	.rodata.strncpy.str1.4,"aMS",@progbits,1
	.align	2
.LC0:
	.string	"AM Panic: "
	.align	2
.LC1:
	.string	"Not implemented"
	.align	2
.LC2:
	.string	" @ /opt/rtl2gds/tools/ysyx-workbench/abstract-machine/klib/src/string.c:28  \n"
	.section	.text.strncpy,"ax",@progbits
	.align	2
	.globl	strncpy
	.hidden	strncpy
	.type	strncpy, @function
strncpy:
	addi	sp,sp,-12
	sw	s0,4(sp)
	sw	ra,8(sp)
	lla	s0,.LC0
.L21:
	lbu	a0,0(s0)
	bne	a0,zero,.L22
	lla	s0,.LC1
.L23:
	lbu	a0,0(s0)
	bne	a0,zero,.L24
	lla	s0,.LC2
.L25:
	lbu	a0,0(s0)
	bne	a0,zero,.L26
	li	a0,1
	call	halt
.L22:
	call	putch
	addi	s0,s0,1
	j	.L21
.L24:
	call	putch
	addi	s0,s0,1
	j	.L23
.L26:
	call	putch
	addi	s0,s0,1
	j	.L25
	.size	strncpy, .-strncpy
	.section	.text.strcat,"ax",@progbits
	.align	2
	.globl	strcat
	.hidden	strcat
	.type	strcat, @function
strcat:
	mv	a5,a0
.L29:
	lbu	a3,0(a5)
	mv	a4,a5
	addi	a5,a5,1
	bne	a3,zero,.L29
.L30:
	lbu	a5,0(a1)
	addi	a1,a1,1
	addi	a4,a4,1
	sb	a5,-1(a4)
	bne	a5,zero,.L30
	ret
	.size	strcat, .-strcat
	.section	.text.strcmp,"ax",@progbits
	.align	2
	.globl	strcmp
	.hidden	strcmp
	.type	strcmp, @function
strcmp:
.L34:
	lbu	a4,0(a0)
	lbu	a5,0(a1)
	beq	a4,zero,.L38
	bne	a5,zero,.L39
.L40:
	li	a0,1
	ret
.L39:
	bne	a4,a5,.L35
	addi	a0,a0,1
	addi	a1,a1,1
	j	.L34
.L35:
	bgtu	a4,a5,.L40
	bgeu	a4,a5,.L34
	li	a0,-1
	ret
.L38:
	snez	a0,a5
	neg	a0,a0
	ret
	.size	strcmp, .-strcmp
	.section	.text.strncmp,"ax",@progbits
	.align	2
	.globl	strncmp
	.hidden	strncmp
	.type	strncmp, @function
strncmp:
	li	a3,0
.L43:
	lbu	a4,0(a0)
	lbu	a5,0(a1)
	beq	a4,zero,.L47
	beq	a5,zero,.L48
	bne	a3,a2,.L49
.L48:
	seqz	a0,a5
	ret
.L49:
	bne	a4,a5,.L44
	addi	a0,a0,1
	addi	a1,a1,1
.L45:
	addi	a3,a3,1
	j	.L43
.L44:
	bgtu	a4,a5,.L50
	bgeu	a4,a5,.L45
	li	a0,-1
	ret
.L50:
	li	a0,1
	ret
.L47:
	snez	a5,a5
	neg	a0,a5
	ret
	.size	strncmp, .-strncmp
	.section	.text.memset,"ax",@progbits
	.align	2
	.globl	memset
	.hidden	memset
	.type	memset, @function
memset:
	beq	a0,zero,.L56
	add	a2,a0,a2
	mv	a5,a0
.L57:
	bne	a5,a2,.L58
.L56:
	ret
.L58:
	sb	a1,0(a5)
	addi	a5,a5,1
	j	.L57
	.size	memset, .-memset
	.section	.rodata.memmove.str1.4,"aMS",@progbits,1
	.align	2
.LC3:
	.string	" @ /opt/rtl2gds/tools/ysyx-workbench/abstract-machine/klib/src/string.c:95  \n"
	.section	.text.memmove,"ax",@progbits
	.align	2
	.globl	memmove
	.hidden	memmove
	.type	memmove, @function
memmove:
	addi	sp,sp,-12
	sw	s0,4(sp)
	sw	ra,8(sp)
	lla	s0,.LC0
.L63:
	lbu	a0,0(s0)
	bne	a0,zero,.L64
	lla	s0,.LC1
.L65:
	lbu	a0,0(s0)
	bne	a0,zero,.L66
	lla	s0,.LC3
.L67:
	lbu	a0,0(s0)
	bne	a0,zero,.L68
	li	a0,1
	call	halt
.L64:
	call	putch
	addi	s0,s0,1
	j	.L63
.L66:
	call	putch
	addi	s0,s0,1
	j	.L65
.L68:
	call	putch
	addi	s0,s0,1
	j	.L67
	.size	memmove, .-memmove
	.section	.rodata.memcmp.str1.4,"aMS",@progbits,1
	.align	2
.LC4:
	.string	"n = %ld\n"
	.section	.text.memcmp,"ax",@progbits
	.align	2
	.globl	memcmp
	.hidden	memcmp
	.type	memcmp, @function
memcmp:
	addi	sp,sp,-12
	sw	s0,4(sp)
	sw	s1,0(sp)
	mv	s0,a1
	sw	ra,8(sp)
	mv	s1,a0
	mv	a1,a2
.L71:
	lbu	a5,0(s1)
	beq	a5,zero,.L76
	lbu	a4,0(s0)
	beq	a4,zero,.L76
	bne	a1,zero,.L77
	li	a0,0
	j	.L70
.L77:
	addi	a1,a1,-1
	bne	a5,a4,.L72
	addi	s1,s1,1
	addi	s0,s0,1
	j	.L71
.L72:
	bleu	a5,a4,.L74
.L78:
	li	a0,1
.L70:
	lw	ra,8(sp)
	lw	s0,4(sp)
	lw	s1,0(sp)
	addi	sp,sp,12
	jr	ra
.L74:
	bgeu	a5,a4,.L71
	li	a0,-1
	j	.L70
.L76:
	li	a0,0
	beq	a1,zero,.L70
	lla	a0,.LC4
	call	printf
	lbu	a5,0(s1)
	bne	a5,zero,.L78
	lbu	a0,0(s0)
	snez	a0,a0
	neg	a0,a0
	j	.L70
	.size	memcmp, .-memcmp
	.ident	"GCC: (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0"
	.section	.note.GNU-stack,"",@progbits
