#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
	.file	"cte.c"
	.option nopic
	.text
	.section	.rodata.__am_irq_handle.str1.4,"aMS",@progbits,1
	.align	2
.LC0:
	.string	"/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/am/src/riscv/minirv/cte.c"
	.align	2
.LC1:
	.string	"Assertion fail at %s:%d\n"
	.section	.text.__am_irq_handle,"ax",@progbits
	.align	2
	.globl	__am_irq_handle
	.hidden	__am_irq_handle
	.type	__am_irq_handle, @function
__am_irq_handle:
	addi	sp,sp,-44
	sw	s0,36(sp)
	sw	s1,32(sp)
	sw	ra,40(sp)
	lw	s1,.LANCHOR0
	mv	s0,a0
	beq	s1,zero,.L2
	li	a5,4
	li	a2,16
	addi	a1,sp,16
	mv	a0,sp
	sw	a5,16(sp)
	sw	zero,20(sp)
	sw	zero,24(sp)
	sw	zero,28(sp)
	call	memcpy
	mv	a1,s0
	mv	a0,sp
	jalr	s1
	mv	s0,a0
	bne	a0,zero,.L2
	li	a2,15
	lla	a1,.LC0
	lla	a0,.LC1
	call	printf
	li	a0,1
	call	halt
.L2:
	lw	ra,40(sp)
	mv	a0,s0
	lw	s0,36(sp)
	lw	s1,32(sp)
	addi	sp,sp,44
	jr	ra
	.size	__am_irq_handle, .-__am_irq_handle
	.section	.text.cte_init,"ax",@progbits
	.align	2
	.globl	cte_init
	.hidden	cte_init
	.type	cte_init, @function
cte_init:
	lla	a5,__am_asm_trap
#APP
# 25 "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/am/src/riscv/minirv/cte.c" 1
	csrw mtvec, a5
# 0 "" 2
#NO_APP
	sw	a0,.LANCHOR0,a5
	li	a0,1
	ret
	.size	cte_init, .-cte_init
	.section	.text.kcontext,"ax",@progbits
	.align	2
	.globl	kcontext
	.hidden	kcontext
	.type	kcontext, @function
kcontext:
	addi	sp,sp,-8
	li	a0,0
	addi	sp,sp,8
	jr	ra
	.size	kcontext, .-kcontext
	.section	.text.yield,"ax",@progbits
	.align	2
	.globl	yield
	.hidden	yield
	.type	yield, @function
yield:
#APP
# 39 "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/am/src/riscv/minirv/cte.c" 1
	li a5, -1; ecall
# 0 "" 2
#NO_APP
	ret
	.size	yield, .-yield
	.section	.text.ienabled,"ax",@progbits
	.align	2
	.globl	ienabled
	.hidden	ienabled
	.type	ienabled, @function
ienabled:
	li	a0,0
	ret
	.size	ienabled, .-ienabled
	.section	.text.iset,"ax",@progbits
	.align	2
	.globl	iset
	.hidden	iset
	.type	iset, @function
iset:
	ret
	.size	iset, .-iset
	.section	.sbss.user_handler,"aw",@nobits
	.align	2
	.set	.LANCHOR0,. + 0
	.type	user_handler, @object
	.size	user_handler, 4
user_handler:
	.zero	4
	.ident	"GCC: (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0"
	.section	.note.GNU-stack,"",@progbits
