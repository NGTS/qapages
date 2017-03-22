#/usr/bin/env python


from __future__ import print_function, absolute_import, division
import argparse
import fitsio
import subprocess as sp
import sys
import os
sys.path.insert(0, os.path.join(
    os.path.dirname(__file__),
    '..'))
from ngqa_common import find_file, find_previous_job_files, update_manifest


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--file-root', required=True)
    parser.add_argument('-m', '--manifest-path', required=True)
    args = parser.parse_args()

    sysrem_cataloguename = find_file(args.file_root, 'sysrem_catalogue')
    with fitsio.FITS(sysrem_cataloguename) as infile:
        prod_id = infile[0].read_header()['prod_id']

    pre_sysrem_files = find_previous_job_files(prod_id, 'sysrem')

    # Filenames to pass to fluxbin_analysis.py
    flux_filename = find_file(args.file_root, 'sysrem_flux')
    catalogue_filename = find_file(args.file_root, 'sysrem_catalogue')
    imagelist_filename = pre_sysrem_files['imagelist']
    flags_filename = pre_sysrem_files['flags']
    fluxerr_filename = pre_sysrem_files['flux3_err']

    output_filename = 'qa_fluxbin.html'
    fluxbin_path = os.path.join(
        os.path.dirname(__file__), 'fluxbin_analysis.py')
    cmd = [sys.executable, fluxbin_path,
           '--flux', flux_filename,
           '--catalogue', catalogue_filename,
           '--imagelist', imagelist_filename,
           '--flags', flags_filename,
           '--fluxerr', fluxerr_filename,
           '--output', os.path.join(os.getcwd(), output_filename)]
    sp.check_call(cmd)

    update_manifest(output_filename, args.manifest_path)