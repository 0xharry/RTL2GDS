module psram(
    input sck,
    input ce_n,
    inout [3:0] dio
);

    wire reset = ce_n; // ce_n低电平有效
    wire QPI_ENABLE = 1;
    typedef enum [3:0] { cmd_t, addr_t, rwait_t, wdata_t, rdata_t, err_t } state_t; //状态机定义
    reg [3:0]  state;
    reg [7:0]  counter;
    reg [7:0]  cmd;
    reg [23:0] addr;
    reg [31:0] wdata;
    wire [31:0] rdata;
    wire [31:0] rdata_rev;

    //高4位，低4位翻转  + 低字节在前
    assign rdata_rev = {rdata[7:0], rdata[15:8], rdata[23:16], rdata[31:24]};
    // 地址指令传送完后,读使能
    wire ren = (state == rwait_t) && (cmd == 8'hEB);
    //wire wen = (state == wdata_t) && (ce_n); //到了传数据阶段，当ce_n为1时，表传送的数据传送完了，即可开始些数据


    wire [31:0] waddr = {8'b0, addr}; //不确定是否对，注意一下
    wire [31:0] raddr = {8'b0, addr}; //不确定是否对，注意一下


    reg [7:0] ram [28'h100_0000:0]; // 2^24 X 8bits  :  4MB,

    // 写存储器/ 读存储器
    always @(posedge ren) begin
        if (ren) begin
            rdata[7:0  ] <= ram[raddr    ];
            rdata[15:8 ] <= ram[raddr + 1];
            rdata[23:16] <= ram[raddr + 2];
            rdata[31:24] <= ram[raddr + 3];
        end
    end

    // 状态机切换逻辑
    always @(posedge sck or posedge reset) begin
        if (reset) state <= cmd_t;
        else begin
            case (state)
                cmd_t:  state <=  (counter == (QPI_ENABLE ? 8'd1 : 8'd7))    ? addr_t  : state;
                addr_t: state <=  (cmd     == 8'h38 )                        ? (counter == 8'd5 ? wdata_t : state) : //写1-4-4
                                  (cmd     == 8'hEB )                        ? (counter == 8'd5 ? rwait_t : state) : //读1-4-4
                                  err_t; //指令不对，因此报错
                rwait_t: state <= (counter == 8'd6  )  ? rdata_t : state;
                wdata_t: state <= state;
                rdata_t: state <= state;
                default: begin
                    state <= state;
                    $fwrite(32'h80000002, "Assertion failed: Unsupported command `%xh`, only support `38h`,`EBH` read command\n", cmd);
                    $fatal;
                end
            endcase
        end
    end

    // 计数器模块
    always@(posedge sck or posedge reset) begin
        if (reset) counter <= 8'd0;
        else begin
            case (state)
                cmd_t:   counter <= (counter < (QPI_ENABLE ? 8'd1 :8'd7) ) ? counter + 8'd1 : 8'd0;
                addr_t:  counter <= (counter < 8'd5 )                      ? counter + 8'd1 : 8'd0;
                rwait_t: counter <= (counter < 8'd6 )                      ? counter + 8'd1 : 8'd0;
                default: counter <= counter + 8'd1;
            endcase
        end
    end

    // 接受cmd指令部分
    always@(posedge sck or posedge reset) begin
      if (reset)               cmd <= 8'd0;
      else if (state == cmd_t) begin
          if (QPI_ENABLE) begin
              cmd <= {cmd[3:0],dio};
          end
          else cmd <= { cmd[6:0], dio[0] };
      end
    end

    // 接收addr部分
    always@(posedge sck or posedge reset) begin
        if (reset) addr <= 24'd0;
        else if (state == addr_t && counter <= 8'd5)
            addr <= {addr[19:0], dio};
    end

    // 接受data部分
    always @(posedge sck or posedge reset) begin
        if (reset) wdata <= 32'd0;
        else if (state == wdata_t) begin   //只要是sck有波形就行
            wdata <= {wdata[27:0],dio};
            if (counter[0] == 1'b1) begin
                ram[waddr + {30'b0,counter[2:1]}] <= {wdata[3:0],dio};
            end
        end
    end

    // rwait部分，得到rdata

    assign dio[0] = (state == rdata_t) ? rdata_rev[31 - 4*counter - 3] : 1'bz;
    assign dio[1] = (state == rdata_t) ? rdata_rev[31 - 4*counter - 2] : 1'bz;
    assign dio[2] = (state == rdata_t) ? rdata_rev[31 - 4*counter - 1] : 1'bz;
    assign dio[3] = (state == rdata_t) ? rdata_rev[31 - 4*counter - 0] : 1'bz;

    import "DPI-C" function void psram_trap();

    always @(posedge sck ) begin
        if (state == wdata_t) begin
            // 计算当前写地址和数据
            if (counter[0] == 1'b1) begin
                logic [31:0] cur_addr = waddr + {30'b0, counter[2:1]};
                logic [7:0]  cur_data = {wdata[3:0], dio};
                if (cur_addr == 32'h00000000 && cur_data == 8'haa) begin
                    //$display("Write magic world: %h to address: %h", {wdata[3:0], dio} , waddr + {30'b0, counter[2:1]} + 32'h80000000);
                    psram_trap();
                end
            end
        end
    end

endmodule
