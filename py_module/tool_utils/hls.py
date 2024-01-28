from hlsynthesizer._verilog import *
from .command import *
from file_structure import *
from hlsynthesizer._file import *

def synthesize_file(file: str, top_fname: str, clock_time: float, output_path: str, tb_path: str, xml_tb: str=None):
    tb_dir = tb_path.rsplit("/", 1)[0]
    def fix_bambu_files():
        dir, file = tb_path.rsplit("/", 1)
        os.system(f"mkdir {dir}")
        os.system(f"touch {tb_path}")
        #os.system("rm array_ref_*.mem") need to devise a way for getting rid of these files without messing up synthesis
        os.system("rm a.out")
        os.system(f"rm simulate_{top_fname}.sh")
        os.system("rm bambu_results_*.xml")
        os.system(f"rm ./synthesize_Synthesis_{top_fname}.sh")
        os.system(f"mv {top_fname}.v {output_path}")
        os.system(f"mv HLS_output/simulation/testbench_{top_fname}.v {tb_path}")
        os.system(f"mv HLS_output/simulation/values.txt {tb_dir}/values.txt")
        os.system("rm -rf HLS_output/")
        os.system("rm results.txt")
        os.system("touch array.mem")

    def fix_bambu_tb():
        print(tb_path)
        text = read_text(tb_path)
        sdf_annotate_statement = f'''
initial
begin
$sdf_annotate("{HLS_WORKING_SDF_PATH}", {top_fname});
'''
        text = text.replace("  initial\n  begin\n", sdf_annotate_statement, 1)
        text = text.replace(f'"{os.getcwd()}/HLS_output//simulation/values.txt"', f'"{tb_dir}/values.txt"')
        old_clock_switching_statement = "always # `HALF_CLOCK_PERIOD clock = !clock;"
        assert text.count(old_clock_switching_statement) == 1
        new_clock_switching_statement = "time half_clock_time = \\\\CLOCK_TIME/2;\nalways # half_clock_time clock = !clock;\n" 
        text = text.replace(old_clock_switching_statement, new_clock_switching_statement)
        text = re.sub(r'res_file = \$fopen\("[\S\s]+?","w"\);', fr'res_file = $fopen("{HLS_WORKING_DIR}/results\\\\THREAD_ID.txt", "w");', text)
        write_text(tb_path, text)

    def generate_tb_xml():
        pass

    xml_tb_filepath: str

    if xml_tb == "generate":
        xml_tb_filepath = generate_tb_xml()
    else:
        xml_tb_filepath = xml_tb
    
    if xml_tb == None or xml_tb == "default":
        print("HERE")
        run_command(f'bambu {file} --clock-period={clock_time} --top-fname={top_fname} --simulate --simulator=ICARUS')    
    else:
        run_command(f'bambu {file} --generate-tb="{xml_tb_filepath}" --clock-period={clock_time} --top-fname={top_fname} --simulate --simulator=ICARUS')    
    fix_bambu_files()
    fix_bambu_tb()
    bambu_out_text = read_text(output_path)
    bambu_out_text = update_plus_modules(bambu_out_text)
    bambu_out_text = convert_minus_modules(bambu_out_text)
    bambu_out_text = update_signed_instances(bambu_out_text)
    write_text(output_path, bambu_out_text)