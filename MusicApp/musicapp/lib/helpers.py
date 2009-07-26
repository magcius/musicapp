"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
# Import helpers as desired, or define your own, ie:
from webhelpers.html import escape
# from webhelpers.html.tags import *


SIZE_SUFFIXES = [("bytes",2**10), ("KiB",2**20), ("MiB",2**30), ("GiB",2**40), ("TiB",2**50)]

def pretty_size(size):
    if size == 0:
        return u""
    for suf, lim in SIZE_SUFFIXES:
        if size > lim:
            continue
        else:
            return u"%d %s" % (round(size/float(lim/2**10),2), suf)
