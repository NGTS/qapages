#!/usr/bin/env python


from __future__ import print_function, absolute_import, division
import argparse
import fitsio
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as Canvas
from matplotlib.figure import Figure


def find_file(root, file_type):
    file_type = file_type.lower()
    stub = {
        'imagelist': '_IMAGELIST.fits',
    }[file_type]
    return root + stub


def compute_night_boundaries(nights):
    indices, labels = [], []
    indices.append(0)
    labels.append(nights[0])

    last_night = nights[0]
    for i, night in enumerate(nights):
        if night != last_night:
            indices.append(i)
            labels.append(night)
            last_night = night

    return np.array(indices), np.array(labels)


def update_manifest(filename, manifest_path):
    with open(manifest_path, 'a') as outfile:
        outfile.write('{}\n'.format(filename))


def mark_nights(axis, nights):
    to_shade = True
    for left, right in zip(nights[0][:-1], nights[0][1:]):
        if to_shade:
            axis.axvspan(left, right, color='0.8')
        to_shade = not to_shade


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

    # Only select some of the labels to print
    label_idx = np.linspace(
        0, len(night_boundaries[0]) - 1, 10).astype(np.int32)

    # Render the image
    fig = Figure()
    canvas = Canvas(fig)

    axis = fig.add_subplot(111)
    axis.plot(frames, stdcrms, 'k,')
    axis.set(xlabel='Frame', ylabel='STDCRMS ["]')

    if len(np.unique(night)) > 1:
        mark_nights(axis, night_boundaries)
        axis.set_xticks(night_boundaries[0][label_idx])
        axis.set_xticklabels(night_boundaries[1][label_idx], rotation=90)

    axis.grid(True, axis='y')
    axis.set(xlim=(0, frames[-1]), ylim=(0.1, 0.7))
    fig.tight_layout()

    output_filename = 'astrometry_stats.png'
    fig.savefig(output_filename)

    update_manifest(output_filename, args.manifest_path)

    # Render the coordinate locations

