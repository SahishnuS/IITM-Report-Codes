// OM OM OM
package InfAndNaNFlagger;
    
    interface InfAndNaNFlagger_Ifc;
        
        method Tuple2#(Bool, Bool) flagFor(Bit#(32) num);
        
    endinterface
    
    module mkInfAndNaNFlagger(InfAndNaNFlagger_Ifc);
        
        method Tuple2#(Bool, Bool) flagFor(Bit#(32) num);
            let exponentAll1 = (&num[30:23]);
            let nan = unpack(exponentAll1 & |num[22:0]);
            let infinity = unpack(exponentAll1 & pack(!nan));
            
            return tuple2(infinity, nan);
        endmethod
        
    endmodule
    
endpackage
