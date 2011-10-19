#!/usr/bin/python
"""Remove files and folders according to removelist

Arguments:
  <removelist>      Path to read removelist from (- for stdin)
                    Entries may be negated by prefixing a `!'
  <srcpath>         Path containing removelist entries (ie. chroot)

Options:
  --dstpath=        Path to directory which will store removed items
                    If not specified, FAB_TMPDIR will be used
"""

import os
import re
import sys
import getopt
from os.path import *

import help
import executil
from common import mkdir, get_tmpdir
from cli_common import fatal, warn

@help.usage(__doc__)
def usage():
    print >> sys.stderr, "Syntax: %s [-options] <removelist> <srcpath>" % sys.argv[0]

def parse_list(raw):
    list = {'yes': [],
            'no':  []}
    
    for line in raw.split("\n"):
        line = re.sub(r'#.*', '', line)
        line = line.strip()
        if not line:
            continue
        m = re.match("!(.*)", line)
        if m:
            list['no'].append(m.group(1))
        else:
            list['yes'].append(line)

    return list

def apply_removelist(rmlist, srcpath, dstpath=None):
    def _move(entry, srcpath, dstpath):
        entry = re.sub("^/","", entry)
        src = join(srcpath, entry)
        dst = join(dstpath, dirname(entry))
    
        if exists(src):
            mkdir(dst)
            if isdir(src):
                executil.system("mv -f %s/* %s/" % (dirname(src), dst))
            else:
                executil.system("mv -f %s %s/" % (src, dst))
        else:
            warn("entry does not exist: " + entry)

    if not dstpath:
        dstpath = get_tmpdir()

    # move entries out of srcpath
    for entry in rmlist['yes']:
        _move(entry, srcpath, dstpath)

    # move entries back into srcpath
    for entry in rmlist['no']:
        _move(entry, dstpath, srcpath)
        
def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "", 
                                       ['dstpath='])
    except getopt.GetoptError, e:
        usage(e)

    if sys.argv.count("-") == 1:
        args.insert(0, "-")
    
    if not len(args) == 2:
        usage()
    
    if args[0] == '-':
        fh = sys.stdin
    else:
        fh = file(args[0], "r")

    rmlist = parse_list(fh.read())
    srcpath = args[1]

    if not os.path.isdir(srcpath):
        fatal("srcpath does not exist: " + srcpath)

    opt_dstpath = None
    for opt, val in opts:
        if opt == '--dstpath':
            opt_removedir.append(val)

    apply_removelist(rmlist, srcpath, opt_dstpath)

        
if __name__=="__main__":
    main()

