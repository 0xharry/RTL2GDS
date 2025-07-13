module gpio_top_apb(
  input         clock,
  input         reset,
  input  [31:0] in_paddr,
  input         in_psel,
  input         in_penable,
  input  [2:0]  in_pprot,
  input         in_pwrite,
  input  [31:0] in_pwdata,
  input  [3:0]  in_pstrb,
  output        in_pready,
  output [31:0] in_prdata,
  output        in_pslverr,

  output [15:0] gpio_out,
  input  [15:0] gpio_in,
  output [7:0]  gpio_seg_0,
  output [7:0]  gpio_seg_1,
  output [7:0]  gpio_seg_2,
  output [7:0]  gpio_seg_3,
  output [7:0]  gpio_seg_4,
  output [7:0]  gpio_seg_5,
  output [7:0]  gpio_seg_6,
  output [7:0]  gpio_seg_7
);

  reg [15:0] gpio_reg;
  assign in_pready  = in_psel && in_penable;
  assign in_pslverr = 1'b0;
  assign in_prdata  = (in_psel && !in_pwrite) ? {16'd0, gpio_reg} : 32'd0;
  assign gpio_out   = gpio_reg;

  always @(posedge clock or posedge reset) begin
      if (reset) begin
          gpio_reg <= 16'd0;
      end else if (in_psel && !in_penable && in_pwrite) begin
          gpio_reg <= in_pwdata[15:0];
      end
  end
endmodule
