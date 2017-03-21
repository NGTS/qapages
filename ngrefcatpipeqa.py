#!/usr/bin/env python


from __future__ import print_function, absolute_import, division
import argparse
import sys
import glob
import os
import subprocess as sp
import glob
sys.path.insert(0, os.path.dirname(__file__))
from ngqa_common import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--manifest-path', required=True)
    parser.add_argument('-w', '--webserver-dir', required=True)
    args = parser.parse_args()

    if not os.path.isdir(args.webserver_dir):
        os.makedirs(args.webserver_dir)

    ROOT_DIR = os.path.realpath(os.path.dirname(__file__))

    create_empty(args.manifest_path)
    to_copy_files = glob.glob('*.png') + glob.glob('*.pdf') + glob.glob('*.jpg')

    for filename in to_copy_files:
        update_manifest(filename, args.manifest_path)

    copy_manifest_files(args.manifest_path, args.webserver_dir)
