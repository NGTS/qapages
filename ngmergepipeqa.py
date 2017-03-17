#!/usr/bin/env python


from __future__ import print_function, absolute_import, division
import argparse
import sys
import glob
import os
import subprocess as sp


def create_empty(filename):
    with open(filename, 'w') as outfile:
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--file-root', required=True)
    parser.add_argument('-m', '--manifest-path', required=True)
    parser.add_argument('-w', '--webserver-dir', required=True)
    args = parser.parse_args()

    ROOT_DIR = os.path.realpath(os.path.dirname(__file__))

    create_empty(args.manifest_path)

    jobs = [
        'plot_astrometry_stats.py',
        ]

    to_copy_files = []
    for script_name in jobs:
        script_path = os.path.join(ROOT_DIR, 'MergePipe', script_name)
        if not os.path.isfile(script_path):
            print('Cannot find script {}, skipping'.format(script_path),
                file=sys.stderr)
            continue

        cmd = [sys.executable, script_path, '--file-root', args.file_root,
            '--manifest-path', args.manifest_path]
        print(cmd)
        sp.check_call(cmd)
