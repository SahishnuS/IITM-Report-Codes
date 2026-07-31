// OM OM OM
package FPA;
    
    import Comparator::*;
    import InfAndNaNFlagger::*;
    import Shifter::*;
    
    interface FPA_Ifc;
        method Action add(Bit#(32) num1, Bit#(32) num2);
    endinterface
    
    typedef enum { ReadyForInput, CheckFlags, ValidateFlags, PerformAddition, Normalise, ResultComputed } Stage deriving (Bits, Eq);
    
    module mkFPA (FPA_Ifc);
        // Submodule Instantiations
        Comparator_Ifc comparator <- mkComparator();
        InfAndNaNFlagger_Ifc iAndNFlagger <- mkInfAndNaNFlagger();
        Shifter_Ifc shifter <- mkShifter();
        
        
        // Number Registors
        Reg#(Bit#(32)) n1 <- mkReg(0);
        Reg#(Bit#(32)) n2 <- mkReg(0);
        Reg#(Bit#(32)) result <- mkReg(6);
        
        
        // Flags Registors
        // For first number
        Reg#(Maybe#(Bool)) infinityN1 <- mkReg(tagged Invalid);
        Reg#(Bool) nanN1 <- mkReg(False);
        // For second number
        Reg#(Bool) infinityN2 <- mkReg(False);
        Reg#(Bool) nanN2 <- mkReg(False);
        
        
        // Internal Registors for control flow
        Reg#(Bool) readyForInput <- mkReg(True);
        Reg#(Bool) resultIsReady <- mkReg(False);
        Reg#(Bool) performAdd <- mkReg(False);
                
                
        // Stage 1: Checking for Infinity & NaN
        rule checkForInfAndNaN (!readyForInput && !isValid(infinityN1));
            match { .infinity1, .nan1 } = iAndNFlagger.flagFor(n1);
            infinityN1 <= tagged Valid infinity1;
            nanN1 <= nan1;
            $display("InfinityN1: %0b", infinity1);
            $display("NaNN1: %0b", nan1);
            
            match { .infinity2, .nan2 } = iAndNFlagger.flagFor(n2);
            infinityN2 <= infinity2;
            nanN2 <= nan2;
            $display("InfinityN1: %0b", infinity2);
            $display("NaNN1: %0b", nan2);
            
        endrule
        
        
        // Stage 2: Handle cases for Infinity and NaN
        rule flagsReady (isValid(infinityN1));
            if (infinityN1 matches tagged Valid .infN1) begin
            
                // If any number is NaN => Result is NaN
                if (nanN1 || nanN2) begin
                    result <= 32'h7FC00000;
                    resultIsReady <= True;
                end
                
                // If both are Infinity with opposite signs => Result is NaN
                else if (infN1 && infinityN2 && n1[31] != n2[31]) begin
                    result <= 32'h7FC00000;
                    resultIsReady <= True;
                end
                
                // If either one is infinity => Result is Infinity with same sign
                else if (infN1 || infinityN2) begin
                    // The result sign is same as n1 sign as add method stores bigger number in n1
                    result <= { n1[31], 31'b1111111100000000000000000000000 };
                    resultIsReady <= True;
                end
                
                // Otherwise we need to do normal calculation.
                else begin
                    performAdd <= True;
                end
            
            end
        endrule
        
        
        // Stage 3: Performing Addition
        rule performAddition (performAdd);
            
            // Step 1: Aligning
            let n2MSB = |n2[30:23];  // Decoding MSB using Exponent check for 0
            let shiftedN2Mantissa = shifter.shift({ n2MSB, n2[22:0] }, (n1[30:23] - n2[30:23]));
            
            // Step 2: Initialising bits to add.
            let n1MSB = |n1[30:23];  // Decoding MSB using Exponent check for 0
            Bit#(25) n1Mantissa = { 0, n1MSB, n1[22:0] };  // Carry bit extension
            Bit#(25) n2Mantissa = { 0, shiftedN2Mantissa };  // Carry bit extension
            
            // Step 3: Adding
            $display("n1Mantissa    : %025b", n1Mantissa);
            $display("n2Mantissa    : %025b", n2Mantissa);
            
            Bit#(25) mantissaResult = n1Mantissa;
            if (unpack(n1[31] ^ n2[31])) begin
                mantissaResult = mantissaResult - n2Mantissa;
            end
            else begin
                mantissaResult = mantissaResult + n2Mantissa;
            end
            
            $display("MantissaResult: %025b\n", mantissaResult);
            resultIsReady <= True;
        endrule
        
        // Stage 4: Normalize mantissa
        // rule Normalize
        
        
        // Stage Final: Displaying the result
        rule resultComputed (resultIsReady);
            $display("N1    : %032b", n1);
            $display("N2    : %032b", n2);
            $display("Result: %032b\n", result);
            
            $finish();
        endrule
        
        
        method Action add(Bit#(32) num1, Bit#(32) num2) if (readyForInput);
            // Alloting the bigger number to the register n1 and the other
            // to n2.
            if (comparator.compare(num1, num2) == 1) begin
                n1 <= num1;
                n2 <= num2;
            end
            else begin
                n1 <= num2;
                n2 <= num1;
            end
            
            readyForInput <= False;
            
        endmethod
        
    endmodule

endpackage



/*
N1    : 0 10000000 10010001111010111000010
N2    : 1 10000000 01000000000000000000000
Result: 0 10000001 01101000111101011100001

n1Mantissa    : 0 1.10010001111010111000010
n2Mantissa    : 0 1.01000000000000000000000
MantissaResult: 0 0.01010001111010111000010


*/

/*
            let shiftedMantissaResult = (mantissaResult[24] == 1) ? mantissaResult[23:1] : mantissaResult[22:0];
            
            // Step 4: Adding Exponent
            let exponentResult = (n1[30:23] + zeroExtend(mantissaResult[24]));
            
            // Step 5: Assigning to result registor
            result <= { n1[31], exponentResult[7:0], shiftedMantissaResult };
            
            
            resultIsReady <= True;
*/
