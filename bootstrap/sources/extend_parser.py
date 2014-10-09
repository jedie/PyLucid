# coding: utf-8

# imports not really needed and just for the editor warning ;)
import sys
from bootstrap.sources.prefix_code import CHOICES


def extend_parser(parser):
    # --- CUT here ---
    parser.add_option("-t", "--type", type="string",
        dest="install_type", default=None,
        help="PyLucid install type: %s (Choose via menu!)" % ", ".join(list(CHOICES.values()))
    )