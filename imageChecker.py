import cv2 
import os, os.path
from PIL import Image
import numpy 

#code to iterate through images. window pixel points are top left CCW currently
def showAllImg(path):
    imgs = []
    paths = []
    valid_images = [".jpg",".gif",".png",".tga"]
    for f in os.listdir(path):
        ext = os.path.splitext(f)[1]
        if ext.lower() not in valid_images:
            continue
        paths.append(os.path.join(path,f))
        imgs.append(Image.open(os.path.join(path,f)))
    for i in range(len(imgs)):
        cv2.namedWindow(paths[i], cv2.WINDOW_NORMAL)        # Create window with freedom of dimensions
        cv2.resizeWindow(paths[i], 800, 600) 
        opencvImage = cv2.cvtColor(numpy.array(imgs[i]), cv2.COLOR_RGB2BGR)
        cv2.imshow(paths[i],opencvImage)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
# def displayDirImage(path,my_dir): 
#     for indx, f in enumerate(os.listdir(path), start=1):
#         image = cv2.imread(os.path.join(my_dir, 'attachments', f))  
#         cv2.imshow("Image-{}".format(indx), image)
#         cv2.waitKey(600)

if __name__ == "__main__":
    showAllImg("./val/finalVal/real/")
