# coding: utf-8

"""
    Source PyLucid bootstrap script.
"""

import os, subprocess

def after_install(options, home_dir):
    etc = os.path.join(home_dir, 'etc')
    if not os.path.exists(etc):
        os.makedirs(etc)
        
    easy_install = os.path.join(home_dir, 'bin', 'easy_install')
        
    subprocess.call([easy_install, '--always-copy', 'pip'])