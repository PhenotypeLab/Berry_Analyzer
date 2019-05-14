import cv2
from numpy import uint8, ones, min, max, zeros
def img_check(img):
    """
    Detects contours in the input image (BGR array) and looks for the white square background and the contours in it.
    :param img: BGR numpy array.
    :return: List with two elements. The first one is a list of contours located inside the white square. The second one
    the contour depicting the square background (None if the square can't be determined).
    """
    frame=img.copy()
    result = []

    w_a, h_a = frame.shape[1], frame.shape[0]

    new_x = 875 / img.shape[1]
    img = cv2.resize(img, None, None, fx=new_x, fy=new_x, interpolation=cv2.INTER_AREA)
    img = cv2.GaussianBlur(img, (5, 5), 0)
    img_roi = cv2.bitwise_or(cv2.Canny(cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[:,:,1], 80, 100),
                             cv2.Canny(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 100, 150))
    M = ones((2, 2), uint8)
    img_roi = cv2.dilate(img_roi, M, iterations=1)

    try:
        _, cnts, hierarchy = cv2.findContours(img_roi, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    except:
        cnts, hierarchy = cv2.findContours(img_roi, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    counter = 0
    major_area=0
    temp=w_a*h_a
    for c in cnts:
        c[:, 0, 0] = c[:, 0, 0] // new_x
        c[:, 0, 1] = c[:, 0, 1] // new_x
        x, y, w, h = cv2.boundingRect(c)
        if (w*h)>=(w_a*h_a)*0.4:
            if temp>(w * h):
                if len(cv2.approxPolyDP(c, 0.04*cv2.arcLength(c,True),True))==4:
                    temp=(w * h)
                    major_area=counter
        counter += 1

    if temp==w_a*h_a:
        return [cnts, None]
    #comparator=cv2.contourArea(cnts[major_area])

    #counter=0
    #for n in hierarchy[0]:
    #    if n[3]==major_area and counter!=major_area and cv2.contourArea(cnts[counter])>comparator*0.7:
    #        temp=counter
    #    counter+=1
    #temp=counter

    #try:
    #    cnts[major_area]
    #except:
    #    return [cnts, None]

    #if temp > 0 and len(cv2.approxPolyDP(cnts[major_area], 0.04*cv2.arcLength(cnts[major_area],True),True))!=4:
    #    return [cnts, None]

    cnts[major_area]=cv2.approxPolyDP(cnts[major_area], 0.04*cv2.arcLength(cnts[major_area],True),True)
    counter = 0

    for n in hierarchy[0]:
        if n[3] == major_area and counter != major_area and len(cnts[counter])>10:
            result.append(cv2.convexHull(cnts[counter]))
        counter += 1
    return [result, cnts[major_area]]

def roi_filter(resolution_xy, contours):
    result=[]
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        cx=int(x+w/2)
        cy=int(y+h/2)
        if w*h>resolution_xy[0]*resolution_xy[1]*0.0001:
            result.append(c)
    return result

def contour_crop(img, cnt, background=False):
    """
    Crop an image to a contour
    :param img: numpy array image. Image to crop
    :param cnt: numpy contour. Selected contour to be cropped in the input image
    :param background: bool. True for return the output image without background (only the portion in the contour)
    :return: numpy array image. Input image cropped to the contour
    """
    temp = img[min(cnt[:, 0, 1]): max(cnt[:,0,1]), min(cnt[:, 0, 0]): max(cnt[:,0,0])]
    if background:
        return temp
    cnt[:, 0, 0] = cnt[:, 0, 0] - min(cnt[:, 0, 0])
    cnt[:, 0, 1] = cnt[:, 0, 1] - min(cnt[:, 0, 1])
    black=zeros((max(cnt[:,0,1]), max(cnt[:,0,0])), uint8)
    cv2.drawContours(black, [cnt], -1, 255, -1)
    return cv2.bitwise_and(temp, temp, mask=black)