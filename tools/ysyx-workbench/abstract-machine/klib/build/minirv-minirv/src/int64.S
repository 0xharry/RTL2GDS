#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
	.file	"int64.c"
	.option nopic
	.text
	.globl	__umodsi3
	.globl	__udivsi3
	.globl	__ctzsi2
	.globl	__clzsi2
	.section	.text.__udivmoddi4,"ax",@progbits
	.align	2
	.globl	__udivmoddi4
	.hidden	__udivmoddi4
	.type	__udivmoddi4, @function
__udivmoddi4:
	addi	sp,sp,-36
	sw	s0,28(sp)
	sw	s1,24(sp)
	mv	t0,a1
	sw	ra,32(sp)
	mv	s0,a0
	mv	a1,a3
	mv	s1,a4
	bne	t0,zero,.L2
	bne	a3,zero,.L3
	beq	a4,zero,.L4
	mv	a1,a2
	sw	a2,0(sp)
	call	__umodsi3
	lw	a2,0(sp)
	sw	a0,0(s1)
	sw	zero,4(s1)
.L4:
	mv	a1,a2
	mv	a0,s0
.L42:
	call	__udivsi3
	mv	s0,a0
.L41:
	li	t0,0
	j	.L5
.L3:
	beq	a4,zero,.L20
	sw	a0,0(s1)
	sw	zero,4(a4)
.L20:
	li	s0,0
	j	.L5
.L2:
	bne	a2,zero,.L6
	bne	a1,zero,.L7
	ebreak
.L7:
	bne	a0,zero,.L8
	beq	a4,zero,.L9
	mv	a0,t0
	sw	a1,4(sp)
	sw	t0,0(sp)
	call	__umodsi3
	lw	a1,4(sp)
	lw	t0,0(sp)
	sw	zero,0(s1)
	sw	a0,4(s1)
.L9:
	mv	a0,t0
	j	.L42
.L8:
	addi	a4,a1,-1
	and	a0,a4,a1
	bne	a0,zero,.L10
	beq	s1,zero,.L11
	and	a4,a4,t0
	sw	s0,0(s1)
	sw	a4,4(s1)
.L11:
	mv	a0,a1
	sw	t0,0(sp)
	call	__ctzsi2
	lw	t0,0(sp)
	srl	s0,t0,a0
	j	.L41
.L10:
	mv	a0,a1
	sw	a2,20(sp)
	sw	t0,16(sp)
	sw	t0,0(sp)
	sw	a2,12(sp)
	sw	a1,8(sp)
	call	__clzsi2
	lw	a5,0(sp)
	sw	a0,4(sp)
	mv	a0,a5
	call	__clzsi2
	lw	t1,4(sp)
	li	a4,30
	lw	a5,0(sp)
	sub	t1,t1,a0
	lw	a1,8(sp)
	lw	a3,12(sp)
	lw	t0,16(sp)
	lw	a2,20(sp)
	bleu	t1,a4,.L12
.L18:
	beq	s1,zero,.L21
	sw	s0,0(s1)
	sw	t0,4(s1)
.L21:
	li	s0,0
	j	.L41
.L12:
	addi	t1,t1,1
	li	a0,32
	sub	a0,a0,t1
	sll	a4,s0,a0
	srl	t2,a5,t1
	sll	a0,a5,a0
	srl	a5,s0,t1
	or	a5,a0,a5
.L13:
	li	s0,0
.L19:
	srli	a0,a5,31
	slli	t2,t2,1
	or	t2,t2,a0
	slli	a5,a5,1
	srli	a0,a4,31
	or	a5,a5,a0
	slli	a4,a4,1
	srli	a0,a3,31
	or	a4,a4,a0
	slli	a3,a3,1
	sub	a0,a2,a5
	sgtu	t0,a0,a2
	or	a3,a3,s0
	sub	s0,a1,t2
	sub	s0,s0,t0
	seqz	a0,a0
	sub	s0,s0,a0
	srai	a0,s0,31
	and	t0,a0,a2
	sub	t0,a5,t0
	sgtu	a5,t0,a5
	sw	a5,0(sp)
	mv	a5,t0
	lw	t0,0(sp)
	and	a0,a0,a1
	sub	a0,t2,a0
	addi	t1,t1,-1
	srli	s0,s0,31
	sub	t2,a0,t0
	bne	t1,zero,.L19
	srli	t0,a3,31
	slli	a4,a4,1
	slli	a3,a3,1
	or	s0,a3,s0
	or	t0,t0,a4
	beq	s1,zero,.L5
	sw	a5,0(s1)
	sw	t2,4(s1)
	j	.L5
.L6:
	bne	a1,zero,.L14
	addi	a4,a2,-1
	and	a3,a4,a2
	bne	a3,zero,.L15
	beq	s1,zero,.L16
	and	a4,a4,a0
	sw	a4,0(s1)
	sw	zero,4(s1)
.L16:
	li	a5,1
	beq	a2,a5,.L5
	mv	a0,a2
	sw	t0,0(sp)
	call	__ctzsi2
	lw	t0,0(sp)
	li	a5,32
	sub	a5,a5,a0
	sll	a5,t0,a5
	srl	s0,s0,a0
	or	s0,a5,s0
	srl	t0,t0,a0
.L5:
	lw	ra,32(sp)
	mv	a0,s0
	lw	s0,28(sp)
	lw	s1,24(sp)
	mv	a1,t0
	addi	sp,sp,36
	jr	ra
.L15:
	mv	a0,a2
	sw	a1,16(sp)
	sw	a1,12(sp)
	sw	t0,0(sp)
	sw	a2,8(sp)
	call	__clzsi2
	lw	a5,0(sp)
	sw	a0,4(sp)
	mv	a0,a5
	call	__clzsi2
	lw	a4,4(sp)
	li	t0,32
	lw	a5,0(sp)
	sub	a0,a4,a0
	addi	t1,a0,33
	lw	a2,8(sp)
	lw	t2,12(sp)
	lw	a1,16(sp)
	mv	a4,s0
	li	a3,0
	beq	t1,t0,.L13
	li	a3,31
	bgtu	t1,a3,.L17
	sub	a0,t0,t1
	srl	a3,s0,t1
	srl	t2,a5,t1
	sll	a5,a5,a0
	or	a5,a5,a3
	sll	a4,s0,a0
	li	a3,0
	j	.L13
.L17:
	li	t0,64
	sub	t0,t0,t1
	addi	a0,a0,1
	sll	a3,s0,t0
	srl	a4,s0,a0
	sll	t0,a5,t0
	or	a4,t0,a4
	srl	a5,a5,a0
	j	.L13
.L14:
	mv	a0,a1
	sw	t0,12(sp)
	sw	t0,0(sp)
	sw	a2,16(sp)
	sw	a1,8(sp)
	call	__clzsi2
	lw	a5,0(sp)
	sw	a0,4(sp)
	mv	a0,a5
	call	__clzsi2
	lw	t1,4(sp)
	li	a4,31
	lw	t0,12(sp)
	sub	t1,t1,a0
	bgtu	t1,a4,.L18
	addi	t1,t1,1
	li	a3,32
	lw	a5,0(sp)
	lw	a1,8(sp)
	lw	a2,16(sp)
	mv	a4,s0
	beq	t1,a3,.L23
	sub	a3,a3,t1
	srl	t2,a5,t1
	srl	a0,s0,t1
	sll	a5,a5,a3
	sll	a4,s0,a3
	or	a5,a5,a0
	li	a3,0
	j	.L13
.L23:
	li	a3,0
	li	t2,0
	j	.L13
	.size	__udivmoddi4, .-__udivmoddi4
	.section	.text.__divdi3,"ax",@progbits
	.align	2
	.globl	__divdi3
	.hidden	__divdi3
	.type	__divdi3, @function
__divdi3:
	srai	a5,a3,31
	srai	t2,a1,31
	xor	a4,a2,a5
	xor	t0,a0,t2
	sub	a2,a4,a5
	xor	a3,a3,a5
	xor	a1,a1,t2
	sub	a0,t0,t2
	sgtu	t1,a2,a4
	sub	a3,a3,a5
	sgtu	t0,a0,t0
	sub	a1,a1,t2
	addi	sp,sp,-12
	li	a4,0
	sub	a3,a3,t1
	sub	a1,a1,t0
	sw	s0,4(sp)
	sw	ra,8(sp)
	xor	s0,t2,a5
	call	__udivmoddi4
	xor	a5,a0,s0
	xor	a1,a1,s0
	sub	a0,a5,s0
	lw	ra,8(sp)
	sub	a1,a1,s0
	lw	s0,4(sp)
	sgtu	a5,a0,a5
	sub	a1,a1,a5
	addi	sp,sp,12
	jr	ra
	.size	__divdi3, .-__divdi3
	.globl	__muldi3
	.section	.text.__divmoddi4,"ax",@progbits
	.align	2
	.globl	__divmoddi4
	.hidden	__divmoddi4
	.type	__divmoddi4, @function
__divmoddi4:
	addi	sp,sp,-32
	sw	ra,28(sp)
	sw	s0,24(sp)
	sw	s1,20(sp)
	sw	a4,8(sp)
	mv	s1,a0
	sw	a2,16(sp)
	sw	a3,12(sp)
	mv	s0,a1
	call	__divdi3
	lw	t1,16(sp)
	lw	a5,12(sp)
	mv	a2,a0
	mv	a3,a1
	sw	a0,4(sp)
	sw	a1,0(sp)
	mv	a0,t1
	mv	a1,a5
	call	__muldi3
	lw	a4,8(sp)
	sub	a0,s1,a0
	sgtu	s1,a0,s1
	sub	s0,s0,a1
	sub	s0,s0,s1
	lw	a2,4(sp)
	lw	a3,0(sp)
	lw	ra,28(sp)
	sw	s0,4(a4)
	lw	s0,24(sp)
	sw	a0,0(a4)
	lw	s1,20(sp)
	mv	a0,a2
	mv	a1,a3
	addi	sp,sp,32
	jr	ra
	.size	__divmoddi4, .-__divmoddi4
	.section	.text.__moddi3,"ax",@progbits
	.align	2
	.globl	__moddi3
	.hidden	__moddi3
	.type	__moddi3, @function
__moddi3:
	addi	sp,sp,-24
	sw	s0,16(sp)
	srai	a4,a3,31
	srai	s0,a1,31
	xor	t1,a2,a4
	xor	a5,a0,s0
	sw	s1,12(sp)
	sub	a2,t1,a4
	sub	a0,a5,s0
	addi	s1,sp,7
	xor	a3,a3,a4
	xor	a1,a1,s0
	andi	s1,s1,-8
	sgtu	a5,a0,a5
	sgtu	t1,a2,t1
	sub	a3,a3,a4
	sub	a1,a1,s0
	mv	a4,s1
	sub	a1,a1,a5
	sub	a3,a3,t1
	sw	ra,20(sp)
	call	__udivmoddi4
	lw	a5,0(s1)
	lw	a1,4(s1)
	lw	ra,20(sp)
	xor	a5,a5,s0
	xor	a1,a1,s0
	sub	a0,a5,s0
	sub	a1,a1,s0
	lw	s0,16(sp)
	sgtu	a5,a0,a5
	lw	s1,12(sp)
	sub	a1,a1,a5
	addi	sp,sp,24
	jr	ra
	.size	__moddi3, .-__moddi3
	.section	.text.__udivdi3,"ax",@progbits
	.align	2
	.globl	__udivdi3
	.hidden	__udivdi3
	.type	__udivdi3, @function
__udivdi3:
	li	a4,0
	tail	__udivmoddi4
	.size	__udivdi3, .-__udivdi3
	.section	.text.__umoddi3,"ax",@progbits
	.align	2
	.globl	__umoddi3
	.hidden	__umoddi3
	.type	__umoddi3, @function
__umoddi3:
	addi	sp,sp,-24
	sw	s0,16(sp)
	addi	s0,sp,7
	andi	s0,s0,-8
	mv	a4,s0
	sw	ra,20(sp)
	call	__udivmoddi4
	lw	a0,0(s0)
	lw	a1,4(s0)
	lw	ra,20(sp)
	lw	s0,16(sp)
	addi	sp,sp,24
	jr	ra
	.size	__umoddi3, .-__umoddi3
	.section	.text.__clzsi2,"ax",@progbits
	.align	2
	.globl	__clzsi2
	.hidden	__clzsi2
	.type	__clzsi2, @function
__clzsi2:
	li	a5,-65536
	and	a5,a0,a5
	seqz	a5,a5
	slli	a3,a5,4
	li	a5,16
	sub	a5,a5,a3
	li	a4,65536
	srl	a5,a0,a5
	addi	a4,a4,-256
	and	a4,a5,a4
	seqz	a4,a4
	slli	a4,a4,3
	li	a2,8
	sub	a2,a2,a4
	srl	a5,a5,a2
	andi	a0,a5,240
	seqz	a0,a0
	add	a4,a4,a3
	slli	a0,a0,2
	li	a3,4
	sub	a3,a3,a0
	srl	a5,a5,a3
	add	a3,a0,a4
	andi	a0,a5,12
	seqz	a0,a0
	slli	a0,a0,1
	li	a2,2
	sub	a4,a2,a0
	srl	a5,a5,a4
	srli	a4,a5,1
	xori	a4,a4,1
	andi	a4,a4,1
	sub	a2,a2,a5
	neg	a4,a4
	and	a4,a4,a2
	add	a0,a0,a3
	add	a0,a4,a0
	ret
	.size	__clzsi2, .-__clzsi2
	.section	.text.__ctzsi2,"ax",@progbits
	.align	2
	.globl	__ctzsi2
	.hidden	__ctzsi2
	.type	__ctzsi2, @function
__ctzsi2:
	slli	a3,a0,16
	srli	a3,a3,16
	seqz	a3,a3
	slli	a3,a3,4
	srl	a5,a0,a3
	andi	a4,a5,255
	seqz	a4,a4
	slli	a4,a4,3
	srl	a5,a5,a4
	add	a4,a4,a3
	andi	a3,a5,15
	seqz	a3,a3
	slli	a3,a3,2
	srl	a5,a5,a3
	add	a3,a3,a4
	andi	a4,a5,3
	seqz	a4,a4
	slli	a4,a4,1
	srl	a5,a5,a4
	srli	a2,a5,1
	andi	a2,a2,1
	li	a0,2
	andi	a5,a5,1
	sub	a0,a0,a2
	addi	a5,a5,-1
	and	a0,a0,a5
	add	a4,a4,a3
	add	a0,a0,a4
	ret
	.size	__ctzsi2, .-__ctzsi2
	.section	.text.__ctzdi2,"ax",@progbits
	.align	2
	.globl	__ctzdi2
	.hidden	__ctzdi2
	.type	__ctzdi2, @function
__ctzdi2:
	addi	sp,sp,-12
	seqz	a5,a0
	sw	s0,4(sp)
	neg	s0,a5
	addi	a5,a5,-1
	and	a1,s0,a1
	and	a0,a5,a0
	or	a0,a0,a1
	sw	ra,8(sp)
	andi	s0,s0,32
	call	__ctzsi2
	lw	ra,8(sp)
	add	a0,s0,a0
	lw	s0,4(sp)
	addi	sp,sp,12
	jr	ra
	.size	__ctzdi2, .-__ctzdi2
	.section	.text.__clzdi2,"ax",@progbits
	.align	2
	.globl	__clzdi2
	.hidden	__clzdi2
	.type	__clzdi2, @function
__clzdi2:
	addi	sp,sp,-12
	seqz	a5,a1
	sw	s0,4(sp)
	neg	s0,a5
	addi	a5,a5,-1
	and	a1,a5,a1
	and	a0,s0,a0
	or	a0,a1,a0
	sw	ra,8(sp)
	andi	s0,s0,32
	call	__clzsi2
	lw	ra,8(sp)
	add	a0,s0,a0
	lw	s0,4(sp)
	addi	sp,sp,12
	jr	ra
	.size	__clzdi2, .-__clzdi2
	.ident	"GCC: (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0"
	.section	.note.GNU-stack,"",@progbits
