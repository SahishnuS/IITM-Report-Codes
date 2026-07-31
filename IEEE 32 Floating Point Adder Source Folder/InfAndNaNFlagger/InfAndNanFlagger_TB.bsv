// OM OM OM
package InfAndNaNFlagger_TB;
    
    import InfAndNaNFlagger::*;
    
    module mkInfAndNaNFlagger_TB();
        
        InfAndNaNFlagger_Ifc inFlagger <- mkInfAndNaNFlagger();
        
        rule test1;
            
            match { .infFlag, .nanFlag } = inFlagger.flagFor(32'h7F800000);
            
            $display("\nTest 1 Completed");
            $display("Infinity Flag: %0b", infFlag);
            $display("NaN Flag     : %0b\n", nanFlag);
            
            $finish();
        endrule
        
    endmodule
    
endpackage
