#ifndef __COMMON_H__
#define __COMMON_H__

#include <stdint.h>
#include <macro.h>
#include <config_macro.h>
#include <inttypes.h>
#include <stdio.h>
#include <assert.h>
#include <stdlib.h>
#include <string.h>

typedef uint32_t word_t;
typedef uint32_t vaddr_t;
typedef uint32_t paddr_t;

typedef int32_t  sword_t;
#define FMT_WORD "0x%08x" //选择输出的十六进制数的位数，若为ISA64,则为"lx"，16位16进制数。
#define FMT_PADDR "0x%08x"

#include <debug.h>

#endif
