from .globals import *
from .constants import *
from .profile import Profile
import statistics
import numpy as np

def print_percentile_delay(percentile: float):
    if da.curr_results_profile == None:
        print("Please simulate something or select a profile to continue.")
    curr_results_profile: Profile = da.data[da.curr_results_profile]
    working_adder_list = curr_results_profile.adders
    working_description_list = curr_results_profile.descriptions
    working_area_list = curr_results_profile.areas
    for i, adder in working_adder_list:
        for j, description in working_adder_list:
            pass

def print_operands_within_percentile(percentile: float):
    if da.curr_results_profile == None:
        print("Please simulate something or select a profile to continue.")
    if percentile<1: percentile*=100
    curr_results_profile: Profile = da.data[da.curr_results_profile]
    working_adder_list = curr_results_profile.adders
    working_description_list = curr_results_profile.descriptions
    working_area_list = curr_results_profile.areas
    operands = curr_results_profile.operands
    context = curr_results_profile.context

    for i, adder in enumerate(working_adder_list):
        description: str = working_description_list[i]
        for j, area in enumerate(working_area_list):
            print(f"{description}, area {area*adder.get_min_area()}")
            delays = curr_results_profile.get_delays(description, area)
            print(f"Operands length: {len(operands)}")
            print(f"Delays length: {len(delays)}")
            threshold_delay = np.percentile(delays, percentile)
            for k, delay in enumerate(delays):
                if threshold_delay > delay:
                    op1 = f"{int(operands[k][0]['a']):#0{16}x}".upper()
                    op2 = f"{int(operands[k][0]['b']):#0{16}x}".upper()
                    op3 = f"{int(operands[k][1]['a']):#0{16}x}".upper()
                    op4 = f"{int(operands[k][1]['b']):#0{16}x}".upper()

                    context1, context2 = context[k][0], context[k][1]

                    addr1, src1, src2 = context1[0], context1[1], context1[2]
                    addr2, src3, src4 = context2[0], context2[1], context2[2]


                    print(f" Vector {k} -> @{addr1} op1/{src1}: {op1}, op2/{src2}: {op2}, @{addr2} op3/{src3}: {op3}, op4/{src4}: {op4}, delay: {delay}")

def print_operands_above_percentile(percentile: float):
    if da.curr_results_profile == None:
        print("Please simulate something or select a profile to continue.")
    if percentile<1: percentile*=100
    curr_results_profile: Profile = da.data[da.curr_results_profile]
    working_adder_list = curr_results_profile.adders
    working_description_list = curr_results_profile.descriptions
    working_area_list = curr_results_profile.areas
    operands = curr_results_profile.operands
    context = curr_results_profile.context


    for i, adder in enumerate(working_adder_list):
        description: str = working_description_list[i]
        for j, area in enumerate(working_area_list):
            print(f"{description}, area {area*adder.get_min_area()}")
            delays = curr_results_profile.get_delays(description, area)
            print(f"Operands length: {len(operands)}")
            print(f"Delays length: {len(delays)}")
            threshold_delay = np.percentile(delays, percentile)
            for k, delay in enumerate(delays):
                if threshold_delay < delay:
                    op1 = f"{int(operands[k][0]['a']):#0{16}x}".upper()
                    op2 = f"{int(operands[k][0]['b']):#0{16}x}".upper()
                    op3 = f"{int(operands[k][1]['a']):#0{16}x}".upper()
                    op4 = f"{int(operands[k][1]['b']):#0{16}x}".upper()

                    context1, context2 = context[k][0], context[k][1]

                    addr1, src1, src2 = context1[0], context1[1], context1[2]
                    addr2, src3, src4 = context2[0], context2[1], context2[2]

                    prefix = f" Vector {k} -> "
                    print(f" Vector {k} -> @{addr1} op1/{src1}: {op1}, op2/{src2}: {op2}\n{' '*len(' Vector  -> ')}@{addr2} op3/{src3}: {op3}, op4/{src4}: {op4}, delay: {delay}")


def _get_delay_percentile(delays, delay):
    for i in range(0, len(delays)):
        if delays[i] > delay:
            return i/len(delays)
    return 1.0

def _get_percentile_delay(description, area, percentile: float):
    delays= da.data[da.curr_results_profile].get_delays(description, area)
    if percentile < 1: percentile*=100
    return np.percentile(delays, percentile)