from unittest import TestCase

import numpy as np
from distance_transform.wave_propagation import *
from combinatorial.pixelmap import PixelMap
from distance_transform.dt_utils import *
from combinatorial.pixelmap import LabelMap
from distance_transform.preprocessing import *
from distance_transform.dijkstra import *
import cv2


class TestDijkstra(TestCase):
    def setUp(self) -> None:
        pass

    def test_generalized_dijkstra_dt_gmap_unweighted(self):
        image = cv2.imread('../data/dt_test_image.png', 0)
        actual_gmap = LabelMap.from_labels(image)
        expected_gmap = LabelMap.from_labels(image)

        generalized_dijkstra_dt_gmap(actual_gmap, [0], [255], generate_accumulation_directions_cell(2))
        generalized_wave_propagation_gmap(expected_gmap, [0], [255], generate_accumulation_directions_cell(2))

        self.assertTrue(gmap_dt_equal(actual_gmap, expected_gmap))
