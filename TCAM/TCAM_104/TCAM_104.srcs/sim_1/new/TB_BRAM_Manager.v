// OM OM OM
`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 23.02.2026 16:17:53
// Design Name: 
// Module Name: TB_BRAM_Manager
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////



module TB_BRAM_Manager;

    // ---------------------------------------------------------
    // Parameters
    // ---------------------------------------------------------
    parameter DEPTH = 16;
    parameter WIDTH = 32;
    localparam ADDR_WIDTH = $clog2(DEPTH);

    // ---------------------------------------------------------
    // DUT Signals
    // ---------------------------------------------------------
    reg clk;
    reg rst;

    reg                  req_valid;
    reg                  req_write;
    reg  [ADDR_WIDTH-1:0] req_addr;
    reg  [WIDTH-1:0]     req_wdata;

    wire                 resp_valid;
    wire [WIDTH-1:0]     resp_rdata;

    // ---------------------------------------------------------
    // Instantiate DUT
    // ---------------------------------------------------------
    BRAM_Manager #(
        .DEPTH(DEPTH),
        .WIDTH(WIDTH),
        .MEM_FILE("")   // No preload for this test
    ) dut (
        .clk(clk),
        .rst(rst),
        .req_valid(req_valid),
        .req_write(req_write),
        .req_addr(req_addr),
        .req_wdata(req_wdata),
        .resp_valid(resp_valid),
        .resp_rdata(resp_rdata)
    );

    // ---------------------------------------------------------
    // Clock Generation (10ns period)
    // ---------------------------------------------------------
    initial clk = 0;
    always #5 clk = ~clk;

    // ---------------------------------------------------------
    // Task: Write
    // ---------------------------------------------------------
    task write_mem;
        input [ADDR_WIDTH-1:0] addr;
        input [WIDTH-1:0] data;
        begin
            @(posedge clk);
            req_valid <= 1;
            req_write <= 1;
            req_addr  <= addr;
            req_wdata <= data;

            @(posedge clk);
            req_valid <= 0;
            req_write <= 0;
        end
    endtask

    // ---------------------------------------------------------
    // Task: Read
    // ---------------------------------------------------------
    task read_mem;
        input [ADDR_WIDTH-1:0] addr;
        begin
            @(posedge clk);
            req_valid <= 1;
            req_write <= 0;
            req_addr  <= addr;

            @(posedge clk);
            req_valid <= 0;
        end
    endtask

    // ---------------------------------------------------------
    // Monitor
    // ---------------------------------------------------------
    always @(posedge clk) begin
        if (resp_valid) begin
            $display("[%0t] READ RESPONSE: Data = 0x%h",
                     $time, resp_rdata);
        end
    end

    // ---------------------------------------------------------
    // Test Sequence
    // ---------------------------------------------------------
    initial begin

        // Initialize
        req_valid = 0;
        req_write = 0;
        req_addr  = 0;
        req_wdata = 0;

        rst = 1;
        repeat (5) @(posedge clk);
        rst = 0;

        $display("---- SIMPLE WRITES ----");

        write_mem(0, 32'hAAAA1111);
        write_mem(1, 32'hBBBB2222);
        write_mem(2, 32'hCCCC3333);

        $display("---- SIMPLE READS ----");

        read_mem(0);
        read_mem(1);
        read_mem(2);

        repeat (5) @(posedge clk);

        $display("---- PIPELINED READS ----");

        // Issue back-to-back reads (fully pipelined)
        @(posedge clk);
        req_valid <= 1;
        req_write <= 0;
        req_addr  <= 0;

        @(posedge clk);
        req_addr  <= 1;

        @(posedge clk);
        req_addr  <= 2;

        @(posedge clk);
        req_valid <= 0;

        repeat (5) @(posedge clk);

        $display("---- MIXED PIPELINED TRAFFIC ----");

        // Continuous pipeline traffic
        @(posedge clk);
        req_valid <= 1;
        req_write <= 1;
        req_addr  <= 3;
        req_wdata <= 32'hDEADBEEF;

        @(posedge clk);
        req_write <= 0;
        req_addr  <= 3;

        @(posedge clk);
        req_addr  <= 0;

        @(posedge clk);
        req_addr  <= 1;

        @(posedge clk);
        req_valid <= 0;

        repeat (10) @(posedge clk);

        $display("---- TEST COMPLETE ----");
        $stop;
    end

endmodule
