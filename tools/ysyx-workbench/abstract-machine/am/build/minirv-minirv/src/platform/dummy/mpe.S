#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
	.file	"mpe.c"
	.option nopic
	.text
	.section	.text.mpe_init,"ax",@progbits
	.align	2
	.globl	mpe_init
	.hidden	mpe_init
	.type	mpe_init, @function
mpe_init:
	li	a0,0
	ret
	.size	mpe_init, .-mpe_init
	.section	.text.cpu_count,"ax",@progbits
	.align	2
	.globl	cpu_count
	.hidden	cpu_count
	.type	cpu_count, @function
cpu_count:
	li	a0,1
	ret
	.size	cpu_count, .-cpu_count
	.section	.text.cpu_current,"ax",@progbits
	.align	2
	.globl	cpu_current
	.hidden	cpu_current
	.type	cpu_current, @function
cpu_current:
	li	a0,0
	ret
	.size	cpu_current, .-cpu_current
	.section	.text.atomic_xchg,"ax",@progbits
	.align	2
	.globl	atomic_xchg
	.hidden	atomic_xchg
	.type	atomic_xchg, @function
atomic_xchg:
	li	a0,0
	ret
	.size	atomic_xchg, .-atomic_xchg
	.ident	"GCC: (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0"
	.section	.note.GNU-stack,"",@progbits
