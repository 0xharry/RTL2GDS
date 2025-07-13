#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
	.file	"multi3.c"
	.option nopic
	.text
	.section	.text.__muldi3,"ax",@progbits
	.align	2
	.globl	__muldi3
	.type	__muldi3, @function
__muldi3:
	addi	sp,sp,-12
	mv	t2,a0
	mv	a0,a2
	mv	t0,a3
	sw	ra,8(sp)
	sw	s0,4(sp)
	sw	s1,0(sp)
	mv	a2,t2
	mv	a3,a0
	li	a4,0
	li	a5,0
	li	t1,0
.L3:
	andi	s1,a3,1
	slli	s0,a4,1
	beq	s1,zero,.L2
	add	s1,a2,t1
	add	a4,a5,a4
	sgtu	a5,t1,s1
	add	a5,a5,a4
	mv	t1,s1
.L2:
	srli	a4,a2,31
	srli	a3,a3,1
	or	a4,s0,a4
	slli	a2,a2,1
	bne	a3,zero,.L3
	beq	a1,zero,.L4
#APP
# 80 "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/am/src/riscv/minirv/libgcc/multi3.c" 1
	call __mulsi3
# 0 "" 2
#NO_APP
	add	a5,a5,a0
.L4:
	beq	t0,zero,.L5
	mv	a0,t2
	mv	a1,t0
#APP
# 83 "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/am/src/riscv/minirv/libgcc/multi3.c" 1
	call __mulsi3
# 0 "" 2
#NO_APP
	add	a5,a0,a5
.L5:
	lw	ra,8(sp)
	lw	s0,4(sp)
	lw	s1,0(sp)
	mv	a0,t1
	mv	a1,a5
	addi	sp,sp,12
	jr	ra
	.size	__muldi3, .-__muldi3
	.ident	"GCC: (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0"
	.section	.note.GNU-stack,"",@progbits
