// OM OM OM
`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 23.02.2026 15:38:36
// Design Name: 
// Module Name: BRAM_Manager
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

(* keep_hierarchy = "yes", dont_touch = "yes" *)
module BRAM_Manager #(
        
        parameter int    DEPTH    = 512,
        parameter int    WIDTH    = 72 ,
        parameter string MEM_FILE = ""
        
    ) (
        
        input  logic clk,
        input  logic rst,
        
        input  logic                     req_valid,
        input  logic                     req_write,
        input  logic [$clog2(DEPTH)-1:0] req_addr,
        input  logic [WIDTH-1:0]         req_wdata,
                                         
        output logic                     resp_valid,
        output logic [WIDTH-1:0]         resp_rdata
        
    );
    
    // ---------------------------------------------------------
    // Local Parameters
    // ---------------------------------------------------------
    localparam int ADDR_WIDTH = $clog2(DEPTH);

    // ---------------------------------------------------------
    // BRAM Storage
    // ---------------------------------------------------------
    (* ram_style = "block", keep = "true", dont_touch = "yes" *)
    logic [WIDTH-1:0] bram [0:DEPTH-1];

    // ---------------------------------------------------------
    // Preload memory from file
    // ---------------------------------------------------------
    initial begin
        if (MEM_FILE != "") begin
            $display("Loading memory from %s", MEM_FILE);
            $readmemh(MEM_FILE, bram);
        end
    end

    // ---------------------------------------------------------
    // Pipeline registers
    // ---------------------------------------------------------
    logic                     req_valid_d;
    logic                     req_write_d;
    logic [ADDR_WIDTH-1:0]    req_addr_d;

    // ---------------------------------------------------------
    // Stage 1 : Capture Request
    // ---------------------------------------------------------
    always_ff @(posedge clk) begin
        if (rst) begin
            req_valid_d <= 1'b0;
            req_write_d <= 1'b0;
            req_addr_d  <= '0;
        end
        else begin
            req_valid_d <= req_valid;
            req_write_d <= req_write;
            req_addr_d  <= req_addr;
        end
    end

    // ---------------------------------------------------------
    // Write Logic (occurs in same cycle as request)
    // ---------------------------------------------------------
    always_ff @(posedge clk) begin
        if (req_valid && req_write) begin
            bram[req_addr] <= req_wdata;
        end
    end

    // ---------------------------------------------------------
    // Read Logic (1-cycle latency)
    // ---------------------------------------------------------
    always_ff @(posedge clk) begin
        if (rst) begin
            resp_rdata <= '0;
        end
        else if (req_valid_d && !req_write_d) begin
            resp_rdata <= bram[req_addr_d];
        end
    end

    // ---------------------------------------------------------
    // Response Valid Generation
    // ---------------------------------------------------------
    always_ff @(posedge clk) begin
        if (rst) begin
            resp_valid <= 1'b0;
        end
        else begin
            resp_valid <= req_valid_d && !req_write_d;
        end
    end
    
endmodule
