#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
	.file	"vme.c"
	.option nopic
	.text
	.section	.text.vme_init,"ax",@progbits
	.align	2
	.globl	vme_init
	.hidden	vme_init
	.type	vme_init, @function
vme_init:
	li	a0,0
	ret
	.size	vme_init, .-vme_init
	.section	.text.protect,"ax",@progbits
	.align	2
	.globl	protect
	.hidden	protect
	.type	protect, @function
protect:
	ret
	.size	protect, .-protect
	.section	.text.unprotect,"ax",@progbits
	.align	2
	.globl	unprotect
	.hidden	unprotect
	.type	unprotect, @function
unprotect:
	ret
	.size	unprotect, .-unprotect
	.section	.text.map,"ax",@progbits
	.align	2
	.globl	map
	.hidden	map
	.type	map, @function
map:
	ret
	.size	map, .-map
	.section	.text.ucontext,"ax",@progbits
	.align	2
	.globl	ucontext
	.hidden	ucontext
	.type	ucontext, @function
ucontext:
	addi	sp,sp,-8
	li	a0,0
	addi	sp,sp,8
	jr	ra
	.size	ucontext, .-ucontext
	.ident	"GCC: (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0"
	.section	.note.GNU-stack,"",@progbits
