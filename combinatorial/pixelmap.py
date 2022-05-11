# AUTOGENERATED! DO NOT EDIT! File to edit: notebooks/02_pixelmap.ipynb (unless otherwise specified).

__all__ = ['PixelMap', 'LabelMap']

# Cell

import logging
import typing

import numpy as np
from combinatorial.utils import *
from .gmaps import nGmap
from .zoo import G2_SQUARE_BOUNDED, G2_SQUARE_UNBOUNDED
import random
from distance_transform.preprocessing import generate_random_color

from memory_profiler import profile

# set seed
random.seed(42)

import matplotlib.pyplot as plt

# Cell


class PixelMap (nGmap):
    """2-gMap representing an RxC image grid"""

    @property
    def n_rows (self):
        return self._nR

    @property
    def n_cols (self):
        return self._nC

    # vertex coordinates for the 8 darts in one pixel
    vertices = np.fromstring("""\
    0 0 1 0 2 0 2 1 2 2 1 2 0 2 0 1
    """, sep=' ', dtype=np.float32).reshape(8, 2)
    vertices -= 1
    vertices *= .95
    vertices += 1
    vertices /= 2
    vertices -= .5

    # text offsets relative to darts
    text_offsets = np.fromstring("""\
    0 0 -1 -1   0  0 1 1
    1 1  0  0  -1 -1 0 0
    """, sep=" ").reshape(2, 8).T

    text_angles = [0,0,-90,-90,0,0,-90,-90]
    text_HAs = 'center center right right center center left left'.split()
    text_VAs = 'top top center center bottom bottom center center'.split()

    def _plot_dart_attribute(self, dart_id, attribute_value, rotate = False):
        if dart_id >= 8*self.n_rows*self.n_cols:
            return # TODO plot the boundary darts, too, if the maps is unbounded
        vi0, vi1 = dart_id % 8, 1 + dart_id % 8
        if vi1 == 8:
            vi1 = 0
        verts = PixelMap.vertices [[vi0,vi1]]
        verts += [(dart_id // 8) % self.n_cols, (dart_id // 8) // self.n_cols]
        mid = .5 * verts[0] + .5 * verts[1]
        mid += 0.005 * PixelMap.text_offsets [vi0]
        plt.text(mid[0], mid[1], attribute_value,
                  ha      = PixelMap.text_HAs  [dart_id % 8],
                  va      = PixelMap.text_VAs   [dart_id % 8],
                  rotation=PixelMap.text_angles[dart_id % 8] * rotate
                  )


    def _plot_dart_no(self, dart, rotate = False):
        # print(f"dart: {dart}")
        if dart >= 8*self.n_rows*self.n_cols:
            return # TODO plot the boundary darts, too, if the maps is unbounded
        vi0, vi1 = dart % 8, 1 + dart % 8
        if vi1 == 8:
            vi1 = 0
        verts = PixelMap.vertices [[vi0,vi1]]
        verts += [(dart // 8) %  self.n_cols, (dart // 8) // self.n_cols]
        mid = .5 * verts[0] + .5 * verts[1]
        mid += 0.005 * PixelMap.text_offsets [vi0]
        plt.text (mid[0],mid[1],dart,
            ha      = PixelMap.text_HAs  [dart%8],
            va      = PixelMap.text_VAs   [dart%8],
            rotation= PixelMap.text_angles[dart%8] * rotate
        )

    def plot_faces_dt(self, number_darts = True):
        vertices = PixelMap.vertices
        # iterate over 2-cells
        for some_dart in self.darts_of_i_cells(2):
            x,y = [],[]
            for dart in self.cell_2 (some_dart): # for 2D maps the orbiting darts of the face are 'sorted'
                x.append (vertices [dart%8,0] + (dart // 8) %  self.n_cols)
                y.append (vertices [dart%8,1] + (dart // 8) // self.n_cols)
                if number_darts:
                    distance = self.distances[dart]
                    self._plot_dart_attribute(dart, distance)
            x.append (vertices [some_dart%8,0] + (some_dart // 8) %  self.n_cols)
            y.append (vertices [some_dart%8,1] + (some_dart // 8) // self.n_cols)

            plt.fill(x, y, alpha=.2, color='w')
            plt.plot(x, y, color='k')
            plt.scatter (x[1::2],y[1::2],marker='+',color='k')
            plt.scatter (x[0::2],y[0::2],marker='o',color='k')

        plt.gca().set_aspect (1)
        plt.xticks ([])  # (np.arange (self.n_cols))
        plt.yticks ([])  # (np.arange (self.n_rows)[::-1])
        plt.ylim (self.n_rows-.5, -.5)
        plt.axis ('off')
        plt.title (self.__str__())
        plt.show() # added by LordCatello. Without it does not work (it only works in a notebook)


    def plot_faces (self, number_darts = True):
        vertices = PixelMap.vertices
        # iterate over 2-cells
        for some_dart in self.darts_of_i_cells (2):
            x,y = [],[]
            for dart in self.cell_2 (some_dart): # for 2D maps the orbiting darts of the face are 'sorted'
                x.append (vertices [dart%8,0] + (dart // 8) %  self.n_cols)
                y.append (vertices [dart%8,1] + (dart // 8) // self.n_cols)
                if number_darts:
                    self._plot_dart_no (dart)
            x.append (vertices [some_dart%8,0] + (some_dart // 8) %  self.n_cols)
            y.append (vertices [some_dart%8,1] + (some_dart // 8) // self.n_cols)

            plt.fill (x, y, alpha=.2)
            plt.plot (x,y)
            plt.scatter (x[1::2],y[1::2],marker='+',color='k')
            plt.scatter (x[0::2],y[0::2],marker='o',color='k')

        plt.gca().set_aspect (1)
        plt.xticks ([])  # (np.arange (self.n_cols))
        plt.yticks ([])  # (np.arange (self.n_rows)[::-1])
        plt.ylim (self.n_rows-.5, -.5)
        plt.axis ('off')
        plt.title (self.__str__())
        plt.show() # added by LordCatello. Without it does not work (it only works in a notebook)

    @classmethod
    def from_shape (cls, R, C, sew = True, bounded = True):
        """Constructs grid-like gmap from number rows and columns

        Args:
            R: number of rows
            C: number of columns
            sew: sew the pixels together (default) or not?
            bounded: set to False to add the outer boundary

        Returns:
            2-gMap representing a pixel array

        """
        def _swap2 (A,  r1,c1,i1,  r2,c2,i2):
            """swap helper to 2-sew darts"""
            tmp = A [r1,c1,i1,2].copy()
            A [r1,c1,i1,2] = A [r2,c2,i2,2]
            A [r2,c2,i2,2] = tmp

        def _iter_boundary (R,C):
            """counter-clockwise boundary iteration around the block darts"""
            c = 0
            for r in range (R):
                yield 8*(r*C+c) + 7
                yield 8*(r*C+c) + 6
            r = R-1
            for c in range(C):
                yield 8*(r*C+c) + 5
                yield 8*(r*C+c) + 4
            c = C-1
            for r in range (R-1,-1,-1):
                yield 8*(r*C+c) + 3
                yield 8*(r*C+c) + 2
            r = 0
            for c in range (C-1,-1,-1):
                yield 8*(r*C+c) + 1
                yield 8*(r*C+c) + 0

        # set the members
        cls._nR = R
        cls._nC = C

        n_all_darts = 8*R*C + (not bounded)*4*(R+C)
        alphas_all = np.full ((3, n_all_darts), fill_value=-1, dtype=np.int32)
        alphas_block = alphas_all [:, :8*R*C ] # view at the block part
        alphas_bound = alphas_all [:,  8*R*C:] # view at the outer boundary part

        # create the square by replicating bounded square with increments
        alphas_square = nGmap.from_string (G2_SQUARE_BOUNDED).T
        A = alphas_block.T.reshape ((R,C,8,3)) # rearrange view at the block part
        for r in range (R):
            for c in range (C):
                A [r,c] = alphas_square + 8 * (r*C + c)

        if sew: # 2-sew the squares
            for r in range (R):
                for c in range (C-1):
                    _swap2 (A, r,c,[2,3], r,c+1, [7,6])
            for c in range (C):
                for r in range (R-1):
                    _swap2 (A, r,c,[4,5], r+1, c, [1,0])

        if not bounded: #` add boundary darts
            # set alpha0 to: 1 0 3 2 5 3 ...
            alphas_bound [0,1::2] = np.arange (0,alphas_bound.shape[1],2)
            alphas_bound [0,0::2] = np.arange (1,alphas_bound.shape[1],2)

            # set alpha1 to: L 2 1 4 3 ... 0
            alphas_bound [1,0]      = alphas_bound.shape[1]-1
            alphas_bound [1,1:-1:2] = np.arange (2,alphas_bound.shape[1],2)
            alphas_bound [1,2:-1:2] = np.arange (1,alphas_bound.shape[1]-1,2)
            alphas_bound [1,-1]     = 0

            # add offsets to alpha0 and alpha1 of the boundary block
            alphas_bound[:2] += 8*R*C

            # 2-sew the the darts of the boundary with the darts of the block
            for d_bound,d_block in enumerate (_iter_boundary(R,C)):
                alphas_block [2, d_block] = d_bound + 8*R*C
                alphas_bound [2, d_bound] = d_block
        return cls.from_alpha_array(alphas_all)

# Cell


class LabelMap (PixelMap):
    # _initial_dart_polylines_00 stores start and end coordinates of darts in pixel (0,0)
    _initial_dart_polylines_00 = np.fromstring("""\
        0 1  2 1   2 2  2 2   2 1  0 1   0 0  0 0
        0 0  0 0   0 1  2 1   2 2  2 2   2 1  0 1
        """, sep=' ', dtype=np.float32).reshape(2, 16).T.reshape(8, 2, 2)
    _initial_dart_polylines_00 -= 1
    _initial_dart_polylines_00 *= .95
    _initial_dart_polylines_00 += 1
    _initial_dart_polylines_00 /= 2
    _initial_dart_polylines_00 -= .5

    @classmethod
    def from_labels(cls, labels, add_polyline: bool = True, connected_components_labels: np.array = None):
        if type(labels) == str:
            n_lines = len (labels.splitlines())
            labels = np.fromstring (labels, sep=' ', dtype=np.uint8).reshape(n_lines, -1)
        c = cls.from_shape(labels.shape[0], labels.shape[1])
        cls._labels = labels

        # add drawable polyline for each dart
        if add_polyline:
            c._dart_polyline = {}
            for d in c.darts:
                c._dart_polyline [d] = LabelMap._initial_dart_polylines_00[d % 8].copy()
                c._dart_polyline [d][..., 0] += (d // 8)  % c.n_cols
                c._dart_polyline [d][..., 1] += (d // 8) // c.n_cols

        # save labels
        cls._save_labels(c, labels, connected_components_labels)

        return c

    def _save_labels(gmap, labels: np.array, connected_components_labels: np.array) -> None:
        for i in range(labels.shape[0]):
            for j in range(labels.shape[1]):
                # Get the first dart associated to each pixel
                start_identifier = (i * labels.shape[1]) * 8 + j * 8
                # Save label to all the darts of the cells
                for k in range(8):
                    gmap.image_labels[start_identifier + k] = labels[i][j]
                    if connected_components_labels is not None:
                        gmap.connected_components_labels[start_identifier + k] = connected_components_labels[i][j]
                    else:
                        gmap.connected_components_labels[start_identifier + k] = -1


    def plot(self, attribute_to_show: str = "dart_id", image_palette='gray'):
        """Plots the label map.

        attribute_to_show: "dart_id, "weight"

        image_palette : None to not show the label pixels.
        """
        for d in self.darts:
            e = self.a0(d)
            plt.plot(self._dart_polyline[d][ :,0], self._dart_polyline[d][: ,1],'k-')
            plt.plot([self._dart_polyline[d][-1,0],self._dart_polyline[e][-1,0]],[self._dart_polyline[d][-1,1],self._dart_polyline[e][-1,1]], 'k-')
            # f = self.a1(d)
            # plt.plot ([self._dart_polyline[d][ 0,0],self._dart_polyline[f][ 0,0]],[self._dart_polyline[d][ 0,1],self._dart_polyline[f][ 0,1]], 'b-')
            if attribute_to_show is not None:
                if attribute_to_show == "dart_id":
                    self._plot_dart_no(d)
                elif attribute_to_show == "weight":
                    self._plot_dart_attribute(d, self.weights[d])
                else:
                    raise Exception("Unsupported attribute type")
            plt.scatter(self._dart_polyline[d][ 0,0], self._dart_polyline[d][ 0,1], c='k')
#             plt.scatter(self._dart_polyline[d][-1,0], self._dart_polyline[d][-1,1], marker='+')

        if image_palette:
            plt.imshow(self.labels, alpha=0.5, cmap=image_palette)

        plt.gca().set_aspect (1)
        plt.xticks([])  # (np.arange (self.n_cols))
        plt.yticks([])  # (np.arange (self.n_rows)[::-1])
        plt.ylim (self.n_rows-.5, -.5)
        plt.axis ('off')
        plt.title (self.__str__())
        plt.show() # added by LordCatello. Without it does not work (it only works in a notebook)

    def _evaluate_max_dt_value(self) -> float:
        max_distance = 0
        for d in self.darts:
            distance = self.distances[d]
            if distance >= 0 and distance > max_distance:
                max_distance = distance

        return max_distance

    def plot_dt(self, show_values=True, fill_cell=None):
        # The coloring of the faces doesn't work super well after
        # the reduction
        # I have to take darts of the same 2-cell

        """

        :param show_values:
        :param fill_cell:       face
        :return:
        """

        # evaluate max distance
        max_distance = self._evaluate_max_dt_value()

        for representative_dart in self.darts_of_i_cells(2):
            # The distance of the cell is evaluated as the min distance among all his darts
            x_values_face = []
            y_values_face = []
            min_distance = float('inf')
            for d in self.cell_2(representative_dart):
                distance = self.distances[d]
                if distance >= 0 and distance < min_distance:
                    min_distance = distance

                e = self.a0(d)
                x = list(self._dart_polyline[d][ :,0]) + [self._dart_polyline[d][-1,0],self._dart_polyline[e][-1,0]]
                y = list(self._dart_polyline[d][: ,1]) + [self._dart_polyline[d][-1,1],self._dart_polyline[e][-1,1]]

                plt.plot(x, y, 'k-')

                if show_values:
                    self._plot_dart_attribute(d, distance)

                plt.scatter(self._dart_polyline[d][0, 0], self._dart_polyline[d][0, 1], c='k')
                x_values_face.append(x)
                y_values_face.append(y)

            if fill_cell == 'face':
                x_values_face_ordered, y_values_face_ordered = build_polygon_from_segments((x_values_face, y_values_face))
                if min_distance == float('inf'):  # all darts are None
                    color_value = 1.0
                else:
                    color_value = min_distance / (max_distance * 2) + 0.4
                if color_value > 1.0:
                    raise Exception("Color value is greater than 1.0")
                plt.fill(x_values_face_ordered, y_values_face_ordered, f"{color_value}")

        plt.gca().set_aspect (1)
        plt.xticks([])
        plt.yticks([])
        plt.ylim (self.n_rows-.5, -.5)
        plt.axis ('off')
        plt.title (self.__str__())
        plt.show()

    def generate_dt_voronoi_diagram(self, propagation_labels: typing.List, seed_labels: typing.List[int] = None) -> np.array:
        """
        It generates an rgb dt voronoi diagram.

        seed_labels contains a list of labels which color should be black.
        It can be used to color the stomata to a different color (black in that case).
        in order to distinguish stomata and the area of influence.

        """

        voronoi_diagram = np.zeros((self.n_rows, self.n_cols, 3))

        colors = {}

        for i in range(voronoi_diagram.shape[0]):
            for j in range(voronoi_diagram.shape[1]):
                # get dart associated to each cell
                dart = (i * voronoi_diagram.shape[1] * 8) + j * 8

                if self.image_labels[dart] not in propagation_labels:
                    voronoi_diagram[i][j] = (255, 255, 255)
                    continue

                # If the darts has been removed, take the new corresponding dart
                # to assign a color to the corresponding cell
                while self.ai(0, dart) == -1:
                    dart = self.face_identifiers[dart]

                if self.distances[dart] == -1:
                    # distance not computed for that dart
                    voronoi_diagram[i][j] = (255, 255, 255)  # white
                    continue

                if seed_labels is not None and self.image_labels[dart] in seed_labels:
                    voronoi_diagram[i][j] = (0, 0, 0)  # black
                    continue

                if self.dt_connected_components_labels[dart] not in colors:
                    colors[self.dt_connected_components_labels[dart]] = generate_random_color()

                voronoi_diagram[i][j] = colors[self.dt_connected_components_labels[dart]]

        return voronoi_diagram

    def build_dt_image(self, propagation_labels: typing.List, interpolate_missing_values: bool = True, ) -> np.array:
        """
        It builds an image that keeps for each pixel the distance value kept in the graph.
        A pixel can have 3 different values:
        - From 0 to +inf if the corresponding cell in the gmap has a valid distance value.
        - -2 if the corresponding cell in the gmap has not been used to propagate distances or it is not in propagation_labels
        - -1 if the corresponding cell in the gmap does not exist (due to reduction).
          and "interpolate_missing_values" is False.

        :param interpolate_missing_values:
        :param propagation_labels: list of labels (stomata, air, ...). A dart is considered only if it is in allowed labels.
                                  It is necessary since if the reduction factor is high (close or equal to 1) it happens that
                                  each connected component is reduced to one point. If that connected component was a cell,
                                  during the computation of the distance transform, if that point is on the border and if it is reacheable
                                  by a stomata, a distance value will be associated to that point.
                                  Using this function, an image where all points in that connected component will share that dt value.
                                  This is not optimal for visualization since we want an image with distance value only for the propagation regions.
                                  So usually we don't want to have a distance value to pixels inside a cell.
                                  We can use propagation_labels to specify which darts should have a distance value in producing an image.
        :return:
        """

        image = np.zeros((self.n_rows, self.n_cols))

        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                # Get the dart associated to each pixel
                dart = (i * image.shape[1] * 8) + j * 8

                if self.image_labels[dart] not in propagation_labels:
                    image[i][j] = -2
                    continue

                # Check if the current dart has been deleted during the reduction process of the gmap
                if self.ai(0, dart) == -1:
                    if interpolate_missing_values:
                        # If the dart has been removed take the new corresponding dart
                        # to assign a distance value to the pixel associated to the removed dart
                        while self.ai(0, dart) == -1:
                            dart = self.face_identifiers[dart]
                    else:
                        image[i][j] = -1
                        continue

                distance = self.distances[dart]
                if distance == -1:
                    # the distance is -1 if the corresponding face has not been used
                    # for propagating the distance
                    image[i][j] = -2
                else:
                    image[i][j] = distance

        return image

    def get_label_image(self, interpolate_missing_values: bool = True) -> np.array:
        image = np.zeros((self.n_rows, self.n_cols))

        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                # Get the dart associated to each pixel
                dart = (i * image.shape[1] * 8) + j * 8

                # Check if the current dart has been deleted during the reduction process of the gmap
                if self.ai(0, dart) == -1:
                    if interpolate_missing_values:
                        # If the dart has been removed take the new corresponding dart
                        # to assign a distance value to the pixel associated to the removed dart
                        while self.ai(0, dart) == -1:
                            dart = self.face_identifiers[dart]
                    else:
                        image[i][j] = 255
                        continue

                image[i][j] = self.image_labels[dart]

        return image

    def build_generalized_dt_image(self, interpolate_missing_values: bool = True) -> np.array:
        """
        It builds an image that keeps for each pixel the distance value kept in the graph.
        A pixel can have 3 different values:
        - From 0 to +inf if the corresponding cell in the gmap has a valid distance value.
        - -2 if the corresponding cell in the gmap has not been used to propagate distances.
        - -1 if the corresponding cell in the gmap does not exist (due to reduction).
          and "interpolate_missing_values" is False.

        In case dt is computed using 2-cells (faces) as accumulation directions all the darts in each cell
        will have the same value. So the value of the corresponding pixel in the image will be equals to the
        value of one of the darts in the cell.

        If other types of accumulation directions are used it can happen that the values of distance associated
        to darts in the same face can be different. In that case the average of the values approximated to the
        closest integer is returned as the value of the pixel.
        If one of the values is negative (-1 or -2) then the smallest negative value is returned (since it's a
        special case, where the cell has not been used during the propagation or interpolate_missing_values has
        not been used, so the averga has not to be computed).

        Since the average of the distance values has to be computed for each cell this function is slower than the
        naive one, since all the darts in the cell have to be considered.

        :param interpolate_missing_values: If True, even if a cell in the actual gmap does not exist due to reduction
                                           a value to the corresponding pixel is computed considering the cell that
                                           contains the disappeared cell after the reduction.
        :return:
        """

        # I have to work on it
        # It's not super simple

        """
        image = np.zeros((self.n_rows, self.n_cols))

        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                # Get the dart associated to each pixel
                dart = (i * image.shape[1] * 8) + j * 8

                # Get all the darts associated to the considered face
                darts = gmap.orb

                # Check if the current dart has been deleted during the reduction process of the gmap
                if self.ai(0, dart) == -1:
                    if interpolate_missing_values:
                        # If the dart has been removed take the new corresponding dart
                        # to assign a distance value to the pixel associated to the removed dart
                        while self.ai(0, dart) == -1:
                            dart = self.face_identifiers[dart]
                    else:
                        image[i][j] = -1
                        continue

                distance = self.distances[dart]
                if distance == -1:
                    # the distance is None if the corresponding cell has not been used
                    # for propagating the distance
                    image[i][j] = 255
                else:
                    # normalize in 0:200 (not 255 because 255 is associated with pixels with no distance values)
                    norm_distance = distance / max_distance * 200
                    image[i][j] = norm_distance
        """

        return None

    def plot_labels(self):
        for representative_dart in self.darts_of_i_cells(2):
            self._plot_dart_attribute(representative_dart, self.labels[representative_dart])
            for d in self.cell_2(representative_dart):
                e = self.a0(d)
                x = list(self._dart_polyline[d][ :,0]) + [self._dart_polyline[d][-1,0],self._dart_polyline[e][-1,0]]
                y = list(self._dart_polyline[d][: ,1]) + [self._dart_polyline[d][-1,1],self._dart_polyline[e][-1,1]]

                plt.plot(x, y, 'k-')

                plt.scatter(self._dart_polyline[d][0, 0], self._dart_polyline[d][0, 1], c='k')

        plt.gca().set_aspect (1)
        plt.xticks([])
        plt.yticks([])
        plt.ylim (self.n_rows-.5, -.5)
        plt.axis ('off')
        plt.title (self.__str__())
        plt.show()

    @property
    def labels(self):
        return self._labels

    def value (self,d):
        """Returns label value for given dart"""
        p = d // 8
        return self.labels [p // self.n_cols, p % self.n_cols]

    def remove_edges(self, reduction_factor: float = 1.0):
        """

        :param reduction_factor: Specify how many edges to remove. If 1.0 all the removable edges will be removed
                                 If < 1.0 a removable edge will be removed only with the specified reduction_factor
                                 probability
        :return:
        """
        # TODO edge removal causes skips in the outer loop if used w/i list() ???
        for d in list (self.darts_of_i_cells (1)):          # d ... some dart while iterating over all edges
            e = self.a2(d)                           # e ... dart of the oposit face

            if d == e:                               # boundary edge
                logging.debug ('Skipping: belongs to boundary.')
                continue
            if d == self.a1(e):                      # dangling dart
                logging.debug (f'{d} : pending')
#                 logging.info (d)
                if random.random() < reduction_factor:
                    self.remove_edge(d)
                continue
            if d == self.a0 (self.a1 (self.a0 (e))): # dangling edge
                logging.debug (f'{d} : pending')
#                 logging.info (d)
                if random.random() < reduction_factor:
                    self.remove_edge(d)
                continue
            if d in self.cell_2 (e):                 # bridge (self-touching face)
                logging.debug (f'Skipping bridge at {d}')
                continue
            if (self.value(d) == self.value(e)).all():       # identical colour in CCL
                logging.debug  (f'{d} : low-contrast')
#                 logging.info (d)
                if random.random() < reduction_factor:
                    self.remove_edge(d)
                continue
            logging.debug (f'Skipping: contrast edge at {d}')

    def remove_vertex (self,d):
        if not self.is_i_removable(0,d):
            return
        for d in self.cell_0 (d):
            e = self.a0 (d)
            self._dart_polyline [e] = np.vstack ((self._dart_polyline [e], self._dart_polyline [d][::-1]))
        super().remove_vertex(d)

    # TODO vetrices removal causes skips in darts in the outer loop if used w/i list() ???
    def remove_vertices (self):
        for d in list (self.darts_of_i_cells (0)):      # d ... some dart while iterating over all vertices
            try:
                self.remove_vertex (d)                  # the degree is checked inside
                logging.debug (f'{d} removed')
            except:
                logging.debug (f'{d} NOT removable')