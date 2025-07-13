#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
	.file	"unused.c"
	.option nopic
	.text
	.section	.rodata.__muldf3.str1.4,"aMS",@progbits,1
	.align	2
.LC0:
	.string	"AM Panic: "
	.align	2
.LC1:
	.string	"Not implement"
	.align	2
.LC2:
	.string	" @ /opt/rtl2gds/tools/ysyx-workbench/abstract-machine/am/src/riscv/minirv/libgcc/unused.c:4  \n"
	.section	.text.__muldf3,"ax",@progbits
	.align	2
	.globl	__muldf3
	.hidden	__muldf3
	.type	__muldf3, @function
__muldf3:
	addi	sp,sp,-12
	sw	s0,4(sp)
	sw	ra,8(sp)
	lla	s0,.LC0
.L2:
	lbu	a0,0(s0)
	bne	a0,zero,.L3
	lla	s0,.LC1
.L4:
	lbu	a0,0(s0)
	bne	a0,zero,.L5
	lla	s0,.LC2
.L6:
	lbu	a0,0(s0)
	bne	a0,zero,.L7
	li	a0,1
	call	halt
.L3:
	call	putch
	addi	s0,s0,1
	j	.L2
.L5:
	call	putch
	addi	s0,s0,1
	j	.L4
.L7:
	call	putch
	addi	s0,s0,1
	j	.L6
	.size	__muldf3, .-__muldf3
	.section	.rodata.__fixdfdi.str1.4,"aMS",@progbits,1
	.align	2
.LC3:
	.string	" @ /opt/rtl2gds/tools/ysyx-workbench/abstract-machine/am/src/riscv/minirv/libgcc/unused.c:5  \n"
	.section	.text.__fixdfdi,"ax",@progbits
	.align	2
	.globl	__fixdfdi
	.hidden	__fixdfdi
	.type	__fixdfdi, @function
__fixdfdi:
	addi	sp,sp,-12
	sw	s0,4(sp)
	sw	ra,8(sp)
	lla	s0,.LC0
.L10:
	lbu	a0,0(s0)
	bne	a0,zero,.L11
	lla	s0,.LC1
.L12:
	lbu	a0,0(s0)
	bne	a0,zero,.L13
	lla	s0,.LC3
.L14:
	lbu	a0,0(s0)
	bne	a0,zero,.L15
	li	a0,1
	call	halt
.L11:
	call	putch
	addi	s0,s0,1
	j	.L10
.L13:
	call	putch
	addi	s0,s0,1
	j	.L12
.L15:
	call	putch
	addi	s0,s0,1
	j	.L14
	.size	__fixdfdi, .-__fixdfdi
	.ident	"GCC: (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0"
	.section	.note.GNU-stack,"",@progbits
