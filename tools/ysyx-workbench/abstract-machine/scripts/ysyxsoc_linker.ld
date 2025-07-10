ENTRY(_start)

MEMORY {
    mrom  : ORIGIN = 0x20000000, LENGTH = 4K
    flash : ORIGIN = 0x30000000, LENGTH = 4M
    sram  : ORIGIN = 0x0f000000, LENGTH = 8K
    psram : ORIGIN = 0x80000000 + 4, LENGTH = 16M -4
    sdram : ORIGIN = 0xa0000000, LENGTH = 16M
}

SECTIONS {
    /* _pmem_start and _entry_offset are defined in LDFLAGS */

    /* 保存了程序的可执行指令*/

    .entry : {
        _entry_start = .;
        *(entry)
        *(.entry)
        _entry_end = .;
    } > flash

    /* 二级加载，存入sram,在sram中实现将text,data的数据从flash移到sdram*/
    .ssbl : {
        _ssbl_MA = LOADADDR(.ssbl); /* 在flash中的地址 */
        _ssbl_SA = .; /*在sram中的地址 */
        *(.ssbl)
        _ssbl_end = .;
    } > sdram AT > flash

    .text : {
        _text_MA = LOADADDR(.text); /* 在flash中的地址 */
        _text_SA = .; /*在sram中的地址 */
        *(.text*)
        _text_end = .;
    } > sdram AT> flash

    .rodata : {
        _rodata_MA = LOADADDR(.rodata); /* 在flash中的地址 */
        _rodata_SA = .; /*在sram中的地址 */
        *(.rodata*)
        *(.srodata*)
        _rodata_end = .;
    } > sdram AT> flash


    .data : {
        _data_MA = LOADADDR(.data); /* 在 flash 中的地址 */
        _data_SA = .;               /* 在 sdram 中的起始地址 */
        *(.data)
        *(.data.*)
        *(.sdata*)
        _data_end = .;
    } >sdram AT> flash

    .bss : {
        _bss_start = .;
        *(.bss*)
        *(.sbss*)
        *(.scommon)
        _bss_end = .;
    } > sdram

    /*=========================================================*/
    /*====================heap与stack管理======================*/
    /*=========================================================*/
    /* stack：放到 SDRAM 顶部 */
    _stack_pointer = ORIGIN(sdram) + LENGTH(sdram);
    _stack_top = _stack_pointer - 0x200000; /* 2MB 栈空间 */

    /* heap：放在 .bss 结束之后 */
    . = _bss_end;
    _heap_start = ALIGN(0x4);
    _heap_end = _stack_top; /* 堆最大到栈底，避免重叠 */
}

    /* . = _ssbl_end;
    _stack_top = ALIGN(0x8);
    _stack_pointer = ORIGIN(sdram) + LENGTH(sdram); */

    /* . = _bss_end;  .bss的最后地址 */
    /* _heap_start = ALIGN(0x10); .代表的地址是.data,.bss分配完后的一个地址,不用担心重叠问题 */
    /* _heap_end   = _heap_start + 0x10000; [>在trm.c中有用到<] */


/*[> 仅只用了ram的版本<]*/
/*SECTIONS {*/
    /*[> 保存了程序的可执行指令<]*/
    /*.entry : {*/
        /*_entry_start = .;*/
        /**(entry)*/
        /**(.entry)*/
        /*_entry_end = .;*/
    /*} > ram*/


    /*.text : {*/
        /*_text_MA = LOADADDR(.text); [> 在flash中的地址 <]*/
        /*_text_SA = .; [>在sram中的地址 <]*/
        /**(.text*)*/
    /*} > ram*/

    /*.rodata : {*/
        /*_rodata_MA = LOADADDR(.rodata); [> 在flash中的地址 <]*/
        /*_rodata_SA = .; [>在sram中的地址 <]*/
        /**(.rodata*)*/
        /**(.srodata*)*/
        /*rodata_end = .;*/
    /*} > ram*/


    /*.data : {*/
        /*_data_MA = LOADADDR(.data); [> 在 flash 中的地址 <]*/
        /*_data_SA = .;               [> 在 sdram 中的起始地址 <]*/
        /**(.data)*/
        /**(.data.*)*/
        /**(.sdata*)*/
        /*data_end = .;*/
    /*} > ram*/

    /*.bss : {*/
        /*_bss_start = .;*/
        /**(.bss*)*/
        /**(.sbss*)*/
        /**(.scommon)*/
        /*_bss_end = .;*/
    /*} > ram*/

    /*[>=========================================================<]*/
    /*[>====================heap与stack管理======================<]*/
    /*[>=========================================================<]*/
    /*[>栈空间分配到sram中<]*/
    /*. = _bss_end; [>.bss的最后地址<]*/
    /*_heap_start = ALIGN(0x10); [>.代表的地址是.data,.bss分配完后的一个地址,不用担心重叠问题<]*/
    /*_heap_end   = _heap_start + 0x800; [>在trm.c中有用到<]*/

    /*. = _heap_end;*/
    /*_stack_top = ALIGN(0x10);*/
    /*_stack_pointer = _stack_top + 0x800;*/

/*}*/

