read_liberty substitution/hardware/NangateOpenCellLibrary_typical.lib
read_verilog {verilog_file}
link_design {design_name}
write_sdf {sdf_file}
read_sdc substitution/hardware/hardware_info.sdc
report_checks
report_checks > report_out
exit

