from cv2 import imread, imwrite, drawContours, bitwise_and
from functions.detect import detect_markers_integrated
from functions.find_objects import img_check, roi_filter, contour_crop
from functions.color_balance_marker import colorBalance
from functions.color_reader import template_reader, tmpl_mask
from functions.four_points_edited import four_point_transform, contour_transform
from functions.geometry import factor_calculator
from functions.fruit_shape import berry_shape, rachis_shape
from functions.json_formatter import Json_formatter
from numpy import zeros, uint8

organs=['bayas', 'raquis']

def analyzer(url, url_output, color_folder, organ, json_data=True):
    img = imread(url)

    # detect the white square and the objects in it
    contours, bg_cnt = img_check(img)

    # transform the image to white square area. Also apply the transformation to the objects
    img, persp_mtx = four_point_transform(img, bg_cnt[:, 0, :])
    contours = contour_transform(contours, persp_mtx)

    # detect marker and delete it from contours
    markers, contours = detect_markers_integrated(img, contours)
    img = colorBalance(img, markers[0].coordinates())

    # (optional) calculate factor pixel to cm
    factor = factor_calculator(markers, real_border=5.0)

    # (optional) filter detected objects
    contours = roi_filter(img.shape[:2][::-1], contours)

    # UNDER CONSTRUCTION: generate a visual output
    black = zeros(img.shape[:2], uint8)
    drawContours(black, contours, -1, 255, -1)
    black = bitwise_and(img, img, mask=black)

    # prepare the header and a data collector variables
    header = []
    result = []
    for c in contours:
        result.append([])

    # (optional) shape analysis. IMPORTANT: change this function according to the photos to be analyze
    if organ=='bayas':
        result, header = berry_shape(contours, factor, prev_result=result, prev_header=header, fancy_output=black)
    elif organ=='raquis':
        result, header = rachis_shape(contours, factor, prev_result=result, prev_header=header, fancy_output=black)

    if color_folder != None:
        # (optional) color balance
        img = colorBalance(img, markers[0].coordinates())

        # (optional) color analysis
        templates = template_reader(color_folder)
        result, header = tmpl_mask(img, templates, factor, contours, prev_result=result, prev_header=header)
    #print(url, url_output)
    if url_output != None:
        if url_output[-1]=='/':
            imwrite(url_output+url.split('/')[-1]+'_watcher.png', black)
        else:
            imwrite(url_output + '/' + url.split('/')[-1] + '_watcher.png', black)
    if json_data:
        return Json_formatter(header, result)
    else:
        return [header]+result
