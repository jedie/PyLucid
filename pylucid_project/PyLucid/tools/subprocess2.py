# -*- coding: utf-8 -*-

"""
    subprocess with timeout
    ~~~~~~~~~~~~~~~~~~~~~~~

    http://www.python-forum.de/topic-14301.html
    http://www.python-forum.de/post-23692.html#23692

    Use some parts from the user 'droptix':
        http://www.python-forum.de/post-96180.html#96180
"""

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = "GNU General Public License (GPL)"
__version__ = "SVN $Rev: $"


import os, sys, subprocess, signal, time

if sys.platform == "win32":
    import win32api
    import win32con
    import win32process
    #FIRST_SIGNAL = win32con.CTRL_C_EVENT
    FIRST_SIGNAL = win32con.CTRL_BREAK_EVENT
else:
    import signal
    FIRST_SIGNAL = signal.SIGTERM # 15
    SECOND_SIGNAL = signal.SIGKILL # 9

DEFAULT_TIMEOUT = 5
DEFAULT_WAIT_TIME = 0.25



class Subprocess2(object):
    """
    subprocess with timeout
    """
    def __init__(self, *args, **kwags):
        self.killed = False
        self.kill_count = 0

        self.timeout = kwags.pop("timeout", DEFAULT_TIMEOUT)
        self.wait_time = kwags.pop("wait_time", DEFAULT_WAIT_TIME)
        self.debug = kwags.pop("debug", False)

        self.start_time = time.time()
        self.process = subprocess.Popen(*args, **kwags)
        self.wait_loop()

    def wait_loop(self):
        """
        Sleep and check if the subprocess is ended, if not terminate it.
        """
        while True:
            time.sleep(self.wait_time)
            returncode = self.process.poll()
            if self.debug: print "debug: returncode:", returncode
            if returncode != None:
                if self.debug: print "debug: process is terminated"
                return
            if time.time() - self.start_time >= self.timeout:
                if self.debug: print "debug: timeout arrived"
                self.killed = True
                self.kill_count += 1
                try:
                    if sys.platform == "win32":
                        self.win32_kill()
                        return # We can only directly terminat the process
                    else:
                        self.os_kill()
                finally:
                    if self.kill_count >= 2:
                        return


    def win32_kill(self):
        """
        terminate the subprocess under windows
        """
        if self.debug: print "debug: terminal process"
        h = win32api.OpenProcess(
            win32con.PROCESS_ALL_ACCESS, False,
            self.process.pid
        )
        handle = h.handle
        win32process.TerminateProcess(handle, 1)

    def os_kill(self):
        """
        terminate the subporocess using os.kill()
        """
        if self.kill_count == 1:
            if self.debug: print "debug: kill with FIRST_SIGNAL"
            kill_signal = FIRST_SIGNAL
        else:
            if self.debug: print "debug: kill with SECOND_SIGNAL"
            kill_signal = SECOND_SIGNAL

        os.kill(self.process.pid, kill_signal)



if __name__ == "__main__":
    print "try 'ls'..."
    p = Subprocess2("ls",
        stdout=subprocess.PIPE,
        shell=True, timeout = 1, debug = True
    )
    print "returncode:", p.process.returncode
    print "killed:", p.killed
    print "stdout: %r" % p.process.stdout.read()

    print "-"*79

    print "start the python interpreter..."
    p = Subprocess2("python",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True, timeout = 1, debug = True
    )
    print "returncode:", p.process.returncode
    print "killed:", p.killed
    if not p.killed:
        # read only if process ended normaly, otherwise the read blocked!
        print "stdout: %r" % p.process.stdout.read()
        print "stderr: %r" % p.process.stderr.read()

    print "-"*79
