// OM OM OM
package FPA_TB;
	
	import FPA::*;
	
	module mkFPA_TB();
		
		FPA_Ifc fpa <- mkFPA();
		
		rule test;
			
			$display("\nTest 1 Completed");
			
			fpa.add(32'h00000003, 32'h00000001);
			
		endrule
		
	endmodule
	
endpackage
