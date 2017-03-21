#!/usr/bin/env python


from __future__ import print_function, absolute_import, division
import argparse
import fitsio
import numpy as np
import json
from matplotlib.backends.backend_agg import FigureCanvasAgg as Canvas
from matplotlib.figure import Figure
import sys
import os
sys.path.insert(0, os.path.join(
    os.path.dirname(__file__),
    '..'))
from ngqa_common import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--file-root', required=True)
    parser.add_argument('-m', '--manifest-path', required=True)
    args = parser.parse_args()

    imagelist_file = find_file(args.file_root, 'imagelist')

    with fitsio.FITS(imagelist_file) as infile:
        hdu = infile['imagelist']
        night = hdu['night'].read()
        stdcrms = hdu['stdcrms'].read()
        action_id = hdu['actionid'].read()
        sub_prod_ids = hdu['prod_id'].read()
        frames = np.arange(stdcrms.size)

        header = infile[0].read_header()

    tag = header['tag'].strip()

    night_boundaries = compute_night_boundaries(night)
    actions = action_id[night_boundaries[0]]
    sub_prod_ids = sub_prod_ids[night_boundaries[0]]

    # Only select some of the labels to print
    label_idx = np.linspace(
        0, len(night_boundaries[0]) - 1, 10).astype(np.int32)

    # Render the image
    output_filename = 'qa_astrometry_stats.png'
    region_filename = 'qa_wcsstats_regions.json'

    with figure_context(output_filename) as fig:

        axis = fig.add_subplot(111)
        axis.plot(frames, stdcrms, 'k,')
        axis.set(
            xlabel='Frame',
            ylabel='STDCRMS ["]',
            xlim=(0, frames[-1]),
            ylim=(0.1, 0.7),
        )
        axis.grid(True, axis='y')

        if len(np.unique(night)) > 1:
            mark_nights(axis, night_boundaries)
            axis.set_xticks(night_boundaries[0][label_idx])
            axis.set_xticklabels(night_boundaries[1][label_idx], rotation=90)

            # Make sure to finish rendering the figure before rendering these regions,
            # including calling `tight_layout`
            fig.tight_layout()
            render_regionfile(fig, region_filename, night_boundaries, sub_prod_ids, args.manifest_path)

    update_manifest(output_filename, args.manifest_path)
