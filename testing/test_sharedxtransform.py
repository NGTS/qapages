import os
import sys
sys.path.insert(0, os.path.join(
    os.path.dirname(__file__),
    '..'))
from ngqa_common import AxisTransform, SharedXTransform, Region
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as Canvas
import tempfile
import pytest
from unittest import TestCase


class TestSharedXTransform(TestCase):

    def setUp(self):
        # Expected pixel coordinates of the data range,
        # extracted from the GIMP
        self.x_pixel_range = (79, 576)
        self.top_y_pixel_range = (19, 199)
        self.bottom_y_pixel_range = (261, 442)

        self.xlims = (10, 90)
        self.ylims = (0, 1024)

        self.figure = Figure(figsize=(6, 5), dpi=100)
        self.axes = (
            self.figure.add_subplot(211),
            self.figure.add_subplot(212),
        )
        for axis in self.axes:
            axis.set(
                xlim=self.xlims,
                ylim=self.ylims,
                xlabel='X LABEL',
                ylabel='Y LABEL',
                )

        self.figure.tight_layout()
        self.canvas = Canvas(self.figure)
        self.transform = SharedXTransform(
            canvas=self.canvas)

    def test_setup(self):
        assert len(self.axes) == 2

    def test_rendering(self):
        filename = os.path.join(
            tempfile.gettempdir(), 'test_multi.png')
        self.canvas.print_figure(filename)
        assert os.path.isfile(filename)

    def test_number_of_regions(self):
        xvals = [10, 30, 80, 90]
        regions = list(self.transform.x_regions(xvals))
        assert len(regions) == 6

    def test_regions(self):
        xvals = [10, 30, 80, 90]
        regions = list(self.transform.x_regions(xvals))

        top_transform = AxisTransform(canvas=self.canvas, axis=self.axes[0])
        bottom_transform = AxisTransform(canvas=self.canvas, axis=self.axes[1])

        # First 3 regions belong to the top axis
        # Last 3 regions belong to the bottom axis

        top_expected = [
            Region(
                xmin=self.x_pixel_range[0],
                xmax=top_transform.transform_pixels(30, 0.)['x'][0],
                ymin=self.top_y_pixel_range[0],
                ymax=self.top_y_pixel_range[1],
                ),
            Region(
                xmin=top_transform.transform_pixels(30, 0)['x'][0],
                xmax=top_transform.transform_pixels(80, 0.)['x'][0],
                ymin=self.top_y_pixel_range[0],
                ymax=self.top_y_pixel_range[1],
                ),
            Region(
                xmin=top_transform.transform_pixels(80, 0)['x'][0],
                xmax=top_transform.transform_pixels(90, 0.)['x'][0],
                ymin=self.top_y_pixel_range[0],
                ymax=self.top_y_pixel_range[1],
                ),
        ]

        bottom_expected = [
            Region(
                xmin=self.x_pixel_range[0],
                xmax=top_transform.transform_pixels(30, 0.)['x'][0],
                ymin=self.bottom_y_pixel_range[0],
                ymax=self.bottom_y_pixel_range[1],
                ),
            Region(
                xmin=top_transform.transform_pixels(30, 0)['x'][0],
                xmax=top_transform.transform_pixels(80, 0.)['x'][0],
                ymin=self.bottom_y_pixel_range[0],
                ymax=self.bottom_y_pixel_range[1],
                ),
            Region(
                xmin=top_transform.transform_pixels(80, 0)['x'][0],
                xmax=top_transform.transform_pixels(90, 0.)['x'][0],
                ymin=self.bottom_y_pixel_range[0],
                ymax=self.bottom_y_pixel_range[1],
                ),
        ]

        for region, expected in zip(regions, top_expected + bottom_expected):
            self.regions_close(region, expected)

    # Helper functions
    @staticmethod
    def integer_close(a, b):
        return abs(a - b) <= 1

    def regions_close(self, a, b):
        return (
              self.integer_close(a.xmin, b.xmin)
            & self.integer_close(a.xmax, b.xmax)
            & self.integer_close(a.ymin, b.ymin)
            & self.integer_close(a.ymax, b.ymax)
            )
