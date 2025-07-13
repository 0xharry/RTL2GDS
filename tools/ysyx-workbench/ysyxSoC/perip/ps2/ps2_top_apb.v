module ps2_top_apb (
    input             clock,
    input             reset,
    input      [31:0] in_paddr,
    input             in_psel,
    input             in_penable,
    input      [ 2:0] in_pprot,
    input             in_pwrite,
    input      [31:0] in_pwdata,
    input      [ 3:0] in_pstrb,
    output reg        in_pready,
    output reg [31:0] in_prdata,
    output            in_pslverr,

    input ps2_clk,
    input ps2_data
);
  // internal signal, for test
  reg [9:0] buffer;  // ps2_data bits

  //==========================================
  //fifo: depth = 8,数据宽度 = 8
  //---- w_ptr: 指向要写入的fifo的地址
  //---- r_ptr: 指向下一个要读出的key的fifo地址
  //==========================================
  reg [7:0] fifo[7:0];  // data fifo
  reg [2:0] w_ptr, r_ptr;  // fifo write and read pointers


  reg [3:0] count;  // count ps2_data bits
  // detect falling edge of ps2_clk
  reg [2:0] ps2_clk_sync;

  //============================================================================
  //因为ps2_clk一个周期的长度是clk周期的很多倍，因此可以通过下面方式来判断ps2的
  //下升沿即采样时间
  //============================================================================
  always @(posedge clock) begin
    ps2_clk_sync <= {ps2_clk_sync[1:0], ps2_clk};
  end

  wire sampling = ps2_clk_sync[2] & ~ps2_clk_sync[1];

  //============================================================================
  // 键码获取及存储的实现过程,只能存储最近的8位键码
  //============================================================================
  always @(posedge clock) begin
    if (reset) begin  //复位
      count <= 0;
      w_ptr <= 0;
      r_ptr <= 0;
    end else begin
      if (sampling) begin
        if (count == 4'd10) begin
          if ((buffer[0] == 0) &&  // start bit
              (ps2_data) &&  // stop bit
              (^buffer[9:1])) begin  // odd  parity
            fifo[w_ptr] <= buffer[8:1];  // kbd scan code 数据写入fifo
            w_ptr <= w_ptr + 3'b1;
          end
          count <= 0;  // for next
        end else begin
          buffer[count] <= ps2_data;  // store ps2_data
          count <= count + 3'b1;
        end
      end
    end
  end

  //============================================================================
  // npc获取fifo中数据
  //============================================================================
  always @(posedge clock) begin
    if (in_penable && ~in_pwrite && ~in_pready) begin
      if (w_ptr > 3'b0) begin  //fifo中存在数据,但是不能是溢出状态
        if (r_ptr < w_ptr + 1) begin
          in_prdata <= {24'b0, fifo[r_ptr]};
          in_pready <= 1'b1;
          r_ptr <= r_ptr + 3'b1;
        end else begin //如果r快于w,则等待
          in_prdata <= 0;
          in_pready <= 1'b1;
          r_ptr <= 0;
        end
      end else begin
        //$display("key fifo empty\n");
        in_prdata <= 0;
        in_pready <= 1'b1;
      end
    end else begin
      in_pready <= 0;
      in_prdata <= 0;
    end
  end



endmodule

