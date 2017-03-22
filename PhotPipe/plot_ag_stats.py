#!/usr/bin/env python


from __future__ import print_function, absolute_import, division
import argparse
import fitsio
import numpy as np
import json
from astropy.stats import sigma_clip, sigma_clipped_stats
from scipy.stats import binned_statistic
from matplotlib.backends.backend_agg import FigureCanvasAgg as Canvas
from matplotlib.figure import Figure
import sys
import os
sys.path.insert(0, os.path.join(
    os.path.dirname(__file__),
    '..'))
from ngqa_common import *


def compute_profile(x, y, bins=100):
    by, bx, _ = binned_statistic(x, y, lambda d: sigma_clipped_stats(d)[1], bins=bins)
    be, _, _ = binned_statistic(x, y, lambda d: sigma_clipped_stats(d)[2], bins=bx)
    bx = (bx[:-1] + bx[1:]) / 2.
    return bx, by, be


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--file-root', required=True)
    parser.add_argument('-m', '--manifest-path', required=True)
    args = parser.parse_args()

    imagelist_file = find_file(args.file_root, 'imagelist')

    with fitsio.FITS(imagelist_file) as infile:
        hdu = infile['imagelist']
        night = hdu['night'].read()
        action_id = hdu['actionid'].read()
        sub_prod_ids = hdu['prod_id'].read()
        ag_errx = hdu['ag_errx'].read()
        ag_erry = hdu['ag_erry'].read()
        frames = np.arange(night.size)

        header = infile[0].read_header()

    tag = header['tag'].strip()


    night_boundaries = compute_night_boundaries(night)
    actions = action_id[night_boundaries[0]]
    sub_prod_ids = sub_prod_ids[night_boundaries[0]]

    # Only select some of the labels to print
    label_idx = np.linspace(
        0, len(night_boundaries[0]) - 1, 10).astype(np.int32)

    # Render the image
    x_output_filename = 'qa_autoguider_stats_x.png'
    y_output_filename = 'qa_autoguider_stats_y.png'

    x_regions_filename = 'qa_autoguider_regions_x.json'
    y_regions_filename = 'qa_autoguider_regions_y.json'

    iterables = zip(
        [ag_errx, ag_erry],
        [x_output_filename, y_output_filename],
        [x_regions_filename, y_regions_filename],
        ['x', 'y'],
        )

    for data, output_filename, region_filename, dimension in iterables:
        with figure_context(output_filename) as fig:
            sc = sigma_clip(data)
            ind = ~sc.mask

            axis = fig.add_subplot(111)
            axis.plot(frames[ind], data[ind], 'k,', alpha=0.3)
            profile_x, profile_med, profile_width = compute_profile(frames[ind], data[ind])
            axis.fill_between(profile_x, profile_med - profile_width / 2., profile_med + profile_width / 2.,
                              color='#BECAE3', alpha=0.5)
            axis.plot(profile_x, profile_med, 'r.')
            # axis.grid(True, axis='y')

            axis.set(
                xlabel='Frame',
                ylabel='Autoguider error {label} ["]'.format(label=dimension),
                xlim=(0, frames[-1]),
                ylim=(-0.75, 0.75),
            )

            if len(np.unique(night)) > 1:
                mark_nights(axis, night_boundaries)
                axis.set_xticks(night_boundaries[0][label_idx])
                axis.set_xticklabels(night_boundaries[1][label_idx], rotation=90)

                # Make sure to finish rendering the figure before rendering these regions,
                # including calling `tight_layout`
                fig.tight_layout()
                render_regionfile(fig, region_filename, night_boundaries, sub_prod_ids, args.manifest_path)

        update_manifest(output_filename, args.manifest_path)
