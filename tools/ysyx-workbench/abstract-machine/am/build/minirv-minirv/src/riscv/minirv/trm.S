#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
	.file	"trm.c"
	.option nopic
	.text
	.section	.text.init_uart,"ax",@progbits
	.align	2
	.globl	init_uart
	.hidden	init_uart
	.type	init_uart, @function
init_uart:
	li	a5,268435456
	li	a4,-125
	sb	a4,3(a5)
	li	a4,1
	sb	a4,0(a5)
	li	a4,3
	sb	a4,3(a5)
	ret
	.size	init_uart, .-init_uart
	.section	.text.putch,"ax",@progbits
	.align	2
	.globl	putch
	.hidden	putch
	.type	putch, @function
putch:
	li	a5,268435456
	sb	a0,0(a5)
	ret
	.size	putch, .-putch
	.section	.rodata.print_hex.str1.4,"aMS",@progbits,1
	.align	2
.LC0:
	.string	"0123456789ABCDEF"
	.section	.text.print_hex,"ax",@progbits
	.align	2
	.globl	print_hex
	.hidden	print_hex
	.type	print_hex, @function
print_hex:
	addi	sp,sp,-40
	sw	s0,32(sp)
	li	a2,17
	mv	s0,a0
	lla	a1,.LC0
	addi	a0,sp,8
	sw	ra,36(sp)
	call	memcpy
	li	a4,0
	li	a3,15
.L4:
	add	a2,sp,a4
	mv	a5,a4
	andi	a4,s0,15
	addi	a4,a4,28
	add	a4,a4,sp
	lbu	a4,-20(a4)
	sb	a4,0(a2)
	mv	a2,s0
	addi	a4,a5,1
	srli	s0,s0,4
	bgtu	a2,a3,.L4
	li	a4,268435456
	li	a3,-1
.L5:
	add	a2,sp,a5
	lbu	a2,0(a2)
	addi	a5,a5,-1
	sb	a2,0(a4)
	bne	a5,a3,.L5
	li	a5,10
	sb	a5,0(a4)
	lw	ra,36(sp)
	lw	s0,32(sp)
	addi	sp,sp,40
	jr	ra
	.size	print_hex, .-print_hex
	.section	.text.halt,"ax",@progbits
	.align	2
	.globl	halt
	.hidden	halt
	.type	halt, @function
halt:
	li	a5,-2147483648
	li	a4,-86
	sb	a4,0(a5)
.L10:
	j	.L10
	.size	halt, .-halt
	.section	.entry,"ax",@progbits
	.align	2
	.globl	my_memcpy
	.hidden	my_memcpy
	.type	my_memcpy, @function
my_memcpy:
	li	a5,0
.L12:
	bne	a5,a2,.L13
	ret
.L13:
	add	a4,a1,a5
	lbu	a3,0(a4)
	add	a4,a0,a5
	addi	a5,a5,1
	sb	a3,0(a4)
	j	.L12
	.size	my_memcpy, .-my_memcpy
	.align	2
	.globl	_FSBL
	.hidden	_FSBL
	.type	_FSBL, @function
_FSBL:
	lla	a0,_ssbl_SA
	lla	a2,_ssbl_end
	addi	sp,sp,-12
	sub	a2,a2,a0
	lla	a1,_ssbl_MA
	sw	ra,8(sp)
	call	my_memcpy
#APP
# 96 "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/am/src/riscv/minirv/trm.c" 1
	lui t0, %hi(_init_memory)
addi t0, t0, %lo(_init_memory)
jalr ra, 0(t0)

# 0 "" 2
#NO_APP
	lw	ra,8(sp)
	addi	sp,sp,12
	jr	ra
	.size	_FSBL, .-_FSBL
	.section	.ssbl,"ax",@progbits
	.align	2
	.globl	_init_memory
	.hidden	_init_memory
	.type	_init_memory, @function
_init_memory:
	lla	a0,_text_SA
	lla	a2,_text_end
	addi	sp,sp,-16
	sub	a2,a2,a0
	lla	a1,_text_MA
	sw	ra,12(sp)
	sw	s0,8(sp)
	call	memcpy
	lla	a0,_rodata_SA
	lla	a2,_rodata_end
	sub	a2,a2,a0
	lla	a1,_rodata_MA
	call	memcpy
	lla	a0,__fsymtab_start
	beq	a0,zero,.L17
	lla	a2,__am_apps_data_end
	sub	a2,a2,a0
	lla	a1,__extra_ma
	call	memcpy
.L17:
	lla	a0,_data_SA
	call	print_hex
	lla	a0,_data_MA
	call	print_hex
	lla	a0,_data_end
	call	print_hex
	lla	s0,_data_SA
	lla	a2,_data_end
	sub	a2,a2,s0
	mv	a0,a2
	sw	a2,0(sp)
	call	print_hex
	lw	a2,0(sp)
	lla	a1,_data_MA
	mv	a0,s0
	call	memcpy
#APP
# 125 "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/am/src/riscv/minirv/trm.c" 1
	lui t0, %hi(_trm_init)
addi t0, t0, %lo(_trm_init)
jalr ra, 0(t0)

# 0 "" 2
#NO_APP
	lw	ra,12(sp)
	lw	s0,8(sp)
	addi	sp,sp,16
	jr	ra
	.size	_init_memory, .-_init_memory
	.section	.text._trm_init,"ax",@progbits
	.align	2
	.globl	_trm_init
	.hidden	_trm_init
	.type	_trm_init, @function
_trm_init:
	addi	sp,sp,-12
	sw	ra,8(sp)
	call	init_uart
	call	malloc_reset
	lla	a0,.LANCHOR0
	call	main
	li	a5,-2147483648
	li	a4,-86
	sb	a4,0(a5)
.L23:
	j	.L23
	.size	_trm_init, .-_trm_init
	.hidden	heap
	.globl	heap
	.section	.rodata.mainargs,"a"
	.align	2
	.set	.LANCHOR0,. + 0
	.type	mainargs, @object
	.size	mainargs, 64
mainargs:
	.string	"the_insert-arg_rule_in_Makefile_will_insert_mainargs_here"
	.zero	6
	.section	.sdata.heap,"aw"
	.align	2
	.type	heap, @object
	.size	heap, 8
heap:
	.word	_heap_start
	.word	_heap_end
	.weak	__extra_ma
	.weak	__am_apps_data_end
	.weak	__fsymtab_start
	.ident	"GCC: (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0"
	.section	.note.GNU-stack,"",@progbits
