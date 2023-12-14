read_liberty substitution/hardware/NangateOpenCellLibrary_typical.lib;
read_verilog {verilog_file};
{submodule_text}
link_design {design_name};
write_sdf -include_typ {sdf_file_out};
read_sdc substitution/hardware/hardware_info.sdc
report_checks
exit

