#ifndef __WATCHPOINT_H
#define __WATCHPOINT_H

#include "sdb.h"
#include <stdint.h>
#include <string.h>

typedef struct watchpoint {
    int                NO;
    struct watchpoint* next;
    /* TODO: Add more members if necessary */
    char *str;
    uint32_t Len;
    uint64_t cur_value;
    uint64_t old_value;
} WP;

void new_wp(char *expr);
WP* get_head(void);
void free_wp(WP *wp);
#endif
