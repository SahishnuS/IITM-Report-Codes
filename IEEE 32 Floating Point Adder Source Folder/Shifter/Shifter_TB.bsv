// OM OM OM
package Shifter_TB;
    
    import Shifter::*;
    
    module mkShifter_TB();
        
        Shifter_Ifc shifter <- mkShifter();
        
        rule test1;
            $display("\nTest 1 Completed");
            
            let shiftedValue = shifter.shift(24'hFFFFFF, 8'h6);
            $display("Shifted Value: %023b\n", shiftedValue);
            
            $finish();
        endrule
        
    endmodule
    
endpackage
