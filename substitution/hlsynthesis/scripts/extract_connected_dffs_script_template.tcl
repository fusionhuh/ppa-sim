read_liberty substitution/hardware/NangateOpenCellLibrary_typical.lib;
read_verilog \\DESIGN_FILE;
\\ADDER_READS
link_design \\DESIGN_NAME;
write_sdf -include_typ temp.sdf;
read_sdc substitution/hardware/hardware_info.sdc
set adder [get_cells "\\ADDER_INST_NAME"]
set dffs [all_registers]
set paths [find_timing_paths -unconstrained -group_count 100000 -through $adder -to $dffs]
set paths_len [llength $paths];
puts "NUM_CONNECTIONS:$paths_len"

for {set i 0} {$i < $paths_len} {incr i} {
	set curr_path [lindex $paths $i];
	set curr_points [get_property -object_type PathEnd $curr_path points];
	set points_len [llength $curr_points];
for {set j 0} {$j < $points_len} {incr j} {
	set curr_point [lindex $curr_points $j]
	set curr_point_pin [get_property -object_type PathRef $curr_point pin]
	set curr_point_pin_name [get_property -object_type pin $curr_point_pin full_name];
	puts "PORT:$curr_point_pin_name";
	set curr_point_net [get_nets -of_objects $curr_point_pin];
	if {$curr_point_net != "NULL"} {
		set curr_point_net_name [get_property -object_type net $curr_point_net full_name];
		puts "NET:$curr_point_net_name";
	}
}
	set endpoint [get_property -object_type PathEnd $curr_path endpoint];
	set pin_name [get_property -object_type pin $endpoint full_name];
	puts "DEST_PIN:$pin_name";
}
exit;

