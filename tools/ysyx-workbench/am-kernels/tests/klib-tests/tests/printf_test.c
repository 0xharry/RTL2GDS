#include "klibtest.h"
#include <limits.h>
#include <stdio.h>
#define DATA_NUM 8
#define STR_NUM 1
int data[DATA_NUM] = {0, INT_MAX / 17, INT_MAX, INT_MIN, INT_MIN + 1,UINT_MAX / 17, INT_MAX / 17, UINT_MAX};
char *str[STR_NUM] = {"HELLO WORLD!"};
char out_str[100] = "";
void check_sprintf() {
    sprintf(out_str,"%d, %s\n",data[0],str[0]);
    check(strcmp(out_str,"0, HELLO WORLD!\n") == 0);

    sprintf(out_str,"%d, %s\n",data[1],str[0]);
    check(strcmp(out_str,"126322567, HELLO WORLD!\n") == 0);

    sprintf(out_str,"%d, %s\n",data[2],str[0]);
    check(strcmp(out_str,"2147483647, HELLO WORLD!\n") == 0);

    sprintf(out_str,"%d, %s\n",data[3],str[0]);
    check(strcmp(out_str,"-2147483648, HELLO WORLD!\n") == 0);

    sprintf(out_str,"%d, %s\n",data[4],str[0]);
    check(strcmp(out_str,"-2147483647, HELLO WORLD!\n") == 0);

    sprintf(out_str,"%d, %s\n",data[5],str[0]);
    check(strcmp(out_str,"252645135, HELLO WORLD!\n") == 0);

    sprintf(out_str,"%d, %s\n",data[6],str[0]);
    check(strcmp(out_str,"126322567, HELLO WORLD!\n") == 0);

    sprintf(out_str,"%d, %s\n",data[7],str[0]);
    check(strcmp(out_str,"-1, HELLO WORLD!\n") == 0);

    
}
int main() {
    check_sprintf();
    /*sprintf(out_str,"%d\n",data[0]);*/
    return 0;
}
