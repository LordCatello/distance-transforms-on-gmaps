import random
from unittest import TestCase

import numpy as np

from combinatorial.utils import build_dt_grey_image_from_gmap
from distance_transform.wave_propagation import *
from combinatorial.pixelmap import PixelMap
from distance_transform.dt_utils import *
from combinatorial.pixelmap import LabelMap
from distance_transform.preprocessing import *
from combinatorial.utils import *
from data.labels import labels
import cv2
import time


class TestWavePropagation(TestCase):
    def setUp(self) -> None:
        self.binary_image_1 = np.array(
            [[1, 1, 1, 1, 0],
            [1, 1, 1, 0, 1],
            [0, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1]])
        self.expected_binary_image_1_dt = np.array(
            [[2, 3, 2, 1, 0],
            [1, 2, 1, 0, 1],
            [0, 1, 2, 1, 2],
            [1, 2, 3, 2, 3],
            [2, 3, 4, 3, 4]])

    def test_wave_propagation_dt_binary_image(self):
        actual = wave_propagation_dt_image(self.binary_image_1)
        self.assertEqual(self.expected_binary_image_1_dt.tolist(), actual.tolist())

    def test_wave_propagation_dt_gmap(self):
        seeds = [2, 4, 7]

        actual_gmap = PixelMap.from_shape(2, 2)
        expected_gmap = PixelMap.from_shape(2, 2)

        # set distances on expected gmap
        expected_gmap.set_dart_distance(0, 1)
        expected_gmap.set_dart_distance(1, 1)
        expected_gmap.set_dart_distance(2, 0)
        expected_gmap.set_dart_distance(3, 1)
        expected_gmap.set_dart_distance(4, 0)
        expected_gmap.set_dart_distance(5, 1)
        expected_gmap.set_dart_distance(6, 1)
        expected_gmap.set_dart_distance(7, 0)
        expected_gmap.set_dart_distance(8, 2)
        expected_gmap.set_dart_distance(9, 3)
        expected_gmap.set_dart_distance(10, 4)
        expected_gmap.set_dart_distance(11, 5)
        expected_gmap.set_dart_distance(12, 4)
        expected_gmap.set_dart_distance(13, 3)
        expected_gmap.set_dart_distance(14, 2)
        expected_gmap.set_dart_distance(15, 1)
        expected_gmap.set_dart_distance(16, 2)
        expected_gmap.set_dart_distance(17, 1)
        expected_gmap.set_dart_distance(18, 2)
        expected_gmap.set_dart_distance(19, 3)
        expected_gmap.set_dart_distance(20, 4)
        expected_gmap.set_dart_distance(21, 5)
        expected_gmap.set_dart_distance(22, 4)
        expected_gmap.set_dart_distance(23, 3)
        expected_gmap.set_dart_distance(24, 4)
        expected_gmap.set_dart_distance(25, 5)
        expected_gmap.set_dart_distance(26, 6)
        expected_gmap.set_dart_distance(27, 7)
        expected_gmap.set_dart_distance(28, 6)
        expected_gmap.set_dart_distance(29, 5)
        expected_gmap.set_dart_distance(30, 4)
        expected_gmap.set_dart_distance(31, 3)

        wave_propagation_dt_gmap(actual_gmap, seeds)

        # plot
        expected_gmap.plot_faces()
        expected_gmap.plot_faces_dt()
        actual_gmap.plot_faces_dt()

        self.assertTrue(gmap_dt_equal(actual_gmap, expected_gmap))

    def test_wave_propagation_dt_gmap_vertex(self):
        """
        Test if distance propagates correctly only through vertices
        """
        seeds = [0, 7]

        actual_gmap = PixelMap.from_shape(2, 2)
        expected_gmap = PixelMap.from_shape(2, 2)

        # set distances on expected gmap
        expected_gmap.set_dart_distance(0, 0)
        expected_gmap.set_dart_distance(1, 1)
        expected_gmap.set_dart_distance(2, 1)
        expected_gmap.set_dart_distance(3, 2)
        expected_gmap.set_dart_distance(4, 2)
        expected_gmap.set_dart_distance(5, 1)
        expected_gmap.set_dart_distance(6, 1)
        expected_gmap.set_dart_distance(7, 0)
        expected_gmap.set_dart_distance(8, 1)
        expected_gmap.set_dart_distance(9, 2)
        expected_gmap.set_dart_distance(10, 2)
        expected_gmap.set_dart_distance(11, 3)
        expected_gmap.set_dart_distance(12, 3)
        expected_gmap.set_dart_distance(13, 2)
        expected_gmap.set_dart_distance(14, 2)
        expected_gmap.set_dart_distance(15, 1)
        expected_gmap.set_dart_distance(16, 1)
        expected_gmap.set_dart_distance(17, 2)
        expected_gmap.set_dart_distance(18, 2)
        expected_gmap.set_dart_distance(19, 3)
        expected_gmap.set_dart_distance(20, 3)
        expected_gmap.set_dart_distance(21, 2)
        expected_gmap.set_dart_distance(22, 2)
        expected_gmap.set_dart_distance(23, 1)
        expected_gmap.set_dart_distance(24, 2)
        expected_gmap.set_dart_distance(25, 3)
        expected_gmap.set_dart_distance(26, 3)
        expected_gmap.set_dart_distance(27, 4)
        expected_gmap.set_dart_distance(28, 4)
        expected_gmap.set_dart_distance(29, 3)
        expected_gmap.set_dart_distance(30, 3)
        expected_gmap.set_dart_distance(31, 2)

        accumulation_directions = generate_accumulation_directions_vertex(2)
        wave_propagation_dt_gmap(actual_gmap, seeds, accumulation_directions)

        # plot
        expected_gmap.plot_faces()
        expected_gmap.plot_faces_dt()
        actual_gmap.plot_faces_dt()

        self.assertTrue(gmap_dt_equal(actual_gmap, expected_gmap))

    def test_wave_propagation_dt_gmap_face(self):
        """
        Test if distance propagates correctly only through faces
        """
        seeds = [0, 1, 2, 3, 4, 5, 6, 7]

        actual_gmap = PixelMap.from_shape(2, 2)
        expected_gmap = PixelMap.from_shape(2, 2)

        # set distances on expected gmap
        expected_gmap.set_dart_distance(0, 0)
        expected_gmap.set_dart_distance(1, 0)
        expected_gmap.set_dart_distance(2, 0)
        expected_gmap.set_dart_distance(3, 0)
        expected_gmap.set_dart_distance(4, 0)
        expected_gmap.set_dart_distance(5, 0)
        expected_gmap.set_dart_distance(6, 0)
        expected_gmap.set_dart_distance(7, 0)
        expected_gmap.set_dart_distance(8, 1)
        expected_gmap.set_dart_distance(9, 1)
        expected_gmap.set_dart_distance(10, 1)
        expected_gmap.set_dart_distance(11, 1)
        expected_gmap.set_dart_distance(12, 1)
        expected_gmap.set_dart_distance(13, 1)
        expected_gmap.set_dart_distance(14, 1)
        expected_gmap.set_dart_distance(15, 1)
        expected_gmap.set_dart_distance(16, 1)
        expected_gmap.set_dart_distance(17, 1)
        expected_gmap.set_dart_distance(18, 1)
        expected_gmap.set_dart_distance(19, 1)
        expected_gmap.set_dart_distance(20, 1)
        expected_gmap.set_dart_distance(21, 1)
        expected_gmap.set_dart_distance(22, 1)
        expected_gmap.set_dart_distance(23, 1)
        expected_gmap.set_dart_distance(24, 2)
        expected_gmap.set_dart_distance(25, 2)
        expected_gmap.set_dart_distance(26, 2)
        expected_gmap.set_dart_distance(27, 2)
        expected_gmap.set_dart_distance(28, 2)
        expected_gmap.set_dart_distance(29, 2)
        expected_gmap.set_dart_distance(30, 2)
        expected_gmap.set_dart_distance(31, 2)

        accumulation_directions = generate_accumulation_directions_cell(2)
        wave_propagation_dt_gmap(actual_gmap, seeds, accumulation_directions)

        # plot
        expected_gmap.plot_faces()
        expected_gmap.plot_faces_dt()
        actual_gmap.plot_faces_dt()

        self.assertTrue(gmap_dt_equal(actual_gmap, expected_gmap))

    def test_wave_propagation_inside(self):
        """
        Test if distance propagates correctly only through faces
        """

        image = cv2.imread('../data/5_5_boundary.png', 0)
        actual_gmap = LabelMap.from_labels(image)
        expected_gmap = LabelMap.from_labels(image)

        # set distances on expected gmap
        for i in range(56):
            expected_gmap.set_dart_distance(i, -1)
        for i in range(56, 80):
            expected_gmap.set_dart_distance(i, 0)
        for i in range(80, 88):
            expected_gmap.set_dart_distance(i, -1)
        for i in range(88, 96):
            expected_gmap.set_dart_distance(i, 0)
        for i in range(96, 112):
            expected_gmap.set_dart_distance(i, 1)
        for i in range(112, 120):
            expected_gmap.set_dart_distance(i, 0)
        for i in range(120, 128):
            expected_gmap.set_dart_distance(i, -1)
        for i in range(128, 136):
            expected_gmap.set_dart_distance(i, 0)
        for i in range(136, 144):
            expected_gmap.set_dart_distance(i, 1)
        for i in range(144, 152):
            expected_gmap.set_dart_distance(i, 2)
        for i in range(152, 160):
            expected_gmap.set_dart_distance(i, 1)
        for i in range(160, 168):
            expected_gmap.set_dart_distance(i, -1)
        for i in range(168, 176):
            expected_gmap.set_dart_distance(i, 0)
        for i in range(176, 184):
            expected_gmap.set_dart_distance(i, 1)
        for i in range(184, 200):
            expected_gmap.set_dart_distance(i, 2)

        accumulation_directions = generate_accumulation_directions_cell(2)
        wave_propagation_dt_gmap(actual_gmap, None, accumulation_directions)

        # plot
        expected_gmap.plot()
        expected_gmap.plot_dt(fill_cell='face')
        actual_gmap.plot_dt(fill_cell='face')

        self.assertTrue(gmap_dt_equal(actual_gmap, expected_gmap))


    def test_dt_after_reduction(self):
        """
        Test if distance propagates correctly only through faces
        """
        random.seed(42)

        image = cv2.imread('../data/5_5_boundary.png', 0)
        actual_gmap = LabelMap.from_labels(image)
        expected_gmap = LabelMap.from_labels(image)

        expected_gmap.plot()

        # simplify gmap
        actual_gmap.remove_edges()
        actual_gmap.remove_vertices()
        expected_gmap.remove_edges()
        expected_gmap.remove_vertices()

        expected_gmap.plot()

        # set distances on expected gmap
        expected_gmap.set_dart_distance(35, -1)
        expected_gmap.set_dart_distance(36, -1)
        expected_gmap.set_dart_distance(51, -1)
        expected_gmap.set_dart_distance(52, -1)
        expected_gmap.set_dart_distance(163, -1)
        expected_gmap.set_dart_distance(164, -1)

        expected_gmap.set_dart_distance(73, 0)
        expected_gmap.set_dart_distance(74, 0)
        expected_gmap.set_dart_distance(61, 0)
        expected_gmap.set_dart_distance(62, 0)
        expected_gmap.set_dart_distance(89, 0)
        expected_gmap.set_dart_distance(90, 0)
        expected_gmap.set_dart_distance(173, 0)
        expected_gmap.set_dart_distance(174, 0)
        expected_gmap.set_dart_distance(173, 0)
        expected_gmap.set_dart_distance(171, 0)
        expected_gmap.set_dart_distance(172, 0)
        expected_gmap.set_dart_distance(115, 0)
        expected_gmap.set_dart_distance(116, 0)

        expected_gmap.set_dart_distance(96, 1)
        expected_gmap.set_dart_distance(103, 1)
        expected_gmap.set_dart_distance(181, 1)
        expected_gmap.set_dart_distance(182, 1)
        expected_gmap.set_dart_distance(153, 1)
        expected_gmap.set_dart_distance(154, 1)

        accumulation_directions = generate_accumulation_directions_cell(2)
        wave_propagation_dt_gmap(actual_gmap, None, accumulation_directions)

        # plot
        expected_gmap.plot_dt(fill_cell='face')
        actual_gmap.plot_dt(fill_cell='face')

        dt_image = build_dt_grey_image_from_gmap(actual_gmap)
        plot_dt_image(dt_image, None)

        self.assertTrue(gmap_dt_equal(actual_gmap, expected_gmap))

    def test_reduction_factor_0(self):
        random.seed(42)
        image = cv2.imread('../data/5_5_boundary.png', 0)
        gmap = LabelMap.from_labels(image)
        gmap.remove_edges(0.0)
        gmap.plot()
        self.assertTrue(True)

    def test_reduction_factor_05(self):
        random.seed(42)
        image = cv2.imread('../data/5_5_boundary.png', 0)
        gmap = LabelMap.from_labels(image)
        gmap.plot(attribute_to_show=True)
        gmap.remove_edges(0.5)
        gmap.remove_vertices()
        gmap.plot(attribute_to_show=True)
        self.assertTrue(True)

    def test_dt_reduction_05(self):
        random.seed(42)
        image = cv2.imread('../data/5_5_boundary.png', 0)
        compute_dt_reduction(image, 0.5)
        self.assertTrue(True)

    def test_dt_reduction_0(self):
        random.seed(42)
        image = cv2.imread('../data/5_5_boundary.png', 0)
        compute_dt_reduction(image, 0)
        self.assertTrue(True)

    def test_reduction_factor_pyramid(self):
        random.seed(42)
        image = cv2.imread('../data/5_5_boundary.png', 0)
        gmap = LabelMap.from_labels(image)
        gmap.remove_edges(0.5)
        gmap.plot()
        gmap.remove_edges(0.5)
        gmap.plot()
        gmap.remove_edges(0.5)
        gmap.plot()
        gmap.remove_edges(0.5)
        gmap.plot()
        self.assertTrue(True)

    def test_wave_propagation_dt_gmap_corner(self):
        seeds = [7]

        actual_gmap = PixelMap.from_shape(2, 2)

        wave_propagation_dt_gmap(actual_gmap, seeds)

        # plot
        actual_gmap.plot_faces_dt()
        self.assertTrue(True)

    def test_generalized_wave_propagation_image(self):
        image = cv2.imread("../data/5_5_boundary.png", 0)
        actual = generalized_wave_propagation_image(image, [0], [195], [255])
        expected = np.zeros(actual.shape, actual.dtype)

        expected.fill(-1)
        expected[1, 2:] = 0
        expected[2:, 1] = 0
        expected[2, 4] = 0
        expected[2:, 2] = 1
        expected[2, 3] = 1
        expected[3, 4] = 1
        expected[3:, 3] = 2
        expected[4, 4] = 2

        print(actual)

        self.assertEqual(actual.tolist(), expected.tolist())

    def test_improved_wave_propagation_gmap_vertex_small_image(self):
        image_name = "bug_image_improved.png"
        image = cv2.imread("../data/" + image_name, 0)
        expected_gmap = LabelMap.from_labels(image)
        actual_gmap = LabelMap.from_labels(image)

        actual_gmap.uniform_labels_for_vertices()
        expected_gmap.uniform_labels_for_vertices()

        accumulation_directions = generate_accumulation_directions_vertex(2)
        generalized_wave_propagation_gmap(expected_gmap, [0], [255], accumulation_directions)
        improved_wave_propagation_gmap_vertex(actual_gmap, [0], [255])

        actual_gmap.plot()
        expected_gmap.plot_dt()
        actual_gmap.plot_dt()

        self.assertTrue(gmap_dt_equal(actual_gmap, expected_gmap))

    def test_improved_wave_propagation_gmap_vertex_big_image(self):
        image_name = "img.png"
        image = cv2.imread("../data/diffusion_distance_images/" + image_name, 0)
        reduced_image = reduce_image_size(image, 11)
        expected_gmap = LabelMap.from_labels(reduced_image)
        actual_gmap = LabelMap.from_labels(reduced_image)

        actual_gmap.uniform_labels_for_vertices()
        expected_gmap.uniform_labels_for_vertices()

        accumulation_directions = generate_accumulation_directions_vertex(2)
        start = time.time()
        generalized_wave_propagation_gmap(expected_gmap, [labels["stomata"]], [labels["air"]], accumulation_directions)
        end = time.time()
        print(f"time s normal: {end - start}")
        start = time.time()
        improved_wave_propagation_gmap_vertex(actual_gmap, [labels["stomata"]], [labels["air"]])
        end = time.time()
        print(f"time s improved: {end - start}")

        plt.imshow(reduced_image, cmap="gray", vmin=0, vmax=255)
        plt.show()
        grey_image = build_dt_grey_image_from_gmap(expected_gmap)
        plot_dt_image(grey_image)
        grey_image = build_dt_grey_image_from_gmap(actual_gmap)
        plot_dt_image(grey_image)

        # It's strange
        # It seems correct, the dt should exist for that value
        # Very strange
        # Probably the bug is in the other algorithm
        # I have to reduce the size of the image in order to find the bug

        self.assertTrue(gmap_dt_equal(actual_gmap, expected_gmap))

    def test_improved_wave_propagation_gmap_vertex_reduced_image(self):
        image_name = "img.png"
        image = cv2.imread("../data/diffusion_distance_images/" + image_name, 0)
        reduced_image = reduce_image_size(image, 11)
        expected_gmap = LabelMap.from_labels(reduced_image)
        actual_gmap = LabelMap.from_labels(reduced_image)

        actual_gmap.uniform_labels_for_vertices()
        expected_gmap.uniform_labels_for_vertices()

        random.seed(42)
        actual_gmap.remove_edges(1)
        actual_gmap.remove_vertices()
        random.seed(42)
        expected_gmap.remove_edges(1)
        expected_gmap.remove_vertices()

        accumulation_directions = generate_accumulation_directions_vertex(2)
        start = time.time()
        generalized_wave_propagation_gmap(expected_gmap, [labels["stomata"]], [labels["air"]], accumulation_directions)
        end = time.time()
        print(f"time s normal: {end - start}")
        start = time.time()
        improved_wave_propagation_gmap_vertex(actual_gmap, [labels["stomata"]], [labels["air"]])
        end = time.time()
        print(f"time s improved: {end - start}")

        plt.imshow(reduced_image, cmap="gray", vmin=0, vmax=255)
        plt.show()
        grey_image = build_dt_grey_image_from_gmap(expected_gmap)
        plot_dt_image(grey_image)
        grey_image = build_dt_grey_image_from_gmap(actual_gmap)
        plot_dt_image(grey_image)

        # It's strange
        # It seems correct, the dt should exist for that value
        # Very strange
        # Probably the bug is in the other algorithm
        # I have to reduce the size of the image in order to find the bug

        self.assertTrue(gmap_dt_equal(actual_gmap, expected_gmap))

