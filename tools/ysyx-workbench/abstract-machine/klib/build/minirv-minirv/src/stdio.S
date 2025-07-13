#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
	.file	"stdio.c"
	.option nopic
	.text
	.globl	__modsi3
	.globl	__divsi3
	.section	.text.itoa.isra.0,"ax",@progbits
	.align	2
	.type	itoa.isra.0, @function
itoa.isra.0:
	addi	sp,sp,-28
	sw	s1,16(sp)
	sw	ra,24(sp)
	sw	s0,20(sp)
	mv	s1,a1
	bne	a0,zero,.L2
	li	a5,48
	sb	a5,0(a1)
	sb	zero,1(a1)
.L1:
	lw	ra,24(sp)
	lw	s0,20(sp)
	lw	s1,16(sp)
	addi	sp,sp,28
	jr	ra
.L2:
	sw	zero,0(sp)
	mv	a5,a0
	mv	a1,a2
	bge	a0,zero,.L4
	li	a4,10
	bne	a2,a4,.L4
	li	a4,1
	neg	a5,a0
	sw	a4,0(sp)
.L4:
	li	s0,0
	j	.L7
.L14:
	mv	s0,a4
.L7:
	mv	a0,a5
	sw	a1,8(sp)
	sw	a5,4(sp)
	call	__modsi3
	li	a4,9
	lw	a5,4(sp)
	lw	a1,8(sp)
	andi	a3,a0,0xff
	ble	a0,a4,.L5
	addi	a3,a3,87
.L20:
	addi	a4,s0,1
	add	a2,s1,a4
	andi	a3,a3,0xff
	sb	a3,-1(a2)
	mv	a0,a5
	sw	a4,12(sp)
	sw	a2,8(sp)
	sw	a1,4(sp)
	call	__divsi3
	lw	a1,4(sp)
	lw	a2,8(sp)
	lw	a4,12(sp)
	mv	a5,a0
	bne	a0,zero,.L14
	lw	a3,0(sp)
	beq	a3,zero,.L9
	li	a3,45
	addi	a4,s0,2
	sb	a3,0(a2)
.L9:
	add	a3,s1,a4
	sb	zero,0(a3)
.L21:
	addi	a4,a4,-1
	bge	a5,a4,.L1
	add	a3,s1,a4
	add	a2,s1,a5
	lbu	a0,0(a3)
	lbu	a1,0(a2)
	addi	a5,a5,1
	sb	a0,0(a2)
	sb	a1,0(a3)
	j	.L21
.L5:
	addi	a3,a3,48
	j	.L20
	.size	itoa.isra.0, .-itoa.isra.0
	.section	.text.vsnprintf,"ax",@progbits
	.align	2
	.globl	vsnprintf
	.hidden	vsnprintf
	.type	vsnprintf, @function
vsnprintf:
	addi	sp,sp,-60
	sw	s0,52(sp)
	sw	s1,48(sp)
	sw	ra,56(sp)
	mv	s1,a0
	mv	a4,a1
	mv	t1,a2
	mv	s0,a0
.L23:
	lbu	a5,0(t1)
	sub	a0,s0,s1
	beq	a5,zero,.L55
	bltu	a0,a4,.L56
.L57:
	add	s1,s1,a4
	sb	zero,-1(s1)
	j	.L22
.L56:
	li	a2,37
	addi	t1,t1,1
	bne	a5,a2,.L80
	li	a5,0
	li	a0,9
	j	.L24
.L26:
	slli	t1,a5,2
	add	a5,t1,a5
	slli	a5,a5,1
	add	a5,a2,a5
	mv	t1,a1
.L24:
	lbu	t0,0(t1)
	addi	a1,t1,1
	addi	a2,t0,-48
	andi	t2,a2,0xff
	bleu	t2,a0,.L26
	li	a2,46
	bne	t0,a2,.L27
	li	a0,9
.L28:
	lbu	a2,0(a1)
	mv	t1,a1
	addi	a1,a1,1
	addi	a2,a2,-48
	andi	a2,a2,0xff
	bleu	a2,a0,.L28
.L27:
	lbu	a2,0(t1)
	li	a1,105
	beq	a2,a1,.L29
	bgtu	a2,a1,.L30
	li	a1,99
	beq	a2,a1,.L31
	li	a1,100
	beq	a2,a1,.L29
	li	a5,37
	beq	a2,a5,.L32
.L33:
	li	a2,37
	addi	a5,s0,1
	sb	a2,0(s0)
	sub	a2,a5,s1
	mv	t0,a3
	bgeu	a2,a4,.L37
	lbu	a3,0(t1)
	addi	a5,s0,2
	sb	a3,1(s0)
	j	.L37
.L30:
	li	a1,117
	beq	a2,a1,.L34
	li	a1,120
	beq	a2,a1,.L35
	li	a5,115
	bne	a2,a5,.L33
	addi	t0,a3,4
	lw	a3,0(a3)
	mv	a5,s0
.L36:
	lbu	a2,0(a3)
	sub	a1,a5,s1
	beq	a2,zero,.L37
	bgtu	a4,a1,.L38
.L37:
	addi	t1,t1,1
	mv	a3,t0
	mv	s0,a5
	j	.L23
.L38:
	addi	a5,a5,1
	addi	a3,a3,1
	sb	a2,-1(a5)
	j	.L36
.L29:
	lw	a0,0(a3)
	addi	t0,a3,4
	li	a2,10
	addi	a1,sp,16
	sw	t1,12(sp)
	sw	a4,8(sp)
	sw	a5,4(sp)
	sw	t0,0(sp)
	call	itoa.isra.0
	addi	a0,sp,16
	call	strlen
	lw	a5,4(sp)
	lw	t0,0(sp)
	lw	a4,8(sp)
	lw	t1,12(sp)
	li	a3,0
	ble	a5,a0,.L39
	sub	a3,a5,a0
.L39:
	mv	a5,s0
	add	a3,s0,a3
	li	a1,48
.L40:
	sub	a0,a3,a5
	sub	a2,a5,s1
	ble	a0,zero,.L61
	bltu	a2,a4,.L42
.L61:
	addi	a3,sp,16
	j	.L81
.L42:
	addi	a5,a5,1
	sb	a1,-1(a5)
	j	.L40
.L43:
	addi	a5,a5,1
	addi	a3,a3,1
	sb	a2,-1(a5)
.L81:
	lbu	a2,0(a3)
	sub	a1,a5,s1
	beq	a2,zero,.L37
	bgtu	a4,a1,.L43
	j	.L37
.L31:
	addi	t0,a3,4
	lw	a3,0(a3)
	addi	a5,s0,1
	sb	a3,0(s0)
	j	.L37
.L35:
	lw	a0,0(a3)
	addi	t0,a3,4
	li	a2,16
	addi	a1,sp,16
	sw	t1,12(sp)
	sw	a4,8(sp)
	sw	a5,4(sp)
	sw	t0,0(sp)
	call	itoa.isra.0
	addi	a0,sp,16
	call	strlen
	lw	a5,4(sp)
	lw	t0,0(sp)
	lw	a4,8(sp)
	lw	t1,12(sp)
	li	a3,0
	ble	a5,a0,.L44
	sub	a3,a5,a0
.L44:
	mv	a5,s0
	add	a3,s0,a3
	li	a1,48
.L45:
	sub	a0,a3,a5
	sub	a2,a5,s1
	ble	a0,zero,.L63
	bgtu	a4,a2,.L47
.L63:
	addi	a3,sp,16
	j	.L82
.L47:
	addi	a5,a5,1
	sb	a1,-1(a5)
	j	.L45
.L48:
	addi	a5,a5,1
	addi	a3,a3,1
	sb	a2,-1(a5)
.L82:
	lbu	a2,0(a3)
	sub	a1,a5,s1
	beq	a2,zero,.L37
	bgtu	a4,a1,.L48
	j	.L37
.L34:
	lw	a0,0(a3)
	addi	t0,a3,4
	li	a2,10
	addi	a1,sp,16
	sw	t1,12(sp)
	sw	a4,8(sp)
	sw	a5,4(sp)
	sw	t0,0(sp)
	call	itoa.isra.0
	addi	a0,sp,16
	call	strlen
	lw	a5,4(sp)
	lw	t0,0(sp)
	lw	a4,8(sp)
	lw	t1,12(sp)
	li	a3,0
	ble	a5,a0,.L49
	sub	a3,a5,a0
.L49:
	mv	a5,s0
	add	a3,s0,a3
	li	a1,48
.L50:
	sub	a0,a3,a5
	sub	a2,a5,s1
	ble	a0,zero,.L65
	bgtu	a4,a2,.L52
.L65:
	addi	a3,sp,16
	j	.L83
.L52:
	addi	a5,a5,1
	sb	a1,-1(a5)
	j	.L50
.L53:
	addi	a5,a5,1
	addi	a3,a3,1
	sb	a2,-1(a5)
.L83:
	lbu	a2,0(a3)
	sub	a1,a5,s1
	beq	a2,zero,.L37
	bgtu	a4,a1,.L53
	j	.L37
.L32:
	addi	a5,s0,1
	sb	a2,0(s0)
	mv	t0,a3
	j	.L37
.L80:
	sb	a5,0(s0)
	addi	s0,s0,1
	j	.L23
.L55:
	bgeu	a0,a4,.L57
	sb	zero,0(s0)
.L22:
	lw	ra,56(sp)
	lw	s0,52(sp)
	lw	s1,48(sp)
	addi	sp,sp,60
	jr	ra
	.size	vsnprintf, .-vsnprintf
	.section	.text.snprintf,"ax",@progbits
	.align	2
	.globl	snprintf
	.hidden	snprintf
	.type	snprintf, @function
snprintf:
	addi	sp,sp,-28
	sw	a3,16(sp)
	addi	a3,sp,16
	sw	ra,12(sp)
	sw	a4,20(sp)
	sw	a5,24(sp)
	sw	a3,0(sp)
	call	vsnprintf
	lw	ra,12(sp)
	addi	sp,sp,28
	jr	ra
	.size	snprintf, .-snprintf
	.section	.text.sprintf,"ax",@progbits
	.align	2
	.globl	sprintf
	.hidden	sprintf
	.type	sprintf, @function
sprintf:
	addi	sp,sp,-32
	sw	a2,16(sp)
	sw	a3,20(sp)
	mv	a2,a1
	addi	a3,sp,16
	li	a1,-1
	sw	ra,12(sp)
	sw	a4,24(sp)
	sw	a5,28(sp)
	sw	a3,0(sp)
	call	vsnprintf
	lw	ra,12(sp)
	addi	sp,sp,32
	jr	ra
	.size	sprintf, .-sprintf
	.section	.text.printf,"ax",@progbits
	.align	2
	.globl	printf
	.hidden	printf
	.type	printf, @function
printf:
	li	t0,-8192
	addi	sp,sp,-2044
	addi	t0,t0,-44
	sw	s0,2016(sp)
	sw	s1,2012(sp)
	sw	ra,2020(sp)
	li	t1,12288
	add	sp,sp,t0
	addi	t2,sp,4
	addi	t0,t1,-2032
	add	t0,t0,t2
	sw	a1,0(t0)
	mv	a1,t1
	addi	t1,t1,-2028
	add	t1,t1,t2
	sw	a2,0(t1)
	mv	a2,a1
	addi	a1,a1,-2024
	add	a1,a1,t2
	sw	a3,0(a1)
	mv	a3,a2
	addi	a2,a2,-2020
	add	a2,a2,t2
	sw	a4,0(a2)
	mv	a4,a3
	addi	a3,a3,-2016
	add	a3,a3,t2
	sw	a5,0(a3)
	addi	a2,a4,-2044
	li	a5,-12288
	addi	a3,a4,-2028
	add	a2,a2,a5
	add	a5,a2,t2
	add	a3,a3,sp
	li	s0,-8192
	sw	a5,0(sp)
	sw	a3,2044(a5)
	addi	s0,s0,-2048
	addi	a5,a4,-2044
	add	a5,a5,s0
	add	s0,a5,t2
	li	a1,12288
	mv	a2,a0
	addi	a1,a1,-2048
	mv	a0,s0
	call	vsnprintf
	mv	s1,a0
.L90:
	lbu	a0,0(s0)
	bne	a0,zero,.L91
	li	t0,8192
	addi	t0,t0,44
	add	sp,sp,t0
	lw	ra,2020(sp)
	mv	a0,s1
	lw	s0,2016(sp)
	lw	s1,2012(sp)
	addi	sp,sp,2044
	jr	ra
.L91:
	call	putch
	addi	s0,s0,1
	j	.L90
	.size	printf, .-printf
	.ident	"GCC: (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0"
	.section	.note.GNU-stack,"",@progbits
