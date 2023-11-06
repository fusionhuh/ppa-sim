import sys
import numpy as np
import matplotlib.pyplot as plt
sys.path.append("py_module/")
sys.path.append("py_module/adder/GateSize/")
import os
from py_module.file_structure import *
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter

from random import randint

from py_module.main.classification import classify, bool_classify
from py_module.main.histogram import draw_hist
from py_module.main.simulation import simulate, quicksim, parametrize_ops
from py_module.main.globals import *
from py_module.main.environment import *
from py_module.main.delay_analysis import print_operands_within_percentile, print_operands_above_percentile
from py_module.main.substitution import synthesize_hls_file, substitute_adders

from py_module.hlsynthesizer import HLSynthesizer

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

def show():
    plt.show()

def quit():
    if (os.system("make clean_log > /dev/null") != 0):
        print("main: Could not clean log files (Makefile error)")

    #if (os.system("make clean_out > /dev/null") != 0):
    #    print("main: Could not clean output files (Makefile error)")
    exit(0)

def call(command: str):
    os.system(command)

def cust_eval(statement: str):
    syscalls = ["ls", "clear"]
    statements = statement.split(";")
    # assert statement is in command list or something
    for statement in statements:
        if statement == "":
            continue
        if statement in syscalls:
            os.system(statement)
            continue
        eval(statement)
    
def gui():
    app = QApplication(["bla"])
    w = QWidget()
    b = QLabel(w)
    b.setText("ppa-sim")

    w.setGeometry(100,100,200,50)
    b.move(50,20)
    w.setWindowTitle("ppa-sim")
    w.show()
    sys.exit(app.exec_())





command_completer = WordCompleter(["add_adder(", "remove_adder(", "print_adder_list()", '""', "quit()", "call(", "set_area_list(", 
                                   "print_area_list()", "simulate(", "set_match(", "print_match()", "draw_hist()", "set_program(", 
                                   "print_program()", "print_path()", "set_instruction_category(", "print_instruction_category()",
                                   "print_operands_within_percentile()", "print_operands_above_percentile()"], ignore_case=False)

while True:
    try:
        profile = "" if da.curr_results_profile == None else f"('{da.curr_results_profile}') "
        user_input = prompt(f"{profile}>> ", history=FileHistory("interface/history.txt"), completer=command_completer)
        cust_eval(user_input)
    except NameError as e:
        print(e)
        print("Invalid command specified.")
    except SyntaxError as e:
        print(e)
        print("Invalid command syntax.")
    #except TypeError as e:
    #    print(e)
    #    print("Something went wrong internally. (TypeError)")
  #  except KeyError as e:
  #      print(e)
  #      print("Something went wrong internally. (KeyError)")
    except KeyboardInterrupt:
        print("\nCommand stopped.")
    #except Exception as e:
    #    print(e)
    #    print("Generic error.")
