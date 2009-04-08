# coding: utf-8

"""
    Create/update the virtualenv bootstrap script BOOTSTRAP_SCRIPT from the BOOTSTRAP_SOURCE file.
"""

import virtualenv


BOOTSTRAP_SCRIPT = "pylucid-boot.py"
BOOTSTRAP_SOURCE = "source-pylucid-boot.py"


def create_bootstrap_script():
    print "read source bootstrap script: %r" % BOOTSTRAP_SOURCE
    f = file(BOOTSTRAP_SOURCE, "r")
    content = f.read()
    f.close()
    
    print "Create/Update %r" % BOOTSTRAP_SCRIPT
    
    output = virtualenv.create_bootstrap_script(content)
    f = file(BOOTSTRAP_SCRIPT, 'w')
    f.write(output)
    f.close()


if __name__ == "__main__":
    create_bootstrap_script()
    print " -- END -- "