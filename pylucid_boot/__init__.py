# coding:utf-8

import subprocess
import warnings


__version__ = (0, 0, 1)


VERSION_STRING = '.'.join(str(part) for part in __version__)


try:
    process = subprocess.Popen(
       ["git", "log", "--format='%h'", "-1", "master"],
       stdout = subprocess.PIPE
    )
except Exception, err:
    warnings.warn("Can't get git hash: %s" % err)
else:
    process.wait()
    returncode = process.returncode
    if returncode == 0:
        output = process.stdout.readline().strip().strip("'")
        if len(output) != 7:
            warnings.warn("Can't get git hash, output was: %r" % output)
        else:
            VERSION_STRING += ".git-%s" % output
    else:
        warnings.warn("Can't get git hash, returncode was: %s" % returncode)


if __name__ == "__main__":
    print VERSION_STRING
