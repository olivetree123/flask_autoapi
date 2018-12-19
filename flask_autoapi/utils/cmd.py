import os
import subprocess


class Result(object):

    def __init__(self, output, err=None, status_code=0):
        self.stdout = output
        self.err = err
        self.status_code = status_code


class Cmd(object):

    def __init__(self, cmd):
        self.cmd = [cmd]

    def __call__(self, *args):
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            self.cmd_line = " ".join(self.cmd + list(args[0]))
        else:
            self.cmd_line = " ".join(self.cmd + list(args))
        process = subprocess.Popen(self.cmd_line, shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        status_code = process.wait()
        if not status_code:
            print("Command Success: {}".format(self.cmd_line))
        else:
            print("Command Failed: {}, ERROR_INFO: {}".format(self.cmd_line, err))
        return Result(out, err, status_code)

sys_apidoc = Cmd("/usr/local/bin/apidoc")
