#ifndef __MEMORY_PADDR_H__
#define __MEMORY_PADDR_H__

#include <common.h>


#define PMEM_LEFT  ((paddr_t)CONFIG_MBASE)
#define PMEM_RIGHT ((paddr_t)CONFIG_MBASE + CONFIG_MSIZE - 1)
#define RESET_VECTOR (PMEM_LEFT + 0)


uint8_t* guest_to_host(paddr_t paddr);
uint8_t* mrom_to_host(paddr_t paddr);
paddr_t host_to_guest(uint8_t *haddr);

static inline bool in_pmem(paddr_t addr) {
  return addr - CONFIG_MBASE < CONFIG_MSIZE;
}

static inline bool in_mrom(paddr_t addr) {
  return addr - 0x20000000 < 0x1000;
}

static inline bool in_flash(paddr_t addr) {
  return addr  < CONFIG_MSIZE;
}

word_t pmem_read(paddr_t paddr, int len);
void pmem_write(paddr_t paddr,  int len,word_t data);

void init_mem(void);
word_t paddr_read(paddr_t addr, int len);
void paddr_write(paddr_t addr, int len, word_t data);

void print_pmem(paddr_t paddr);
uint32_t mrom_addr_read(uint32_t addr);
uint32_t flash_addr_read(uint32_t addr);


#endif
