// OM OM OM
`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 23.02.2026 17:47:48
// Design Name: 
// Module Name: Word_Parser
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


module Word_Parser #(
        
        parameter int INPUTWORD = 104,
        parameter int SPLIT = 12
        
    ) (
        
        input  logic [INPUTWORD-1:0] input_word,
        output logic [(INPUTWORD + SPLIT - 1)/SPLIT - 1:0][SPLIT-1:0] output_word
        
    );
    
    // Calculate number of split words
    localparam int NUM_WORDS = (INPUTWORD + SPLIT - 1) / SPLIT;

    genvar i;

    generate
        for (i = 0; i < NUM_WORDS; i++) begin : GEN_SPLIT

            localparam int UPPER = INPUTWORD - (i * SPLIT) - 1;
            localparam int LOWER = INPUTWORD - ((i + 1) * SPLIT);

            if (LOWER >= 0) begin
                // Full slice
                assign output_word[i] = input_word[UPPER:LOWER];
            end
            else begin
                // Partial slice - zero padded
                localparam int REM_BITS = INPUTWORD - (i * SPLIT);
                assign output_word[i] = {
                    {(SPLIT-REM_BITS){1'b0}},
                    input_word[UPPER:0]
                };
            end

        end
    endgenerate
    
endmodule
