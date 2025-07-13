`define CONFIG_STA_MODE
/****指令类型判断*****/
`define TYPE_I ((~op[6] && ~op[5] && (op[4]+1) && ~op[3] && ~op[2] && op[1] && op[0]) || (op[6] && op[5] && ~op[4] && ~op[3] && op[2] && op[1] && op[0]))
`define TYPE_R (~op[6] && op[5] && op[4] && ~op[3] && ~op[2] && op[1] && op[0])
`define TYPE_U (~op[6] && (op[5]+1) && op[4] && ~op[3] && op[2] && op[1] && op[0])
`define TYPE_J (op[6] && op[5] && ~op[4] && op[3] && op[2] && op[1] && op[0])
`define TYPE_B (op[6] && op[5] && ~op[4] && ~op[3] && ~op[2] && op[1] && op[0])
`define TYPE_S (~op[6] && op[5] && ~op[4] && ~op[3] && ~op[2] && op[1] && op[0])
// I-type中运算类指令
`define TYPE_IR `INSTPAT_1(7'b0010011)
// I-type中LOAD指令
`define TYPE_LOAD `INSTPAT_1(7'b0000011)
// csr相关指令+ecall,ebreak
`define TYPE_IC `INSTPAT_1(7'b1110011)



/**************无条件跳转*****************/
`define INST_JAL    `INSTPAT_1(7'b1101111)
`define INST_JALR   `INSTPAT_2(3'b000,7'b1100111)

/*************有条件跳转B-type*************/
`define INST_BEQ    `INSTPAT_2(3'b000,7'b1100011)
`define INST_BNE    `INSTPAT_2(3'b001,7'b1100011)
`define INST_BLT    `INSTPAT_2(3'b100,7'b1100011)
`define INST_BGE    `INSTPAT_2(3'b101,7'b1100011)
`define INST_BLTU   `INSTPAT_2(3'b110,7'b1100011)
`define INST_BGEU   `INSTPAT_2(3'b111,7'b1100011)

/***************load I-type****************/
`define INST_LB     `INSTPAT_2(3'b000, 7'b0000011)
`define INST_LH     `INSTPAT_2(3'b001, 7'b0000011)
`define INST_LW     `INSTPAT_2(3'b010, 7'b0000011)
`define INST_LBU    `INSTPAT_2(3'b100, 7'b0000011)
`define INST_LHU    `INSTPAT_2(3'b101, 7'b0000011)

/*********store S-type*********************/
`define INST_SB     `INSTPAT_2(3'b000,7'b0100011)
`define INST_SH     `INSTPAT_2(3'b001,7'b0100011)
`define INST_SW     `INSTPAT_2(3'b010,7'b0100011)

/**************运算imm  I-type *************/
`define INST_ADDI   `INSTPAT_2(3'b000,7'b0010011)
`define INST_SLTI   `INSTPAT_2(3'b010,7'b0010011)
`define INST_SLTUI  `INSTPAT_2(3'b011,7'b0010011)
`define INST_XORI   `INSTPAT_2(3'b100,7'b0010011)
`define INST_ORI    `INSTPAT_2(3'b110,7'b0010011)
`define INST_ANDI   `INSTPAT_2(3'b111,7'b0010011)

`define INST_SLLI   `INSTPAT_3(7'b0000000, 3'b001, 7'b0010011)
`define INST_SRLI   `INSTPAT_3(7'b0000000, 3'b101, 7'b0010011)
`define INST_SRAI   `INSTPAT_3(7'b0100000, 3'b101, 7'b0010011)

/*********************  R-type *********************/
`define INST_ADD    `INSTPAT_3(7'b0000000, 3'b000, 7'b0110011)
`define INST_SUB    `INSTPAT_3(7'b0100000, 3'b000, 7'b0110011)
`define INST_SLL    `INSTPAT_3(7'b0000000, 3'b001, 7'b0110011)
`define INST_SLT    `INSTPAT_3(7'b0000000, 3'b010, 7'b0110011)
`define INST_SLTU   `INSTPAT_3(7'b0000000, 3'b011, 7'b0110011)
`define INST_XOR    `INSTPAT_3(7'b0000000, 3'b100, 7'b0110011)
`define INST_SRL    `INSTPAT_3(7'b0000000, 3'b101, 7'b0110011)
`define INST_SRA    `INSTPAT_3(7'b0100000, 3'b101, 7'b0110011)
`define INST_OR     `INSTPAT_3(7'b0000000, 3'b110, 7'b0110011)
`define INST_AND    `INSTPAT_3(7'b0000000, 3'b111, 7'b0110011)

/******************* U-type *********************/
`define INST_LUI    `INSTPAT_1(7'b0110111)
`define INST_AUIPC  `INSTPAT_1(7'b0010111)

/*************... *************/
`define INST_EBREAK (inst == 32'h00100073)
`define INST_ECALL  (inst == 32'h00000073)
`define INST_MRET   (inst == 32'h30200073)

/*************** CSR ************/
`define INST_CSRRW  `INSTPAT_2(3'b001,7'b1110011)
`define INST_CSRRS  `INSTPAT_2(3'b010,7'b1110011)
`define INST_CSRRC  `INSTPAT_2(3'b011,7'b1110011)

/********************特殊类指令*******************/
//看作普通的I指令，走运算imm通道
`define INST_FENCE_I `INSTPAT_2(3'b001,7'b0001111)


`ifndef MACROS_VH
`define MACROS_VH


/*************** 指令pattern *********************/
/*用于识别指令*/
`define INSTPAT_3(inst_funct7,inst_funct3,inst_op) ((inst_op == op)&&(inst_funct3 == funct3)&&(inst_funct7==funct7))
`define INSTPAT_2(inst_funct3,inst_op) ((inst_op == op)&&(inst_funct3 == funct3))
`define INSTPAT_1(inst_op) (inst_op == op)
/******************end**********************/

/* 用于评估时屏蔽DPI-C */
`define CONFIG_STA_MODE

`endif // MACROS_VH
module ysyx_22050499_ALL_SLAVE (
    input             clock,
    input             reset,
    input      [31:0] raddr,
    input      [31:0] waddr,
    input      [31:0] wdata,
    input      [ 3:0] wstrb,
    input      [ 3:0] xbar_decode,
    input             ren,
    input             wen,
    output reg [31:0] slave_rdata,
    output reg        slave_arready,
    output            slave_awready,
    output            slave_wready,
    output reg        slave_rvalid
);
  //wire        slave1_arready;
  //wire        slave1_rvalid;
  //wire [31:0] slave1_rdata;
  //wire        slave1_awready;
  //wire        slave1_wready;

  //wire        slave2_arready;
  //wire        slave2_rvalid;
  //wire [31:0] slave2_rdata;
  //wire        slave2_awready;
  //wire        slave2_wready;

  wire        slave3_arready;
  wire        slave3_rvalid;
  wire [31:0] slave3_rdata;
  wire        slave3_awready;
  wire        slave3_wready;
  // 选择下游设备,各个模块被xbar_decode所限制，如果不是译码对应的设备，其功
  // 能无效
  always @(posedge clock) begin
    if (xbar_decode == 4'b0001) begin
    //=================================
    //只读设备CLINT
    //=================================
      slave_awready <= slave3_awready;
      slave_wready  <= slave3_wready;
      slave_arready <= slave3_arready;
      slave_rvalid  <= slave3_rvalid;
      slave_rdata   <= slave3_rdata;
    end else begin
      slave_awready <= 0;
      slave_wready  <= 0;
      slave_arready <= 0;
      slave_rvalid  <= 0;
      slave_rdata   <= 0;
    end
    //if (xbar_decode == 4'h0001) begin //SRAM
    //slave_awready <= slave1_awready;
    //slave_wready  <= slave1_wready;
    //slave_arready <= slave1_arready;
    //slave_rvalid  <= slave1_rvalid;
    //slave_rdata   <= slave1_rdata;
    //end else if (xbar_decode == 4'b0010) begin //UART
    //slave_awready <= slave2_awready;
    //slave_wready  <= slave2_wready;
    //slave_arready <= slave2_arready;
    //slave_rvalid  <= slave2_rvalid;
    //slave_rdata   <= slave2_rdata;

  end
  // slave3: CLINT
  ysyx_22050499_CLINT ysyx_22050499_CLINT (
      .clock      (clock),
      .reset      (reset),
      .xbar_decode(xbar_decode),
      .arready    (slave3_arready),
      .awready    (slave3_awready),
      .wready     (slave3_wready),
      .rvalid     (slave3_rvalid),
      .raddr      (raddr),
      .ren        (ren),
      .rdata      (slave3_rdata)
  );
endmodule
//暂时只有加法功能
module ysyx_22050499_ALU #(DATA_WITDH = 32) (
    input [DATA_WITDH-1:0]  srcA,
    input [DATA_WITDH-1:0]  srcB,
    input                   SUBctr,
    input [13:0]            OPctr,
    input [2:0]             BRctr,
    output                  BR_result,
    output [DATA_WITDH-1:0] alu_result
);
    wire                  carry;
    wire [DATA_WITDH-1:0] and_result;
    wire [DATA_WITDH-1:0] slt_result;
    wire [DATA_WITDH-1:0] sltu_result;
    wire [DATA_WITDH-1:0] or_result;
    wire [DATA_WITDH-1:0] xor_result;
    wire [DATA_WITDH-1:0] lui_result;
    wire [DATA_WITDH-1:0] add_result;
    wire [DATA_WITDH-1:0] sll_result;
    wire [DATA_WITDH-1:0] srl_result;
    wire [DATA_WITDH-1:0] sra_result;
    wire [DATA_WITDH-1:0] csrrw_result;
    wire [DATA_WITDH-1:0] csrrc_result;
    wire [DATA_WITDH-1:0] csrrs_result;


    wire  beq_result;
    wire  bne_result;
    wire  blt_result;
    wire  bge_result;
    wire  bltu_result;
    wire  bgeu_result;

    wire op_lui     = OPctr[0];
    wire op_add_sub = OPctr[1];
    wire op_sll     = OPctr[2];
    wire op_slt     = OPctr[3];
    wire op_sltu    = OPctr[4];
    wire op_xor     = OPctr[5];
    wire op_srl     = OPctr[6];
    wire op_sra     = OPctr[7];
    wire op_or      = OPctr[8];
    wire op_and     = OPctr[9];
    wire op_csrrw   = OPctr[10];
    wire op_csrrs   = OPctr[11];
    wire op_csrrc   = OPctr[12];
    wire op_add     = OPctr[13];


    assign and_result = srcA & srcB;
    assign or_result = srcA | srcB;
    assign xor_result = srcA ^ srcB;
    assign lui_result = srcB;
    assign add_result = srcA + srcB;
    assign sll_result   = srcA << srcB[4:0];
    assign srl_result   = srcA >> srcB[4:0];
    assign sra_result   = ($signed(srcA)) >>> srcB[4:0];

    assign csrrw_result =  srcA;
    assign csrrs_result =  srcA | srcB;
    assign csrrc_result =  srcB &~ srcA;

    /*得到add,sub运算的结果*/
    wire adder_cin;    // 低位进位
    wire overflow;
    wire [DATA_WITDH-1:0] adder_A;
    wire [DATA_WITDH-1:0] adder_B;
    wire [DATA_WITDH-1:0] add_sub_result;


    assign adder_cin = SUBctr;
    assign adder_A = srcA;
    assign adder_B = srcB ^ {32{SUBctr}}; // 处理后的数据
    assign {carry,add_sub_result} = adder_A + adder_B + {31'b0,adder_cin};

    //不一定对
    assign overflow = (adder_A[31] == adder_B[31]) && (adder_A[31] != add_sub_result[31]); //溢出判断


    assign slt_result[31:1] = 31'b0;
    assign slt_result[0] = overflow ^ add_sub_result[31]; //已证明，没问题
    assign sltu_result[31:1] = 31'b0;
    assign sltu_result[0] = adder_cin ^ carry;

    /*****************分支指令************************/
    assign beq_result = srcA == srcB;
    assign bne_result = srcA != srcB;
    assign bge_result = (srcA[31] == srcB[31] ? ~add_sub_result[31] : /* 如果符号相等，则符号位为0时，符合条件*/
                        (srcA[31] == 0        ? 1                   : 0 ));  // 如果符号不相等，则当srcA为正数时，符合条件
    assign bgeu_result = carry; //add_sub运算有溢出的时候，A>=B
    assign blt_result = ~bge_result; //与bge相反
    assign bltu_result = ~bgeu_result; //与bgeu相反

    assign BR_result =  (BRctr == 3'b000 ? beq_result  :
                        (BRctr == 3'b001 ? bne_result  :
                        (BRctr == 3'b010 ? bge_result  :
                        (BRctr == 3'b011 ? bgeu_result :
                        (BRctr == 3'b100 ? blt_result  :
                        (BRctr == 3'b101 ? bltu_result :
                                           0))))));

    /***************end*******************/
    // 根据OPctr选择结果输出
    assign alu_result = ({32{op_lui     }}      & lui_result)
                      | ({32{op_add_sub }}      & add_sub_result)
                      | ({32{op_sll     }}      & sll_result)
                      | ({32{op_slt     }}      & slt_result)
                      | ({32{op_sltu    }}      & sltu_result)
                      | ({32{op_xor     }}      & xor_result)
                      | ({32{op_srl     }}      & srl_result)
                      | ({32{op_sra     }}      & sra_result)
                      | ({32{op_or      }}      & or_result)
                      | ({32{op_and     }}      & and_result)
                      | ({32{op_csrrw   }}      & csrrw_result)
                      | ({32{op_csrrs   }}      & csrrs_result)
                      | ({32{op_csrrc   }}      & csrrc_result)
                      | ({32{op_add     }}      & add_result);




endmodule


// resp不同值的含义
`define OKAY 2'b00
`define EXOKAY 2'b01
`define SLVERR 2'b10
`define DECERR 2'b11
/********end**********/

module ysyx_22050499_AXI_BUS (
    input              clock,
    input              reset,
    input      [ 33:0] if_axi_data,
    input      [78:0]  mem_axi_data,
    input              io_master_rlast,
    input              io_master_rvalid,
    input      [  1:0] io_master_rresp,
    input      [ 31:0] io_master_rdata,
    input              io_master_awready,
    input              io_master_wready,
    input              io_master_bvalid,
    input      [  1:0] io_master_bresp,
    input      [  3:0] io_master_bid,
    input              io_master_arready,
    input              fence_i,
    output reg         if_access_done,
    output reg         mem_access_done,
    output reg [ 31:0] rdata,              //传送给主机的
    output reg [120:0] o_master_axi_data,
    /* 与icache ifu 交互 */
    input              icache_ok,
    output reg [127:0] sdram_rdata,
    output reg         sdram_read_ok

);

  parameter s_idle = 3'h0;  //空闲状态
  parameter s_1    = 3'h1;  // 成功实现AW通信，准备W通信
  parameter s_2    = 3'h2;  // 成功W通信，准备B通信。 通信成功则回到idle
  parameter s_3    = 3'h3;  // 成功实现AR通信，准备R通信,通信成功回到idle
  parameter s_4    = 3'h5;  // 成功读sdram,等icache完成写入相关操作
  parameter s_0    = 3'h4; // 成功传递数据
  reg [2:0] s_states;


  `define IO_MASTER_ARBURST o_master_axi_data[120:119]
  `define IO_MASTER_ARLEN   o_master_axi_data[118:111]
  `define IO_MASTER_ARADDR  o_master_axi_data[110:79]
  `define IO_MASTER_ARADDR  o_master_axi_data[110:79]
  `define IO_MASTER_ARSIZE  o_master_axi_data[78:76]
  `define IO_MASTER_AWSIZE  o_master_axi_data[75:73]
  `define IO_MASTER_ARVALID o_master_axi_data[72]
  `define IO_MASTER_RREADY  o_master_axi_data[71]
  `define IO_MASTER_AWADDR  o_master_axi_data[70:39]
  `define IO_MASTER_AWVALID o_master_axi_data[38]
  `define IO_MASTER_WDATA   o_master_axi_data[37:6]
  `define IO_MASTER_WSTRB   o_master_axi_data[5:2]
  `define IO_MASTER_WVALID  o_master_axi_data[1]
  `define IO_MASTER_BREADY  o_master_axi_data[0]


  `define MEM_ARSIZE  mem_axi_data[78:76]
  `define MEM_AWSIZE  mem_axi_data[75:73]
  `define MEM_ARVALID mem_axi_data[72]
  `define MEM_RREADY  mem_axi_data[71]
  `define MEM_ADDR    mem_axi_data[70:39]
  `define MEM_AWVALID mem_axi_data[38]
  `define MEM_WDATA   mem_axi_data [37:6]
  `define MEM_WSTRB   mem_axi_data[5:2]
  `define MEM_WVALID  mem_axi_data[1]
  `define MEM_BREADY  mem_axi_data[0]

  `define IFU_ADDR    if_axi_data[33:2]
  `define IFU_ARVALID if_axi_data[1]
  `define IFU_RREADY  if_axi_data[0]

  //=====================================================================================
  // AXI仲裁器
  //=====================================================================================
  wire is_fetch = `IFU_ARVALID && ~if_access_done;
  wire is_read  = `MEM_ARVALID && ~mem_access_done;
  wire is_write = `MEM_AWVALID && ~mem_access_done;

  wire happen_conflict = (is_fetch && (is_read || is_write)) && ~axi_actived;
  localparam CONFLICT_STATE_IDLE = 2'b00;
  localparam CONFLICT_STATE_IFU = 2'b01;
  localparam CONFLICT_STATE_LSU = 2'b10;
  localparam CONFLICT_STATE_WAIT = 2'b11;
  reg [1:0] conflict_state;
  reg axi_actived;

  always @(posedge clock) begin
    if (~happen_conflict) begin
      if (write_mode || read_mode || fetch_mode) begin
        axi_actived <= 1'b1;
      end else begin
        axi_actived <= 1'b0;
      end
    end
  end
  always @(posedge clock) begin
    if (reset) begin
      conflict_state <= CONFLICT_STATE_IDLE;
    end else begin
      if (conflict_state == CONFLICT_STATE_IDLE) begin
        if (happen_conflict) begin
          conflict_state <= CONFLICT_STATE_IFU;
        end

      end else if (conflict_state == CONFLICT_STATE_IFU) begin
        if (if_access_done) begin
          conflict_state <= CONFLICT_STATE_LSU;
        end

      end else if (conflict_state == CONFLICT_STATE_LSU) begin
        if (mem_access_done) begin
          conflict_state <= CONFLICT_STATE_WAIT;
        end

      end else if (conflict_state == CONFLICT_STATE_WAIT) begin
        if (~happen_conflict) begin
          conflict_state <= CONFLICT_STATE_IDLE;
        end
      end
    end
  end

  //=====================================================================================
  // XBAR-译码器: 根据地址译码
  //=====================================================================================
  wire xbarDecodeStart = is_fetch || is_read || is_write;
  reg  [3:0] xbar_decode;//在通信开始时赋值，结束时为0
  wire [3:0] xbar_decode_t  =
    (xbarDecodeStart) ?
      ((is_read || is_write)&&(~mem_access_done)&&(~happen_conflict ||  (conflict_state == CONFLICT_STATE_LSU)) ? /* 没发生冲突或发生冲突但已解决时*/
        ((`MEM_ADDR >= 32'h2000_0000 && `MEM_ADDR < 32'h2000_1000) ? 4'b0010 : /*MROM*/
         (`MEM_ADDR >= 32'h0200_0000 && `MEM_ADDR < 32'h0201_0000) ? 4'b0001 : /*CLINT*/
         (`MEM_ADDR >= 32'h1000_0000 && `MEM_ADDR < 32'h1000_1000) ? 4'b0011 : /*UART*/
         (`MEM_ADDR >= 32'h0f00_0000 && `MEM_ADDR < 32'h0f00_2000) ? 4'b0100 : /*SRAM*/
         (`MEM_ADDR >= 32'h3000_0000 && `MEM_ADDR < 32'h4000_0000) ? 4'b0101 : /*XIP to flash */
         (`MEM_ADDR >= 32'h1000_1000 && `MEM_ADDR < 32'h1000_2000) ? 4'b0110 : /*SPI*/
         (`MEM_ADDR >= 32'h8000_0000 && `MEM_ADDR < 32'h9000_0000) ? 4'b0111 : /*PSRAM*/
         (`MEM_ADDR >= 32'ha000_0000 && `MEM_ADDR < 32'hc000_0000) ? 4'b1000 : /*SDRAM*/
         (`MEM_ADDR >= 32'h1001_1000 && `MEM_ADDR < 32'h1001_1008) ? 4'b1001 : /*PS2*/
         (`MEM_ADDR >= 32'h2100_0000 && `MEM_ADDR < 32'h2120_0000) ? 4'b1010 : /*VGA*/
                                                                    4'b0000) :
      (is_fetch && (~if_access_done) ?
        ((`IFU_ADDR >= 32'h2000_0000 && `IFU_ADDR < 32'h2000_1000) ? 4'b0010 : /*MROM*/
         (`IFU_ADDR >= 32'h0f00_0000 && `IFU_ADDR < 32'h0f00_2000) ? 4'b0100 : /*SRAM*/
         (`IFU_ADDR >= 32'h3000_0000 && `IFU_ADDR < 32'h4000_0000) ? 4'b0101 : /*XIP to flash */
         (`IFU_ADDR >= 32'h8000_0000 && `IFU_ADDR < 32'h9000_0000) ? 4'b0111 : /*PSRAM*/
         (`IFU_ADDR >= 32'ha000_0000 && `IFU_ADDR < 32'hc000_0000) ? 4'b1111 : /*SDRAM special */
                                                                    4'b0000) :
         4'b0000)
    ) : 4'b0000;



  //=====================================================================================
  //  delay模块，维持access  1个周期有效
  //=====================================================================================
  reg [1:0] counter;
  always @(posedge clock) begin
    if (reset) begin
      counter <= 2'b0;
    end else if (if_access_done || mem_access_done) begin //维持access_done 2周期
      if_access_done <= 1'b0;
      mem_access_done <= 1'b0;
    end
  end

  //=====================================================================================
  // 传递数据给对应通信,并切换状态至s_0
  // 传递译码信号给xbar_decode,确定通信模式
  //=====================================================================================
  reg fetch_mode;
  reg read_mode;
  reg write_mode;
  always @(posedge clock) begin
    if (reset) begin
      s_states <= s_idle;
      xbar_decode <= 4'b0;
    end else begin
      if (s_states <= s_idle) begin
        if (is_write && (~happen_conflict || (conflict_state == CONFLICT_STATE_LSU))) begin
          xbar_decode <= xbar_decode_t;
          write_mode <= 1;
          // B通道
          `IO_MASTER_BREADY  <= `MEM_BREADY;
          //AW通道
          `IO_MASTER_AWVALID <= 0;
          `IO_MASTER_AWADDR  <= `MEM_ADDR;
          `IO_MASTER_AWSIZE  <= `MEM_AWSIZE;
          //W通道
          `IO_MASTER_WVALID  <= 0;
          case (`MEM_ADDR & 32'b11)
            32'h0: begin
              `IO_MASTER_WSTRB <= `MEM_WSTRB << 0;
              `IO_MASTER_WDATA <= `MEM_WDATA << 0;
            end
            32'h1: begin
              `IO_MASTER_WSTRB <= `MEM_WSTRB << 1;
              `IO_MASTER_WDATA <= `MEM_WDATA << 8;
            end
            32'h2: begin
              `IO_MASTER_WSTRB <= `MEM_WSTRB << 2;
              `IO_MASTER_WDATA <= `MEM_WDATA << 16;
            end
            32'h3: begin
              `IO_MASTER_WSTRB <= `MEM_WSTRB << 3;
              `IO_MASTER_WDATA <= `MEM_WDATA << 24;
            end
          endcase
          s_states <= s_0;
        end else if (is_read && (~happen_conflict || (conflict_state == CONFLICT_STATE_LSU))) begin
          read_mode <= 1'b1;
          xbar_decode <= xbar_decode_t;
          //R通道
          `IO_MASTER_RREADY  <= `MEM_RREADY;
          //AR通道
          `IO_MASTER_ARVALID <= 0;
          `IO_MASTER_ARADDR  <= `MEM_ADDR;
          `IO_MASTER_ARSIZE  <= `MEM_ARSIZE;
          `IO_MASTER_ARBURST <= 2'b0;
          `IO_MASTER_ARLEN   <= 8'b0;
          s_states <= s_0;
        end else if (is_fetch && (~happen_conflict || (conflict_state == CONFLICT_STATE_IFU))) begin
          fetch_mode <= 1'b1;
          xbar_decode <= xbar_decode_t;
          //R通道
          `IO_MASTER_RREADY  <= `IFU_RREADY;
          //AR通道
          `IO_MASTER_ARVALID <= 0;
          `IO_MASTER_ARADDR  <= `IFU_ADDR;
          `IO_MASTER_ARSIZE  <= 3'b010;
          s_states           <= s_0;
          `IO_MASTER_ARBURST <= 2'b0;
          `IO_MASTER_ARLEN   <= 8'b0;
        end else begin
          s_states <= s_states;
        end
      end
    end
  end



  //=====================================================================================
  // AXI总线通信
  // `access_done`: 通信完成信号,传递给IFU,MEM环节
  // 通信结束时，xbar_decode <= 0
  //=====================================================================================
  always @(posedge clock) begin
    if (reset) begin
      if_access_done <= 1'b0;
      mem_access_done <= 1'b0;
    end else begin
      if (xbar_decode == 4'b0010 || xbar_decode == 4'b0011 ||
          xbar_decode == 4'b0110 || xbar_decode == 4'b0101 ||
          xbar_decode == 4'b1001 || xbar_decode == 4'b1010 ||
          xbar_decode == 4'b0100 || xbar_decode == 4'b0111 ||
          xbar_decode == 4'b1000) begin
        if (s_states == s_0) begin
          if (`IO_MASTER_AWVALID && io_master_awready &&
              `IO_MASTER_WVALID  && io_master_wready) begin
            `IO_MASTER_AWVALID <= 1'b0;
            `IO_MASTER_WVALID <= 1'b0;
            s_states <= s_2;
          end else if (`IO_MASTER_ARVALID & io_master_arready) begin
            `IO_MASTER_ARVALID <= 1'b0;
            s_states <= s_3;
          end else begin  //保证是第一次进行写/读
            if (read_mode) begin
              `IO_MASTER_AWVALID <= 0; //将axi的数据传给io_master,如果不是写指令，这个值是0
              `IO_MASTER_WVALID  <= 0; //将axi的数据传给io_master,如果不是写指令，这个值是0
              `IO_MASTER_ARVALID <= `MEM_ARVALID; //将axi的数据传给io_master,如果不是读指令，这个值是0
            end else if (write_mode) begin
              `IO_MASTER_AWVALID <= `MEM_AWVALID; //将axi的数据传给io_master,如果不是写指令，这个值是0
              `IO_MASTER_WVALID  <= `MEM_WVALID; //将axi的数据传给io_master,如果不是写指令，这个值是0
              `IO_MASTER_ARVALID <= 0; //将axi的数据传给io_master,如果不是读指令，这个值是0
            end else if (fetch_mode) begin
              `IO_MASTER_AWVALID <= 0; //将axi的数据传给io_master,如果不是写指令，这个值是0
              `IO_MASTER_WVALID  <= 0; //将axi的数据传给io_master,如果不是写指令，这个值是0
              `IO_MASTER_ARVALID <= `IFU_ARVALID; //将axi的数据传给io_master,如果不是读指令，这个值是0
            end
          end
        end else if (s_states == s_2) begin
          if (io_master_bvalid) begin
            if (`IO_MASTER_BREADY) begin
              if (io_master_bresp == 0) begin  //写正确
                `IO_MASTER_BREADY <= 1'b0;
                mem_access_done <= 1;
                s_states <= s_idle;
                xbar_decode <= 4'b0;
                write_mode <= 0;
              end
            end
          end
        end else if (s_states == s_3) begin
          if (io_master_rvalid) begin
            if (`IO_MASTER_RREADY) begin
              //// 根据sram一个地址对应一个字节数据的性质，已经soc中ram一
              //// 个地址对应8字节数据的性质进行一定处理
              case (`IO_MASTER_ARADDR & 32'b11)
                32'h0: begin
                  rdata <= io_master_rdata[31:0];
                end
                32'h1: begin
                  rdata <= {8'b0, io_master_rdata[31:8]};
                end
                32'h2: begin
                  rdata <= {16'b0, io_master_rdata[31:16]};
                end
                32'h3: begin
                  rdata <= {24'b0, io_master_rdata[31:24]};
                end
              endcase
              s_states <= s_idle;
              if (read_mode) begin
                mem_access_done <= 1'b1;
                read_mode <= 1'b0;
              end else if (fetch_mode) begin
                if_access_done <= 1'b1;
                fetch_mode <= 1'b0;
              end
              xbar_decode <= 4'b0;
            end else begin
              if (read_mode) begin
                `IO_MASTER_RREADY <= `MEM_RREADY;
              end else if (fetch_mode) begin
                `IO_MASTER_RREADY <= `IFU_RREADY;
              end
            end
          end
        end
      end
    end
  end

  //======================================================================================
  // ICACHE
  //======================================================================================

  //=====================================================================================
  // ICACHE与SDRAM
  //=====================================================================================
  always @(posedge clock) begin
    if (reset) begin
    end else begin
      if (xbar_decode == 4'b1111) begin
        if (s_states == s_0) begin
          `IO_MASTER_ARBURST <= 2'b01;  //递增突发
          `IO_MASTER_ARLEN   <= 8'h03;  //4次传输，突发长度16字节(因为arsize=3'010)
          if (`IO_MASTER_ARVALID & io_master_arready) begin
            `IO_MASTER_ARVALID <= 1'b0;
            s_states <= s_3;
          end else begin  //保证是第一次进行写/读
            if (fetch_mode) begin
              `IO_MASTER_ARVALID <= `IFU_ARVALID; //将axi的数据传给io_master,如果不是读指令，这个值是0
            end else begin
              `IO_MASTER_ARVALID <= 0;
            end
          end
        end else if (s_states == s_3) begin
          `IO_MASTER_RREADY <= `IFU_RREADY;
          if (io_master_rvalid) begin
            if (`IO_MASTER_RREADY) begin
              s_states    <= s_3;
              sdram_rdata <= {sdram_rdata[95:0], io_master_rdata[31:0]};
              if (io_master_rlast) begin
                s_states      <= s_4;  //等待icacheok
                sdram_read_ok <= 1'b1;
              end
            end else begin
              if (fetch_mode) begin
                `IO_MASTER_RREADY <= `IFU_RREADY; //将axi的数据传给io_master,如果不是读指令，这个值是0
              end else begin
                `IO_MASTER_RREADY <= 0;
              end
            end
          end
        end else if (s_states == s_4) begin
          if (icache_ok == 1'b1) begin
            xbar_decode   <= 4'b0;
            sdram_read_ok <= 1'b0;
            s_states <= s_idle;
            fetch_mode <= 1'b0;
          end
        end
      end
    end
  end

  //=====================================================================================
  // AXI总线与内部设备通信
  //=====================================================================================
  wire [31:0] internal_slave_rdata;
  wire        internal_slave_arready;
  wire        internal_slave_awready;
  wire        internal_slave_wready;
  wire        internal_slave_rvalid;
  reg         internal_ren;
  reg         internal_wen;

  ysyx_22050499_ALL_SLAVE internal_slave (
      .clock        (clock),
      .reset        (reset),
      .raddr        (`MEM_ADDR),
      .waddr        (`MEM_ADDR),
      .wdata        (`MEM_WDATA),
      .wstrb        (`MEM_WSTRB),
      .xbar_decode  (xbar_decode),
      .ren          (internal_ren),
      .wen          (internal_wen),
      .slave_rdata  (internal_slave_rdata),
      .slave_arready(internal_slave_arready),
      .slave_awready(internal_slave_awready),
      .slave_wready (internal_slave_wready),
      .slave_rvalid (internal_slave_rvalid)
  );
  always @(posedge clock) begin
    /* ----------------CLINT --------------*/
    if (reset) begin
      internal_ren <= 0;
      internal_wen <= 0;
    end else if (xbar_decode == 4'b0001) begin
      if (`MEM_ARVALID) begin  //相当于ren
        if (internal_slave_arready) begin
          internal_ren    <= 1'b1;
        end
      end
      // 等待slave读完毕，接受slave读出的数据
      if (internal_slave_rvalid) begin
        if (`MEM_RREADY) begin
          internal_ren <= 1'b0;
          xbar_decode  <= 4'b0;
          read_mode <= 1'b0;
          rdata        <= internal_slave_rdata;
          mem_access_done  <= 1'b1;  //访存完成
          s_states <= s_idle; //因为之前进入了传值状态s_0,这里我懒得实现状态机
        end
      end

      //传送写地址给从设备
      if (`MEM_AWVALID) begin
        if (internal_slave_awready) begin
          //...
        end
      end

      // 传送写数据等给从设备
      if (`MEM_WVALID) begin
        if (internal_slave_wready) begin
          // 通信是不存在的，所以这里相当于乱写
        end
      end
    end
  end
endmodule
module ysyx_22050499_CLINT (
    input             clock,
    input             reset,
    input      [31:0] raddr,
    input      [ 3:0] xbar_decode,
    input             ren,
    output reg [31:0] rdata,
    output reg        arready,
    output            awready,
    output            wready,
    output reg        rvalid
);

  assign awready = 1'b1;  //恒为1,可以一直等待更新写addr

  reg [63:0] mtime;
  initial begin
    mtime = 0;
  end
  always @(posedge clock) begin
    if (reset) begin
      wready  <= 1'b0;
      arready <= 1'b0;
      rvalid  <= 1'b0;
      mtime   <= 64'b0;
    end else begin
      mtime <= mtime + 1;
      /* 写操作 */
      if (xbar_decode == 4'b0001) begin
        /* 读操作 */
        if (ren == 1'b1) begin  //读使能
          if (raddr == 32'h0200_0048) begin
            rdata  <= mtime[31:0];
            rvalid <= 1'b1;  // 已经读完成
          end else if (raddr == 32'h0200_004c) begin
            rdata  <= mtime[63:32];
            rvalid <= 1'b1;  // 已经读完成
          end
        end else begin
          arready <= 1'b1;
        end
      end else begin
        rvalid <= 1'b0;
      end
    end
  end

endmodule
module ysyx_22050499_CSRs #(
    parameter DATA_WIDTH = 32
) (
    input                       clock,
    input                       reset,
    input      [DATA_WIDTH-1:0] wdata,
    input      [           2:0] addr,
    input      [           2:0] waddr,
    input                       wen,
    input                       Ecall,
    input      [          31:0] pc,
    //output reg [DATA_WIDTH-1:0]     rf[7:0],
    output reg [DATA_WIDTH-1:0] rdata
);

  reg [DATA_WIDTH-1:0] rf[7:0];
  // rf[0] 不是csr中的值
  assign rdata = rf[addr];  //输出rs1的值
  always @(posedge clock) begin
    if (reset) begin
      rf[3'h0] <= 0;
      rf[3'h1] <= 0;
      rf[3'h2] <= 0;
      rf[3'h3] <= 0;
      rf[3'h4] <= 32'h1800;  //m_status
      rf[3'h5] <= 32'h79737978;  //mvendorid,ysyx编号
      rf[3'h6] <= 32'd22050499;  //marchid,ysyx学号
      rf[3'h7] <= 0;
    end else begin
      if (wen) rf[waddr] <= wdata;
      if (Ecall) begin
        rf[3'b010] <= pc;  //mepc
        rf[3'b011] <= 32'b1;  //mcause
      end
      rf[3'b100] <= 32'h1800;  //mstatus
      rf[3'b000] <= 32'h0;  //mstatus
    end
  end

endmodule

module ysyx_22050499_EXP(
    input [31:0]    inst,
    input [2:0]     ExtOp,
    output [31:0]   imm
); //扩展器
    reg [31:0] immI,immU,immS,immB,immJ;
    assign  immI = {{20{inst[31]}}, inst[31:20]};
    assign  immU = {inst[31:12],12'b0};
    assign  immS = {{20{inst[31]}}, inst[31:25], inst[11:7]};
    assign  immB = {{20{inst[31]}}, inst[7], inst[30:25], inst[11:8], 1'b0};
    assign  immJ = {{12{inst[31]}}, inst[19:12], inst[20], inst[30:21], 1'b0};

    assign  imm = ~ExtOp[2] & ~ExtOp[1] & ~ExtOp[0] ? immI :
                (~ExtOp[2] & ~ExtOp[1] &  ExtOp[0] ? immU :
                (~ExtOp[2] &  ExtOp[1] & ~ExtOp[0] ? immS :
                (~ExtOp[2] &  ExtOp[1] &  ExtOp[0] ? immB :
                ( ExtOp[2] & ~ExtOp[1] & ~ExtOp[0] ? immJ : 32'b0))));

endmodule

module ysyx_22050499_EXU (
    input              clock,
    input              reset,
    output     [31:0]  ex_pc,
    input      [31:0]  mem_pc,
    output     [31:0]  ex_dnpc,

    output             predict_wrong,
    output     [4:0]  ex_Rd,

    input              ex_out_ready, //下一阶段的准备信号
    input              ex_in_valid,  //上一阶段数据有效信号
    input      [208:0] ex_in_bits,   //上一阶段的数据
    output             ex_in_ready,  //当前阶段是否空闲信号
    output             ex_out_valid, //当前阶段输出数据有效信号
    output     [148:0] ex_out_bits   //当前阶段输出数据
);

  wire [31:0] alu_result;

  wire [ 0:0] MemRe          = ex_in_bits[208:208];
  assign      ex_pc          = ex_in_bits[207:176];
  wire [ 0:0] fence_i        = ex_in_bits[175:175];
  wire [31:0] imm            = ex_in_bits[174:143];
  wire [31:0] Rs1_data       = ex_in_bits[142:111];
  wire [ 0:0] ALUASrc        = ex_in_bits[110:110];
  wire [ 2:0] ALUBSrc        = ex_in_bits[109:107];
  wire [ 0:0] SUBctr         = ex_in_bits[106:106];
  wire [13:0] OPctr          = ex_in_bits[105:92];
  wire [ 2:0] BRctr          = ex_in_bits[91:89];
  wire [ 0:0] Jump           = ex_in_bits[88:88];
  wire [ 0:0] Jump_r         = ex_in_bits[87:87];
  wire [ 0:0] Branch         = ex_in_bits[86:86];
  wire [ 0:0] Ebreak         = ex_in_bits[85:85];
  wire [ 0:0] Ecall          = ex_in_bits[84:84];
  wire [ 0:0] Mret           = ex_in_bits[83:83];
  wire [31:0] Rs2_data       = ex_in_bits[82:51];
  wire [ 2:0] MemWidth       = ex_in_bits[50:48];
  wire [ 2:0] MemDataSext    = ex_in_bits[47:45];
  wire [ 0:0] MemWe          = ex_in_bits[44:44];
  wire [31:0] csrs_out       = ex_in_bits[43:12];
  wire [ 1:0] MemtoReg       = ex_in_bits[11:10];
  wire [ 2:0] csrs_addr      = ex_in_bits[9:7];
  wire [ 4:0] Rd             = ex_in_bits[6:2];
  wire [ 0:0] CSRs_We        = ex_in_bits[1:1];
  wire [ 0:0] RegWe          = ex_in_bits[0:0];

  assign ex_Rd = Rd;




  wire [31:0] srcA;
  wire [31:0] srcB;
  /* 读取或写入数据到寄存器 */
  // 选择输入源
  assign srcA = ALUASrc ? ex_pc : Rs1_data;
  assign srcB = (ALUBSrc == 3'b000 ? Rs2_data :
                (ALUBSrc == 3'b001 ? 32'b100  :
                (ALUBSrc == 3'b010 ? imm      :
                (ALUBSrc == 3'b011 ? csrs_out :
                                      32'b0))));


  wire BR_result;
  ysyx_22050499_ALU #(32) ysyx_22050499_ALU (
      .srcA      (srcA      ),
      .srcB      (srcB      ),
      .OPctr     (OPctr     ),
      .SUBctr    (SUBctr    ),
      .BRctr     (BRctr     ),
      .BR_result (BR_result ),
      .alu_result(alu_result)
  );



//=====================================================================================
// dnpc的产生逻辑
// 传递到年轻指令的年老阶段，此时dnpc必须是基于当前pc计算出来的，因此不能用
// ex_pc_t
//=====================================================================================
  assign ex_dnpc = (Jump               ? (ex_pc + imm)            :
                   (Jump_r             ? ((Rs1_data+imm)&~1)      :
                   (Branch & BR_result ? (ex_pc + imm)          :
                   (Ecall              ?  srcB                    :  //即mtvec
                   (Mret               ?  srcB + 4                :
                                         (ex_pc + 32'h4))))));



  //=====================================================================================
  // 流水级信号
  //=====================================================================================

  assign ex_out_bits  = {
    MemRe,        // bus[148:148]
    ex_pc,        // bus[147:116]
    fence_i,      // bus[115:115]
    alu_result,   // bus[114: 83]
    Rs2_data,     // bus[ 82: 51]
    MemWidth,     // bus[ 50: 48]
    MemDataSext,  // bus[ 47: 45]
    MemWe,        // bus[ 44: 44]
    csrs_out,     // bus[ 43: 12]
    MemtoReg,     // bus[ 11: 10]
    csrs_addr,    // bus[  9:  7]
    Rd,           // bus[  6:  2]
    CSRs_We,      // bus[  1:  1]
    RegWe         // bus[  0:  0]
  };

  reg ex_out_valid_t;
  assign ex_out_valid = ex_out_valid_t & (ex_pc != mem_pc);
  assign ex_in_ready  = ex_out_ready;

  assign predict_wrong = (ex_dnpc != (ex_pc + 4)); //只有接受新数据时，结果有效

  // ex_out_valid 更新逻辑
  always @(posedge clock) begin
    if (reset) begin
      ex_out_valid_t <= 0;
    end else begin
      // 获得新数据时，out_valid_t = 1
      if (ex_in_ready & ex_in_valid) begin
        ex_out_valid_t <= 1;
      // 传输数据时，out_valid_t = 0.优先级比上面的低
      end else if (ex_out_valid & ex_out_ready) begin
        ex_out_valid_t <= 0;
      end else begin
        ex_out_valid_t <= ex_out_valid_t;
      end
    end
  end


endmodule

module ysyx_22050499_GPRs #(
    parameter ADDR_WIDTH = 16,
    parameter DATA_WIDTH = 32
) (
    input                           clock,
    input                           reset,
    input [DATA_WIDTH-1:0]          wdata,
    input [3:0]                     waddr,
    input [3:0]                     rs1,
    input [3:0]                     rs2,
    input                           wen,
    //output  reg [DATA_WIDTH-1:0] rf [ADDR_WIDTH-1:0], //寄存器
    output  [DATA_WIDTH-1:0]     rs1_data,
    output  [DATA_WIDTH-1:0]     rs2_data
);
    reg [DATA_WIDTH-1:0] rf [ADDR_WIDTH-1:0]; //寄存器
    assign rs1_data = rf[rs1]; //输出rs1的值
    assign rs2_data = rf[rs2]; //输出rs1的值

    always @(posedge clock) begin
        if (reset) begin
            rf[0] <= 0;
            rf[1] <= 0;
            rf[2] <= 0;
            rf[3] <= 0;
            rf[4] <= 0;
            rf[5] <= 0;
            rf[6] <= 0;
            rf[7] <= 0;
            rf[8] <= 0;
            rf[9] <= 0;
            rf[10] <= 0;
            rf[11] <= 0;
            rf[12] <= 0;
            rf[13] <= 0;
            rf[14] <= 0;
            rf[15] <= 0;
        end else begin
            rf[0] <= 0;           //0号寄存器的特性
            if (wen && (waddr != 4'b0)) rf[waddr] <= wdata;
        end
    end

endmodule

module ysyx_22050499_ICACHE (
    input clock,
    input reset,
    input fence_i,
    input check_icache,
    input [31:0] raddr,
    input [127:0] sdram_rdata,
    input         sdram_read_ok,
    output     [31:0] icache_rdata,
    output reg icache_ok,
    output     icache_hit
);

  //=====================================================================================
  // I-Cache 参数: 规定了大小，可以根据ICACHE_LINE_SIZE调节各个参数
  // 64bit, 1 Way, 16 Line,  1Line = 4B
  //=====================================================================================
  parameter ICACHE_SIZE       = 64;                              //ICACHE 的总大小,单位为Byte
  parameter ICACHE_INST_NUM   = 16;                              //ICACHE 的指令的总数量


  parameter ICACHE_WAY        = 1;                               //暂时不采用组相联，故暂时用不到
  parameter ICACHE_LINE_SIZE  = 4 * (2**m);                      //块大小，单位Byte
  parameter ICACHE_LINE_COUNT = ICACHE_SIZE / ICACHE_LINE_SIZE;  // 块数量

  parameter m = 0;// ICACHE_LINE_SIZE  = 4* (2**m),一个块可以存多少条指令的log2
  parameter n = 4;// ICACHE_LINE_COUNT = 2**n;

  /* 随时根据m的值来注释或不注释,m = 0时注释 */
  //`define M_THAN_0 1

  //=====================================================================================
  // I-Cache 地址编码             [31    : 2    ] 适用于m >= 1
  // tag   : 对应数据的唯一标识符,[31    : m+n+2]
  // index : 块的索引号,          [m+n+1 : m+2  ]
  // offset: 块中的偏移量,        [m+1   : 2    ]
  //
  // icache[index,offset] =  inst,不过要对上tag才有效
  //=====================================================================================

  reg [        31:0]   Icache       [0 : ICACHE_INST_NUM-1];
  reg [31-(m+n+2) : 0] Icache_tag   [0 : ICACHE_LINE_COUNT-1];
  reg                  Icache_valid [0 : ICACHE_LINE_COUNT-1];

  // icache值的复位
  integer i;
  always @(posedge clock) begin
    if (reset || fence_i) begin
      // 对 Icache 数组进行复位
      for (i = 0; i < ICACHE_INST_NUM; i = i + 1) begin
        Icache[i]     <= 32'b0;  // 将每个 Icache 寄存器清零
      end
      // 对 Icache_valid 数组进行复位
      for (i = 0; i < ICACHE_LINE_COUNT; i = i + 1) begin
        Icache_valid[i] <= 1'b0;  // 将每个 Icache_valid 寄存器清零
        Icache_tag[i] <= 0;  // 将每个 Icache_tag 寄存器清零
      end
    end else begin
    end
  end

  //=====================================================================================
  // Icache 命中判断
  //=====================================================================================


  wire [29-(m+n) : 0] tag    = raddr[31    : m+n+2];
  wire [n-1      : 0] index  = raddr[m+n+1 : m+2];
  `ifdef M_THAN_0
  wire [m-1      : 0] offset = raddr[m+1   : 2  ];
  `endif

  wire [31:0] addr1 = raddr + 4;
  wire [31:0] addr2 = raddr + 8;
  wire [31:0] addr3 = raddr + 12;
  wire [29-(m+n) : 0] tag1 = addr1[31: m+n+2];
  wire [29-(m+n) : 0] tag2 = addr2[31: m+n+2];
  wire [29-(m+n) : 0] tag3 = addr3[31: m+n+2];
  wire [n-1      : 0] index1  = addr1[m+n+1 : m+2];
  wire [n-1      : 0] index2  = addr2[m+n+1 : m+2];
  wire [n-1      : 0] index3  = addr3[m+n+1 : m+2];

  `ifdef M_THAN_0
    assign icache_rdata = Icache[{index,offset}];
  `else
    assign icache_rdata = Icache[{index}];
  `endif
  assign icache_hit = (Icache_valid[index] == 1) && (Icache_tag[index] == tag);

  always @(posedge clock) begin
    if (check_icache) begin
      if (sdram_read_ok) begin
        icache_ok                   <= 1'b1;
        Icache_valid[index ]     <= 1;
        Icache_valid[index1]     <= 1;
        Icache_valid[index2]     <= 1;
        Icache_valid[index3]     <= 1;
        Icache      [index ]     <= sdram_rdata[127:96];
        Icache      [index1]     <= sdram_rdata[95 :64];
        Icache      [index2]     <= sdram_rdata[63 :32];
        Icache      [index3]     <= sdram_rdata[31 :0];
        Icache_tag  [index ]     <= tag;
        Icache_tag  [index1]     <= tag1;
        Icache_tag  [index2]     <= tag2;
        Icache_tag  [index3]     <= tag3;
      end
    end else begin
      icache_ok <= 1'b0;
    end
  end

endmodule

module ysyx_22050499_IDU (
    input              clock,
    input              reset,
    output     [31:0]  id_pc,
    input      [31:0]  mem_pc,

    output             raw_handle,
    input              predict_wrong,
    input [31:0]       ex_pc,
    input [31:0]       ex_dnpc,

    input              ex_in_ready,
    input              mem_in_ready,
    input              wb_in_ready, //其实是~wb_out_valid

    input      [  4:0] ex_Rd,
    input      [  4:0] mem_Rd,
    input      [  4:0] wb_Rd,

    input      [ 31:0] wb_pc,
    input              wb_RegWe,
    input              wb_CSRs_We,
    input      [  4:0] wb_reg_waddr,
    input      [  2:0] wb_csrs_waddr,
    input      [ 31:0] wb_reg_DataIn,
    input      [ 31:0] wb_csrs_wdata,

    input              id_out_ready, //下一阶段的准备信号
    input              id_in_valid,  //上一阶段数据有效信号
    input      [63 :0] id_in_bits,   //上一阶段的数据
    output             id_in_ready,  //当前阶段是否空闲信号
    output             id_out_valid, //当前阶段输出数据有效信号
    output     [208:0] id_out_bits   //当前阶段输出数据
);

  wire [31:0] inst = id_in_bits[31:0];
  assign  id_pc = id_in_bits[63:32];

  //=====================================================================================
  // ID内部控制信号生成逻辑
  //=====================================================================================
  wire        MemRe;
  wire        fence_i;
  wire [31:0] imm;
  wire [31:0] Rs1_data;
  wire [ 0:0] ALUASrc;
  wire [ 2:0] ALUBSrc;
  wire [ 0:0] SUBctr;
  wire [13:0] OPctr;
  wire [ 2:0] BRctr;
  wire [ 0:0] Jump;
  wire [ 0:0] Jump_r;
  wire [ 0:0] Branch;
  wire [ 0:0] Ebreak;
  wire [ 0:0] Ecall;
  wire [ 0:0] Mret;
  wire [31:0] Rs2_data;
  wire [ 2:0] MemWidth;
  wire [ 2:0] MemDataSext;
  wire [ 0:0] MemWe;
  wire [31:0] csrs_out;
  wire [ 1:0] MemtoReg;
  wire [ 2:0] csrs_addr;
  wire [ 4:0] Rd;
  wire [ 0:0] CSRs_We;
  wire [ 0:0] RegWe;


  assign fence_i = `INST_FENCE_I;
  wire [3:0] inst_type;
  assign inst_type =   (`INST_JAL || `INST_JALR || `TYPE_B || `INST_ECALL || `INST_MRET ? 4'h5 :
                       (`TYPE_IR  || `TYPE_R    || `TYPE_U                              ? 4'h1 :
                       (`TYPE_S                                                         ? 4'h3 :
                       (`TYPE_LOAD                                                      ? 4'h2 :
                       (`TYPE_IC                                                        ? 4'h4 :
                                                                                          4'hf)))));
  //always @(posedge clock) begin
    //if (status == 4'h1) begin
      //`ifdef CONFIG_STA_MODE
        //update_perf_counter({28'b0,inst_type});
      //`endif
      //id_valid <= 1'b1;
    //end else begin
      //id_valid <= 1'b0;
    //end
  //end


  wire [6:0] op = inst[6:0];
  wire [2:0] funct3 = inst[14:12];
  wire [6:0] funct7 = inst[31:25];
  wire [2:0] ExtOp;
  assign ExtOp =    (`TYPE_I || `TYPE_IC    ? 3'b000 :
                    (`TYPE_U                ? 3'b001 :
                    (`TYPE_S                ? 3'b010 :
                    (`TYPE_B                ? 3'b011 :
                    (`TYPE_J                ? 3'b100 :
                                              3'b111)))));

  assign RegWe = `TYPE_I || `TYPE_R || `TYPE_U || `INST_JAL || `INST_JALR || `TYPE_IC;
  assign MemWe = `TYPE_S;
  assign MemRe = `TYPE_LOAD;
  assign MemtoReg = ((op == 7'b0000011) ? 2'b01 : ((`TYPE_IC) ? 2'b10 : 2'b00));

  assign MemWidth = (`INST_SB ? 3'b001 : (`INST_SH ? 3'b010 : (`INST_SW ? 3'b100 : 3'b000)));
  assign MemDataSext =   (`INST_LB  ? 3'b001 :
                         (`INST_LBU ? 3'b010 :
                         (`INST_LH  ? 3'b011 :
                         (`INST_LHU ? 3'b100 :
                                      3'b000))));

  //包含了lui指令，但是lui不用ALU,所以不会有影响
  assign ALUASrc = `INST_JAL || `INST_JALR || `INST_AUIPC;  //为1时，选择pc


  assign ALUBSrc = ((`TYPE_R   || `TYPE_B)                  ? 3'b000 :  /* 选择rs2*/
                   ((`INST_JAL || `INST_JALR)               ? 3'b001 :  /* 选择4*/
                   ((`TYPE_I   || `TYPE_U     || `TYPE_S)   ? 3'b010 :  /* 选择imm*/
                   (`TYPE_IC   || `INST_ECALL || `INST_MRET ? 3'b011 :  /* 选择CSRs_OUT*/
                                                              3'b111))));  /* 不选择 */

  assign SUBctr = ((`TYPE_R) && (!`INST_ADD)) ||  /*不包含add的所有R指令*/
      ((op == 7'b0010011) && (funct3 != 3'b0))   || /*不包括addi的所有I运算相关指令(不包括load)*/
      (`TYPE_B);  /*用于大小比较*/


  assign BRctr =  (`INST_BEQ  ? 3'b000 :
                    (`INST_BNE  ? 3'b001 :
                    (`INST_BGE  ? 3'b010 :
                    (`INST_BGEU ? 3'b011 :
                    (`INST_BLT  ? 3'b100 :
                    (`INST_BLTU ? 3'b101 :
                                  3'b111))))));
  //加(减)法，按位或，操作数B(lui),小于置1,按位与，按位异或
  assign OPctr = (`INST_LUI                 ? 14'b0000_0000_0000_01 :  /* lui */
                 (`INST_ADD  || `INST_SUB   ? 14'b0000_0000_0000_10 :  /* 加减法 */
                 (`INST_SLL  || `INST_SLLI  ? 14'b0000_0000_0001_00 :  /* 逻辑右移 */
                 (`INST_SLT  || `INST_SLTI  ? 14'b0000_0000_0010_00 :  /* 有符号小于置1*/
                 (`INST_SLTU || `INST_SLTUI ? 14'b0000_0000_0100_00 :  /* 无符号小于置1*/
                 (`INST_XOR  || `INST_XORI  ? 14'b0000_0000_1000_00 :  /* 按位异或 */
                 (`INST_SRL  || `INST_SRLI  ? 14'b0000_0001_0000_00 :  /* 逻辑右移 */
                 (`INST_SRA  || `INST_SRAI  ? 14'b0000_0010_0000_00 :  /* 算术右移 */
                 (`INST_OR   || `INST_ORI   ? 14'b0000_0100_0000_00 :  /* 按位或 */
                 (`INST_AND  || `INST_ANDI  ? 14'b0000_1000_0000_00 :  /* 按位与 */
                 (`INST_CSRRW               ? 14'b0001_0000_0000_00 :  /* csrrw */
                 (`INST_CSRRS               ? 14'b0010_0000_0000_00 :  /* csrrs */
                 (`INST_CSRRC               ? 14'b0100_0000_0000_00 :  /* csrrc */
                                              14'b1000_0000_0000_00)))))))))))));  /* 默认就是加法 */

  assign CSRs_We = (`INST_CSRRS || `INST_CSRRW || `INST_CSRRC || `INST_ECALL);
  assign Ecall = `INST_ECALL;
  assign Mret = `INST_MRET;

  assign Jump = `INST_JAL;
  assign Jump_r = `INST_JALR;
  assign Branch = `TYPE_B;
  assign Ebreak = `INST_EBREAK;


  //=====================================================================================
  // imm扩展器
  //=====================================================================================
  ysyx_22050499_EXP ysyx_22050499_EXP (
      .inst (inst),
      .ExtOp(ExtOp),
      .imm  (imm)
  );


  //=====================================================================================
  // GPRs
  //=====================================================================================
  wire [4:0] Rs1;
  wire [4:0] Rs2;

  assign Rd  = inst[11:7];
  assign Rs1 = inst[19:15];
  assign Rs2 = inst[24:20];

  ysyx_22050499_GPRs #(16, 32) ysyx_22050499_GPRs (
      .clock   (clock),
      .reset   (reset),
      .wen     (wb_RegWe),
      .wdata   (wb_reg_DataIn),
      .waddr   (wb_reg_waddr[3:0]),  //rv32e只有16个寄存器
      .rs1     (Rs1[3:0]),
      .rs2     (Rs2[3:0]),
      .rs1_data(Rs1_data),
      .rs2_data(Rs2_data)
  );

  //=====================================================================================
  // CSRs
  //=====================================================================================
  assign csrs_addr = (Ecall ? 3'b001 : (Mret ? 3'b010 :
      /* 对应地址对应的csrs寄存器*/
      (imm == 32'h305 ? 3'b001 :  //mtvec
      (imm == 32'h341 ? 3'b010 :  //mepc
      (imm == 32'h342 ? 3'b011 :  //mcause
      (imm == 32'h300 ? 3'b100 :  //mstatus
      (imm == 32'hf11 ? 3'b101 :  //mvendorid,ysyx编号
      (imm == 32'hf12 ? 3'b110 :  //marchid, ysyx学号
      3'b000))))))));

  ysyx_22050499_CSRs #(32) ysyx_22050499_CSRs (
      .reset(reset),
      .clock(clock),
      .rdata(csrs_out),
      .Ecall(Ecall),
      .wen  (wb_CSRs_We),
      .addr (csrs_addr),
      .waddr(wb_csrs_waddr),
      //这里可能有点问题，之后再说
      .pc   (id_pc),
      //.rf   (csrs),
      .wdata(wb_csrs_wdata)
  );


  //=====================================================================================
  // ID译码结果
  //=====================================================================================
  assign id_out_bits = {
    MemRe,        //[208:208]
    id_pc,        //[207:176]
    fence_i,      //[175:175]
    imm,          // bus[174:143]
    Rs1_data,     // bus[142:111]
    ALUASrc,      // bus[110:110]
    ALUBSrc,      // bus[109:107]
    SUBctr,       // bus[106:106]
    OPctr,        // bus[105: 92]
    BRctr,        // bus[ 91: 89]
    Jump,         // bus[ 88: 88]
    Jump_r,       // bus[ 87: 87]
    Branch,       // bus[ 86: 86]
    Ebreak,       // bus[ 85: 85]
    Ecall,        // bus[ 84: 84]
    Mret,         // bus[ 83: 83]
    Rs2_data,     // bus[ 82: 51]
    MemWidth,     // bus[ 50: 48]
    MemDataSext,  // bus[ 47: 45]
    MemWe,        // bus[ 44: 44]
    csrs_out,     // bus[ 43: 12]
    MemtoReg,     // bus[ 11: 10]
    csrs_addr,    // bus[  9:  7]
    Rd,           // bus[  6:  2]
    CSRs_We,      // bus[  1:  1]
    RegWe         // bus[  0:  0]
  };


  //=====================================================================================
  // *  数据冒险判断逻辑
  // ** exu,mem,wbu阶段的指令一定比id阶段年老,当其中Rd与id中rs1,rs2相同时，则
  //    可能导致数据冒险
  //=====================================================================================
  //wire [4:0] ex_Rd_valid  = ex_Rd  & {5{~ex_in_ready  & (ex_pc  != id_pc)}};
  //wire [4:0] mem_Rd_valid = mem_Rd & {5{~mem_in_ready & (mem_pc != id_pc)}};
  //wire [4:0] wb_Rd_valid  = wb_Rd  & {5{~wb_in_ready  & (wb_pc  != id_pc)}};
  wire [4:0] ex_Rd_valid  = ex_Rd  & {5{(ex_pc  != id_pc)}};
  wire [4:0] mem_Rd_valid = mem_Rd & {5{(mem_pc != id_pc)}};
  wire [4:0] wb_Rd_valid  = wb_Rd  & {5{(wb_pc  != id_pc)}};

  wire happen_raw = (id_pc != 32'h3000_0000) && ~(`INST_JAL) && ~(`TYPE_U) && ~(ex_pc == wb_pc) &&
                    (Rs1  != 0  &&                              ((Rs1 == ex_Rd_valid) || (Rs1 == mem_Rd_valid) || (Rs1 == wb_Rd_valid)) ||
                    ((Rs2 != 0) && ~(`TYPE_I) && ~(`TYPE_IC) && ((Rs2 == ex_Rd_valid) || (Rs2 == mem_Rd_valid) || (Rs2 == wb_Rd_valid)))) ;

  reg happen_raw_t; //延迟一周期的发生数据冒险判断
  assign raw_handle = happen_raw | happen_raw_t; //发生数据冒险的有效处理时间

  always @(posedge clock) begin
    if (reset) begin
    end else begin
      if (id_in_valid && id_in_ready) begin //只有准备接受新数据的时候
      end
      if (happen_raw || happen_raw_t) begin
        if (happen_raw) begin
          happen_raw_t <= 1'b1;
        end else begin
          //延迟一个周期再置0
          happen_raw_t <= 1'b0;
        end
      end
    end
  end

  //=====================================================================================
  // IDU 流水级信号处理
  //=====================================================================================
  //reg    id_in_ready_t;
  reg    id_out_valid_t;
  assign id_in_ready  = (~raw_handle) & (ex_in_ready);
  assign id_out_valid = id_out_valid_t & (id_pc != ex_pc) & (~raw_handle) & (predict_wrong ? (id_pc == ex_dnpc) :1); //输出一直有效

  //=====================================================================================
  // id_out_valid_t 更新逻辑
  //=====================================================================================
  always @(posedge clock) begin
    if (reset) begin
      id_out_valid_t <= 0;
    end else begin
      // 接受新PC时，valid_t = 1;
      if (id_in_ready & id_in_valid) begin
        id_out_valid_t <= 1;
      // 能够传输给下一阶段时,valid_t = 0;
      end else if (id_out_valid & id_out_ready) begin
        id_out_valid_t <= 0;
      end else begin
        id_out_valid_t <= id_out_valid_t;
      end
    end
  end


endmodule

module ysyx_22050499_IFU (
    input             clock,
    input             reset,
    output reg [31:0] if_pc,
    /* AXI 总线通信接口*/
    input      [31:0] rdata,
    input             if_access_done,//后期可考虑换成if_rvalid不过再说
    output     [33:0] if_axi_data,
    /* icache相关控制信号 */
    input             fence_i,
    input [127:0]     sdram_rdata,
    input             sdram_read_ok,
    output            icache_ok,

    /* 控制冒险处理接口 */
    input      [31:0] ex_dnpc,
    input             predict_wrong,
    /* 流水级通信接口 */
    input             if_out_ready, //下一阶段的准备信号
    input             if_in_valid,  //上一阶段数据有效信号
    input      [9:0]  if_in_bits,   //上一阶段的数据,初始化时默认wb阶段的输出pc为pc+4
    output reg        if_in_ready,  //当前阶段是否空闲信号
    output            if_out_valid, //当前阶段输出数据有效信号
    output     [63:0] if_out_bits,
    input      [63:0] id_in_bits
);

  //=====================================================================================
  // PC 更新逻辑
  // 1. 一切正常进行时: out_valid & out_ready 时更新PC + 4
  // 2. 预测错误时predict_wrong. 若正在取错误的PC,等待取好. 然后更新PC,不用等
  // 待下一阶段ready
  //=====================================================================================
  wire [31:0] snpc;
  assign snpc = if_pc + 32'd4;

  wire update_pc;
  assign update_pc = ( if_out_ready  & if_out_valid) ||
                     ( predict_wrong & (if_pc != ex_dnpc) & (got_inst | got_inst_t));

  always @(posedge clock) begin
    if (reset) begin
      if_pc <= 32'h3000_0000;
    end else begin
      if (update_pc) begin
        if_pc <= (predict_wrong & (if_pc != ex_dnpc)) ? ex_dnpc : snpc;
      end
    end
  end


  //=====================================================================================
  // AXI 总线通信信号
  //=====================================================================================

  wire        if_arvalid;
  wire [31:0] if_araddr;
  wire        if_rready;

  assign if_arvalid = ~(got_inst || got_inst_t);
  //assign if_araddr   = ~is_sdram ? if_pc : (if_pc&32'hFFFF_FFF0); //低4位进行归零，这个位数其实要根据icache_line_size来定
  assign if_araddr   = if_pc;
  assign if_rready   = if_access_done ? 1'b0 : 1'b1;
  assign if_axi_data = {if_araddr, if_arvalid, if_rready}; //与axi总线通信,暂时不做处理


  //=====================================================================================
  // IFU 流水级信号处理
  //=====================================================================================

  assign if_in_ready  = if_out_ready & (~predict_wrong);

  // 当发生预测错误时，保证传下去的新指令是对的
  assign if_out_valid = (got_inst_t || got_inst) && (predict_wrong ? (if_pc == ex_dnpc) :1); //默认取到的指令都有效

  assign if_out_bits  = {if_pc, ~is_sdram ? (got_inst_t ? inst : rdata) : (icache_rdata)};



  //=====================================================================================
  // 取指
  //=====================================================================================
  wire is_sdram = (if_pc >= 32'ha000_0000) && (if_pc < 32'hc000_0000);
  reg [31:0] inst;
  wire got_inst; //是否获得当前PC地址的值
  reg  got_inst_t;

  assign got_inst = if_access_done || icache_hit;

  always @(posedge clock) begin
    if (reset) begin
      got_inst_t <= 0;
    end else begin
      if (got_inst || got_inst_t) begin
        if (update_pc) begin
          got_inst_t <= 0;
        end else begin
          if (~got_inst_t) begin
            inst <= rdata;
          end else begin
            inst <= inst;
          end
          got_inst_t <= 1;
        end
      end else begin
        got_inst_t <= 0;
      end
    end
  end



  //======================================================================================
  // ICACHE
  //======================================================================================

  wire check_icache = is_sdram  && (icache_ok == 0) && (icache_hit == 0);
  wire icache_hit;
  wire [31:0] icache_rdata;


  ysyx_22050499_ICACHE icache(
    .clock             (clock            ),
    .reset             (reset            ),
    .check_icache      (check_icache     ),
    .raddr             (if_pc            ),
    .sdram_rdata       (sdram_rdata      ),
    .sdram_read_ok     (sdram_read_ok    ),
    .icache_rdata      (icache_rdata     ),
    .icache_ok         (icache_ok        ),
    .icache_hit        (icache_hit       ),
    .fence_i           (fence_i          )
  );

endmodule



module ysyx_22050499_MEM (
    input              clock,
    input              reset,
    output     [ 31:0] mem_pc,
    output     [  4:0] mem_Rd,

    input              mem_access_done,
    input      [ 31:0] slave_rdata,    //接受到的读数据
    output     [ 78:0] mem_axi_data,
    input              mem_out_ready,  //下一阶段的准备信号
    input              mem_in_valid,   //上一阶段数据有效信号
    input      [148:0] mem_in_bits,    //上一阶段的数据
    output reg         mem_in_ready,   //当前阶段是否空闲信号
    output             mem_out_valid,  //当前阶段输出数据有效信号
    output     [178:0] mem_out_bits,    //当前阶段输出数据
    input      [31:0]  wb_pc
);

  wire [ 0:0] MemRe       = mem_in_bits [148:148];
  assign      mem_pc      = mem_in_bits [147:116];
  wire [0 :0] fence_i     = mem_in_bits [115 :115];

  //因为mem访存并不是立马传递数据给axi,因此数据需存到mem_out_bits,以免被更改
  wire [31:0] mem_addr    = mem_in_bits [114 :83 ];  //alu_result
  wire [31:0] mem_wdata   = mem_in_bits [82  :51 ];  //rs2_data
  wire [2 :0] MemWidth    = mem_in_bits [50  :48 ];
  wire [2 :0] MemDataSext = mem_in_bits [47  :45 ];
  wire [0 :0] MemWe       = mem_in_bits [44  : 44];  //因为要对该值会有更改，所以直接用的mem_bus_data

  wire [31:0] csrs_out    = mem_in_bits [43  :12 ];
  wire [1 :0] MemtoReg    = mem_in_bits [11  :10 ];
  wire [2 :0] csrs_addr   = mem_in_bits [9   :7  ];
  wire [4 :0] Rd          = mem_in_bits [6   :2  ];
  wire [0 :0] CSRs_We     = mem_in_bits [1   :1  ];
  wire [0 :0] RegWe       = mem_in_bits [0   :0  ];

  assign mem_Rd = Rd;

  //=====================================================================================
  // 与AXI通信的数据
  //=====================================================================================
  wire [3:0] mem_wstrb;  //mask
  assign     mem_wstrb = (MemWidth == 3'h1 ? 4'b0001 :
                         (MemWidth == 3'h2 ? 4'b0011 :
                         (MemWidth == 3'h4 ? 4'b1111 :
                                         4'b0000)));
  wire [2:0] mem_awsize = (MemWidth == 3'b001 ? 3'b000 :  //1字节
                          (MemWidth == 3'b010 ? 3'b001 :
                          (MemWidth == 3'b100 ? 3'b010 :
                                            3'b000)));//64位，这种时候一般不会传输，不用管
  wire [2:0] mem_arsize = (MemDataSext == 3'b001 ? 3'b000 :  //1字节
                          (MemDataSext == 3'b010 ? 3'b000 :  //1字节
                          (MemDataSext == 3'b011 ? 3'b001 :  //2字节
                          (MemDataSext == 3'b100 ? 3'b001 :  //2字节
                                               3'b010))));  //4字节

  reg mem_awvalid;
  reg mem_wvalid;
  reg mem_arvalid;
  wire mem_rready = mem_access_done ? 1'b0 : 1'b1;
  // 这些暂时没有用到
  wire mem_bready = mem_access_done ? 1'b0 : 1'b1;

  wire        ren = (MemtoReg == 2'b1);

  reg  [31:0] rdata;  // master
  wire [31:0] DataOut;

  //=====================================================================================
  // 这里用mem_out_bits的mem_datasext控制信号，防止因新的控制信号传递过来，导
  // 致结果错误。
  //=====================================================================================
  assign DataOut = (MemDataSext == 3'b001 ? {{24{rdata[7]}}, rdata[7  :0]} :  // LB
                   (MemDataSext == 3'b010 ? {{24{1'b0}}, rdata[7      :0]} :  // LBU
                   (MemDataSext == 3'b011 ? {{16{rdata[15]}}, rdata[15:0]} :  // LH
                   (MemDataSext == 3'b100 ? {{16{1'b0}}, rdata[15     :0]} :  // LHU
                                            rdata))));                        // LW
  assign mem_axi_data = {
    mem_arsize,
    mem_awsize,
    mem_arvalid,
    mem_rready,
    mem_addr,
    mem_awvalid,
    mem_wdata,
    mem_wstrb,
    mem_wvalid,
    mem_bready
  };

  assign mem_out_bits = {
    DataOut,       // bus[178,147]
    mem_pc,        // bus[146:115]
    mem_in_bits[114:0]
  };



  //=====================================================================================
  // 流水级信号
  //=====================================================================================

  assign mem_out_valid = ((state == STATE_NO_LS) || (state == STATE_SEND_DATA)) && mem_out_valid_t && (mem_pc != wb_pc);
  reg mem_out_valid_t;

  // mem_out_valid 更新逻辑
  always @(posedge clock) begin
    if (reset) begin
      mem_out_valid_t <= 0;
    end else begin
      if (mem_in_ready & mem_in_valid) begin
        mem_out_valid_t <= 1;
      end else if (mem_out_valid & mem_out_ready) begin
        mem_out_valid_t <= 0;
      end else begin
        mem_out_valid_t <= mem_out_valid_t;
      end
    end
  end

  // mem_in_ready 更新逻辑

  always @(posedge clock) begin
    if (reset) begin
      mem_in_ready <= 1; //初始化时为空闲状态
    end else begin

      //----------------------------------------------------------
      // 当前阶段: 空闲与忙碌状态的切换逻辑
      //----------------------------------------------------------
      if (mem_in_ready) begin
        /* 空闲状态唯有等上一阶段输出有效时，才能切换至忙碌状态*/
        if (mem_in_valid) begin
          mem_in_ready <= 0; //由于WB忙碌，故mem进入忙碌状态
        end
      end else begin
        /* 忙碌状态: 唯有下一阶段空闲时，才能切换至空闲状态*/
        if (state == STATE_NO_LS || state == STATE_SEND_DATA) begin
          mem_in_ready <= 1'b1;
        end
      end
    end
  end


  //=====================================================================================
  // AXI通信状态机
  //=====================================================================================

  localparam STATE_IDLE = 4'h0;
  localparam STATE_START_LS = 4'h1;
  localparam STATE_SEND_DATA = 4'h2;
  localparam STATE_NO_LS = 4'h3;

  reg [3:0] state;
  always @(posedge clock) begin
    if (reset) begin
    end else begin
      case (state)
        //----------------------------------------------------------
        // STATE_IDLE: if处于忙碌状态时,才能进行axi通信
        //----------------------------------------------------------
        STATE_IDLE: begin
          if (~mem_in_ready) begin
            if (MemWe) begin
              state <= STATE_START_LS;
              mem_awvalid <= 1'b1;
              mem_wvalid  <= 1'b1;
            end else if (MemRe) begin
              state <= STATE_START_LS;
              mem_arvalid <= 1'b1;
            end else begin
              state <= STATE_NO_LS;
            end
          end
        end
        //----------------------------------------------------------
        // STATE_START_LS
        //----------------------------------------------------------
        STATE_START_LS: begin
          if (mem_access_done) begin
            mem_arvalid <= 1'b0;
            mem_awvalid <= 1'b0;
            mem_wvalid  <= 1'b0;
            state <= STATE_SEND_DATA;
            rdata <= slave_rdata;
          end
        end
        //-----------------------------------------------------------------
        // STATE_SEND_DATA: 等待下一阶段ok,然后再切换到idle状态
        //-----------------------------------------------------------------
        STATE_SEND_DATA: begin
          //如果是读，这里需要将最新的dataout传下去
          if (mem_out_ready) begin
            state <= STATE_IDLE;
          end
        end
        //-----------------------------------------------------------------
        // STATE_NO_LS: 等待下一阶段ok,然后再切换到idle状态
        //-----------------------------------------------------------------
        STATE_NO_LS: begin
          if (mem_out_ready) begin
            state <= STATE_IDLE;
          end
        end
        default: begin
        end
      endcase
    end
  end

endmodule

`ifdef CONFIG_STA_MODE
import "DPI-C" function int pmem_read(input int raddr);
import "DPI-C" function void pmem_write(input int waddr, input int wdata, input byte wmask);
`endif
module ysyx_22050499_SRAM(
    input               clock,
    input               reset,
    input      [3:0]    status,
    input      [31:0]   raddr,
    input      [31:0]   waddr,
    input      [31:0]   wdata,
    input      [3:0]    wstrb,
    input      [3:0]    xbar_decode,
    output reg          ren,
    output reg          wen,
    output reg          access_done,
    output reg [31:0]   rdata,
    output reg          arready,
    output              awready,
    output              wready,
    output reg          rvalid
);

    assign awready = 1'b1; //恒为1,可以一直等待更新写addr

    wire [4:0] shift_bits;
    assign shift_bits = (raddr[1:0] == 2'b00 ? 5'b00000 :
                        (raddr[1:0] == 2'b01 ? 5'b01000 :
                        (raddr[1:0] == 2'b10 ? 5'b10000 :
                        (raddr[1:0] == 2'b11 ? 5'b11000 :
                                               5'b00000))));

    parameter [4:0] LSFR = 5'd2;
    always @ (posedge clock) begin
        /* 写操作 */
        if (reset) begin
            ren       <= 1'b0;
            wen       <= 1'b0;
            wready    <= 1'b0;
            arready   <= 1'b0;
            rvalid    <= 1'b0;
        end else begin
            if (xbar_decode == 4'b0001) begin
                if (status == 4'h9) begin
                    if (wen==1'b1 && access_done == 1'b0) begin // 有写请求时
                        `ifdef CONFIG_STA_MODE
                        pmem_write(waddr, wdata, {{4{1'b0}},wstrb}); //延迟一个周期写入数据
                        `endif
                        //wen       <= 1'b0;
                        //wready    <= 1'b0;
                        access_done <= 1'b1;//写完成
                    end else begin
                        wready <= 1'b1; //使能wready,接受新信号
                    end
                /* 读操作 */
                end else if (status == 4'hC || status == 4'h0) begin
                    if (ren==1'b1 && access_done == 1'b0) begin //读使能
                        `ifdef CONFIG_STA_MODE
                        rdata     <= pmem_read(raddr) >> shift_bits;
                        `endif
                        //ren       <= 1'b0;
                        //arready   <= 1'b0;
                        rvalid    <= 1'b1; // 已经读完成
                    end else begin
                        arready <= 1'b1;
                    end
                /* 无读写操作 */
                end else begin
                    ren       <= 1'b0; //避免因延迟导致的错误握手
                    wen       <= 1'b0; //避免因延迟导致的错误握手
                    wready    <= 1'b0;
                    arready   <= 1'b0;
                    rvalid    <= 1'b0;
                end
            end
        end
    end

endmodule
module ysyx_22050499_STATUS (
    input        clock,
    output [3:0] status
);
// status = 0 : 取指
// ---
// status = 1 : 译码
// ---
// status = 2 : 跳转类指令(jal,jalr,B-type, Ecall, Mret)的EXE阶段
// status = 3 : MEM阶段 (空)
// status = 4 : 跳转类指令的WB阶段: 写Rd
// ---
// status = 5 :  I-type(运算类) + R-type + U-type + CSR相关指令: EXE阶段
// status = 6 :  MEM阶段 (空) 多了一个fence_i来刷新icache
// status = 7 :  I-type(运算类) + R-type + U-type:  WB阶段: 写入Rd;
// ---
// status = 8 : S-type: EXE
// status = 9 : MEM阶段: 写内存
// status = A : WB阶段: (空)
// ---
// status = B: LOAD: EXE
// status = C: MEM阶段: 访存
// status = D: LOAD: 写Rd

endmodule
module ysyx_22050499_UART(
    input               clock,
    input               reset,
    input      [3:0]    status,
    input      [31:0]   raddr,
    input      [31:0]   waddr,
    input      [31:0]   wdata,
    input      [3:0]    wstrb,
    input      [3:0]    xbar_decode,
    output reg          ren,
    output reg          wen,
    output reg          access_done,
    output reg [31:0]   rdata,
    output reg          arready,
    output              awready,
    output              wready,
    output reg          rvalid
);

    assign awready = 1'b1; //恒为1,可以一直等待更新写addr

    wire [4:0] shift_bits;
    assign shift_bits = (raddr[1:0] == 2'b00 ? 5'b00000 :
                        (raddr[1:0] == 2'b01 ? 5'b01000 :
                        (raddr[1:0] == 2'b10 ? 5'b10000 :
                        (raddr[1:0] == 2'b11 ? 5'b11000 :
                                               5'b00000))));

    parameter [4:0] LSFR = 5'd2;
    always @ (posedge clock) begin
        if (reset) begin
            ren       <= 1'b0;
            wen       <= 1'b0;
            wready    <= 1'b0;
            arready   <= 1'b0;
            rvalid    <= 1'b0;
        end else begin
        /* 写操作 */
            if (xbar_decode == 4'b0010) begin
                if (status == 4'h9) begin
                    if (wen==1'b1 && access_done == 1'b0) begin // 有写请求时
                        `ifdef CONFIG_STA_MODE
                        $write("%c",wdata[7:0]);
                        $fflush;//强制刷新缓冲区
                        `endif
                        access_done <= 1'b1;//写完成
                    end else begin
                        wready <= 1'b1; //使能wready,接受新信号
                    end
                /* 读操作 */
                end else if (status == 4'hC || status == 4'h0) begin
                    if (ren==1'b1 && access_done == 1'b0) begin //读使能
                        `ifdef CONFIG_STA_MODE
                        $display("错误到达UART读功能");
                        `endif
                    end
                /* 无读写操作 */
                end else begin
                    ren       <= 1'b0; //避免因延迟导致的错误握手
                    wen       <= 1'b0; //避免因延迟导致的错误握手
                    wready    <= 1'b0;
                    arready   <= 1'b0;
                    rvalid    <= 1'b0;
                end
            end
        end
    end

endmodule
`ifdef CONFIG_STA_MODE
import "DPI-C" function void update_perf_counter(input int tags);
import "DPI-C" function void npc_update_pc(input int addr);
`endif
module ysyx_22050499 (
    input clock,
    input reset,
    input io_interrupt,

    // Master AW channel
    input         io_master_awready,
    output        io_master_awvalid,
    output [31:0] io_master_awaddr,
    output [ 3:0] io_master_awid,
    output [ 7:0] io_master_awlen,
    output [ 2:0] io_master_awsize,
    output [ 1:0] io_master_awburst,

    // Slave AW channel
    output        io_slave_awready,
    input         io_slave_awvalid,
    input  [31:0] io_slave_awaddr,
    input  [ 3:0] io_slave_awid,
    input  [ 7:0] io_slave_awlen,
    input  [ 2:0] io_slave_awsize,
    input  [ 1:0] io_slave_awburst,

    // Master W channel
    input         io_master_wready,
    output        io_master_wvalid,
    output [31:0] io_master_wdata,
    output [ 3:0] io_master_wstrb,
    output        io_master_wlast,

    // Slave W channel
    output        io_slave_wready,
    input         io_slave_wvalid,
    input  [31:0] io_slave_wdata,
    input  [ 3:0] io_slave_wstrb,
    input         io_slave_wlast,

    // Master B channel
    output       io_master_bready,
    input        io_master_bvalid,
    input  [1:0] io_master_bresp,
    input  [3:0] io_master_bid,

    // Slave B channel
    input        io_slave_bready,
    output       io_slave_bvalid,
    output [1:0] io_slave_bresp,
    output [3:0] io_slave_bid,

    // Master AR channel
    input             io_master_arready,
    output reg        io_master_arvalid,
    output     [31:0] io_master_araddr,
    output     [ 3:0] io_master_arid,
    output     [ 7:0] io_master_arlen,
    output     [ 2:0] io_master_arsize,
    output     [ 1:0] io_master_arburst,

    // Slave AR channel
    output        io_slave_arready,
    input         io_slave_arvalid,
    input  [31:0] io_slave_araddr,
    input  [ 3:0] io_slave_arid,
    input  [ 7:0] io_slave_arlen,
    input  [ 2:0] io_slave_arsize,
    input  [ 1:0] io_slave_arburst,

    // Master R channel
    output        io_master_rready,
    input         io_master_rvalid,
    input  [ 1:0] io_master_rresp,
    input  [31:0] io_master_rdata,
    input         io_master_rlast,
    input  [ 3:0] io_master_rid,

    // Slave R channel
    input         io_slave_rready,
    output        io_slave_rvalid,
    output [ 1:0] io_slave_rresp,
    output [31:0] io_slave_rdata,
    output        io_slave_rlast,
    output [ 3:0] io_slave_rid
);

  wire [120:0] o_master_axi_data;
  assign io_master_arburst = o_master_axi_data[120:119];
  assign io_master_arlen   = o_master_axi_data[118:111];
  assign io_master_araddr  = o_master_axi_data[110:79];
  assign io_master_arsize  = o_master_axi_data[78:76];
  assign io_master_awsize  = o_master_axi_data[75:73];
  assign io_master_arvalid = o_master_axi_data[72];
  assign io_master_rready  = o_master_axi_data[71];
  assign io_master_awaddr  = o_master_axi_data[70:39];
  assign io_master_awvalid = o_master_axi_data[38];
  assign io_master_wdata   = o_master_axi_data[37:6];
  assign io_master_wstrb   = o_master_axi_data[5:2];
  assign io_master_wvalid  = o_master_axi_data[1];
  assign io_master_bready  = o_master_axi_data[0];

  //没有写突发，所以在穿过去wdata后，立马结束
  assign io_master_wlast   = io_master_wvalid;

  //slave输入到axi与master的通信信号

  /*================================================*/
  /* ================ 无用信号赋值0 ===========*/
  /*================================================*/
  // Master AW channel
  assign io_master_awid    = 0;
  assign io_master_awburst = 0;
  assign io_master_awlen   = 0;

  // Slave AW channel
  assign io_slave_awready  = 0;

  // Master W channel

  // Slave W channel
  assign io_slave_wready   = 0;

  // Slave B channel
  assign io_slave_bvalid   = 0;
  assign io_slave_bresp    = 0;
  assign io_slave_bid      = 0;

  // Master AR channel
  assign io_master_arid    = 0;

  // Slave AR channel
  assign io_slave_arready  = 0;

  // Slave R channel
  assign io_slave_rvalid   = 0;
  assign io_slave_rresp    = 0;
  assign io_slave_rdata    = 0;
  assign io_slave_rlast    = 0;
  assign io_slave_rid      = 0;
  /*===================end======================*/





  //=====================================================================================
  // IFU阶段的流水级信号
  //=====================================================================================
  wire [31:0] if_pc;
  wire        if_access_done;
  wire        if_out_ready = id_in_ready;       //下一阶段准备好信号

  wire        if_in_ready;                      //当前阶段是否空闲信号
  wire        if_in_valid  = wb_out_valid;      //当前阶段输入数据有效信号
  wire [9 :0] if_in_bits   = wb_out_bits[9:0];  //当前阶段输入数据

  wire [63:0] if_out_bits;
  wire        if_out_valid;                     //当前阶段输出数据有效信号
  wire [33:0] if_axi_data;                      //if与axi总线通信数据


  /* icache 与 axi交互的信号 */
  wire icache_ok;
  wire [127:0] sdram_rdata;
  wire sdram_read_ok;

  ysyx_22050499_IFU ysyx_22050499_IFU (
    .clock                  (clock                         ),
    .reset                  (reset                         ),
    .rdata                  (rdata                         ),
    .if_pc                  (if_pc                         ),
    .ex_dnpc                (ex_dnpc                       ),
    .predict_wrong          (predict_wrong                 ),
    .icache_ok              (icache_ok                     ),
    .sdram_read_ok          (sdram_read_ok                 ),
    .sdram_rdata            (sdram_rdata                   ),
    .fence_i                (fence_i                       ),
    .if_access_done         (if_access_done                ),  //后期可考虑换成if_rvalid不过再说
    .if_axi_data            (if_axi_data                   ),
    .if_out_ready           (if_out_ready                  ),  //下一阶段的准备信号
    .if_in_valid            (if_in_valid                   ),  //上一阶段数据有效信号
    .if_in_bits             (if_in_bits                    ),  //上一阶段的数据,初始化时默认wb阶段的输出pc为pc+4
    .id_in_bits             (id_in_bits                    ),
    .if_in_ready            (if_in_ready                   ),  //当前阶段是否空闲信号
    .if_out_valid           (if_out_valid                  ),  //当前阶段输出数据有效信号
    .if_out_bits            (if_out_bits                   )  //当前阶段输出数据
  );


  //=====================================================================================
  // IF-ID 流水级间寄存器
  // !!!ID不会得到错误的PC值
  //=====================================================================================
  always @(posedge clock) begin
    if (if_out_valid && if_out_ready) begin
      id_in_bits <= if_out_bits;
    end
  end

  //=====================================================================================
  // IDU阶段的流水级信号
  //=====================================================================================
  wire [31 :0] id_pc;

  wire         id_in_ready;                 //当前阶段是否空闲信号
  wire         id_in_valid  = if_out_valid; //当前阶段输入数据有效信号
  reg  [63 :0] id_in_bits;                  //当前阶段输入数据

  wire [208:0] id_out_bits;                 //当前阶段输出数据
  wire         id_out_ready = ex_in_ready;  //下一阶段准备好信号
  wire         id_out_valid;                //当前阶段输出数据有效信号

  wire         raw_handle;

  ysyx_22050499_IDU ysyx_22050499_IDU (
    .clock                 (clock                 ),
    .reset                 (reset                 ),
    .id_pc                 (id_pc                 ),
    .wb_pc                 (wb_pc                 ),
    .mem_pc                (mem_pc                 ),
    .ex_pc                 (ex_pc                 ),

    .wb_Rd                 (wb_Rd                 ),
    .ex_Rd                 (ex_Rd                 ),
    .mem_Rd                (mem_Rd                ),

    .ex_dnpc               (ex_dnpc               ),
    .predict_wrong         (predict_wrong         ),

    .ex_in_ready           (ex_in_ready           ),
    .mem_in_ready          (mem_in_ready          ),
    .wb_in_ready           (~wb_out_valid         ), //wb阶段的特殊性，用wb_out_valid当作ready

    .wb_RegWe              (wb_RegWe              ),
    .wb_CSRs_We            (wb_CSRs_We            ),
    .wb_reg_waddr          (wb_reg_waddr          ),
    .wb_csrs_waddr         (wb_csrs_waddr         ),
    .wb_reg_DataIn         (reg_write_data        ),
    .wb_csrs_wdata         (csrs_wdata            ),
    .id_out_ready          (id_out_ready          ),  //下一阶段的准备信号
    .id_in_valid           (id_in_valid           ),  //上一阶段数据有效信号
    .id_in_bits            (id_in_bits            ),  //上一阶段的数据
    .id_in_ready           (id_in_ready           ),  //当前阶段是否空闲信号
    .id_out_valid          (id_out_valid          ),  //当前阶段输出数据有效信号
    .id_out_bits           (id_out_bits           ),  //当前阶段输出数据
    .raw_handle(raw_handle)
  );


  //=====================================================================================
  // ID-EX 流水级间寄存器
  //=====================================================================================
  always @(posedge clock) begin
    if (id_out_valid && id_out_ready) begin
      ex_in_bits <= id_out_bits;
    end
  end

  //=====================================================================================
  //EXU阶段的流水级信号
  //=====================================================================================
  wire [31 :0] ex_pc;
  wire         ex_out_ready = mem_in_ready;//下一阶段准备好信号
  wire         ex_in_valid  = id_out_valid;//当前阶段输入数据有效信号
  reg  [208:0] ex_in_bits;                 //当前阶段输入数据
  wire [148:0] ex_out_bits;                //当前阶段输出数据
  wire         ex_in_ready;                //当前阶段是否空闲信号
  wire         ex_out_valid;               //当前阶段输出数据有效信号

  /*  其他信号  */
  wire         fence_i      = ex_out_bits[115];
  wire [4:0] ex_Rd;

  wire [31 :0] ex_dnpc;
  wire         predict_wrong;

  ysyx_22050499_EXU ysyx_22050499_EXU (
    .clock                (clock                ),
    .reset                (reset                ),
    .ex_pc                (ex_pc                ),
    .ex_Rd                (ex_Rd                ),
    .mem_pc               (mem_pc               ),
    .ex_dnpc              (ex_dnpc              ),
    .predict_wrong        (predict_wrong        ),
    .ex_out_ready         (ex_out_ready         ),  //下一阶段的准备信号
    .ex_in_valid          (ex_in_valid          ),  //上一阶段数据有效信号
    .ex_in_bits           (ex_in_bits           ),  //上一阶段的数据
    .ex_in_ready          (ex_in_ready          ),  //当前阶段是否空闲信号
    .ex_out_valid         (ex_out_valid         ),  //当前阶段输出数据有效信号
    .ex_out_bits          (ex_out_bits          )   //当前阶段输出数据
  );

  //=====================================================================================
  // EX-MEM 流水级间寄存器
  //=====================================================================================
  always @(posedge clock) begin
    if (ex_out_valid && ex_out_ready) begin
      mem_in_bits <= ex_out_bits;
    end
  end

  //=====================================================================================
  // MEM阶段的流水级信号
  //=====================================================================================
  wire [31 :0] mem_pc;
  wire         mem_out_ready = wb_in_ready; //下一阶段准备好信号
  wire         mem_in_valid  = ex_out_valid;//当前阶段输入数据有效信号
  reg  [148:0] mem_in_bits;                 //当前阶段输入数据
  wire [178:0] mem_out_bits;                //当前阶段输出数据
  wire         mem_in_ready;                //当前阶段是否空闲信号
  wire         mem_out_valid;               //当前阶段输出数据有效信号
  /*   总线信号 */
  wire [ 78:0] mem_axi_data;
  wire         mem_access_done;

  wire [ 4:0]  mem_Rd;

  ysyx_22050499_MEM ysyx_22050499_MEM (
    .clock           (clock          ),
    .reset           (reset          ),
    .mem_access_done (mem_access_done),
    .mem_pc          (mem_pc         ),
    .wb_pc           (wb_pc          ),
    .mem_Rd          (mem_Rd         ),
    .slave_rdata     (rdata          ),
    .mem_axi_data    (mem_axi_data   ),
    .mem_out_ready   (mem_out_ready  ),  //下一阶段的准备信号
    .mem_in_valid    (mem_in_valid   ),  //上一阶段数据有效信号
    .mem_in_bits     (mem_in_bits    ),  //上一阶段的数据
    .mem_in_ready    (mem_in_ready   ),  //当前阶段是否空闲信号
    .mem_out_valid   (mem_out_valid  ),  //当前阶段输出数据有效信号
    .mem_out_bits    (mem_out_bits   )  //当前阶段输出数据
  );

  //=====================================================================================
  // MEM-WB 流水级间寄存器
  //=====================================================================================
  always @(posedge clock) begin
    if (mem_out_valid && mem_out_ready) begin
      wb_in_bits <= mem_out_bits;
      `ifdef CONFIG_STA_MODE
      npc_update_pc(mem_out_bits[146:115]);
      `endif
    end
  end

  //=====================================================================================
  // WB阶段的流水级信号
  //=====================================================================================
  wire [31 :0]  wb_pc;
  wire         wb_out_ready = if_in_ready; //下一阶段准备好信号
  wire         wb_in_valid = mem_out_valid;//当前阶段输入数据有效信号
  reg  [178:0] wb_in_bits;               //当前阶段输入数据
  wire [9  :0] wb_out_bits;//当前阶段输出数据
  wire         wb_in_ready;//当前阶段是否空闲信号
  wire         wb_out_valid;//当前阶段输出数据有效信号

  wire [4:0]   wb_Rd;

  //-------------------------------------------------------------------------------------
  //写回阶段相关控制信号及写数据: 只持续一个周期
  //-------------------------------------------------------------------------------------
  wire [2:0] wb_csrs_waddr = wb_in_bits[9:7] & {3{wb_out_valid}};
  wire [4:0] wb_reg_waddr  = wb_in_bits[6:2] & {5{wb_out_valid}};
  wire [0:0] wb_CSRs_We    = wb_in_bits[1:1] & {1{wb_out_valid}};
  wire [0:0] wb_RegWe      = wb_in_bits[0:0] & {1{wb_out_valid}};

  /*     其他信号  */
  wire [31 :0] reg_write_data;
  wire [31 :0] csrs_wdata;

  ysyx_22050499_WB ysyx_22050499_WB (
    .clock          (clock         ),
    .reset          (reset         ),
    .wb_pc          (wb_pc         ),
    .wb_Rd          (wb_Rd         ),
    .reg_write_data (reg_write_data),
    .csrs_wdata     (csrs_wdata    ),
    .wb_out_ready   (wb_out_ready  ),  //下一阶段的准备信号
    .wb_in_valid    (wb_in_valid   ),  //上一阶段数据有效信号
    .wb_in_bits     (wb_in_bits    ),  //上一阶段的数据
    .wb_in_ready    (wb_in_ready   ),  //当前阶段是否空闲信号
    .wb_out_valid   (wb_out_valid  ),  //当前阶段输出数据有效信号
    .wb_out_bits    (wb_out_bits   )   //当前阶段输出数据
  );


  //=====================================================================================
  // AXI4总线通信模块
  //=====================================================================================
  reg  [31:0] rdata; //重要，axi输出到IFU,MEM

  ysyx_22050499_AXI_BUS ysyx_22050499_AXI (
      .clock            (clock            ),
      .reset            (reset            ),
      .if_axi_data      (if_axi_data      ),
      .mem_axi_data     (mem_axi_data     ),
      .rdata            (rdata            ),
      .if_access_done   (if_access_done   ),
      .mem_access_done  (mem_access_done  ),
      .fence_i          (fence_i          ),
      .icache_ok        (icache_ok        ),
      .sdram_read_ok    (sdram_read_ok    ),
      .sdram_rdata      (sdram_rdata      ),
      .io_master_rvalid (io_master_rvalid ),
      .io_master_rresp  (io_master_rresp  ),
      .io_master_rdata  (io_master_rdata  ),
      .io_master_rlast  (io_master_rlast  ),
      .io_master_awready(io_master_awready),
      .io_master_wready (io_master_wready ),
      .io_master_bvalid (io_master_bvalid ),
      .io_master_bresp  (io_master_bresp  ),
      .io_master_bid    (io_master_bid    ),
      .io_master_arready(io_master_arready),
      .o_master_axi_data(o_master_axi_data)
  );


endmodule
module ysyx_22050499_WB (
    input               clock,
    input               reset,
    output     [31 :0]  wb_pc,
    output     [ 4 :0]  wb_Rd,
    output     [31 :0]  reg_write_data,
    output     [31 :0]  csrs_wdata,
    input               wb_out_ready,    //下一阶段的准备信号
    input               wb_in_valid,     //上一阶段数据有效信号
    output reg          wb_in_ready,     //当前阶段是否空闲信号
    output reg          wb_out_valid,    //当前阶段输出数据有效信号
    input      [178:0]  wb_in_bits,      //上一阶段的数据
    output reg [9  :0]  wb_out_bits      //当前阶段输出数据
);

  //reg [178:0] wb_in_bits_valid;
  wire [31:0] mem_DataOut = wb_in_bits[178:147];
  wire [31:0] alu_result  = wb_in_bits[114:83];
  wire [31:0] csrs_out    = wb_in_bits[43:12];
  wire [ 1:0] MemtoReg    = wb_in_bits[11:10];
  wire [ 4:0] Rd          = wb_in_bits[ 6:2];

  assign wb_Rd = Rd;
  //选择写入GPRs的数据
  assign reg_write_data = (MemtoReg == 2'b01 ? mem_DataOut :
                          (MemtoReg == 2'b10 ? csrs_out    :
                                               alu_result));
  // 选择写入CSRs的数据
  assign csrs_wdata = alu_result;


  //=====================================================================================
  // 流水级间通信
  //=====================================================================================
  //assign wb_out_bits =  wb_in_bits[9:0];


  assign wb_pc = wb_in_bits[146:115];
  //=====================================================================================
  // 流水级信号更新逻辑
  //=====================================================================================

  always @(posedge clock) begin
    if (reset) begin
      wb_in_ready <= 1; //初始化时为空闲状态
      wb_out_valid <= 0;
    end else begin
      wb_in_ready <= 1'b1;
      if (wb_in_valid) begin
        wb_out_valid <= 1'b1;
        wb_out_bits  <= wb_in_bits[9:0];
      end else begin
        wb_out_valid <= 1'b0;
      end
    end
  end

endmodule
