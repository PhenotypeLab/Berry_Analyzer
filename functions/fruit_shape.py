from cv2 import putText, LINE_AA, fitEllipse, FONT_HERSHEY_SIMPLEX, ellipse, circle, contourArea, boundingRect, \
    minAreaRect, drawContours, boxPoints
from math import pi
from .geometry import line_newPoint
from numpy import int0

def berry_shape(cnts, factor=1, prev_result=None, prev_header=None, fancy_output=None):
    """
    Calculates the equatorial and polar size of the berries by fitting an ellipse.
    :param cnts: List of contours that depicts the berries
    :param factor: value used to transform linear distance in pixels to a measurement unit. 1 by default
    :param prev_result: List. Previous data corresponding to each berry where the new data columns are going to be
    appended. If not given, returns a new list
    :param prev_header: List. Where the new data headers are going to be appended
    :param fancy_output: Numpy array image. Image to be edited with a visual output of the acquired data.
    :return: List. Data obtained for each berry; header for the data acquired.
    """
    font = FONT_HERSHEY_SIMPLEX
    if prev_header==None:
        header=['organ','width', 'height', 'area', 'pos_x', 'pos_y']
    else:
        header=prev_header+['organ','width', 'height', 'area', 'pos_x', 'pos_y']
    if prev_result==None:
        result=[]
    else:
        result=prev_result.copy()
    counter=0
    for cnt in cnts:
        area=contourArea(cnt)

        try:
            fancy_output[0]

            center, (MA, ma), angles = fitEllipse(cnt)
            ellipse(fancy_output, (center, (MA, ma), angles), (0,255,0), 1)
            # in angles, is the angle and start angle. We need the angle.
            point_a=line_newPoint(center, MA/2, (angles*(pi/180)))
            point_b=line_newPoint(center, ma/2, ((angles+90)*(pi/180)))

            circle(fancy_output, point_a, 5, (255, 255, 0), -1)
            circle(fancy_output, point_b, 5, (255, 0, 255), -1)

            x, y, w, h = boundingRect(cnt)
            putText(fancy_output, 'width: ' + str(round(MA * factor, 2)), (x+w+2, y+h+2), font, 0.5,
                        (255, 255, 0), 1, LINE_AA)
            putText(fancy_output, 'height: ' + str(round(ma * factor, 2)), (x+w+17, y+h+17), font, 0.5, (255, 0, 255), 1,
                        LINE_AA)


        except:
            _, (MA, ma), _ = fitEllipse(cnt)
        if prev_result==None:
            result.append(['bayas', round(MA * factor, 2), round(ma * factor, 2), round(area*(factor**2), 2), int(center[0]), int(center[1])])
        else:
            result[counter]=result[counter]+['bayas', round(MA * factor, 2), round(ma * factor, 2), round(area*(factor**2), 2), int(center[0]), int(center[1])]
        counter+=1
    return [result, header]

def rachis_shape(cnts, factor=1, prev_result=None, prev_header=None, fancy_output=None):
    if prev_header==None:
        header=['organ','width', 'height', 'area', 'pos_x', 'pos_y']
    else:
        header=prev_header+['organ','width', 'height', 'area', 'pos_x', 'pos_y']
    if prev_result==None:
        result=[]
    else:
        result=prev_result.copy()
    counter=0
    font = FONT_HERSHEY_SIMPLEX
    for cnt in cnts:
        area = contourArea(cnt)
        try:
            fancy_output[0]
            temp_1, (width, height), temp_2 = minAreaRect(cnt)
            drawContours(fancy_output, [int0(boxPoints((temp_1, (width, height), temp_2)))], 0, (0, 255, 0),
                             2)
            x, y, w, h = boundingRect(cnt)
            box = boxPoints((temp_1, (width, height), temp_2))
            box = int0(box)
            circle(fancy_output,
                       (int(((box[1][0] - box[0][0]) / 2) + box[0][0]), int(((box[1][1] - box[0][1]) / 2) + box[0][1])),
                       5,
                       (255, 0, 255), -1)
            circle(fancy_output,
                       (int(((box[3][0] - box[0][0]) / 2) + box[0][0]), int(((box[3][1] - box[0][1]) / 2) + box[0][1])),
                       5,
                       (255, 255, 0), -1)
            putText(fancy_output, 'width: ' + str(round(width * factor, 2)), (x + w + 2, y + h + 2), font, 0.5,
                        (255, 255, 0), 1, LINE_AA)
            putText(fancy_output, 'height: ' + str(round(height * factor, 2)), (x + w + 17, y + h + 17), font, 0.5,
                        (255, 0, 255), 1,
                        LINE_AA)
        except:
            _, (width, height), _ = minAreaRect(cnt)
        if prev_result==None:
            result.append(['raquis',width * factor, height * factor, area*(factor**2)])
        else:
            result[counter]=result[counter]+['raquis',width * factor, height * factor, area*(factor**2)]
        counter+=1
    return [result, header]