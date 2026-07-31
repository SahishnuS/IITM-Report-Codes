// OM OM OM
package FPA;
    
    import Comparator::*;
    import InfAndNaNFlagger::*;
    import Shifter::*;
    
    interface FPA_Ifc;
        method Action add(Bit#(32) num1, Bit#(32) num2);
        method Bit#(32) getResult();
	     method Bool done();
    endinterface
    
    typedef enum { ReadyForInput, CheckFlags, ValidateFlags, PerformAddition, Normalise, MergeResult, ResultComputed } Stage deriving (Bits, Eq);
    
    (* synthesize *)
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
        
        // Internal Registors and control flow registor
        Reg#(Stage) stage <- mkReg(ReadyForInput);
        Reg#(Bit#(25)) resultMantissa <- mkReg(6);
        Reg#(Bit#(8)) normalizeShiftCount <- mkReg(0);
        
        // For loading into FPGA
        Reg#(Bool) done_r <- mkReg(False);
                
        // Stage 1: Checking for Infinity & NaN
        rule checkForInfAndNaN (stage == CheckFlags);
            match { .infinity1, .nan1 } = iAndNFlagger.flagFor(n1);
            infinityN1 <= tagged Valid infinity1;
            nanN1 <= nan1;
            // $display("InfinityN1: %0b", infinity1);
            // $display("NaNN1: %0b", nan1);
            
            match { .infinity2, .nan2 } = iAndNFlagger.flagFor(n2);
            infinityN2 <= infinity2;
            nanN2 <= nan2;
            // $display("InfinityN1: %0b", infinity2);
            // $display("NaNN1: %0b", nan2);
            
            stage <= ValidateFlags;
            // $display("Checking Flags");
        endrule
        
        // Stage 2: Handle cases for Infinity and NaN
        rule flagsReady (stage == ValidateFlags);
            if (infinityN1 matches tagged Valid .infN1) begin
            
                // If any number is NaN => Result is NaN
                if (nanN1 || nanN2) begin
                    result <= 32'h7FC00000;
                    stage <= ReadyForInput;
                end
                
                // If both are Infinity with opposite signs => Result is NaN
                else if (infN1 && infinityN2 && n1[31] != n2[31]) begin
                    result <= 32'h7FC00000;
                    stage <= ResultComputed;
                end
                
                // If either one is infinity => Result is Infinity with same sign
                else if (infN1 || infinityN2) begin
                    // The result sign is same as n1 sign as add method stores bigger number in n1
                    result <= { n1[31], 31'b1111111100000000000000000000000 };
                    stage <= ResultComputed;
                end
                
                // Otherwise we need to do normal calculation.
                else begin
                    stage <= PerformAddition;
                end
            
            end
            // $display("Evaluating Flags");
        endrule
        
        
        // Stage 3: Performing Addition
        rule performAddition (stage == PerformAddition);
            
            // Step 1: Aligning
            let n2MSB = |n2[30:23];  // Decoding MSB using Exponent check for 0
            let shiftedN2Mantissa = shifter.shift({ n2MSB, n2[22:0] }, (n1[30:23] - n2[30:23]));
            
            // Step 2: Initialising bits to add.
            let n1MSB = |n1[30:23];  // Decoding MSB using Exponent check for 0
            Bit#(25) n1Mantissa = { 0, n1MSB, n1[22:0] };  // Carry bit extension
            Bit#(25) n2Mantissa = { 0, shiftedN2Mantissa };  // Carry bit extension
            
            // Step 3: Adding
            
            Bit#(25) mantissaResult = n1Mantissa;
            if (unpack(n1[31] ^ n2[31])) begin
                mantissaResult = mantissaResult - n2Mantissa;
            end
            else begin
                mantissaResult = mantissaResult + n2Mantissa;
            end
            
            resultMantissa <= mantissaResult;
            
            if (unpack(~(n1MSB & n2MSB)) && mantissaResult < 25'b00111111111111111111111) begin
                stage <= MergeResult;
            end
            else begin
                stage <= Normalise;
            end
            
            // $display("Performing Addition");
        endrule
        
        // Stage 4: Normalize mantissa
        rule normalizeMantissa (stage == Normalise);
            if (resultMantissa[24] != 1 && normalizeShiftCount <= 25) begin
                resultMantissa <= resultMantissa << 1;
                normalizeShiftCount <= normalizeShiftCount + 1;
            end
            else if (normalizeShiftCount == 26) begin
                normalizeShiftCount <= 1;
                stage <= MergeResult;
                // $display("Normalizing Mantissa");
            end
            else begin
                stage <= MergeResult;
                // $display("Normalizing Mantissa");
            end
        endrule
        
        // Stage 5: Merge Result to result registor
        rule mergeResult (stage == MergeResult);
        
            Bit#(8) resultExponent = n1[30:23] - normalizeShiftCount;
            let resultMant = resultMantissa[23:1];
            if (unpack(((|n1[30:23]) | (|n2[30:23])))) begin
                resultExponent = resultExponent + 1;
            end
            else begin
                resultMant = resultMantissa[22:0];
            end
            
            result <= { n1[31], resultExponent, resultMant };
            
            stage <= ResultComputed;
            
            // $display("Merging Result\n");
        endrule
        
        // Stage Final: Displaying the result
        rule resultComputed (stage == ResultComputed);
            // $display("N1    : %08h", n1);
            // $display("N2    : %08h", n2);
            // $display("Mant. : %025b", resultMantissa);
            // $display("Result: %08h\n", result);
            
            
            // $finish();
            
            // For loading into FPGA
            done_r <= True;
            stage <= ReadyForInput;
            
        endrule
        
        
        method Action add(Bit#(32) num1, Bit#(32) num2) if (stage == ReadyForInput);
        		
        		done_r <= False;
        		normalizeShiftCount <= 0;
        		
            // Alloting the bigger number to the register n1 and the other
            // to n2.
            // $display("Got numbers");
            if (comparator.compare(num1, num2) == 1) begin
                n1 <= num1;
                n2 <= num2;
            end
            else begin
                n1 <= num2;
                n2 <= num1;
            end
            // $display("Assigned Numbers");
            stage <= CheckFlags;
            
        endmethod
        
        // For loading in FPGA
        method Bit#(32) getResult();
        		return result;
        endmethod
        
        method Bool done();
        	return done_r;
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

Mant. : 010 0011 1101 0111 0000 1000
Result: 0 10000011    010 0011 1101 0111 0000 1000

Mant. : 010 0011 1101 0111 0000 1000
Result: 0 01111110    010 0011 1101 0111 0000 1000

*/

/*
            let shiftedMantissaResult = (mantissaResult[24] == 1) ? mantissaResult[23:1] : mantissaResult[22:0];
            
            // Step 4: Adding Exponent
            let exponentResult = (n1[30:23] + zeroExtend(mantissaResult[24]));
            
            // Step 5: Assigning to result registor
            result <= { n1[31], exponentResult[7:0], shiftedMantissaResult };
            
            
            resultIsReady <= True;
*/
