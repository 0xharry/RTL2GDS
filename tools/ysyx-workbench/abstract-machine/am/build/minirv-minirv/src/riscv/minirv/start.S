#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
#include "/opt/rtl2gds/tools/ysyx-workbench/abstract-machine/tools/minirv/inst-replace.h"
.section entry, "ax"
.globl _start
.type _start, @function

_start:
  mv s0, zero
  la sp, _stack_pointer
  call _FSBL

.size _start, . - _start
