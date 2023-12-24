import os
import signal
import subprocess
import pexpect
import sys
import shlex

def touch_file(file: str, fail_func = None):
    if os.system(f"touch {file}") != 0:
        if fail_func != None: fail_func()
        raise Exception(f"Could not create file '{file}'")

def write_to_fd(fd: int, text: str):
    print(fd)
    with os.fdopen(fd, "w") as fp:
        fp.write(f"{text}\n")
        fp.close()

def interrupt_process(pid: int):
    os.kill(pid, signal.SIGINT)

def run_command(command: str, redirect: str = "", touch_list: list = [], fail_func = None, as_subprocess=False):
    for file in touch_list:
        touch_file(file)
    if as_subprocess == True:
        full_command = f'/bin/bash -c "{command} > {redirect}"'
        child: pexpect.spawn  = pexpect.spawn(full_command)
        return child

    if redirect != "":
        if os.system(f"{command} | tee {redirect}") != 0:
            if fail_func != None: fail_func()
            raise Exception(f"Could not run '{command} > {redirect}'")
    else:
        if os.system(f"{command}") != 0:
            if fail_func != None: fail_func()
            raise Exception(f"Could not run '{command}'")
    