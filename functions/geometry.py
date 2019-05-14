from math import hypot, cos, sin
from cv2 import contourArea
def points_distance(pt1, pt2):
    """
    Distance between two points
    :param pt1: x,y pair 1
    :param pt2: x,y pair 2
    :return: float
    """
    return hypot(pt2[0] - pt1[0], pt2[1] - pt1[1])

def line_newPoint(point, length,rad):
    """
    Calculates the coordinates of a new point given an origin point, a length and an angle
    :param point: x,y pair origin point
    :param length: Distance to the new point
    :param rad: float. Angle of the new point to the origin point (in radians)
    :return: int tuple. Coordinates of the new point
    """
    x = int(point[0] + (length * cos(rad)))
    y = int(point[1] + (length * sin(rad)))
    return (int(x), int(y))

def factor_calculator(markers_list, real_border=1):
    return (real_border*0.895) / (contourArea(markers_list[0].coordinates().reshape(4, 1, 2)) ** (1 / 2))