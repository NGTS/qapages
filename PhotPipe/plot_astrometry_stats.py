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


class AxisTransform(object):

    def __init__(self, canvas, axis):
        self.canvas = canvas
        self.axis = axis

    def transform(self, x, y):
        x = np.atleast_1d(x)
        y = np.atleast_1d(y)

        points = np.array([x, y]).T
        x, y = self.axis.transData.transform(points).T
        _, height = self.canvas.get_width_height()
        return {
            'x': x.tolist(),
            'y': (height - y).tolist(),
        }

    def transform_pixels(self, *args, **kwargs):
        results = self.transform(*args, **kwargs)
        x, y = results['x'], results['y']
        return {
            'x': np.round(x).astype(np.int32).tolist(),
            'y': np.round(y).astype(np.int32).tolist(),
        }


class FigureTransform(object):

    def __init__(self, figure):
        self.figure = figure
        assert self.canvas is not None, 'A canvas object must be set'
        self.width, self.height = self.canvas.get_width_height()

    def axis(self, index):
        return AxisTransform(self.canvas, self.canvas.figure.axes[index])

    def transform(self, *args, **kwargs):
        if self.naxes > 1:
            raise RuntimeError('Figure contains more than one axis. '
                               'This is unsupported')
        return self.axis(0).transform(*args, **kwargs)

    def transform_pixels(self, *args, **kwargs):
        if self.naxes > 1:
            raise RuntimeError('Figure contains more than one axis. '
                               'This is unsupported')
        return self.axis(0).transform_pixels(*args, **kwargs)

    @property
    def naxes(self):
        return len(self.figure.axes)

    @property
    def canvas(self):
        return self.figure.canvas


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


def mark_nights(axis, nights):
    to_shade = True
    for left, right in zip(nights[0][:-1], nights[0][1:]):
        if to_shade:
            axis.axvspan(left, right, color='0.8')
        to_shade = not to_shade


def render_regionfile(figure, boundaries, prod_ids, manifest_path):
    assert len(boundaries[0]) == len(prod_ids) == len(boundaries[1])
    output_filename = 'qa_wcsstats_regions.json'

    trans = FigureTransform(figure)

    results = trans.transform_pixels(
        boundaries[0], np.ones(len(boundaries[0])) * 0.4)
    xs = np.array(results['x'][:-1])
    widths = np.diff(results['x'])

    ind = widths >= 1
    xs, widths = [data[ind] for data in [xs, widths]]

    yrange_pix = trans.transform_pixels([0, 0], [0.1, 0.7])['y']
    ys = np.ones_like(xs) * yrange_pix[0]
    heights = np.ones_like(xs) * (yrange_pix[1] - yrange_pix[0])

    hrefs = np.array([
        get_url('phot', prod_id) for prod_id in prod_ids
    ])[ind].tolist()

    renderable_data = {
        'coords': {
            'xmin': xs.tolist(),
            'ymin': ys.tolist(),
            'xmax': (xs + widths).tolist(),
            'ymax': (ys + heights).tolist(),
        },
        'hrefs': hrefs,
    }

    with open(output_filename, 'w') as outfile:
        json.dump(renderable_data, outfile, indent=2)

    update_manifest(output_filename, manifest_path)


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

    with figure_context(output_filename) as fig:

        axis = fig.add_subplot(111)
        axis.plot(frames, stdcrms, 'k,')
        axis.set(xlabel='Frame', ylabel='STDCRMS ["]')

        if len(np.unique(night)) > 1:
            mark_nights(axis, night_boundaries)
            axis.set_xticks(night_boundaries[0][label_idx])
            axis.set_xticklabels(night_boundaries[1][label_idx], rotation=90)

            render_regionfile(fig, night_boundaries, sub_prod_ids, args.manifest_path)

        axis.grid(True, axis='y')
        axis.set(xlim=(0, frames[-1]), ylim=(0.1, 0.7))

    update_manifest(output_filename, args.manifest_path)

