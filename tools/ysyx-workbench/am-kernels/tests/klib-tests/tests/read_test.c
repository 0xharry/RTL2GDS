#include "klibtest.h"
#define N 15
const char s1[N] = "1111HELLO WORLD";
const char s2[N] = "0000HELLO world";
const int cmp_res[N] = {1,1,1,1,0,0,0,0,0,0,-32,-32,-32,-32,-32};
void check_result(int fun_result,int l, int r) {
    // 找到cmp_res中的指定区间[l,r]中的第一个非零值(如果有的话)
    int first_non_zero = 0;
    for (; l < r; l ++) {
        if (cmp_res[l] != 0) {
            first_non_zero = cmp_res[l];
            break;
        }
    }
    if (first_non_zero > 0) {
        assert(fun_result > 0);
    }else if (first_non_zero < 0) {
        assert(fun_result < 0);
    }else if (first_non_zero == 0) {
        assert(fun_result == 0);
    }
}
void check_memcmp() {
    int l,r;
    int fun_result;
    for (l = 0; l < N; l ++) {
        for (r = l + 1; r < N; r ++) {
            fun_result = memcmp(s1+l,s2+l,r-l);
            check_result(fun_result, l, r);
        }
    }
}

void check_strlen() {
    int l;
    int fun_result;
    for (l = 0; l < N; l ++) {
        fun_result = strlen(s1+l);
        assert(fun_result == N-l);
    }
}
int main() {
    check_memcmp();
    check_strlen();
    return 0;
}
