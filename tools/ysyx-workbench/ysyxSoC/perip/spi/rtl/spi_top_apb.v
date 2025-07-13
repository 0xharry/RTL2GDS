// define this macro to enable fast behavior simulation
// for flash by skipping SPI transfers
`define FAST_FLASH

module spi_top_apb #(
    parameter flash_addr_start = 32'h30000000,
    parameter flash_addr_end   = 32'h3fffffff,
    parameter spi_ss_num       = 8
) (
    input         clock,
    input         reset,
    input  [31:0] in_paddr,
    input         in_psel,
    input         in_penable,
    input  [2:0]  in_pprot,
    input         in_pwrite,
    input  [31:0] in_pwdata,
    input  [3:0]  in_pstrb,
    output reg        in_pready,
    output reg [31:0] in_prdata,
    output reg        in_pslverr,

    output                  spi_sck,
    output [spi_ss_num-1:0] spi_ss,
    output                  spi_mosi,
    input                   spi_miso,
    output                  spi_irq_out
);

`ifdef FAST_FLASH
    wire [31:0] data;
    parameter invalid_cmd = 8'h0;
    flash_cmd flash_cmd_i(
      .clock(clock),
      .valid(in_psel && !in_penable),
      .cmd(in_pwrite ? invalid_cmd : 8'h03),
      .addr({8'b0, in_paddr[23:2], 2'b0}),
      .data(data)
    );
    assign spi_sck    = 1'b0;
    assign spi_ss     = 8'b0;
    assign spi_mosi   = 1'b1;
    assign spi_irq_out= 1'b0;
    assign in_pslverr = 1'b0;
    assign in_pready  = in_penable && in_psel && !in_pwrite;
    assign in_prdata  = data[31:0];
`else

    reg  [31:0] paddr;
    reg         psel;
    reg         penable;
    reg  [2:0]  pprot;
    reg         pwrite;
    reg  [31:0] pwdata;
    reg  [3:0]  pstrb;
    //output
    reg         pready;
    reg  [31:0] prdata;
    reg         pslverr;
    


    wire is_xip = in_paddr >= 32'h3000_0000 && in_paddr <= 32'h3fffffff;
    wire is_spi = in_paddr >= 32'h1000_1000 && in_paddr <= 32'h10001fff;
    typedef enum [3:0] {s_idle, s_normal, s_tx, s_ss, s_dv, s_ctrl, s_go, s_waitok, s_rx, s_error}  state_t;
    reg [3:0] state;

    always @(posedge clock) begin
        if (in_psel && ~in_pready) begin
            if (state == s_idle) begin
                state <= is_xip ? s_tx : (is_spi ? s_normal : state);
            end else if (state == s_normal) begin
                state <= in_pready ? s_idle : state;
                paddr   <= in_paddr;
                psel    <= in_psel;
                penable <= in_penable;
                pprot   <= in_pprot;
                pwrite  <= in_pwrite;
                pwdata  <= in_pwdata;
                pstrb   <= in_pstrb;
                //output
                in_pready  <= pready;
                in_prdata  <= prdata;
                in_pslverr <= pslverr;
            end else if (state == s_tx) begin
                paddr <= 32'h1000_1004; //Tx寄存器地址
                pwdata <= {8'h03,in_paddr[23:0]}; //flash取指指令+地址
                psel <= 1'b1;
                penable <= 1'b1;
                pwrite <= 1'b1;
                pstrb <= 4'b1111;
                if (pready) begin
                    state <= s_ss;
                    psel <= 1'b0;
                    penable <= 1'b0;
                end
            end else if (state == s_ss) begin
                paddr <= 32'h1000_1018; //SS寄存器地址
                pwdata <= 32'h1; //使能ss_0即flash
                psel <= 1'b1;
                penable <= 1'b1;
                pwrite <= 1'b1;
                pstrb <= 4'b1111;
                if (pready) begin
                    state <= s_dv;
                    psel <= 1'b0;
                    penable <= 1'b0;
                    pwrite <= 1'b0;
                end
            end else if (state == s_dv) begin
                paddr <= 32'h1000_1014;   //DV寄存器j
                pwdata <= 32'h0; //0,即sck : clk = 1 : 2
                psel <= 1'b1;
                penable <= 1'b1;
                pwrite <= 1'b1;
                pstrb <= 4'b1111;
                if (pready) begin
                    state <= s_ctrl;
                    psel <= 1'b0;
                    penable <= 1'b0;
                    pwrite <= 1'b0;
                end
            end else if (state == s_ctrl) begin
                paddr <= 32'h1000_1010;  //设置ctrl寄存器
                pwdata <= 32'h0000_2040; //传输位数64位，ass置1
                psel <= 1'b1;
                penable <= 1'b1;
                pwrite <= 1'b1;
                pstrb <= 4'b1111;
                if (pready) begin
                    state <= s_go;
                    psel <= 1'b0;
                    penable <= 1'b0;
                    pwrite <= 1'b0;
                end
            end else if (state == s_go) begin
                paddr <= 32'h1000_1010; 
                pwdata <= 32'h0000_2140;  //go_busy置1
                psel <= 1'b1;
                penable <= 1'b1;
                pwrite <= 1'b1;
                pstrb <= 4'b1111;
                if (pready) begin
                    state <= s_waitok;
                    psel <= 1'b0;
                    penable <= 1'b0;
                    pwrite <= 1'b0;
                end
            end else if (state == s_waitok) begin
                paddr <= 32'h1000_1010;
                psel <= 1'b1;
                penable <= 1'b1;
                if (pready) begin
                    if (prdata[8] == 1'b0) begin //prdata[8]:go_busy
                        psel <= 1'b0;
                        penable <= 1'b0;
                        state <= s_rx;
                    end else begin
                        state <= state;
                    end
                end
            end else if (state == s_rx) begin
                paddr <= 32'h1000_1000; //Rx0
                penable <= 1'b1;
                psel <= 1'b1;
                in_pready <= pready;
                if (pready) begin
                    in_prdata <= {prdata[7:0], prdata[15:8], prdata[23:16], prdata[31:24]};
                    in_pslverr <= pslverr;
                    penable <= 1'b0;
                    psel <= 1'b0;
                    state <= s_idle;
                end
            end
        end else begin
          if (in_psel) begin //说明还在延迟阶段，等待psel为0时，才真正结束
            in_pready <= 1;
          end else begin
            in_pready <= 0;
          end
          state <= s_idle;
        end
    end


    spi_top u0_spi_top (
        .wb_clk_i(clock),
        .wb_rst_i(reset),
        .wb_adr_i(paddr[4:0]),
        .wb_dat_i(pwdata),
        .wb_dat_o(prdata),
        .wb_sel_i(pstrb),
        .wb_we_i (pwrite),
        .wb_stb_i(psel),
        .wb_cyc_i(penable),
        .wb_ack_o(pready),
        .wb_err_o(pslverr),
        .wb_int_o(spi_irq_out),
    
        .ss_pad_o(spi_ss),
        .sclk_pad_o(spi_sck),
        .mosi_pad_o(spi_mosi),
        .miso_pad_i(spi_miso)
    );

`endif // FAST_FLASH

endmodule
