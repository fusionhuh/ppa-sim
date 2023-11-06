from .globals import *
from .constants import *
import numpy as np
import matplotlib.pyplot as plt
from .helpers import _get_adder_label

def draw_hist():
    if da.curr_results_profile == None:
        print("Please simulate something before drawing a histogram.")
        return
    
    profile_data = da.data[da.curr_results_profile]

    global fig_num
    fig = plt.figure(fig_num)
    ax = fig.subplots()

    iteration = 0 # for keeping track of COLORS
    extra_plotting_info: list = []
    for i, a in enumerate(da.adder_list):
        if da.adder_str_list[i] not in profile_data["delay_lists"].keys():
            print(f"Data has not been collected for adder '{da.adder_str_list[i]}'")
            return
        description = da.adder_str_list[i]
        area_list = profile_data["worst_delays"][description].keys()
        for j, area in enumerate(area_list):
            worst,best = profile_data["worst_delays"][description][area], profile_data["best_delays"][description][area]
            sta_worst = profile_data["sta_worst_delays"][description][area]
            delays = profile_data["delay_lists"][description][area]
            label =_get_adder_label(a, area)
            mean = profile_data["means"][description][area]
            stdev = profile_data["stdevs"][description][area]
            ax.hist(delays, histtype = "stepfilled", bins=np.arange(best,worst*1.05,0.005), alpha=0.3, color=COLORS[iteration], label=label, ec="k")            
            extra_plotting_info.append((worst, best, mean, stdev, iteration, sta_worst))
            
            iteration+=1

    extra_plotting_info = sorted(extra_plotting_info, key=lambda x: x[2], reverse=True)
    ylim = ax.get_ylim()[1]
    curr_vert_pos = 0.9
    for info in extra_plotting_info:
        height = ylim*curr_vert_pos
        curr_vert_pos-=0.1
        worst, best, mean, stdev, iteration, sta_worst = info
        color = COLORS[iteration]
        ax.plot([mean, mean], [0, height+0.05*ylim], color=color)
        ax.plot([mean-stdev,mean-stdev], [height-0.05*ylim, height], color=color, linestyle="dashed")
        ax.plot([mean+stdev,mean+stdev], [height-0.05*ylim, height], color=color, linestyle="dashed")
        ax.plot([mean-stdev, mean+stdev], [height-0.025*ylim,height-0.025*ylim], color=color, linestyle="dashed")
        ax.plot([mean-stdev, best], [height-0.025*ylim,height-0.025*ylim], color = color, linestyle="dotted")
        ax.plot([mean+stdev, worst], [height-0.025*ylim,height-0.025*ylim], color = color, linestyle="dotted")
        ax.plot([best,best], [height-0.05*ylim, height], color=color, linestyle="dotted")
        ax.plot([worst,worst], [height-0.05*ylim, height], color=color, linestyle="dotted")
        ax.plot([sta_worst, sta_worst], [0, ylim*0.2], color=color)
    if profile_data["mode"] == "random":
        ax.set_title("Distribution of delays from random inputs")
    elif profile_data["mode"] == "program":
        ax.set_title("Distribution of delays from running program (add title)")
    ax.legend(loc="upper right")
    fig_num+=1