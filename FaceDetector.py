import cv2
import os
import mtcnn
haardCascadeTemplateList = [
     "haarcascade_righteye_2splits.xml",
 "haarcascade_profileface.xml",
 "haarcascade_lefteye_2splits.xml",
 "haarcascade_frontalface_default.xml",
 "haarcascade_frontalface_alt_tree.xml",
 "haarcascade_frontalface_alt2.xml",
 "haarcascade_eye_tree_eyeglasses.xml",
 "haarcascade_eye.xml",
"haarcascade_frontalface_alt.xml"
]

class FaceDetector:
    def __init__(self):
        self.detector = mtcnn.MTCNN()
        cascadesFiles = list(filter(lambda x: x.find(".xml") != -1,os.listdir(cv2.haarcascades)))
        self.cascades = []
        for fileName in cascadesFiles:
            if fileName in haardCascadeTemplateList:
                cascade = cv2.CascadeClassifier()
                cascade.load(cv2.samples.findFile(cv2.haarcascades+fileName))
                self.cascades.append(cascade)

    def detectFaceWithMTCNN(self,imagePath):
        image = cv2.imread(imagePath)
        imageNewFile = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        detectedFacesInfo = self.detector.detect_faces(imageNewFile)
        faceLocations = [faceInfo['box'] for faceInfo in detectedFacesInfo]
        self.__drawMarks(image,faceLocations)

        return (image,faceLocations)

    def detectFaceWithCascades(self, imagePath):
        image = cv2.imread(imagePath)
        grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        grayImage = cv2.equalizeHist(grayImage)
        faceLocations = []
        for cascade in self.cascades:
            locations = cascade.detectMultiScale(grayImage)
            for loc in locations:
                faceLocations.append(loc)
        self.__drawMarks(image, faceLocations)
        return (image,faceLocations)

    def __drawMarks(self,image,faceLocations):
        for (x0, y0, w, h) in faceLocations:
            image = cv2.rectangle(image, (x0, y0),(x0+w, y0+h), (0, 0, 255), 2)
            # center = (x + w // 2, y + h // 2)
            # image = cv2.ellipse(image, center, (w // 2, h // 2), 0, 0, 360, (255, 0, 255), 4)
        return image

