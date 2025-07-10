#include <cpu/cpu.h>
#include <cpu/difftest.h>
#include <cpu/decode.h>
#include <locale.h>
#include <stdio.h>
#include "../monitor/sdb/watchpoint.h"
#include "debug.h"
#include "utils.h"
#include <sim_v.h>


/* The assembly code of instructions executed is only output to the screen
 * when the number of instructions executed is less than this value.
 * This is useful when you use the `si' command.
 * You can modify this value as you want.
 */
#define MAX_INST_TO_PRINT 50   // 最多显示到屏幕的指令数

riscv32_CPU_state cpu = {};
uint64_t g_nr_guest_inst = 0;
static uint64_t g_timer = 0; // unit: us
static bool g_print_step = false;

void device_update();

typedef struct queue_node {
    int     status; // 1:正常执行， 0: 执行出错
    char    buf[128];
    struct queue_node *next;
}Iringbuf_Node;

typedef struct queue {
    Iringbuf_Node *front;
    Iringbuf_Node *rear;
    int count;
}Iringbuf;

Iringbuf *init_queue() {
    Iringbuf *q=(Iringbuf*)malloc(sizeof(Iringbuf));
    if(q==NULL){    //建立失败，退出
        Assert(0, "创建Iringbuf队列失败");
    }
    //头尾结点均赋值NULL
    q->front=NULL;
    q->rear=NULL;
    q->count = 0;
    return q;
}

static Iringbuf *iring_queue = NULL;
// 队列进入-用于iringbuf
void queue_push (Iringbuf *q, int status, const char *log_buf) {
    Iringbuf_Node *n   = (Iringbuf_Node *)malloc (sizeof (Iringbuf_Node));
    n->status = status;
    n->next   = NULL;
    strcpy(n->buf,log_buf);
    q->count ++;
    if (q->front == NULL) {
        q->front = n;
        q->rear  = n;
    }
    else {
        q->rear->next = n;
        q->rear       = n;
    }
}
// 队列弹出-用于iringbuf
void queue_pop(Iringbuf *q){
    Iringbuf_Node *n=q->front;
    if(q->front == NULL){
        return;
    }
    if(q->front==q->rear){
        q->front=NULL;  //只有一个元素时直接将两端指向制空即可
        q->rear=NULL;
        q->count --;
        free(n);        //记得归还内存空间
    }else{
        q->front=q->front->next;
        q->count --;
        free(n);
    }
}
void print_queue(void) {
  // 输出出错指令和之前的指令
  while (iring_queue->front != NULL) {
      if (iring_queue->front->status == 1) {
        printf("    %s\n",iring_queue->front->buf);
        queue_pop(iring_queue);
      }else {
        printf("--> %s\n",iring_queue->front->buf);
        queue_pop(iring_queue);
      }
  }

}

static void trace_and_difftest(Decode *_this, vaddr_t dnpc) {
#ifdef CONFIG_ITRACE_COND
  log_write("%s\n", _this->logbuf);
#endif
  if (g_print_step) { IFDEF(CONFIG_ITRACE, puts(_this->logbuf)); }
  IFDEF(CONFIG_DIFFTEST, difftest_step(_this->pc, dnpc));

// iringbuf相关
  if (iring_queue->count < 8) {  // 只保存最近的八条指令
    queue_push(iring_queue,1,_this->logbuf);
  }else {
    queue_pop(iring_queue);
    queue_push(iring_queue,1,_this->logbuf);
  }
#ifdef CONFIG_WATCHPOINT    // 检查监视点的代码块
  WP *head = NULL;
  head     = get_head();
  uint8_t trigger_times = 0;
  bool  success = true;
  if (head->next != NULL) {
      head = head->next;
      while (head != NULL) {
          head->cur_value = expr(head->str, &success);
          if (head->cur_value != head->old_value) {
              Log("触发来监视点 %d : %s",head->NO, head->str);
              printf("Old value = %lu\n", head->old_value);
              printf("New value = %lu\n", head->cur_value);
              head->old_value = head->cur_value;
              trigger_times++;
          }
          head = head->next;
      }
  }
  if (trigger_times > 0) {
      npc_state.state = NPC_STOP;
  }
#endif
}

static void exec_once (Decode *s) {
  // inst_clk_cycle(s); //执行一个指令周期,执行完更新一次
  s->pc = cpu.pc; //当前pc,即将执行的指令的pc
#ifdef CONFIG_ITRACE  //暂时不实现,s是Decode
  char *p       = s->logbuf;
  p             += snprintf (p, sizeof (s->logbuf), FMT_WORD ":", s->pc); //将当前pc的值写入logbuf
  int      ilen = 4;
  int      i;
  uint8_t *inst = (uint8_t *)&s->isa.inst.val;
  for (i = ilen - 1; i >= 0; i--) {
      p += snprintf (p, 4, " %02x", inst[i]); //写入指令
  }
  int ilen_max  = MUXDEF (CONFIG_ISA_x86, 8, 4);
  int space_len = ilen_max - ilen;
  if (space_len < 0) space_len = 0;
  space_len = space_len * 3 + 1;
  memset (p, ' ', space_len);
  p += space_len;

  // void disassemble (char *str, int size, uint64_t pc, uint8_t *code, int nbyte);
  // disassemble (p, s->logbuf + sizeof (s->logbuf) - p,
  //              (uint64_t)(s->pc), (uint8_t *)&s->isa.inst.val,
  //              ilen);
#endif
}

static void execute (uint64_t n) {
  Decode s;
  for (; n > 0; n--) { //执行n次
      exec_once (&s);
      g_nr_guest_inst++;//已执行指令次数
      trace_and_difftest (&s, cpu.pc); ///踪迹，记录程序的执行过程
      if (npc_state.state != NPC_RUNNING) break; //遇到ebreak时，会将state设置为NPC_STOP
  }
}

static void statistic () {
#define NUMBERIC_FMT MUXDEF (CONFIG_TARGET_AM, "%", "%'") PRIu64
  Log ("host time spent = " NUMBERIC_FMT " us,"  "%fs" , g_timer, g_timer/1000000.0);
  Log ("total guest instructions = " NUMBERIC_FMT, g_nr_guest_inst);
  if (g_timer > 0) {
      Log ("simulation frequency = " NUMBERIC_FMT " inst/s",
           g_nr_guest_inst * 1000000 / g_timer);
  }
  else
      Log ("Finish running in less than 1 us and can not calculate the simulation "
           "frequency");
}

void assert_fail_msg () {
  // isa_reg_display();

  // 程序出错,将错误的指令写入iringbuf
  char cur_pc[128];
  snprintf (cur_pc, 128, FMT_WORD ":", cpu.pc); //将当前pc的值写入logbuf

  queue_push(iring_queue, 0, cur_pc);
  print_queue();
  statistic();
}

/* Simulate how the CPU works. */
void cpu_exec (uint64_t n) {
  g_print_step = (n < MAX_INST_TO_PRINT);
  iring_queue = init_queue();
  switch (npc_state.state) {
      case NPC_END:
      case NPC_ABORT:
          printf ("Program execution has ended. To restart the program, exit NPC and "
                  "run again.\n");
          return;
      default: npc_state.state = NPC_RUNNING;
  }

  uint64_t timer_start = get_time();

  execute (n);

  uint64_t timer_end = get_time();
  g_timer            += timer_end - timer_start;

  switch (npc_state.state) {
      case NPC_RUNNING: npc_state.state = NPC_STOP; break;

      case NPC_END:
      case NPC_ABORT:
          Log ("npc: %s at pc = " FMT_WORD,
              (npc_state.state == NPC_ABORT
                   ? ANSI_FMT ("ABORT", ANSI_FG_RED)
                   : (npc_state.halt_ret == 0 ? ANSI_FMT ("HIT GOOD TRAP", ANSI_FG_GREEN)
                                               : ANSI_FMT ("HIT BAD TRAP", ANSI_FG_RED))),
              npc_state.halt_pc);
          // fall through
      case NPC_QUIT: statistic();
  }
}
