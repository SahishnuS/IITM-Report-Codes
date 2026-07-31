// OM OM OM
`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 23.02.2026 20:37:35
// Design Name: 
// Module Name: TB_TCAM
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


module TB_TCAM;

    // -------------------------------------------------
    // Clock & Reset
    // -------------------------------------------------
    logic clk;
    logic rst;

    // -------------------------------------------------
    // DUT Signals
    // -------------------------------------------------
    logic req_valid;
    logic [103:0] input_word;

    logic resp_valid;
    logic result;
    logic [8:0] matched_rule_index;

    // -------------------------------------------------
    // Instantiate DUT (Parameters left default)
    // -------------------------------------------------
    TCAM dut (
        .clk        (clk),
        .rst        (rst),
        
        .req_valid  (req_valid),
        .input_word (input_word),
        
        .resp_valid (resp_valid),
        .result     (result),
        .matched_rule_index (matched_rule_index)
        
    );

    // -------------------------------------------------
    // Clock Generation (10ns period)
    // -------------------------------------------------
    always #5 clk = ~clk;

    // -------------------------------------------------
    // Task to send one request
    // -------------------------------------------------
    task send_req(input logic [103:0] word);
    begin
        @(posedge clk);
        input_word <= word;
        req_valid  <= 1'b1;

        @(posedge clk);
        req_valid  <= 1'b0;
    end
    endtask

    // -------------------------------------------------
    // Test Sequence
    // -------------------------------------------------
    initial begin

        // Initialize
        clk        = 0;
        rst        = 1;
        req_valid  = 0;
        input_word = 0;

        // Apply reset
        repeat (5) @(posedge clk);
        rst = 0;

        // Repeat 5 times
        repeat (5) begin
            
            // Send 32'b0
            send_req(104'b0);

            // Wait 5 cycles
            repeat (5) @(posedge clk);

            // Send 32'b1
            send_req(104'b01000000010110110110101100010101100000001101111010000010010100010000000000000000000001000000000000000110);

            // Wait 5 cycles
            repeat (5) @(posedge clk);
        end

        $display("Simulation Completed Successfully.");
        $finish;
    end

endmodule
