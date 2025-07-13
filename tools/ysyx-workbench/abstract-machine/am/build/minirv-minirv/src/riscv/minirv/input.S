#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
	.file	"input.c"
	.option nopic
	.text
	.section	.text.__am_input_keybrd,"ax",@progbits
	.align	2
	.globl	__am_input_keybrd
	.hidden	__am_input_keybrd
	.type	__am_input_keybrd, @function
__am_input_keybrd:
	sb	zero,0(a0)
	sw	zero,4(a0)
	ret
	.size	__am_input_keybrd, .-__am_input_keybrd
	.ident	"GCC: (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0"
	.section	.note.GNU-stack,"",@progbits
