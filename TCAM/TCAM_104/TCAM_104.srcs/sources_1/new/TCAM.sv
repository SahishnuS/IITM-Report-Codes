// OM OM OM
`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 23.02.2026 15:38:36
// Design Name: 
// Module Name: TCAM
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


module TCAM #(
        
//        parameter int INPUTWORD  = 32,
//        parameter int RANK       = 2,
//        parameter int BANK       = 4,
//        parameter int BRAM_WIDTH = 72,
//        parameter int BRAM_DEPTH = 512,
//        parameter int PRIORITY_ENCODER_SIZE = 256
        
        parameter int INPUTWORD  = 104,
        parameter int RANK       = 5,
        parameter int BANK       = 12,
        parameter int BRAM_WIDTH = 72,
        parameter int BRAM_DEPTH = 512,
        parameter int PRIORITY_ENCODER_SIZE = RANK * BRAM_WIDTH
        
    ) ( 
        
        input  logic clk,
        input  logic rst,
        
        input  logic                 req_valid,
        input  logic [INPUTWORD-1:0] input_word,
   
        output logic                 resp_valid,
        output logic                 result,
        output logic [$clog2(PRIORITY_ENCODER_SIZE)-1:0] matched_rule_index
        
    );
    
    // ------------------------------------------------------------
    // Local parameters
    // ------------------------------------------------------------

    localparam int ADDR_WIDTH = $clog2(BRAM_DEPTH);

    // ------------------------------------------------------------
    // 2D arrays for BRAM connections
    // ------------------------------------------------------------

    logic [RANK-1:0][BANK-1:0]                     bram_req_valid;
    logic [RANK-1:0][BANK-1:0]                     bram_resp_valid;
    logic [RANK-1:0][BANK-1:0][BRAM_WIDTH-1:0]     bram_resp_rdata;

    logic [BANK-1:0][ADDR_WIDTH-1:0]               parsed_addr;

    // ------------------------------------------------------------
    // Word to Each Bank Address Parser
    // ------------------------------------------------------------

    Word_Parser #(
    
        .INPUTWORD (INPUTWORD),
        .SPLIT     (ADDR_WIDTH)
        
    ) u_word_parser (
    
        .input_word  (input_word),
        .output_word (parsed_addr)
        
    );
    

    // Broadcast req_valid to all BRAMs
//    assign bram_req_valid = '{default: req_valid};
    generate
        for (genvar r = 0; r < RANK; r++) begin
            for (genvar b = 0; b < BANK; b++) begin
                assign bram_req_valid[r][b] = req_valid;
            end
        end
    endgenerate
    
    
    // ------------------------------------------------------------
    // Generate RANK x BANK BRAM_Manager instances
    // ------------------------------------------------------------

    genvar r, b;
    generate
        for (r = 0; r < RANK; r++) begin : GEN_RANK
            for (b = 0; b < BANK; b++) begin : GEN_BANK

                BRAM_Manager #(
                    .DEPTH    (BRAM_DEPTH),
                    .WIDTH    (BRAM_WIDTH),
                    .MEM_FILE ($sformatf("mem_%0d_%0d.mem", r + 1, b + 1))
//                    .MEM_FILE ("mem_0_0.mem")
                ) u_bram_manager (

                    .clk        (clk),
                    .rst        (rst),

                    .req_valid  (bram_req_valid[r][b]),
                    .req_write  (1'b0),
                    .req_addr   (parsed_addr[b]),
                    .req_wdata  ({BRAM_WIDTH{1'b0}}),

                    .resp_valid (bram_resp_valid[r][b]),
                    .resp_rdata (bram_resp_rdata[r][b])

                );

            end
        end
    endgenerate

    // ------------------------------------------------------------
    // Result Calculation Logic (Combinational)
    // ------------------------------------------------------------
    
    // ------------------------------------------------------------
    // Checking if BRAM Response Data is ready
    logic all_resp_valid;
    
    always_comb begin
        all_resp_valid = 1'b1;
        for (int r = 0; r < RANK; r++) begin
            for (int b = 0; b < BANK; b++) begin
                all_resp_valid &= bram_resp_valid[r][b];
            end
        end
    end
    
    // ------------------------------------------------------------
    // Doing the reduction to calculate the result
    /// AND Across Banks of all Ranks
    logic [RANK-1:0][BRAM_WIDTH-1:0] rank_data;
    
    always_comb begin
        for (int r = 0; r < RANK; r++) begin
            rank_data[r] = {BRAM_WIDTH{1'b1}};  // start with all 1s
            for (int b = 0; b < BANK; b++) begin
                rank_data[r] &= bram_resp_rdata[r][b];
            end
        end
    end
    
    /// OR Reduce across each rank
    logic [RANK-1:0] rank_match_bit;
    
    always_comb begin
        for (int r = 0; r < RANK; r++) begin
            rank_match_bit[r] = |rank_data[r];
        end
    end
    
    logic final_match;
    
    assign final_match = |rank_match_bit;
    
    // ------------------------------------------------------------
    // Driving the output 
    
    /// Uncomment this if you want three cycle read latency
//    always_ff @(posedge clk or posedge rst) begin
//        if (rst) begin
//            resp_valid <= 1'b0;
//            result     <= 1'b0;
//        end
//        else begin
//            resp_valid <= all_resp_valid;
//            result     <= final_match;
//        end
//    end
    
    /// Uncomment this if you want 2 cycle read latency
    assign resp_valid = all_resp_valid;
    assign result = final_match;
    
    
    // ------------------------------------------------------------
    // Priority Encoder Part
    // ------------------------------------------------------------
    logic [PRIORITY_ENCODER_SIZE-1:0] merged_match_data;
    logic [PRIORITY_ENCODER_SIZE-1:0] pe_input;
    
    assign merged_match_data = { >>{ rank_data } };
    
    always_comb begin
        
        for (int i = 0; i < PRIORITY_ENCODER_SIZE; i++) begin
            pe_input[i] = merged_match_data[PRIORITY_ENCODER_SIZE-i-1];
        end
        
    end
    
    Priority_Encoder #(
        
        .N(PRIORITY_ENCODER_SIZE)
        
    ) pe (
        
        .in(pe_input),
        .index(matched_rule_index)
        
    );
    
    
endmodule
