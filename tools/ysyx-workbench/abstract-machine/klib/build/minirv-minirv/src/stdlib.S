#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
	.file	"stdlib.c"
	.option nopic
	.text
	.globl	__mulsi3
	.section	.text.rand,"ax",@progbits
	.align	2
	.globl	rand
	.hidden	rand
	.type	rand, @function
rand:
	addi	sp,sp,-12
	sw	s0,4(sp)
	lla	s0,.LANCHOR0
	lw	a0,0(s0)
	li	a1,1103515648
	addi	a1,a1,-403
	sw	ra,8(sp)
	call	__mulsi3
	li	a5,12288
	addi	a5,a5,57
	add	a0,a0,a5
	sw	a0,0(s0)
	lw	ra,8(sp)
	lw	s0,4(sp)
	slli	a0,a0,1
	srli	a0,a0,17
	addi	sp,sp,12
	jr	ra
	.size	rand, .-rand
	.section	.text.srand,"ax",@progbits
	.align	2
	.globl	srand
	.hidden	srand
	.type	srand, @function
srand:
	sw	a0,.LANCHOR0,a5
	ret
	.size	srand, .-srand
	.section	.text.abs,"ax",@progbits
	.align	2
	.globl	abs
	.hidden	abs
	.type	abs, @function
abs:
	srai	a5,a0,31
	xor	a0,a5,a0
	sub	a0,a0,a5
	ret
	.size	abs, .-abs
	.section	.text.atoi,"ax",@progbits
	.align	2
	.globl	atoi
	.hidden	atoi
	.type	atoi, @function
atoi:
	mv	a5,a0
	li	a4,32
.L6:
	lbu	a3,0(a5)
	beq	a3,a4,.L7
	li	a0,0
	li	a2,9
.L8:
	lbu	a3,0(a5)
	addi	a4,a3,-48
	andi	a4,a4,0xff
	bleu	a4,a2,.L9
	ret
.L7:
	addi	a5,a5,1
	j	.L6
.L9:
	slli	a4,a0,2
	add	a0,a4,a0
	slli	a0,a0,1
	add	a0,a0,a3
	addi	a0,a0,-48
	addi	a5,a5,1
	j	.L8
	.size	atoi, .-atoi
	.section	.text.malloc_reset,"ax",@progbits
	.align	2
	.globl	malloc_reset
	.hidden	malloc_reset
	.type	malloc_reset, @function
malloc_reset:
	la a5, heap; lw a5, 0(a5);
	addi	a5,a5,3
	andi	a5,a5,-4
	sw	a5,.LANCHOR1,a4
	ret
	.size	malloc_reset, .-malloc_reset
	.section	.rodata.malloc.str1.4,"aMS",@progbits,1
	.align	2
.LC0:
	.string	"/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/klib/src/stdlib.c"
	.align	2
.LC1:
	.string	"Assertion fail at %s:%d\n"
	.section	.text.malloc,"ax",@progbits
	.align	2
	.globl	malloc
	.hidden	malloc
	.type	malloc, @function
malloc:
	lla	a4,.LANCHOR1
	addi	a5,a0,3
	lw	a0,0(a4)
	addi	sp,sp,-12
	andi	a5,a5,-4
	sw	ra,8(sp)
	add	a5,a0,a5
	sw	a5,0(a4)
	lla	a4,heap
	lw	a2,0(a4)
	bgtu	a2,a5,.L12
	lw	a4,4(a4)
	mv	a3,a0
	bgtu	a4,a5,.L13
.L12:
	li	a2,45
.L19:
	lla	a1,.LC0
	lla	a0,.LC1
	call	printf
	li	a0,1
	call	halt
.L14:
	sw	zero,0(a3)
	addi	a3,a3,4
.L13:
	bne	a5,a3,.L14
	sub	a5,a5,a2
	sub	a4,a4,a2
	bleu	a5,a4,.L11
	li	a2,49
	j	.L19
.L11:
	lw	ra,8(sp)
	addi	sp,sp,12
	jr	ra
	.size	malloc, .-malloc
	.section	.text.free,"ax",@progbits
	.align	2
	.globl	free
	.hidden	free
	.type	free, @function
free:
	ret
	.size	free, .-free
	.section	.sbss.hbrk,"aw",@nobits
	.align	2
	.set	.LANCHOR1,. + 0
	.type	hbrk, @object
	.size	hbrk, 4
hbrk:
	.zero	4
	.section	.sdata.next,"aw"
	.align	2
	.set	.LANCHOR0,. + 0
	.type	next, @object
	.size	next, 4
next:
	.word	1
	.ident	"GCC: (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0"
	.section	.note.GNU-stack,"",@progbits
