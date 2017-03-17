#!/usr/bin/env python


from __future__ import print_function, absolute_import, division
import argparse
import sys
import glob
import os
import subprocess as sp
sys.path.insert(0, os.path.dirname(__file__))
from ngqa_common import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--file-root', required=True)
    parser.add_argument('-m', '--manifest-path', required=True)
    parser.add_argument('-w', '--webserver-dir', required=True)
    args = parser.parse_args()

    if not os.path.isdir(args.webserver_dir):
        os.makedirs(args.webserver_dir)

    ROOT_DIR = os.path.realpath(os.path.dirname(__file__))

    create_empty(args.manifest_path)

    jobs = [
        'plot_flux_vs_rms.py',
        ]

    for script_name in jobs:
        script_path = os.path.join(ROOT_DIR, 'SysremPipe', script_name)
        if not os.path.isfile(script_path):
            print('Cannot find script {}, skipping'.format(script_path),
                file=sys.stderr)
            continue

        cmd = [sys.executable, script_path, '--file-root', args.file_root,
            '--manifest-path', args.manifest_path]
        print(cmd)
        sp.check_call(cmd)

    copy_manifest_files(args.manifest_path, args.webserver_dir)
