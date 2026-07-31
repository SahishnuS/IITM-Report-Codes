// OM OM OM
package Comparator_tb;
    
    import Comparator::*;
    
    module mkComparator_tb ();
        Comparator_Ifc comparator <- mkComparator;
        
        rule test1;
            $display("\nComparator Module Instantiated Successfully");
            
            $display("Comparator Result: %01b\n", comparator.compare(10, 6));
            
            $finish();
        endrule
        
    endmodule
    
endpackage
