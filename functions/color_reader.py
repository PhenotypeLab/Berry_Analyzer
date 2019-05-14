from numpy import asarray, array, argwhere
from cv2 import COLOR_BGR2Lab, cvtColor, inRange, add, countNonZero, imshow, waitKey
from .find_objects import contour_crop
from os import listdir

def tmpl_mask(img, tmpls_parsed, factor=1, cnts=None, prev_result=None, prev_header=None):
    """
    Apply the 32x32 color templates to the input image.
    :param img: numpy array image. Input image
    :param tmpls_parsed: List. Parsed templates
    :param factor: value used to transform linear distance in pixels to a measurement unit. 1 by default
    :param cnts: List. Contours that defines the objects in the input image to be analyzed. If not given, a whole image
    analysis is going to be performed.
    :param prev_result: List. Previous data corresponding to each berry where the new data columns are going to be
    appended. If not given, returns a new list
    :param prev_header: List. Data obtained for each berry; header for the data acquired.
    :return:
    """
    try:
        cnts[0][0]
    except:
        cnts=[asarray([(0,0), (0, img.shape[0]), (img.shape[1], img.shape[0]), (img.shape[1], 0)]).reshape(4,1,2)]
    img = cvtColor(img, COLOR_BGR2Lab)
    if prev_result==None:
        result=[]
    else:
        result=prev_result.copy()
    counter=0
    if prev_header==None:
        header=[]
    else:
        header=prev_header.copy()
    for cnt in cnts:
        if prev_result==None:
            result.append([])

        img_temp=contour_crop(img, cnt, background=True)
        total=[]
        for (name,tmpl_parsed) in tmpls_parsed:
            if counter==0:
                header.append(name+'_area')
                header.append(name + '_%')
            masked = ''
            for n in tmpl_parsed:
                boundaries_c = [(
                    [
                        0,
                        range(0, 257, 8)[n[1]],
                        range(0, 257, 8)[::-1][n[0] + 1]
                    ],  # lower
                    [
                        250 * n[2],
                        range(0, 257, 8)[n[1] + 1] - 1,
                        range(0, 257, 8)[::-1][n[0]] - 1
                    ]  # upper
                )]
                for (lower, upper) in boundaries_c:
                    lower = array(lower, dtype="uint8")
                    upper = array(upper, dtype="uint8")
                c_mask = inRange(img_temp, lower, upper)
                if type(masked) == str:
                    masked = c_mask

                masked = add(masked, c_mask)
            total.append(round(countNonZero(masked) * (factor ** 2), 2))
            #if prev_result==None:
            #    result[-1].append(round(countNonZero(masked) * (factor ** 2), 2))
            #else:
            #    result[counter].append(round(countNonZero(masked) * (factor ** 2), 2))
        all=sum(total)
        for n in total:
            if prev_result==None:
                #result[-1].append(round(countNonZero(masked) * (factor ** 2), 2))
                result[-1].append(n)
                result[-1].append(round((n/all)*100, 2))
            else:
                #result[counter].append(round(countNonZero(masked) * (factor ** 2), 2))
                result[counter].append(n)
                result[counter].append(round((n / all) * 100, 2))
        counter+=1
    return [result, header]

def template_reader(directory):
    """
    Parse the colour templates from a folder
    :param directory: path to the folder containing the colour template files
    :return: list. For each file, the name of the colour template files and the values are appended to the returned list
    """
    result=[]
    if directory[-1]!='/':
        directory+='/'
    for n in listdir(directory):
        if '.tsv' not in n:
            continue
        filess = open(directory+n, 'r')
        filess_tab = filess.read().replace('\n', '\t').split('\t')
        if filess_tab[len(filess_tab) - 1] == '':
            filess_tab = filess_tab[:len(filess_tab) - 1]
        filess.close()
        filess_tab = [float(n) for n in filess_tab]
        filess_tab = asarray(filess_tab)
        chromatic_arr = filess_tab.reshape(32, 32)
        filess_tab = argwhere(chromatic_arr > 0 )
        n_arr = []
        for (x, y) in filess_tab:
            n_arr.append([x, y, chromatic_arr[x][y]])
        result.append([n[:-4], n_arr])
    return result