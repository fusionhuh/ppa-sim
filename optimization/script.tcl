read_liberty hardware/NangateOpenCellLibrary_typical.lib
read_verilog optimization/verilog/base/hybrid/hybrid64_3_MAX_AREA_630.v
link_design hybrid64_3_630
write_sdf optimization/sdf/base/hybrid/hybrid64_3_MAX_AREA_630.sdf
read_sdc hardware/hardware_info.sdc
report_checks
report_checks > report_out
exit