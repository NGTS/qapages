#!/usr/bin/env python


'''
Things to extract:

* binned flux values
* bias level
* over - pre
* sky background
* chassis temperature

Bin edges:

bin 0: 10 24.3415
bin 1: 24.3415 59.2507
bin 2: 59.2507 144.225
bin 3: 144.225 351.065
bin 4: 351.065 854.543
bin 5: 854.543 2080.08
bin 6: 2080.08 5063.23
bin 7: 5063.23 12324.6
bin 8: 12324.6 30000

TODO:

* look at the raw data
* look at post-coarse decorrelation only

'''


import argparse
import base64
from collections import namedtuple
from io import BytesIO
import os
import subprocess as sp
import fitsio
import jinja2
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import binned_statistic
from astropy.stats import sigma_clip
import tempfile

TEMPLATE_FILENAME = os.path.join(
    os.path.dirname(__file__), 'fluxbin_analysis_template.html')
assert os.path.isfile(TEMPLATE_FILENAME), 'cannot find template file {}'.format(TEMPLATE_FILENAME)

FLUXBIN_PATH = os.path.expanduser(
    os.path.join(
        '~', 'work', 'NGTS', 'ngts-git', 'sysrem', 'fluxbin'
        )
    )

assert os.path.isfile(FLUXBIN_PATH), 'cannot find fluxbin binary: {}'.format(FLUXBIN_PATH)

def build_axes(fig, nplots, margins, inner_margin):
    ''' Build a list of axes for the given figure, where
    the axes have fixed locations on the screen, and the labels
    have to sort themselves out. This is important as we need the
    two plots to line up.

    `margins` must include "top", "bottom", "left", "right" and
    defines the outer margins around the plots. The vertical inner
    margin height is defined with `inner_margin`.
    '''
    for key in ['top', 'bottom', 'left', 'right']:
        assert key in margins, 'Key {} missing from margins'.format(
            key
            )

    height = (1 - margins['top'] - margins['bottom'] - (nplots - 1) * inner_margin) / float(nplots)
    width = 1. - margins['left'] - margins['right']

    axes = []
    for n in range(nplots):
        start_x = margins['left']
        start_y = margins['bottom'] + n * (inner_margin + height)

        axes.append(fig.add_axes([start_x, start_y, width, height]))

    # Have to reverse, as we've built them bottom to top, and `subplots`
    # returns them in top to bottom order
    return axes[::-1]


class Dataset(object):

    def __init__(self, time_series, label, frame=None):
        self.time_series = time_series
        self.label = label
        self.frame = frame if frame is not None else np.arange(len(self.time_series))

    def plot(self, axis, frame_range, *args, **kwargs):
        markersize = kwargs.pop('ms', 1)

        if frame_range is None:
            ind = np.ones_like(self.frame, dtype=bool)
        else:
            ind = (self.frame >= min(frame_range)) & (self.frame <= max(frame_range))
        axis.plot(self.frame[ind], self.time_series[ind], '.',
                  markersize=markersize, *args, **kwargs)
        axis.set(ylabel=self.label)

    @classmethod
    def load_above_zero(cls, data, label):
        ind = data > 0
        frame = np.arange(len(data))
        return cls(data[ind], label, frame=frame[ind])


class CachedFluxbin(object):

    cache_dir = os.path.join(
        tempfile.gettempdir(), 'fluxbinout'
        )

    def __init__(self, analyser):
        self.flux = analyser.flux
        self.catalogue = analyser.catalogue
        self.imagelist = analyser.imagelist
        self.flags = analyser.flags
        self.fluxerr = analyser.fluxerr
        self.output = analyser.output

    def run(self):
        self.ensure_cache_dir()
        cached_filename = self.compute_fluxbin_cache_filename()
        if not os.path.isfile(cached_filename):
            self._run_fluxbin(cached_filename)

        return cached_filename

    @property
    def sysrem_prod_id(self):
        with fitsio.FITS(self.flux) as infile:
            return infile[0].read_header()['prod_id']

    @property
    def merge_prod_id(self):
        with fitsio.FITS(self.fluxerr) as infile:
            return infile[0].read_header()['prod_id']

    def _run_fluxbin(self, output_filename):
        cmd = [FLUXBIN_PATH, '--flux', self.flux, '--catalogue',
               '{}[1]'.format(self.catalogue), '--imagelist', self.imagelist,
               '--flags', self.flags, '--fluxerr', self.fluxerr,
               '--output', output_filename]
        sp.check_call(cmd)

    def compute_fluxbin_cache_filename(self):
        return os.path.join(
            self.cache_dir, 'fluxbin-sysrem.P{}-merge.P{}.fits'.format(
                self.sysrem_prod_id, self.merge_prod_id)
            )

    def ensure_cache_dir(self):
        if not os.path.isdir(self.cache_dir):
            os.makedirs(self.cache_dir)


class NightBoundaries(object):

    def __init__(self, nights):
        self.nights = nights
        self.boundary_indices = [0]
        self.unique_nights = [self.nights[0]]

        current_night = self.nights[0]
        for i, night in enumerate(self.nights):
            if night != current_night:
                self.unique_nights.append(night)
                self.boundary_indices.append(i)
                current_night = night

        assert len(self.boundary_indices) == len(self.unique_nights)

    def within_range(self, frame_min, frame_max):
        for index, night in zip(self.boundary_indices, self.unique_nights):
            if frame_min <= index <= frame_max:
                yield index, night



class FluxbinAnalysis(object):

    flux_colour = '#D43245'
    ambient_colour = '#2077B4'

    def __init__(self, args):
        self.flux = args.flux
        self.catalogue = args.catalogue
        self.imagelist = args.imagelist
        self.flags = args.flags
        self.fluxerr = args.fluxerr
        self.output = args.output
        self.frame_range = args.frame_range
        self.nbins = args.nbins
        self.bin_edges = np.logspace(1, np.log10(30000), 10)
        self.night_boundaries = self.compute_night_boundaries()

        self.load_from_imagelist()

    def compute_night_boundaries(self):
        with fitsio.FITS(self.imagelist) as infile:
            hdu = infile[1]
            night = hdu['night'].read()

        return NightBoundaries(night)

    def flux_label(self, index):
        return '{:.1f}-{:.1f}'.format(
            self.bin_edges[index], self.bin_edges[index + 1])

    def relative_flux_lims(self, left_lims, index):
        bin_min, bin_max = self.bin_edges[index:index + 2]
        bin_mean = 10 ** ((np.log10(bin_min) +
                           np.log10(bin_max)) / 2.)
        return (left_lims[0] * 100 / bin_mean, left_lims[1] * 100 / bin_mean)

    def load_from_imagelist(self):
        with fitsio.FITS(self.imagelist) as infile:
            hdu = infile[1]
            self.overscan_level = hdu['biasover'].read()
            self.prescan_level = hdu['biaspre'].read()
            self.chassis_temperature = hdu['chstemp'].read()
            self.sky_level = hdu['skylevel'].read()
            self.ambient_temperature = hdu['wxtemp'].read()
            self.psf = (hdu['psf_a_5'].read() + hdu['psf_b_5'].read()) / 2.

        # Add some normal noise to the chassis temperature to make it
        # more visually appealing
        self.chassis_temperature += np.random.normal(
            0., 0.1, len(self.chassis_temperature))

        self.overscan_difference = self.overscan_level - self.prescan_level

        self.datasets = [
            Dataset(self.sky_level, 'Sky'),
            Dataset(self.psf, 'PSF'),
            Dataset(self.overscan_level, 'Overscan'),
            Dataset(self.prescan_level, 'Prescan'),
            Dataset(self.chassis_temperature, 'Chassis temp'),
            Dataset.load_above_zero(self.ambient_temperature, 'Ambient temperature'),
            Dataset(self.overscan_difference, 'Overscan difference'),
        ]

    @staticmethod
    def load_binned_flux_values(filename):
        with fitsio.FITS(filename) as infile:
            binned_flux = infile['flux_mean'].read()
            binned_flux_err = infile['flux_err'].read()

        return binned_flux, binned_flux_err

    @staticmethod
    def _fig_to_encoded_png(fig):
        s = BytesIO()
        fig.savefig(s, format='png')
        s.seek(0)
        png_data = base64.b64encode(s.getvalue()).decode()
        return 'data:image/png;base64,{}'.format(png_data)

    def render(self, binned_flux, binned_flux_err):
        frame = np.arange(binned_flux.shape[1])
        nbins = binned_flux.shape[0]

        fig_width = 8
        subplot_height = 2

        # Render the binned flux
        fig = plt.figure(figsize=(fig_width, nbins * subplot_height))
        margins = {
            'top': 0.01,
            'bottom': 0.03,
            'left': 0.1,
            'right': 0.1,
            }
        inner_margin = 0.01
        axes = build_axes(fig, nbins, margins, inner_margin)
        for i in range(nbins):
            axis = axes[i]
            sc = sigma_clip(binned_flux[i])
            ind = ~sc.mask

            x = frame[ind]
            y = binned_flux[i][ind]
            bx, by = self.bin_up(x, y, self.nbins)

            if self.frame_range is not None:
                frame_min = min(self.frame_range)
                frame_max = max(self.frame_range)
                ind = ind & (frame >= frame_min) & (frame <= frame_max)

                binned_ind = (bx >= frame_min) & (bx <= frame_max)
            else:
                binned_ind = np.ones_like(bx, dtype=bool)

            axis.plot(frame[ind], binned_flux[i][ind], ',', ms=1,
                      color='k', alpha=0.1)
            axis.plot(bx[binned_ind], by[binned_ind], '.', ms=1,
                      color=self.flux_colour)
            axis.set(ylabel=self.flux_label(i))

            xlims = axis.get_xlim()
            for index, _ in self.night_boundaries.within_range(*xlims):
                axis.axvline(index, ls=':', color='0.7')
            axis.grid(True, axis='y')

            tax = axis.twinx()
            tax.set_ylim(*self.relative_flux_lims(axis.get_ylim(), i))
            tax.set(ylabel='Relative flux [%]')

        remove_axes_labels(axes[:-1])
        axes[-1].set(xlabel='Frame')

        binned_flux_png_data = self._fig_to_encoded_png(fig)

        # Render the metadata
        fig = plt.figure(figsize=(fig_width, len(self.datasets) * subplot_height))
        axes = build_axes(fig, len(self.datasets), margins, inner_margin)

        for i, dataset in enumerate(self.datasets):
            axis = axes[i]
            dataset.plot(
                axis, color=self.ambient_colour, frame_range=self.frame_range
                )

            xlims = axis.get_xlim()
            for index, _ in self.night_boundaries.within_range(*xlims):
                axis.axvline(index, ls=':', color='0.7')
            axis.grid(True, axis='y')

        remove_axes_labels(axes[:-1])

        axes[-1].set(xlabel='Frame')

        meta_png_data = self._fig_to_encoded_png(fig)

        self.render_html(binned_flux_png_data, meta_png_data)

    @staticmethod
    def bin_up(x, y, nbins):
        by, bx, _ = binned_statistic(x, y, 'median', nbins)
        return (bx[:-1] + bx[1:]) / 2., by

    def render_html(self, binned_flux_png_data, meta_png_data):

        with open(TEMPLATE_FILENAME) as infile:
            template = jinja2.Template(infile.read())

        with open(self.output, 'w') as outfile:
            outfile.write(template.render(
                fluxbin_image=binned_flux_png_data,
                meta_image=meta_png_data
                ))

    def run(self):
        cached_filename = CachedFluxbin(self).run()
        binned_flux, binned_flux_err = self.load_binned_flux_values(
            cached_filename)
        self.render(binned_flux, binned_flux_err)


def remove_axes_labels(axes):
    for ax in axes:
        ax.set(xticklabels=[])


def main(args):
    FluxbinAnalysis(args).run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--flux', required=True)
    parser.add_argument('-c', '--catalogue', required=True)
    parser.add_argument('-i', '--imagelist', required=True)
    parser.add_argument('-F', '--flags', required=True)
    parser.add_argument('-e', '--fluxerr', required=True)
    parser.add_argument('-b', '--nbins', required=False, type=int,
                        default=5000)
    parser.add_argument('--frame-range', required=False, nargs=2,
                        type=int)
    parser.add_argument('-o', '--output', required=True)
    main(parser.parse_args())
