import os
import sys
sys.path.insert(0, os.path.join(
    os.path.dirname(__file__),
    '..'))
from ngqa_common import AxesTransform, Region
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as Canvas
import tempfile
import pytest
from unittest import TestCase


class TestFigureTransform(TestCase):

    def setUp(self):
        self.figure = Figure(figsize=(6, 5), dpi=100)
        self.axes = (
            self.figure.add_subplot(211),
            self.figure.add_subplot(212),
        )
        self.figure.tight_layout()
        self.canvas = Canvas(self.figure)
        self.transform = AxesTransform(
            canvas=self.canvas,
            axes=self.axes)

    def test_setup(self):
        assert len(self.axes) == 2
