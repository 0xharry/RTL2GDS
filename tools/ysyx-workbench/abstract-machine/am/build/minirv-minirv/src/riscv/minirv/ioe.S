#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
	.file	"ioe.c"
	.option nopic
	.text
	.section	.text.__am_timer_config,"ax",@progbits
	.align	2
	.type	__am_timer_config, @function
__am_timer_config:
	li	a5,1
	sb	a5,0(a0)
	sb	a5,1(a0)
	ret
	.size	__am_timer_config, .-__am_timer_config
	.section	.text.__am_input_config,"ax",@progbits
	.align	2
	.type	__am_input_config, @function
__am_input_config:
	li	a5,1
	sb	a5,0(a0)
	ret
	.size	__am_input_config, .-__am_input_config
	.section	.text.__am_uart_config,"ax",@progbits
	.align	2
	.type	__am_uart_config, @function
__am_uart_config:
	sb	zero,0(a0)
	ret
	.size	__am_uart_config, .-__am_uart_config
	.section	.rodata.fail.str1.4,"aMS",@progbits,1
	.align	2
.LC0:
	.string	"AM Panic: "
	.align	2
.LC1:
	.string	"access nonexist register"
	.align	2
.LC2:
	.string	" @ /opt/rtl2gds/tools/ysyx-workbench/abstract-machine/am/src/riscv/minirv/ioe.c:24  \n"
	.section	.text.fail,"ax",@progbits
	.align	2
	.type	fail, @function
fail:
	addi	sp,sp,-12
	sw	s0,4(sp)
	sw	ra,8(sp)
	lla	s0,.LC0
.L5:
	lbu	a0,0(s0)
	bne	a0,zero,.L6
	lla	s0,.LC1
.L7:
	lbu	a0,0(s0)
	bne	a0,zero,.L8
	lla	s0,.LC2
.L9:
	lbu	a0,0(s0)
	bne	a0,zero,.L10
	li	a0,1
	call	halt
.L6:
	call	putch
	addi	s0,s0,1
	j	.L5
.L8:
	call	putch
	addi	s0,s0,1
	j	.L7
.L10:
	call	putch
	addi	s0,s0,1
	j	.L9
	.size	fail, .-fail
	.section	.text.ioe_init,"ax",@progbits
	.align	2
	.globl	ioe_init
	.hidden	ioe_init
	.type	ioe_init, @function
ioe_init:
	addi	sp,sp,-12
	sw	ra,8(sp)
	lla	a5,.LANCHOR0
	lla	a4,.LANCHOR0+512
	lla	a3,fail
.L14:
	lw	a2,0(a5)
	bne	a2,zero,.L13
	sw	a3,0(a5)
.L13:
	addi	a5,a5,4
	bne	a5,a4,.L14
	call	__am_timer_init
	lw	ra,8(sp)
	li	a0,1
	addi	sp,sp,12
	jr	ra
	.size	ioe_init, .-ioe_init
	.section	.text.ioe_read,"ax",@progbits
	.align	2
	.globl	ioe_read
	.hidden	ioe_read
	.type	ioe_read, @function
ioe_read:
	slli	a4,a0,2
	lla	a5,.LANCHOR0
	add	a5,a5,a4
	lw	a5,0(a5)
	mv	a0,a1
	jr	a5
	.size	ioe_read, .-ioe_read
	.section	.text.ioe_write,"ax",@progbits
	.align	2
	.globl	ioe_write
	.hidden	ioe_write
	.type	ioe_write, @function
ioe_write:
	tail	ioe_read
	.size	ioe_write, .-ioe_write
	.section	.data.lut,"aw"
	.align	2
	.set	.LANCHOR0,. + 0
	.type	lut, @object
	.size	lut, 512
lut:
	.zero	4
	.word	__am_uart_config
	.zero	8
	.word	__am_timer_config
	.word	__am_timer_rtc
	.word	__am_timer_uptime
	.word	__am_input_config
	.word	__am_input_keybrd
	.zero	476
	.ident	"GCC: (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0"
	.section	.note.GNU-stack,"",@progbits
