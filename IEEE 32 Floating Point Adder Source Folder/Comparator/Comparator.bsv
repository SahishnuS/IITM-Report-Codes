// OM OM OM
package Comparator;

    interface Comparator_Ifc;
        
        method Bit#(1) compare(Bit#(32) a, Bit#(32) b);
        
    endinterface
    
    module mkComparator(Comparator_Ifc);
        
        // Compare the exponent bits to determine which number is bigger
        method Bit#(1) compare(Bit#(32) a, Bit#(32) b);
            let x = pack(a[30:0] > b[30:0]);
            
            if (a[31] == b[31] && a[31] == 0) begin
                return x;
            end
            
            else if (a[31] == b[31] && a[31] == 1) begin
                return ~x;
            end
            
            else begin
                return pack(a[31] == 0);
            end
            
            // return (a[30:22] > b[30:22]) ?  1 : 0;
        endmethod
        
    endmodule

endpackage
