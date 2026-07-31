// OM OM OM
package Shifter;
    
    interface Shifter_Ifc;
        
        method Bit#(24) shift(Bit#(24) mantissa, Bit#(8) amount);
        
    endinterface
    
    module mkShifter(Shifter_Ifc);
        
        // 24 Bits to include the 1 before the decimal point
        method Bit#(24) shift(Bit#(24) mantissa, Bit#(8) amount);
            
            return mantissa >> amount;
            
        endmethod
        
    endmodule
    
endpackage
