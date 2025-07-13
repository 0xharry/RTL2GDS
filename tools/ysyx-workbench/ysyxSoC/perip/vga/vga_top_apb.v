module vga_top_apb (
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
    output     [31:0] in_prdata,
    output            in_pslverr,

    output [7:0] vga_r,
    output [7:0] vga_g,
    output [7:0] vga_b,
    output reg vga_hsync,
    output reg vga_vsync,
    output reg vga_valid
);

  parameter h_frontporch = 96;
  parameter h_active = 144;
  parameter h_backporch = 784;
  parameter h_total = 800;

  parameter v_frontporch = 2;
  parameter v_active = 35;
  parameter v_backporch = 515;
  parameter v_total = 525;

  reg [9:0] x_cnt;
  reg [9:0] y_cnt;
  wire h_valid;
  wire v_valid;
  wire [9:0] h_addr;
  wire [9:0] v_addr;

  reg  start_send; //由上层软件指定
  reg [23:0] vga_all_data [21'h1FFFFF: 0]; //2M * 3Byte
  always @(posedge clock) begin
    if (reset == 1'b1) begin
      x_cnt <= 1;
      y_cnt <= 1;
    end else begin
      if (start_send) begin
        if (x_cnt == h_total) begin
          x_cnt <= 1;
          if (y_cnt == v_total)  begin
            y_cnt <= 1;
            start_send <= 0;
          end
          else y_cnt <= y_cnt + 1;
        end else x_cnt <= x_cnt + 1;
      end
    end
  end

  //生成同步信号
  assign vga_hsync = (x_cnt > h_frontporch);
  assign vga_vsync = (y_cnt > v_frontporch);
  //生成消隐信号
  assign h_valid = (x_cnt > h_active) & (x_cnt <= h_backporch);
  assign v_valid = (y_cnt > v_active) & (y_cnt <= v_backporch);
  assign vga_valid = h_valid & v_valid;
  //计算当前有效像素坐标
  assign h_addr = h_valid ? (x_cnt - 10'd145) : 10'd0;
  assign v_addr = v_valid ? (y_cnt - 10'd36) : 10'd0;
  //设置输出的颜色值
  wire [23:0] vga_data;
  assign vga_data = vga_all_data[(v_addr-1)*640 + h_addr];
  assign {vga_r, vga_g, vga_b} = vga_data;

  always @(posedge clock) begin
    if (reset) begin
    end else begin
      if (in_penable && in_pwrite && ~in_pready) begin  //只有在写使能时才能写
        if (in_paddr[20:0] == 21'b0) begin
          $display("开始传输\n");
          start_send <= 1; //开始传输帧缓冲数据给nvboard,这里设置为传输完才会停止
        end else begin //地址都是与4对齐的
          vga_all_data[in_paddr[22:2] - 1] <= in_pwdata[23:0];
        end
        in_pready <= 1;
      end else begin
        if (in_pready) begin
          if (~in_penable) begin  //等待使能信号结束，再将pready置1，避免多次传输
            in_pready <= 0;
          end
        end
      end
    end

  end

endmodule
