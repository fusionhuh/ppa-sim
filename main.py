import math
import argparse
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator,
                               FormatStrFormatter,
                               AutoMinorLocator)
from matplotlib import collections as mc
sys.path.append("py_module/")
sys.path.append("py_module/adder/GateSize/")
from random import randint
import statistics
from scipy.stats import norm
import math
import os
from py_module.file_structure import *



from py_module.adder import Adder

parser = argparse.ArgumentParser()

parser.add_argument("description")
parser.add_argument("-g", "--graph", help="Displays graph structure of selected adder (only works for basic designs)", action="store_true")

parser.add_argument("-a", "--area_list", help="List of area multipliers to be used with each adder", action="store")
parser.add_argument("--plot", help="TBD", action="store")
parser.add_argument("--hist", help="TBD", action="store")
parser.add_argument("--bin", help="TBD", action="store")
parser.add_argument("-m", "--match", help="Scales area multipliers of area_list to ensure all adders maintain same areas for histogram comparisons", action="store_true")


SIM_MAX_CASES = 30000

args = parser.parse_args()
description = args.description

draw: bool = False

adder_list: list
mode: str = "single"
if "^" in description and "," in description:
    print("main: Cannot do two contradictory actions (^ and ,) (error)")
    exit()
elif "^" in description:
    adder_list = description.split("^")
    mode = "compare"
elif "," in description:
    adder_list = description.split(",")
    mode = "concatenate"
else:
    adder_list = [description]


adder_list = [Adder(desc) for desc in adder_list]

plot_list = None
if args.plot != None:
    plot_list = args.plot.split(",")
    if "pareto" in plot_list:
        assert len(plot_list) == 2

hist_mode = None
if args.hist != None:
    if plot_list != None:
        print("main: Selected both 'hist' and 'plot' (error)")
        exit()
    hist_mode = args.hist


program = None
if args.bin != None:
    if plot_list == None and hist_mode == None:
        print("main: Program can only be run with 'hist' or 'plot' selected (error)")
        exit()
    program = args.bin
    print(f"Running '{program}'...")
    if (os.system(f"pin -t simulation/pintool/obj-intel64/MyPinTool.so -- {program}") != 0):
        print("main: Something went wrong while extracting operand data from program (error)")
        exit()
    os.system(f"rm {PIN_RESULTS_PATH}")
    os.system(f"mv operands_output.txt {PIN_RESULTS_PATH}")
elif hist_mode == "program" or plot_list == "program":
    print("main: Binary needs to be supplied with --bin option if running in 'program' mode (error)")
    exit()

fig, ax = plt.subplots()

colors = ["blue", "red", "green", "purple", "orange","yellow","cyan"]*10

def generate_random_cases(width: int, count: int)->list:
    cases_list: list = []
    upper_bound = 2**width
    for i in range(0, count):
        cases_list.append({"a":randint(0,upper_bound),"b":randint(0,upper_bound),"cin":randint(0,1)})
    return cases_list

def get_adder_label(a: Adder, area=1) -> str:
    return a.get_verbose_name() + f", area = {int(area*a.get_min_area()+1)}"

def plot_random_distribution(a: Adder, area, count: int, plot_worst_case=False):
    width = a.width
    name = get_adder_label(a, area)

    rand_cases = generate_random_cases(width, count)
    results = a.simulate([area], rand_cases, clear=False, target="individual")
    results = results[0]
    plot_distribution(results, label_name=name)
    if not plot_worst_case:
        return
    worst_case = a.get_worst_case_delays([area])[0]
    ax.plot([worst_case, worst_case], [0, count*0.2], color=colors[0])


results_map: dict = {}
curr_vert_pos = 0.9
def plot_distribution(results: list, title="Untitled", label_name="Unnamed"):
    color = colors[0]

    results_map[label_name] = results
    results_map[label_name].sort()

    worst, best = max(results), min(results)
    counts = ax.hist(results, histtype="stepfilled", bins=np.arange(best,worst*1.05,0.005), alpha=0.3, color=color, label=label_name, ec="k")[0]
    global curr_vert_pos
    height = ax.get_ylim()[1]*curr_vert_pos
    curr_vert_pos-=0.1
    counts.sort()
    max_count = counts[-1]
    mean = statistics.mean(results)
    se = statistics.stdev(results)
    ax.plot([mean, mean], [0, 1.1*height], color=color)
    ax.plot([mean-se,mean-se], [height*0.9,1.0*height], color=color)
    ax.plot([mean+se,mean+se], [height*0.9,1.0*height], color=color)
    ax.plot([mean-se, mean+se], [height*0.95,height*0.95], color=color)
    ax.plot([mean-se, best], [height*0.95,height*0.95], color = color, linestyle="dashed")
    ax.plot([mean+se, worst], [height*0.95,height*0.95], color = color, linestyle="dashed")
    ax.set(xlabel='Delay (ns)', ylabel='# of occurrences')
    ax.set_title(title)

def get_delay_percentile(a: Adder, area: int, delay: float) -> float:
    delays = results_map[get_adder_label(a, area)]
    for i in range(0, len(delays)):
        if delays[i] > delay:
            return i/len(delays)
    return 1.0

def get_percentile_delay(a: Adder, area: int, percentile: float) -> float:
    delays = results_map[get_adder_label(a, area)]
    index = int(percentile*len(delays))
    return delays[index]

def plot_area_delay_curve(a: Adder, areas_list: list, cases: list):
    results = a.simulate(areas_list, cases, clear=False, target="total")
    min_area = a.get_min_area()
    real_areas = [area*min_area for area in areas_list]
    ax.plot(real_areas, results, color=colors[0], label=a.get_verbose_name())

def plot_worst_case_delay_curve(a: Adder, areas_list: list):
    delays = a.get_worst_case_delays(areas_list)
    real_areas = [area*a.get_min_area() for area in areas_list]
    ax.plot(real_areas, delays, color=colors[0], label=a.get_verbose_name() + " (worst)", linestyle="dashed")

def plot_opt_delay_curve(a: Adder, areas_list: list):
    delays = a.get_optimizer_delays(areas_list)
    real_areas = [area*a.get_min_area() for area in areas_list]
    ax.plot(real_areas, delays, color=colors[0], label=a.get_verbose_name() + " (optimizer)", linestyle="dotted")

def get_minimum_scale_factors(adders: list) -> list:
    max_area = max([adder.get_min_area() for adder in adders])
    scale_factors = [max_area/adder.get_min_area() for adder in adders]
    return scale_factors

def plot_pareto_optimal_curve():
    lines = ax.get_lines()
    line_funcs = list(map(convert_line_to_piecewise, lines))
    xbegin, xend = 20, 1000
    xdata, ydata = list(), list()
    for i in range(xbegin, xend, 2):
        yvals = [func(i) for func in line_funcs]
        yvals.sort()
        xdata.append(i)
        ydata.append(yvals[0]-0.0001)
    ax.plot(xdata, ydata, color="black", label="Pareto Optimal Curve")

def simulate_program(a: Adder, area, program: str):
    cases = convert_pin_output_to_cases()
    print(f"Full # of cases: {len(cases)}")
    if len(cases) > SIM_MAX_CASES*2.5:
        print(f"Too many cases, randomly sampling {SIM_MAX_CASES} cases")
        new_cases = [None]*SIM_MAX_CASES
        visited = set()
        index: int = 0
        while index < SIM_MAX_CASES:
            sample: int = randint(0,SIM_MAX_CASES-1)
            while sample in visited:
                sample: int = randint(0, SIM_MAX_CASES-1)
            new_cases[index] = cases[sample]
            index += 1
            visited.add(sample)
        cases = new_cases
    results = a.simulate([area], cases, clear=False, target="individual")[0]
    plot_distribution(results, title="a", label_name=get_adder_label(a, area))
    worst_case = a.get_worst_case_delays([area])[0]
    ax.plot([worst_case, worst_case], [0, ax.get_ylim()[1]*0.2], color=colors[0])

prev_case_list = None
def convert_pin_output_to_cases() -> list:
    global prev_case_list
    if prev_case_list != None:
        return prev_case_list
    output = open(PIN_RESULTS_PATH).read()
    lines = output.split("\n")
    case_list: list = []
    for line in lines:
        if "\\" not in line: continue
        info = line.split("\\")
        opcode = info[-1]
        if opcode == "SUB":
            op2 = ~(int(info[1]))
            case_list.append({"a":info[0],"b":op2,"cin":1})
        elif opcode == "ADD":
            case_list.append({"a":info[0], "b":info[1], "cin":0})
        elif opcode == "LEA":
            pass
        else:
            print("main.convert_pin_output_to_cases: Error (unrecognized opcode)")
            exit()
    prev_case_list = case_list
    return case_list

def convert_line_to_piecewise(line):
    xdata = list(line.get_xdata())
    ydata = list(line.get_ydata())
    xranges = [(xdata[i], xdata[i+1]) for i in range(0, len(xdata)-1)]
    yranges = [(ydata[i], ydata[i+1]) for i in range(0, len(ydata)-1)]
    def piecewise(x: float) -> float:
        for i in range(0, len(xdata)-1):
            if x >= xranges[i][0] and x <= xranges[i][1]:
                interp = (x-xranges[i][0])/(xranges[i][1]-xranges[i][0])
                return yranges[i][0] + interp*(yranges[i][1]-yranges[i][0])
        return float("inf")
    return piecewise

def print_percentile_stats(a: Adder, area: int):
    print(f"{a.get_verbose_name()}, area = {int(area*a.get_min_area()+1)}")
    print(f" 99th percentile delay: {get_percentile_delay(a, area, 0.99)}")
    print(f" 95th percentile delay: {get_percentile_delay(a, area, 0.95)}")
    print(f" 50th percentile delay: {get_percentile_delay(a, area, 0.5)}")
    print(f" 5th percentile delay: {get_percentile_delay(a, area, 0.05)}")
    print(f" 1st percentile delay: {get_percentile_delay(a, area, 0.01)}")
    for delay in np.arange(0.1,0.5,0.025):
        print(f" CDF({round(delay,3)}) = {round(get_delay_percentile(a, area, delay), 3)}")

scale_factors: list
for i in range(0, len(adder_list)):
    a: Adder = adder_list[i]
    if not a.is_generated():
        a.generate_verilog()
        print(f"Done generating high-level verilog for {a.get_verbose_name()}")
    else:
        print(f"Adder '{a.get_verbose_name()}' has already been generated")
    if not a.is_synthesized():
        a.synthesize()
        print(f"Done synthesizing for {a.get_verbose_name()}")
    else:
        print(f"Adder '{a.get_verbose_name()}' has already been synthesized")
    if args.area_list == None:
        continue

for i in range(0, len(adder_list)):
    a: Adder = adder_list[i]
    scale_factors = get_minimum_scale_factors(adder_list) if args.match else [1]*len(adder_list)
    area_list = list(eval("np.arange("+args.area_list+")"))
    area_list = [area*scale_factors[i] for area in area_list]
    if not a.is_optimized(area_list):
        a.optimize(area_list)
        print(f"Done optimizing for {a.get_verbose_name()}")
    else:
        print(f"Adder '{a.get_verbose_name()}' has already been optimized")
    if plot_list != None:
        if "worst" in plot_list:
            plot_worst_case_delay_curve(a, area_list)
        if "opt" in plot_list:
            plot_opt_delay_curve(a, area_list)
        if "program" in plot_list:
            simulate_program(a, area_list[0], "ls")
        colors.pop(0)
    if hist_mode != None:
        if hist_mode == "random":
            for area in area_list:
                plot_random_distribution(a, area, 40000, plot_worst_case=True)
        elif hist_mode == "program":
            simulate_program(a, area_list[0], program="ls")
        else:
            print("Error: Invalid hist mode selected")
            exit()
        colors.pop(0)

if hist_mode != "None": 
    for i in range(0, len(adder_list)):
        a: Adder = adder_list[i]
        scale_factors = get_minimum_scale_factors(adder_list) if args.match else [1]*len(adder_list)
        area_list = list(eval("np.arange("+args.area_list+")"))
        area_list = [area*scale_factors[i] for area in area_list]
        for area in area_list:
            print_percentile_stats(a, area)

if plot_list != None:
    xleft, xright = ax.get_xlim()
    xtick_width = int((xright-xleft)/8)
    if xtick_width<10:
        xtick_width=10
    else:
        xtick_width -= xtick_width%10
    ax.xaxis.set_major_locator(MultipleLocator(xtick_width))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%g'))

    ax.xaxis.set_minor_locator(MultipleLocator(xtick_width/2))

    ytop, ybottom = ax.get_ylim()
    ytick_width = (ytop-ybottom)/10
    if ytick_width<.01:
        ytick_width=.01
    else:
        ytick_width -= ytick_width%.01
    ax.yaxis.set_major_locator(MultipleLocator(ytick_width))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%g'))

    ax.yaxis.set_minor_locator(MultipleLocator(ytick_width/2))

    ax.set_xlabel(u"Area (\u03bcm)")
    ax.set_ylabel("Delay (ns)")
    if "pareto" in plot_list:
        plot_pareto_optimal_curve()
        ax.set_title("Pareto-Optimal Area-Delay Curve")
    else:
        ax.set_title("Area-Delay Curves")
    plt.legend(loc="upper right")
    plt.show()

if hist_mode != None:
    xleft, xright = ax.get_xlim()
    xtick_width = (xright-xleft)/8
    if xtick_width<0.025:
        xtick_width=0.025
    else:
        xtick_width -= xtick_width%0.025
        pass
    ax.xaxis.set_major_locator(MultipleLocator(xtick_width))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%g'))

    ax.xaxis.set_minor_locator(MultipleLocator(xtick_width/2))

    ytop, ybottom = ax.get_ylim()
    ytick_width = int((ybottom-ytop)/8)
    if ytick_width<500:
        ytick_width=500
    else:
        ytick_width -= ytick_width%500
    ax.yaxis.set_major_locator(MultipleLocator(ytick_width))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%g'))

    ax.yaxis.set_minor_locator(MultipleLocator(ytick_width/2))

    ax.set_xlabel("Delay (ns)")
    ax.set_ylabel("Number of occurrences")
    plt.legend(loc="upper right")
    if hist_mode == "random":
        ax.set_title("Distribution of delays from random inputs")
    elif hist_mode == "program":
        ax.set_title(f"Distribution of delays from running '{args.bin}'")
    #print(results_map.keys())
    #print(get_delay_percentile(adder_list[0], results_map[results_map.keys()[0]], 0.2))
    #print(get_delay_percentile(adder_list[1], results_map[results_map.keys()[1]], 0.2))
    plt.show()