#include <common.h>
#include <cstdint>
#include <cstdio>
#include <memory/paddr.h>
#include <getopt.h>
#include <cpu/cpu.h>
#include <cpu/difftest.h>

void init_sdb();
void init_rand();
void init_log(const char *log_file);
void init_mem();
void init_difftest(char *ref_so_file, long img_size, int port);
// void init_disasm(const char *triple);


void welcome () {
  // Log("Trace: %s", MUXDEF(CONFIG_TRACE, ANSI_FMT("ON", ANSI_FG_GREEN), ANSI_FMT("OFF", ANSI_FG_RED)));
  // IFDEF(CONFIG_TRACE, Log("If trace is enabled, a log file will be generated "
  //       "to record the trace. This may lead to a large log file. "
  //       "If it is not necessary, you can disable it in menuconfig"));
  // Log("Build time: %s, %s", __TIME__, __DATE__);
  // printf("Welcome to YSYX-SOC!\n");
  // printf("For help, type \"help\"\n");
  assert(1);
}

#include <getopt.h>

void sdb_set_batch_mode();

static char *log_file = NULL;
static char *diff_so_file = NULL;
static char *img_file = NULL;
FILE *elf_file = NULL;
static int difftest_port = 1234;


extern void ftrace_init();
static int parse_args(int argc, char *argv[]) {
    const struct option table[] = {
        {"batch"    , no_argument      , NULL, 'b'},
        {"diff"     , required_argument, NULL, 'd'},
        {"port"     , required_argument, NULL, 'p'},
        {"log"      , required_argument, NULL, 'l'},
        {"elf"      , required_argument, NULL, 'e'}, // 参数是带有elf文件路径的字符串
        {0          , 0                , NULL,  0 },
    };
    int o;
    while ( (o = getopt_long(argc, argv, "-bhl:d:p:e:", table, NULL)) != -1) {
      switch (o) {
        case 'b': sdb_set_batch_mode(); break;
        case 'l': log_file = optarg; break;
        case 'p': sscanf(optarg, "%d", &difftest_port); break;
        case 'd': diff_so_file = optarg; break;
        case 'e': elf_file = fopen(optarg,"rb");ftrace_init(); break;
        case 1: img_file = optarg; return 0;
        default:
          printf("Usage: %s [OPTION...] IMAGE [args]\n\n", argv[0]);
          printf("\t-b,--batch              run with batch mode\n");
          printf("\t-d,--diff=REF_SO        run DiffTest with reference REF_SO\n");
          printf("\t-p,--port=PORT          run DiffTest with port PORT\n");
          printf("\t-l,--log=FILE           output log to FILE\n");
          printf("\t-e,--elf=ELF_FILE       Initialize ftrace \n");
          printf("\tIMG,IMG=IMG_FILE       Initialize img \n");
          printf("\n");
          exit(0);
      }
    }
    return 0;

}

/* @brief : 从.bin文件中读取指令
 * @return: 所有指令大小
 */
static long load_img (void) {
    if (img_file == NULL) {
      // Log ("No image is given. Use the default build-in image");
      return 4096;
    }
    FILE *fp = fopen (img_file, "rb");
    Assert (fp, "Can not open '%s'", img_file);

    fseek (fp, 0, SEEK_END);
    long size = ftell (fp);

    // Log ("The image is %s, size = %ld", img_file, size);

    fseek (fp, 0, SEEK_SET);
    int ret = fread (guest_to_host (RESET_VECTOR), size, 1, fp);    // 将image的内容存入地址中
    assert (ret == 1);

    fclose (fp);
    return size;
}

static const uint32_t img [] = {
  0x800002b7,  // lui t0,0x80000
  0x0002a023,  // sw  zero,0(t0)
  0x0002a503,  // lw  a0,0(t0)
  0x00100073,  // ebreak (used as nemu_trap)
};

static void restart() {
  /* Set the initial program counter. */
  cpu.pc = RESET_VECTOR;

  /* The zero register is always 0. */
  cpu.gpr[0] = 0;
}

/* @brief : 初始化指令集架构
 * @return: NONE
 */
void init_isa() {
  /* Load built-in image. */
  memcpy(guest_to_host(RESET_VECTOR), img, sizeof(img));

  /* Initialize this virtual computer system. */
  restart();
}

void init_monitor (int argc, char *argv[]) {

    // 分析参数
    parse_args (argc, argv);
    /* Set random seed. */
    init_rand();

    /* Open the log file. */
    init_log (log_file);

    // 初始化内存
    init_mem();

    init_isa();

    long img_size = load_img();    // 如果没有img_file,将使用默认的img

    // 如果是作为ref,则会更新img_file为dut执行的img
    // init_difftest(diff_so_file,img_size,difftest_port);

    // init_sdb();
    // IFDEF(CONFIG_ITRACE, init_disasm("riscv32""-pc-linux-gnu"));
    welcome();
}
