// OM OM OM
`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 23.02.2026 18:55:56
// Design Name: 
// Module Name: TB_Word_Parser
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


`timescale 1ns / 1ps

module TB_Word_Parser;

    parameter INPUTWORD = 32;
    parameter SPLIT     = 9;
    localparam NUM_WORDS = (INPUTWORD + SPLIT - 1) / SPLIT;

    reg  [INPUTWORD-1:0] input_word;
    wire [NUM_WORDS-1:0][SPLIT-1:0] output_word;

    // Instantiate DUT
    Word_Parser #(
        .INPUTWORD(INPUTWORD),
        .SPLIT(SPLIT)
    ) DUT (
        .input_word(input_word),
        .output_word(output_word)
    );

    integer i;

    initial begin
        // Apply test input
        input_word = 32'b00000000000000000000111111000001;

        #10;

        $display("Input Word  = %b", input_word);
        for (i = 0; i < NUM_WORDS; i = i + 1) begin
            $display("output_word[%0d] = %b", i, output_word[i]);
        end

        $finish;
    end

endmodule
