module axi4_delayer (
    input clock,
    input reset,

    output        in_arready,
    input         in_arvalid,
    input  [ 3:0] in_arid,
    input  [31:0] in_araddr,
    input  [ 7:0] in_arlen,
    input  [ 2:0] in_arsize,
    input  [ 1:0] in_arburst,
    input         in_rready,
    output        in_rvalid,
    output [ 3:0] in_rid,
    output [31:0] in_rdata,
    output [ 1:0] in_rresp,
    output        in_rlast,
    output        in_awready,
    input         in_awvalid,
    input  [ 3:0] in_awid,
    input  [31:0] in_awaddr,
    input  [ 7:0] in_awlen,
    input  [ 2:0] in_awsize,
    input  [ 1:0] in_awburst,
    output        in_wready,
    input         in_wvalid,
    input  [31:0] in_wdata,
    input  [ 3:0] in_wstrb,
    input         in_wlast,
    in_bready,
    output        in_bvalid,
    output [ 3:0] in_bid,
    output [ 1:0] in_bresp,

    input         out_arready,
    output        out_arvalid,
    output [ 3:0] out_arid,
    output [31:0] out_araddr,
    output [ 7:0] out_arlen,
    output [ 2:0] out_arsize,
    output [ 1:0] out_arburst,
    output        out_rready,
    input         out_rvalid,
    input  [ 3:0] out_rid,
    input  [31:0] out_rdata,
    input  [ 1:0] out_rresp,
    input         out_rlast,
    input         out_awready,
    output        out_awvalid,
    output [ 3:0] out_awid,
    output [31:0] out_awaddr,
    output [ 7:0] out_awlen,
    output [ 2:0] out_awsize,
    output [ 1:0] out_awburst,
    input         out_wready,
    output        out_wvalid,
    output [31:0] out_wdata,
    output [ 3:0] out_wstrb,
    output        out_wlast,
    out_bready,
    input         out_bvalid,
    input  [ 3:0] out_bid,
    input  [ 1:0] out_bresp
);

  //=====================================================================================
  // 及时发送的数据，发送给AXI4子设备
  //=====================================================================================
  assign out_arvalid = in_arvalid;
  assign out_arid = in_arid;
  assign out_araddr = in_araddr;
  assign out_arlen = in_arlen;
  assign out_arsize = in_arsize;
  assign out_arburst = in_arburst;
  assign out_rready = in_rready;


  assign out_awvalid = in_awvalid;
  assign out_awid = in_awid;
  assign out_awaddr = in_awaddr;
  assign out_awlen = in_awlen;
  assign out_awsize = in_awsize;
  assign out_awburst = in_awburst;

  assign out_wvalid = in_wvalid;
  assign out_wdata = in_wdata;
  assign out_wstrb = in_wstrb;
  assign out_wlast = in_wlast;
  assign out_bready = in_bready;

  //=====================================================================================
  // 需要经过延时处理再发送的数据
  //=====================================================================================
  localparam STATE_IDLE = 4'd0;
  localparam STATE_START_TRANS = 4'd1;
  localparam STATE_CAL_DELAY = 4'd2;
  localparam STATE_DELAY = 4'd3;

  reg [31:0] counter;
  reg [31:0] k_r[0:7]; //计算各个节点的延迟时间
  reg [ 3:0] state_r;
  reg [ 3:0] state_w;

  //reg        delay_arready;
  reg        delay_rvalid;
  reg [ 3:0] delay_rid[0:7];
  reg [31:0] delay_rdata[0:7];
  reg [ 1:0] delay_rresp[0:7];
  reg        delay_rlast;
  reg [31:0] delay_rdata_t;
  reg [ 1:0] delay_rresp_t;
  reg [ 3:0] delay_rid_t;

  reg        delay_bvalid;
  reg [ 3:0] delay_bid;
  reg [ 1:0] delay_bresp;


  assign in_arready = out_arready; //这里不做延迟处理，不会影响最后的结果
  assign in_rvalid = delay_rvalid;
  assign in_rid = delay_rid_t;
  assign in_rdata = delay_rdata_t;
  assign in_rresp = delay_rresp_t;
  assign in_rlast = delay_rlast;

  assign in_awready = out_awready; //这里不做延迟处理，不会影响最后的结果
  assign in_wready = out_wready; //这里不做延迟处理，不会影响最后的结果
  assign in_bvalid = delay_bvalid;
  assign in_bid = delay_bid;
  assign in_bresp = delay_bresp;



  //assign in_awready = out_awready;
  //assign in_wready = out_wready;
  //assign in_bvalid = out_bvalid;
  //assign in_bid = out_bid;
  //assign in_bresp = out_bresp;

  //=====================================================================================
  //状态机切换逻辑: READ通道
  //=====================================================================================
  reg [2:0] rvalid_times;  //一次通信，rvalid的发送次数
  always @(posedge clock) begin
    if (reset) begin
      state_r <= STATE_IDLE;
      rvalid_times <= 0;
    end else begin
      case (state_r)
        //-------------------------------------
        //STATE_IDLE: 遇到ARREADY时切换状态
        //------------------------------------
        STATE_IDLE: begin
          if (in_arvalid) begin
            state_r <= STATE_START_TRANS;
          end
        end
        //------------------------------------------------
        // STATE_START_TRANS: 遇到rvalid & rlast时切换状态
        //------------------------------------------------
        STATE_START_TRANS: begin
          if (out_rvalid) begin
            k_r[rvalid_times] <= counter;
            if (out_rlast) begin
              counter <= 1;
              state_r <= STATE_DELAY;
              // 这里不对rvalid_times+1,因为rvalid_times从0开始有效
            end else begin
              state_r <= state_r;
              rvalid_times <= rvalid_times + 1;
            end
          end
        end
        //-------------------------------------------
        // STATE_CAL_DELAY: 计算延迟时间k
        //-------------------------------------------
        STATE_CAL_DELAY: begin
          state_r <= STATE_DELAY;
        end
        //-------------------------------------------
        // STATE_DELAY: 结束后通过后续行为切换状态
        //-------------------------------------------
        STATE_DELAY: begin
          if (delay_rlast) begin
            state_r <= STATE_IDLE;
          end
        end
        default: begin
        end
      endcase
    end
  end


  //=====================================================================================
  // STATE_IDLE
  //=====================================================================================

  always @(posedge clock) begin
    if (reset) begin
    end else if (state_r == STATE_IDLE) begin
      delay_rlast <= 1'b0;
      delay_rvalid <= 1'b0;
    end
  end
  //=====================================================================================
  // STATE_START_TRANS
  // 功能: 记录发送给从设备的信号
  // 深度: 8,一次通信可以最多存储8次突发读取
  //=====================================================================================

  always @(posedge clock) begin
    if (reset) begin
      counter <= 0;
    end else if (state_r == STATE_START_TRANS) begin
      counter <= counter + 1;
      // 及时得到数据
      delay_rdata[rvalid_times]  <= out_rdata;
      delay_rresp[rvalid_times]  <= out_rresp;
      delay_rid  [rvalid_times]  <= out_rid;
    end
  end

  //=====================================================================================
  // STATE_DELAY: 延迟k*r个周期
  //=====================================================================================
  reg [31:0] counter_cycle;
  reg [2:0]  pass_rvalid_times;//已经传递回master的rvalid等数据的次数
  localparam r = 4'd2 - 4'd1; //得到下游传回的通信时，已经相当于延迟了一个周期，故减1

  always @(posedge clock) begin
    if (reset) begin
      counter_cycle <= 0;
      pass_rvalid_times <= 0;
    end else if (state_r == STATE_DELAY) begin
      if (counter_cycle < k_r[pass_rvalid_times]) begin  //循环计数r
        delay_rvalid <= 1'b0;
        if (counter < r) begin
          counter <= counter + 1;
        end else begin
          counter <= 1;
          counter_cycle <= counter_cycle + 1;
        end
      end else begin //计数完毕
        if (pass_rvalid_times == rvalid_times) begin
          delay_rlast <= 1'b1; //持续一个周期,idle状态失效
          delay_rvalid <= 1'b1; //持续一个周期,idle状态失效
          delay_rdata_t <= delay_rdata[pass_rvalid_times];
          delay_rid_t <= delay_rid[pass_rvalid_times];
          delay_rresp_t <= delay_rresp[pass_rvalid_times];
          //结束传递
          rvalid_times <= 0;
          pass_rvalid_times <= 0;
          counter_cycle <= 0;
          //state_r <= STATE_IDLE;
        end else begin
          //继续传输
          pass_rvalid_times <= pass_rvalid_times + 1;
          delay_rvalid <= 1'b1;  //持续一个周期
          delay_rdata_t <= delay_rdata[pass_rvalid_times];
          delay_rid_t <= delay_rid[pass_rvalid_times];
          delay_rresp_t <= delay_rresp[pass_rvalid_times];
        end
      end
    end else begin
    end
  end


  //=====================================================================================
  //状态机切换逻辑: WRITE通道
  //=====================================================================================
  reg [31:0] k_w;
  reg [31:0] w_counter;
  always @(posedge clock) begin
    if (reset) begin
      state_w <= STATE_IDLE;
      k_w <= 0;
    end else begin
      case (state_w)
        //-------------------------------------
        //STATE_IDLE: 遇到awvalid时切换状态
        //------------------------------------
        STATE_IDLE: begin
          if (in_awvalid) begin
            state_w <= STATE_START_TRANS;
          end
        end
        //------------------------------------------------
        // STATE_START_TRANS: 遇到bvalid
        //------------------------------------------------
        STATE_START_TRANS: begin
          if (out_bvalid) begin //等bvalid就结束
            k_w <= w_counter;
            w_counter <= 1;
            state_w <= STATE_DELAY;
          end
        end
        //-------------------------------------------
        // STATE_DELAY: 结束后通过后续行为切换状态
        //-------------------------------------------
        STATE_DELAY: begin
          if (delay_bvalid) begin
            state_w <= STATE_IDLE;
            delay_bvalid <= 1'b0;
          end
        end
        default: begin
        end
      endcase
    end
  end


  //=====================================================================================
  // STATE_IDLE
  //=====================================================================================

  always @(posedge clock) begin
    if (reset) begin
    end else if (state_w == STATE_IDLE) begin
      delay_bvalid <= 1'b0;
    end
  end
  //=====================================================================================
  // STATE_START_TRANS
  // 功能: 记录发送给从设备的信号
  // 深度: 8,一次通信可以最多存储8次突发读取
  //=====================================================================================

  always @(posedge clock) begin
    if (reset) begin
      w_counter <= 0;
    end else if (state_w == STATE_START_TRANS) begin
      w_counter <= w_counter + 1;
      // 及时得到数据
      delay_bresp  <= out_bresp;
      delay_bid    <= out_bid;
    end
  end

  //=====================================================================================
  // STATE_DELAY: 延迟k*r个周期
  //=====================================================================================
  reg [31:0] w_counter_cycle;

  always @(posedge clock) begin
    if (reset) begin
      w_counter_cycle <= 0;
    end else if (state_w == STATE_DELAY) begin
      if (w_counter_cycle < k_w) begin  //循环计数r
        if (w_counter < r) begin
          w_counter <= w_counter + 1;
        end else begin
          w_counter <= 1;
          w_counter_cycle <= w_counter_cycle + 1;
        end
      end else begin //计数完毕
        delay_bvalid <= 1'b1;
        //结束传递
        w_counter_cycle <= 0;
        w_counter <= 0;
      end
    end
  end

endmodule
