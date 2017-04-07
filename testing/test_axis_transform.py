import os
import sys
sys.path.insert(0, os.path.join(
    os.path.dirname(__file__),
    '..'))
from ngqa_common import AxisTransform, Region
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as Canvas
import tempfile
import pytest
from unittest import TestCase


class TestAxisTransform(TestCase):

    def setUp(self):

        # Expected pixel coordinates of the data range,
        # extracted from the GIMP
        self.x_pixel_range = (79, 576)
        self.y_pixel_range = (19, 442)

        self.figure = Figure(figsize=(6, 5), dpi=100)
        self.xlims = (10, 90)
        self.ylims = (0, 1024)
        self.axis = self.figure.add_subplot(111)
        self.axis.set(
            xlim=self.xlims,
            ylim=self.ylims,
            xlabel='X LABEL',
            ylabel='Y LABEL',
            )
        self.figure.tight_layout()
        self.canvas = Canvas(self.figure)

        self.transform = AxisTransform(
            canvas=self.canvas,
            axis=self.axis)

    def test_setup(self):
        assert self.figure is not None
        assert self.canvas is not None
        assert isinstance(self.transform, AxisTransform)

    def test_rendering(self):
        filename = os.path.join(
            tempfile.gettempdir(), 'test.png')
        self.canvas.print_figure(filename)
        assert os.path.isfile(filename)

    def test_expected_positions(self):
        # XXX y is inverted!!! XXX
        positions = [
            (self.xlims[0], self.ylims[0]),
            (self.xlims[0], self.ylims[1]),
            (self.xlims[1], self.ylims[0]),
            (self.xlims[1], self.ylims[1]),
        ]
        expecteds = [
            (self.x_pixel_range[0], self.y_pixel_range[1]),
            (self.x_pixel_range[0], self.y_pixel_range[0]),
            (self.x_pixel_range[1], self.y_pixel_range[1]),
            (self.x_pixel_range[1], self.y_pixel_range[0]),
        ]

        assert len(positions) == len(expecteds)

        for i, (position, expected) in enumerate(zip(positions, expecteds)):
            print(i, position, expected)
            res = self.transform.transform_pixels(*position)
            assert self.integer_close(res['x'][0], expected[0])
            assert self.integer_close(res['y'][0], expected[1])

    def test_regions(self):
        xvals = [10, 30, 80, 90]
        regions = list(self.transform.x_regions(xvals))
        assert len(regions) == 3

        expected_regions = [
            Region(
                xmin=self.x_pixel_range[0],
                xmax=self.transform.transform_pixels(30, 0.)['x'][0],
                ymin=self.y_pixel_range[0],
                ymax=self.y_pixel_range[1],
                ),
            Region(
                xmin=self.transform.transform_pixels(30, 0)['x'][0],
                xmax=self.transform.transform_pixels(80, 0.)['x'][0],
                ymin=self.y_pixel_range[0],
                ymax=self.y_pixel_range[1],
                ),
            Region(
                xmin=self.transform.transform_pixels(80, 0)['x'][0],
                xmax=self.transform.transform_pixels(90, 0.)['x'][0],
                ymin=self.y_pixel_range[0],
                ymax=self.y_pixel_range[1],
                ),
        ]

        assert len(expected_regions) == len(regions)

        for i, (region, expected) in enumerate(zip(regions, expected_regions)):
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
