#/usr/bin/env python


from __future__ import print_function, absolute_import, division
import argparse
import fitsio
import sys
import os
sys.path.insert(0, os.path.join(
    os.path.dirname(__file__),
    '..'))
from ngqa_common import *
from matplotlib.ticker import LogFormatter, LogLocator


# This was computed by comparing the `mag_mean` in the archive database,
# with the corresponding NOMAD r-magnitude, computing the zero point per
# object and taking the sigma-clipped mean. Full floating point value:
# 20.08804549381188 but we round as there's no point using the full
# precision.
APPROXIMATE_ZERO_POINT = 20.1


def compute_stellar_magnitudes(post_sysrem_hdu, pre_sysrem_hdu):
    # TODO check if the catalogue data are in either of the catalogue HDUs and
    # return the R magnitude if available, otherwise return the flux mean from
    # the post-sysrem analysis, and convert to approximate R magnitudes using
    # the approximate zero point hard-coded in this file.
    instrumental_magnitudes = post_sysrem_hdu['mag_mean'].read()
    stellar_magnitudes = APPROXIMATE_ZERO_POINT + instrumental_magnitudes
    return stellar_magnitudes, False, None


def render_single_sysrem(sysrem_cataloguename, pre_sysrem_cataloguename,
                         manifest_path):
    with fitsio.FITS(sysrem_cataloguename) as infile:
        hdu = infile['sysrem_catalogue']
        mag_rms = hdu['mag_rms'].read()
        mag_mean = hdu['mag_mean'].read()

        with fitsio.FITS(pre_sysrem_cataloguename) as infile:
            pre_sysrem_hdu = infile['catalogue']
            pre_sysrem_mag_rms = pre_sysrem_hdu['mag_rms'].read()

            stellar_magnitudes, external_magnitudes, band = compute_stellar_magnitudes(
                hdu, pre_sysrem_hdu)

    output_filename = 'qa_post_sysrem_flux_vs_rms.png'
    with figure_context(output_filename) as fig:
        axis = fig.add_subplot(111)
        axis.semilogy(stellar_magnitudes, pre_sysrem_mag_rms * 100., '.', alpha=0.3)
        axis.semilogy(stellar_magnitudes, mag_rms * 100., 'k.')
        axis.set(
            ylabel='FRMS [%]',
            ylim=(0.1, 100),
            )
        if external_magnitudes:
            axis.set(xlabel='{band} magnitude'.format(band=band))
        else:
            axis.set(xlabel='Approximate R magnitude [ZP={zero_point:.1f}]'.format(
                zero_point=APPROXIMATE_ZERO_POINT))

        axis.invert_xaxis()

    update_manifest(
        filename=output_filename,
        manifest_path=manifest_path)


def render_sysrem_improvement(sysrem_cataloguename,
                              pre_sysrem_cataloguename,
                              manifest_path):
    with fitsio.FITS(sysrem_cataloguename) as infile:
        hdu = infile['sysrem_catalogue']
        mag_rms = hdu['mag_rms'].read()
        mag_mean = hdu['mag_mean'].read()

        with fitsio.FITS(pre_sysrem_cataloguename) as infile:
            pre_sysrem_hdu = infile['catalogue']
            pre_sysrem_mag_rms = pre_sysrem_hdu['mag_rms'].read()

            stellar_magnitudes, external_magnitudes, band = compute_stellar_magnitudes(
                hdu, pre_sysrem_hdu)

    output_filename = 'qa_sysrem_improvement.png'
    with figure_context(output_filename) as fig:
        axis = fig.add_subplot(111)
        axis.plot(stellar_magnitudes, pre_sysrem_mag_rms / mag_rms, 'k.')
        axis.invert_xaxis()

        axis.set(
            ylabel='RMS(pre-sysrem) / RMS(post-sysrem)',
            )

        if external_magnitudes:
            axis.set(xlabel='{band} magnitude'.format(band=band))
        else:
            axis.set(xlabel='Approximate R magnitude [ZP={zero_point:.1f}]'.format(
                zero_point=APPROXIMATE_ZERO_POINT))

    update_manifest(
        filename=output_filename,
        manifest_path=manifest_path)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--file-root', required=True)
    parser.add_argument('-m', '--manifest-path', required=True)
    args = parser.parse_args()

    sysrem_cataloguename = find_file(args.file_root, 'sysrem_catalogue')
    with fitsio.FITS(sysrem_cataloguename) as infile:
        prod_id = infile[0].read_header()['prod_id']

    pre_sysrem_files = find_previous_job_files(prod_id, 'sysrem')
    pre_sysrem_cataloguename = pre_sysrem_files['catalogue']

    render_single_sysrem(sysrem_cataloguename, pre_sysrem_cataloguename,
                         manifest_path=args.manifest_path)
    render_sysrem_improvement(sysrem_cataloguename, pre_sysrem_cataloguename,
                              manifest_path=args.manifest_path)
