read_liberty synthesis/NangateOpenCellLibrary_typical.lib
read_verilog optimization/verilog/base/skl/skl16_MAX_AREA_600.v
link_design skl16_600
read_sdc optimization/hardware_info.sdc
write_sdf optimization/sdf/base/skl/skl16_MAX_AREA_600.sdf
report_checks
report_checks > report_out
exit