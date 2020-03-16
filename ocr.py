''' OCR an image file

EXAMPLE
print(ocr('ETKU0TXXgAEc06q.jpeg',black=20, white=250,smooth=True, smoothsize=(5,5), morph='close'))

"THE LAB-CREATED COROMA VIRUS WAS A COVER-UP FOR
ae es
eg sie eacit g

a gy Be Dy

CELEBRITIES, AND CEOS, INCLUDING GLOBAL ELITES AND
BANKERS SUCH AS GEORGE SOROS, ULM. OFFICIALS, AND
THE FOUMBERS OF GRETA, INC."

2020-03-16
Tom Taylor

'''


def ocr(path_to_image, black=0, white=255, smooth=False, smoothsize=(3,3), morph=None, kernel = np.ones((3,3),np.uint8)) :
    """outputs text extracted from image, blak and white expect integer between 0 and 254, 
    smooth is boolean, smoothsize requires a tuple of odd integers, morph is in     
    [None,'open', close', 'dilate'], kernel is an odd-dimensioned 2x2 numpy array of uint8
    """
    import cv2
    import pytesseract as pt
    import numpy as np
    img = cv2.imread( path_to_image )
    grayimg = cv2.cvtColor( img, cv2.COLOR_BGR2GRAY )
    if smooth == True :
        grayimg = cv2.GaussianBlur(grayimg,smoothsize,0)
    blackwhite = cv2.threshold(grayimg, black, white, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    if morph == 'open' :
        blackwhite = cv2.morphologyEx(blackwhite, cv2.MORPH_OPEN, kernel)
    elif morph == 'close' :
        blackwhite = cv2.morphologyEx(blackwhite, cv2.MORPH_CLOSE, kernel)
    elif morph == 'dilate' :
        blackwhite = cv2.dilate(blackwhite,kernel)
    else :
        pass
    
    return pt.image_to_string(blackwhite)



