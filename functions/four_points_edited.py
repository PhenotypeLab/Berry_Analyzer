import numpy as np
from cv2 import getPerspectiveTransform, warpPerspective, perspectiveTransform

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def contour_transform(contours_list, perspective_matrix):
    """
    Apply a perspective matrix to a list of contours.
    :param contours_list: List. Contours to be transformed
    :param perspective_matrix: perspective matrix from the getPerspectiveTransform of the OpenCV library
    :return: List. List of transformed contours
    """
    result=[]
    for cnt in contours_list:
        cnt = perspectiveTransform(cnt.reshape(1, len(cnt), 2).astype('float32'), perspective_matrix)
        result.append(cnt.reshape(len(cnt[0]), 1, 2).astype('int'))
    return result

def four_point_transform(image, pts):
    """
    Edited four points transformation function from imutils package.
    :param image: numpy array image.
    :param pts: four pairs of x,y coordinates
    :return: List. Numpy array transformed image; perspective matrix.
    """

    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")
    M = getPerspectiveTransform(rect, dst)
    warped = warpPerspective(image, M, (maxWidth, maxHeight))
    return [warped, M]