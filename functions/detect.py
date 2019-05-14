try:
    import cv2
except ImportError:
    raise Exception('Error: OpenCv is not installed')

import numpy as np
from ar_markers.coding import decode, extract_hamming_code
from .marker import HammingMarker

BORDER_COORDINATES = [
    [0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [1, 0], [1, 6], [2, 0], [2, 6], [3, 0],
    [3, 6], [4, 0], [4, 6], [5, 0], [5, 6], [6, 0], [6, 1], [6, 2], [6, 3], [6, 4], [6, 5], [6, 6],
]

ORIENTATION_MARKER_COORDINATES = [[1, 1], [1, 5], [5, 1], [5, 5]]

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def four_point_transform(image, pts):
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
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped

def validate_and_turn(marker):
    # first, lets make sure that the border contains only zeros
    for crd in BORDER_COORDINATES:
        if marker[crd[0], crd[1]] != 0.0:
            raise ValueError('Border contians not entirely black parts.')
    # search for the corner marker for orientation and make sure, there is only 1
    orientation_marker = None
    for crd in ORIENTATION_MARKER_COORDINATES:
        marker_found = False
        if marker[crd[0], crd[1]] == 1.0:
            marker_found = True
        if marker_found and orientation_marker:
            raise ValueError('More than 1 orientation_marker found.')
        elif marker_found:
            orientation_marker = crd
    if not orientation_marker:
        raise ValueError('No orientation marker found.')
    rotation = 0
    if orientation_marker == [1, 5]:
        rotation = 1
    elif orientation_marker == [5, 5]:
        rotation = 2
    elif orientation_marker == [5, 1]:
        rotation = 3
    marker = np.rot90(marker, k=rotation)
    return marker


def detect_markers(img, area_thresh=100):
    """
    This is the main function for detecting markers in an image.

    Input:
      img: a color or grayscale image that may or may not contain a marker.

    Output:
      a list of found markers. If no markers are found, then it is an empty list.
    """
    #cv2.namedWindow('watcher', cv2.WINDOW_NORMAL)
    if len(img.shape) > 2:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = img.copy()

    width, height = img.shape
    img = cv2.Canny(img, 100, 255)
    #M = np.ones((2, 2), np.uint8)
    #img = cv2.dilate(img, M, iterations=1)

    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2:]

    # We only keep the long enough contours
    min_contour_length = width*height / area_thresh

    markers_list = []
    for contour in contours:
        rect = cv2.minAreaRect(contour)

        if rect[1][0]*rect[1][1] <= min_contour_length:
            continue

        box = cv2.boxPoints(rect)
        box = np.int0(box)

        warped_gray = four_point_transform(gray, box)
        umbral = 120
        _, warped_bin = cv2.threshold(warped_gray, umbral, 255, cv2.THRESH_BINARY)

        marker = cv2.resize(warped_bin, (7,7), interpolation=cv2.INTER_LINEAR)

        #cv2.imshow('watcher', marker)
        #cv2.waitKey(0)

        marker[marker < 255] = 0
        marker[marker == 255] = 1
        try:
            marker = validate_and_turn(marker)
            hamming_code = extract_hamming_code(marker)
            marker_id = int(decode(hamming_code), 2)
            markers_list.append(HammingMarker(id=marker_id, contours=box))
        except ValueError:
            continue
    return markers_list

def detect_markers_integrated(img, contours, area_thresh=100):
    """
    This is the main function for detecting markers in an image.

    Input:
      img: a color or grayscale image that may or may not contain a marker.

    Output:
      a list of found markers. If no markers are found, then it is an empty list.
    """
    if len(img.shape) > 2:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img.copy()

    width, height = gray.shape

    # We only keep the long enough contours
    min_contour_length = width*height / area_thresh

    markers_list = []
    new_contours=[]
    for contour in contours:
        rect = cv2.minAreaRect(contour)
        if rect[1][0]*rect[1][1] <= min_contour_length:
            new_contours.append(contour)
            continue

        box = cv2.boxPoints(rect)
        box = np.int0(box)

        if np.min(box)<0 or np.max(box[:,0])>gray.shape[1] or np.max(box[:,1])>gray.shape[0]:
            new_contours.append(contour)
            continue

        warped_gray = four_point_transform(gray, box)
        umbral = 110
        _, warped_bin = cv2.threshold(warped_gray, umbral, 255, cv2.THRESH_BINARY)

        marker = cv2.resize(warped_bin, (7,7), interpolation=cv2.INTER_LINEAR)

        marker[marker < 255] = 0
        marker[marker == 255] = 1
        try:
            marker = validate_and_turn(marker)
            hamming_code = extract_hamming_code(marker)
            marker_id = int(decode(hamming_code), 2)
            markers_list.append(HammingMarker(id=marker_id, contours=box))
        except ValueError:
            new_contours.append(contour)
            continue
    return [markers_list, new_contours]