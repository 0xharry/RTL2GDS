#include <memory/host.h>
#include <cpu/cpu.h>
#include <memory/paddr.h>
#include <common.h>

static uint8_t pmem[CONFIG_MSIZE] = {}; //物理内存

/* @brief : 将客户地址转换成主机地址
 * @param :
 *      paddr:  物理内存地址
 * @return: 主机内存地址
 */
uint8_t* guest_to_host(paddr_t paddr) {
    return pmem + paddr - CONFIG_MBASE;
}

uint8_t* flash_to_host(paddr_t paddr) {
    return pmem + paddr;
}
uint8_t* mrom_to_host(paddr_t paddr) {
    return pmem + paddr - 0x20000000;
}

paddr_t host_to_guest(uint8_t *haddr) { return haddr - pmem + CONFIG_MBASE; }



/* @brief : 读物理内存
 * @param :  paddr: 物理内存地址
 * @param :  len  : 读取内存长度(一般为4)
 * @return: 返回内存读取结果
 */
word_t pmem_read(paddr_t paddr, int len) {
    word_t ret =  host_read(guest_to_host(paddr),len);
    return ret;
}


void pmem_write(paddr_t addr, int len, word_t data) {
  host_write(guest_to_host(addr), len, data);
}

void print_pmem(paddr_t paddr) {
    printf("0x%x\n",host_read( pmem + paddr - 0x30000000,4));
}



static void out_of_bound(paddr_t addr) {
    printf(ANSI_FMT("address = " FMT_PADDR " is out of bound of pmem [" FMT_PADDR ", " FMT_PADDR "] at pc =" FMT_WORD"\n",ANSI_FG_RED),addr, PMEM_LEFT, PMEM_RIGHT,cpu.pc);
    extern void assert_fail_msg();
    assert_fail_msg();
    extern void sim_exit();
    sim_exit();
    //npc_state.state = NPC_ABORT;
    assert(0);
    //panic("address = " FMT_PADDR " is out of bound of pmem [" FMT_PADDR ", " FMT_PADDR "] at pc =" FMT_WORD,addr, PMEM_LEFT, PMEM_RIGHT,cpu.pc);
}



word_t paddr_read(paddr_t addr, int len) {
  if (likely(in_pmem(addr))) return pmem_read(addr, len);
  Log("paddr_read():");
  out_of_bound(addr);
  return 0;
}



void paddr_write(paddr_t addr, int len, word_t data) {
  if (likely(in_pmem(addr))) { pmem_write(addr, len, data); return; }
  Log("paddr_write():");
  out_of_bound(addr);
}


void init_mem(void) {
    // Log("physical memory area [" FMT_PADDR ", " FMT_PADDR "]", PMEM_LEFT, PMEM_RIGHT);
}


uint32_t mrom_addr_read(uint32_t addr) {
    if (likely(in_mrom(addr))) {
        word_t ret =  host_read(mrom_to_host(addr),4);
        //printf("read inst 0x%x at 0x%x\n",ret,addr);
        return ret;
    }
    out_of_bound(addr);
    return 0;
}

uint32_t flash_addr_read(uint32_t addr) {
    if (likely(in_flash(addr))) { //0x3000_0000在传入falsh时会被截断为{8'b0, in_paddr[23:2], 2'b0}
        word_t ret =  host_read(flash_to_host(addr),4);
        // printf("read inst %08x at %08x\n",ret,addr + 0x30000000);
        return ret;
    }
    Log("flash_addr_read():");
    out_of_bound(addr);
    return 0;
}

