#include <klib.h>
#include <klib-macros.h>
#include <stdint.h>

#if !defined(__ISA_NATIVE__) || defined(__NATIVE_USE_KLIB__)

size_t strlen (const char *s) {
    size_t count = 0;//计数
    while (*s != '\0')
    {
        count++;//当它的字符不等于'\0'时，计数加一
        s++;//再往下一个字符找
    }
    return count;
    /*panic ("Not implemented");*/
}

char *strcpy (char *dst, const char *src) {
    if (dst == NULL || src == NULL)
        return NULL;
    char *ret = dst;
    while ((*dst++=*src++)!='\0');
    return ret;
    /*panic ("Not implemented");*/
}

char *strncpy (char *dst, const char *src, size_t n) {
    panic ("Not implemented");
}

char *strcat (char *dst, const char *src) {
    char* temp = dst;
    while (*temp != '\0') temp++;
    while ((*temp++ = *src++) != '\0');

    return dst;
}

int strcmp (const char *s1, const char *s2) {
    while (s1[0] != '\0' && s2[0] != '\0') {
        if (s1[0] == s2[0]) {
            s1+=1;
            s2+=1;
        }else if (s1[0] > s2[0]) {
            return 1;
        }else if (s1[0] < s2[0]) {
            return -1;
        }
    }
    if (s1[0] != '\0') 
        return 1;
    else if (s2[0] != '\0')
        return -1;
    else
        return 0;
    /*panic ("Not implemented");*/
}

int strncmp (const char *s1, const char *s2, size_t n) {
    for (int i = 0; (s1[0] != '\0' && s2[0] != '\0') && i < n; i ++) {
        if (s1[0] == s2[0]) {
            s1+=1;
            s2+=1;
        }else if (s1[0] > s2[0]) {
            return 1;
        }else if (s1[0] < s2[0]) {
            return -1;
        }
    }
    if (s1[0] != '\0' && s2[0] != '\0') {
        return 0;
    }else if (s1[0] != '\0') 
        return 1;
    else if (s2[0] != '\0')
        return -1;
    else
        return 0;

    /*panic ("Not implemented");*/
}

void *memset (void *s, int c, size_t n) {
    if (s == NULL) 
        return NULL;
    char *c_s = (char *)s;
    while (n--) {
        *c_s =  c;
        c_s ++;
    }
    return s;
    /*panic ("Not implemented");*/
}

void *memmove (void *dst, const void *src, size_t n) {
    panic ("Not implemented");
}

void *memcpy (void *out, const void *in, size_t n) {
    //没实现 out不够大报警的情况
    if (out == NULL || in == NULL) { return NULL; }
    char *v_dst = (char *)out;
    char *v_src = (char *)in;

    while (n--) {
        *v_dst = *v_src;
        v_dst++;
        v_src++;
    }

    return out;
    /*panic ("Not implemented");*/
}

int memcmp (const void *s1, const void *s2, size_t n) {
    unsigned char *ps1 = (unsigned char *)s1;
    unsigned char *ps2 = (unsigned char *)s2;
    while (ps1[0] != '\0' && ps2[0] != '\0' && n != 0) {
        n--;
        if (ps1[0] == ps2[0]) {
            ps1+=1;
            ps2+=1;
        }else if (ps1[0] > ps2[0]) {
            return 1;
        }else if (ps1[0] < ps2[0]) {
            return -1;
        }
    }
    if (n > 0) {
        printf("n = %ld\n",n);
        if (ps1[0] != '\0')
            return 1;
        else if (ps2[0] != '\0')
            return -1;
    }
    return 0;
    /*panic ("Not implemented");*/
}

#endif
