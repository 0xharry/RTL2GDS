module sdram (
    input        clk,
    input        cke,
    input        cs,
    input        ras,
    input        cas,
    input        we,
    input [12:0] a,
    input [ 1:0] ba,
    input [ 1:0] dqm,
    inout [15:0] dq
);
  localparam CMD_W                 = 4;
  localparam CMD_NOP               = 4'b0111;//7
  localparam CMD_TERMINATE         = 4'b0110;
  localparam CMD_READ              = 4'b0101;//5
  localparam CMD_WRITE             = 4'b0100;//4
  localparam CMD_ACTIVE            = 4'b0011;//3
  localparam CMD_PRECHARGE         = 4'b0010;//2
  localparam CMD_REFRESH           = 4'b0001;//1
  localparam CMD_LOAD_MODE         = 4'b0000;//0

  localparam SDRAM_BANKS           = 4;//bank的数量
  localparam SDRAM_ROW_W           = 14;
  //assign dq = 16'bz;



  wire [CMD_W-1:0] cmd = {cs, ras, cas, we};  //传来指令
  wire internal_clk = clk & cke;  //cke为1时，时钟才有效

  //===========================================
  //读/写
  //=========================================
  reg is_read;
  reg [15:0] rdata;

  wire is_write = (cmd == CMD_WRITE) | write_burst_start;
  //===========================================
  //行地址+列地址+ 当前打开的bank    访存
  //=========================================
  reg [SDRAM_BANKS-1:0] row_open_q;                     //代表对应bank中存在正处于活动的行,bool
  reg [12           :0] active_row_q[0     :SDRAM_BANKS-1];  //对应于活动的行的行数,addr
  reg [8            :0] addr_col;// 列地址 相当于{aw/araddr[9:2],1'b0}
  reg [1            :0] open_bank [0: 7];

  // 16MB存储器
  reg [15:0] mem[0:24'hFF_FFFF];
  //===========================================
  //突发传输相关相关
  //=========================================
  reg [2:0] burst_counter;//从2开始传输，因为需要等待CL个周期
  reg write_burst_start;

  //===========================================
  //mode相关
  //burst_length: 000: 1次(2 Byte),
  //              001: 2次(4 Byte),
  //              010: 4次(8 Byte),
  //              011: 8次(16Byte),
  //              100,...保留
  //=========================================
  reg [12:0] mode_reg;
  wire [2:0] burst_length = mode_reg[2:0]; //默认为001,4字节
  wire [2:0] CAS  = mode_reg[6:4];

  reg  [2:0] burst_times;
  reg  [2:0] done_burst_times;

  reg [15:0] queue[0:1];
  reg  [1:0] queue_counter;
  always @(posedge internal_clk) begin
    case (cmd)
      CMD_LOAD_MODE: begin
        mode_reg <= a;
      end
      CMD_ACTIVE: begin
        row_open_q <= 4'b1 << ba; //一次只有一个bank打开，通过移位实现
        open_bank[0] <= ba;
        active_row_q[ba] <= a;//激活某一bank中的行的地址
      end
      CMD_READ: begin
        is_read <= 1'b1;
        queue_counter <= 0;
        queue[0] <= mem[{{active_row_q[ba]},ba,a[8:0]}] & {{8{~dqm[1]}},{8{~dqm[0]}}};
        queue[1] <= mem[{{active_row_q[ba]},ba,(a[8:0]+9'b1)}] & {{8{~dqm[1]}},{8{~dqm[0]}}};

        rdata <= queue[queue_counter[0]];
      end
      CMD_WRITE: begin
        write_burst_start <= 1;
        burst_counter <= 3'd0;
        //mem[{{active_row_q[ba]},ba,a[8:0]}] <= dq & {{8{~dqm[1]}},{8{~dqm[0]}}};
        open_bank[0] <= ba;
        case (dqm)
          2'b00: begin
            mem[{{active_row_q[ba]}, ba, a[8:0]}] <= dq;
          end
          2'b01: begin
            mem[{{active_row_q[ba]}, ba, a[8:0]}] <= {dq[15:8],mem[{{active_row_q[ba]}, ba, a[8:0]}][7:0]};
          end
          2'b10: begin
            mem[{{active_row_q[ba]}, ba, a[8:0]}] <= {mem[{{active_row_q[ba]}, ba, a[8:0]}][15:8],dq[7:0]};
          end
          2'b11: begin
            //不写
          end
        endcase
        addr_col <= a[8:0] + 1;
      end
      CMD_NOP: begin
        if (queue_counter <= 1) begin
          queue_counter <= queue_counter +1;
          rdata <= queue[queue_counter[0]];
        end else if (write_burst_start) begin
          if (is_write) begin
            if(burst_counter < burst_length) begin
              burst_counter <= burst_counter + 1;
              case (dqm)
                2'b00: begin
                  mem[{{active_row_q[open_bank[0]]}, open_bank[0], addr_col}] <= dq;
                end
                2'b01: begin
                  mem[{{active_row_q[open_bank[0]]}, open_bank[0], addr_col}] <= {dq[15:8],mem[{{active_row_q[open_bank[0]]}, open_bank[0], addr_col}][7:0]};
                end
                2'b10: begin
                  mem[{{active_row_q[open_bank[0]]}, open_bank[0], addr_col}] <= {mem[{{active_row_q[open_bank[0]]}, open_bank[0], addr_col}][15:8],dq[7:0]};
                end
                2'b11: begin
                  //不写
                end
              endcase
            end else begin
              burst_counter <= 3'b0;
              write_burst_start <= 0;
            end
          end
        end else begin
          is_read <= 0; //结束read;
        end
      end
      default: begin
        //CMD_PRECHARGE,CMD_REFRESH,指令与电气相关，不需实现
        //CMD_TERMINATE控制器不会发送
      end
    endcase
  end
  assign dq = is_read ? rdata : 16'bz;

endmodule
