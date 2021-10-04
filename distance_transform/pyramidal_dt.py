import typing

import numpy as np
import math


from distance_transform.wave_propagation import wave_propagation_dt_image


def pyramidal_dt_binary_image(image: np.array, stride: int) -> np.array:
    """
    Parallel approximate algorithm that should (hopefully) takes O(log(n))
    where n is the number of darts

    Time complexity: O(log(n)) ?
    Space complexity: O(n) ?

    Algorithm:
    1) Reduce image size through a pyramid
    2) Compute dt on a reduced image
    3) Interpolate the obtained values for each level

    :param image:
    :param stride:
    :return:
    """

    dt_image = np.zeros(image.shape, dtype=image.dtype)

    # reduce image
    reduced_image = reduce_size_binary_image(image, stride)

    # compute dt
    dt_image = wave_propagation_dt_image(reduced_image)

    # interpolate


    return dt_image


def reduce_size_binary_image(image: np.array, stride: int) -> np.array:
    """
    How to compress the image?
    A binary image has only zeroes and ones.

    The idea is to use a kernel to compress all the values under the kernel to a unique value in the reduced image.
    How to chose the value?
    1) If all the values under the kernel are the same (all zeroes or all ones) the new value in the reduced image
       is the same value in the original one.
    2) If the values are not the same two different approaches can be pursued:
        a) take the most representative value
        b) take always 0 (seed value). In fact we won't lose the seeds, so it could be a good idea to preserve them
        In either cases we are losing information, so we should be careful.
        Maybe different approaches can be tried.

    How to manage boundaries if the kernel size is not perfect?
    I can add ones to the boundaries if the kernel size does not fit perfectly.

    PRECONDITIONS:
    At the moment, for simplicity, only 2d images are considered.

    :param image:
    :param stride: for simplicity for the moment it is only an integer (square kernel). It could be a tuple of integers
                   if kernels of different forms would be used
    :return:
    """

    def compute_reduced_value(image: np.array, reduced_image_x: int, reduced_image_y: int, stride: int) -> int:
        start_x = reduced_image_x * stride
        start_y = reduced_image_y * stride
        end_x = start_x + stride
        end_y = start_y + stride

        for i in range(start_x, end_x):
            for j in range(start_y, end_y):
                if i > (image.shape[0] - 1) or j > (image.shape[1] - 1):
                    continue
                if image[i][j] == 0:
                    return 0

        return 1

    # Allocate new image
    # Ceil has to be used because if the kernel does not cover perfectly the image ones will be added to the
    # original image to fit the kernel
    reduced_image_shape = [math.ceil(dim / stride) for dim in image.shape]
    reduced_image = np.zeros(reduced_image_shape, dtype=image.dtype)

    for i in range(reduced_image_shape[0]):
        for j in range(reduced_image_shape[1]):
            reduced_value = compute_reduced_value(image, i, j, stride)
            reduced_image[i][j] = reduced_value

    return reduced_image


def interpolate_dt_binary_image(dt_reduced_image: np.array, stride: int) -> np.array:
    """
    The algorithm is sequential but it can be parallelized to obtain (hopefully) O(1) time complexity.

    Moreover the algorithm has been implemented giving priority to readability, sacrificing performance.
    If the results will be good a more efficient version of the algorithm will be implemented.

    :param dt_reduced_image:
    :param stride:
    :return:
    """

    def wave_propagation_interpolation(image: np.array, center_position: typing.Tuple[int, int], stride: int) -> None:
        # Get sub-image centered in center_position and call wave propagation algorithm
        center_x = center_position[0]
        center_y = center_position[1]
        radius = stride - 1

        left_x = max(center_x - radius, 0)
        left_y = max(center_y - radius, 0)

        right_x = center_x + radius + 1  # +1 is necessary because right_x and right_y are included
        right_y = center_y + radius + 1

        sub_image_center_x = center_x - left_x
        sub_image_center_y = center_y - left_y

        output_image = wave_propagation_dt_image(image[left_x:right_x, left_y:right_y],
                                                 seeds=[(sub_image_center_x, sub_image_center_y)])

        # Update the input image saving the minimum between the current value and the new one for each pixel
        for i in range(output_image.shape[0]):
            for j in range(output_image.shape[1]):
                original_x = i + left_x
                original_y = j + left_y
                if image[original_x][original_y] == -1:
                    image[original_x][original_y] = output_image[i][j]
                else:
                    image[original_x][original_y] = min(image[original_x][original_y], output_image[i][j])

    dt_original_image_shape = [dim * stride for dim in dt_reduced_image.shape]
    dt_original_image = np.zeros(dt_original_image_shape, dtype=dt_reduced_image.dtype)

    # Initialization
    for i in range(dt_original_image.shape[0]):
        for j in range(dt_original_image.shape[1]):
            dt_original_image[i][j] = -1

    # 1) Fill original image with values obtained from the reduced one multiplied by stride
    #    The values will always be placed in the top left position
    #    Example
    """
         0 1
         1 2
         
         0 ? 2 ?
         ? ? ? ?
         2 ? 4 ?
         ? ? ? ?
    """
    for i in range(dt_reduced_image.shape[0]):
        for j in range(dt_reduced_image.shape[1]):
            dt_original_image[i*stride][j*stride] = dt_reduced_image[i][j] * stride

    # 2) Interpolate
    """
    Algorithm:
        For each not -1 value in the original image apply wave propagation considering a square
        centered in the value with radius/diagonal equals to (stride - 1)
        
        Square Example
        stride = 3
        
        x x x x x
        x x x x x
        x x 4 x x
        x x x x x
        x x x x x
        
        The x values indicated the pixels where wave propagation has to be applied
        
        Apply wave propagation this way collision between different centers will happen.
        This is the desired behaviour. In fact if for a pixel multiple values have been evaluated
        from different centers only the smallest one will be kept.
    
        This will ensure that a coherent dt image will be obtained, where coherent means that the distance between
        each two neighbours pixels is never greater than 1 and the growth direction is coherent.
        
        A detailed explanations and more examples can be found in my notebook.
    """

    for i in range(dt_reduced_image.shape[0]):
        for j in range(dt_reduced_image.shape[1]):
            original_image_center_position = (i * stride, j * stride)
            wave_propagation_interpolation(dt_original_image, original_image_center_position, stride)

    print(dt_original_image)

    return dt_original_image
