import os

def touch_file(file: str, fail_func = None):
    if os.system(f"touch {file}") != 0:
        if fail_func != None: fail_func()
        raise Exception(f"Could not create file '{file}'")

def run_command(command: str, redirect: str = "", touch_list: list = [], fail_func = None):
    for file in touch_list:
        touch_file(file)
    if redirect != "":
        if os.system(f"{command} > {redirect}") != 0:
            if fail_func != None: fail_func()
            raise Exception(f"Could not run '{command} > {redirect}'")
    else:
        if os.system(f"{command}") != 0:
            if fail_func != None: fail_func()
            raise Exception(f"Could not run '{command}'")
    