module apb_delayer (
    input         clock,
    input         reset,
    input  [31:0] in_paddr,
    input         in_psel,
    input         in_penable,
    input  [ 2:0] in_pprot,
    input         in_pwrite,
    input  [31:0] in_pwdata,
    input  [ 3:0] in_pstrb,
    output        in_pready,
    output [31:0] in_prdata,
    output        in_pslverr,

    output [31:0] out_paddr,
    output        out_psel,
    output        out_penable,
    output [ 2:0] out_pprot,
    output        out_pwrite,
    output [31:0] out_pwdata,
    output [ 3:0] out_pstrb,
    input         out_pready,
    input  [31:0] out_prdata,
    input         out_pslverr
);

  localparam STATE_IDLE = 4'd0;
  localparam STATE_START_TRANS = 4'd1;
  localparam STATE_CAL_DELAY = 4'd2;
  localparam STATE_DELAY = 4'd3;
  reg [31:0] counter;
  reg [ 3:0] state;
  reg        pready;
  reg [31:0] prdata;
  reg        pslverr;


  //到了就立马传送
  assign out_paddr   = in_paddr;
  assign out_psel    = in_psel;
  assign out_penable = in_penable;
  assign out_pprot   = in_pprot;
  assign out_pwrite  = in_pwrite;
  assign out_pwdata  = in_pwdata;
  assign out_pstrb   = in_pstrb;

  //延迟传送
  assign in_pready  = pready;
  assign in_prdata  = prdata;
  assign in_pslverr = pslverr;

  //=====================================================================================
  //状态机切换逻辑
  //=====================================================================================
  always @(posedge clock) begin
    if (reset) begin
      counter <= 0;
      state   <= STATE_IDLE;
    end else if (in_psel && ~in_pready) begin
      case (state)
        STATE_IDLE: begin
          state <= STATE_START_TRANS;
        end

        STATE_START_TRANS: begin
          if (out_pready) begin  //trans_ok
            state <= STATE_CAL_DELAY;
          end
        end

        STATE_CAL_DELAY: begin
          state <= STATE_DELAY;
        end
        //state_dealy: 见后
        default: begin
          state <= state;
        end
      endcase
    end
  end

  always @(posedge clock) begin
    if (state == STATE_IDLE) begin
      counter <= 0;
    end
  end

  //=====================================================================================
  // STATE_START_TRANS
  // 功能: 记录发送信号给从设备，到回复的时间
  //=====================================================================================

  always @(posedge clock) begin
    if (reset) begin
      counter <= 0;
    end else if (state == STATE_START_TRANS) begin
      counter <= counter + 1;
      // 及时得到数据
      prdata  <= out_prdata;
      pslverr <= out_pslverr;
    end
  end

  //=====================================================================================
  // STATE_CAL_DELAY
  // 功能: 得到周期数k
  //=====================================================================================
  reg [31:0] k;  //周期数
  always @(posedge clock) begin
    if (state == STATE_CAL_DELAY) begin
      if (counter >= 1) begin
        k <= counter - 1; //1是进入到该周期消耗的clk
        counter <= 1;     //已经延迟了1个周期了
      end else begin
        $display("apb_delayer环节有问题,不可能小于1周期,状态转换就需要1周期");
      end
    end
  end

  //=====================================================================================
  // STATE_DELAY: 延迟k*r个周期
  //=====================================================================================
  reg [31:0] counter_cycle;
  localparam r = 4'd2 - 4'd1; //得到下游传回的通信时，已经相当于延迟了一个周期，故减1

  always @(posedge clock) begin
    if (reset) begin
      counter_cycle <= 0;
    end else if (state == STATE_DELAY) begin
      if (counter_cycle < k) begin  //循环计数r
        if (counter < r) begin
          counter <= counter + 1;
        end else begin
          counter <= 1;
          counter_cycle <= counter_cycle + 1;
        end
      end else begin //计数完毕
        pready <= 1'b1;  //持续一个周期
        state <= STATE_IDLE;
        k <= 0;
        counter_cycle <= 0;
      end
    end else begin
      pready <= 1'b0;
    end
  end

endmodule
