// OM OM OM
`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03.03.2026 15:15:53
// Design Name: 
// Module Name: Priority_Encoder
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


module Priority_Encoder #(
        
        parameter int N = 16
        
    ) (
        
        input logic [N-1:0] in,
        
        output logic [$clog2(N)-1:0] index
        
    );
    
        always_comb begin
            index = '0;
        
            // Search from MSB toward LSB
            for (int i = N-1; i >= 0; i--) begin
                if (in[i]) begin
                    index = N-i-1;
                    break;
                end
            end
        end

    
endmodule
