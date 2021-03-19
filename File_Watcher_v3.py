# Importing necessary library
# import sys
import time
import numpy as np
# from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import cv2
# import os
# import re
import easyocr
import logging
from logging.handlers import RotatingFileHandler
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

# LOGGER
l1 = datetime.now()
logger = logging.getLogger("Rotating Log")
logger.setLevel(logging.INFO)
# add a time rotating handler
handler = TimedRotatingFileHandler("/home/vert/Desktop/log/logger_{}.log".format(l1), when="m",interval=60)
logger.addHandler(handler)

# DEFINING EASY_OCR with language
reader = easyocr.Reader(["en"],gpu = False, )

# reader1 = easyocr.Reader(["te"],gpu = False)

# Assigning YOLO MODEL into our net variable
net = cv2.dnn.readNet('/home/vert/Coil_Code/yolov3_training_last_v1.weights',
                      '/home/vert/Coil_Code/yolov3_testing.cfg')

# Assigning class for the model to detect
classes = []
with open("/home/vert/Coil_Code/classes.txt", "r") as f:
    classes = f.read().splitlines()

logger.info("class and weight have been assign")

# Create a function to monitor the folder & what ever you want to perform when any change happen write here.
def on_Created(event):

    # sleep your code for 1 sec to read image
    time.sleep(1)

    print(event)

    # From event taking image path
    Image_path = str(str(event)[49:-22])
    print("image path-{}".format(Image_path))

    logger.info("Image Path-{}".format(Image_path))

    # Checking image Format.
    if (Image_path[-3:]) == 'jpg':

        # Taking Image name from vent
        imagename = str(str(event)[75:-26])
        print("image name-{}".format(imagename))
        time.sleep(1)

        # logger.info("Image Path-{}".format(Image_path))
        logger.info("Image Name-{}".format(imagename))

        # Reading the Image from on_created function
        img = cv2.imread(Image_path)
        # cv2.imshow('image', img)
        logger.info("image read")

        # Assigning color to the image
        colors = np.random.randint(0, 255, size=(len(classes), 3), dtype="uint8")

        # Checking Image status
        if img is None:
            print("Image not available")
            pass

        logger.info("image available")

        # Scaling(resize) image to display
        scale_percent = 40
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        logger.info('width height-{} {}'.format(width,height))

        # Resize the original image
        img= cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)

        # Taking Width and height
        (W, H) = (None, None)
        if W is None or H is None:
            (H, W) = img.shape[:2]

        logger.info("print W and H-{},{}".format(W,H))

        width = int(img.shape[1])
        height = int(img.shape[0])

        # Converting image to blob format to give our model to work
        logger.info("Image passing to model")
        blob = cv2.dnn.blobFromImage(img, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        net.setInput(blob)
        ln = net.getUnconnectedOutLayersNames()
        layerOutputs = net.forward(ln)

        # Assigning empty list to append all details
        boxes = []
        confidences = []
        classIDs = []

        # Running for loop into the layer output which came from blob format to know the score
        for output in layerOutputs:
            for detection in output:
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]

                # Getting the confidence score from the detected object
                logger.info("checking confidence")
                if confidence >= 0.4:
                    width = int(img.shape[1])
                    height = int(img.shape[0])

                    # Creating W and H
                    box = detection[0:4] * np.array([W, H, W, H])
                    (centerX, centerY, width, height) = box.astype("int")
                    x_a = int(centerX - (width / 2))
                    y_a = int(centerY - (height / 2))

                    # Appending all the box, confidence and class
                    boxes.append([x_a, y_a, int(width), int(height)])
                    confidences.append(float(confidence))
                    classIDs.append(classID)

        # Finally here we can come to know the detection for the object
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, 0.2, 0.4)
        print(len(idxs))

        # If length of idex is > then o that means model has detect something
        if len(idxs) > 0:

            # Flatten the detection object
            for i in idxs.flatten():

                # Creating bounding box
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])
                color = [int(c) for c in colors[classIDs[i]]]
                cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)

                # Checking coil from the detected object
                if "code" == classes[classIDs[i]]:
                    logger.info("class-{}".format(classes[classIDs[i]]))

                    logger.info("corp the image")

                    # Crop the image
                    img_crop=img[y:y+h,x:x+w]

                    # SAVE IMAGE WITH BOUNDING BOX
                    cv2.imwrite("/home/vert/Desktop/Corp_images/{}.jpg".format(datetime.now()),img)

                    # Once crop done we need to check index value for reading easyocr
                    if img_crop.shape[1] != 0 and img_crop.shape[0] != 0:
                        cv2.imwrite("/home/vert/Desktop/Corp_images/{}.jpg".format(imagename), img_crop)
                        logger.info("Image has been corped")
                        # img_cropg = cv2.cvtColor(img_crop, cv2.COLOR_BGR2GRAY)
                        result = reader.readtext(img_crop)
                        # result1 = reader1.readtext(img_crop)
                        print("result,{}".format(result))
                        # print("result1,{}".format(result1))
                        logger.info("easy ocr processed ")
                        img_crop = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)

                        # Removing all the special chract
                        if result:
                            l = []
                            for z in result:

                                # Take the proper number from the list
                                i = str(z[1])

                                # Replace the special char to 1
                                a = i.replace('|', '1')
                                b = a.replace('/', '1')
                                c = b.replace('!', '1')
                                d = c.replace('(', '1')
                                e = d.replace(')', '1')
                                f = e.replace('S', '5')
                                g = f.replace('&', 'x')
                                h = g.replace('%', 'x')
                                i = h.replace('^', '1')
                                j = i.replace('p', 'B')
                                result = j.replace('?', '1')
                                l.append(result)

                            # save text result in a list to write in txt
                            m = ""
                            for x in l:
                                m += x
                                m += ";"
                            # print(l)
                                # print(result)

                            # Create a txt file in specific folder give the path
                            with open("/home/vert/Desktop/Images/{}.txt".format(imagename), "a+") as f:

                                # Writing the result
                                f.write(m)
                                f.write("\n")
                                f.write(" ")
                                f.write("\n")
                                logger.info("Code has been written")
                                time.sleep(1)

                            # with open("/home/vert/Desktop/Images/{}.txt".format(imagename), "r+") as k:
                            #     content = k.read()
                            #     content = content.replace(', ', ";")
                            #     k.write(content)
                            #     k.close()


                        else:

                            with open("/home/vert/Desktop/Images/{}.txt".format(imagename), "a") as f:

                                # Writing the result
                                f.write(" ")
                                f.write("\n")
                                logger.info("Unable to detect Code from Image")
                                time.sleep(1)
        else:
            with open("/home/vert/Desktop/Images/{}.txt".format(imagename), "a") as f:

            # Writing the result
                f.write(" ")
                logger.info("Unable to detect Code from Image")
                time.sleep(1)

        # cv2.imshow("crop_image",img_crop)
        # cv2.imshow("normal_image",img)
        # cv2.waitKey(0)

    else:
        pass
    # When everything done, release the capture
    # cap.release()
    # cv2.waitKey(0)
cv2.destroyAllWindows()

if __name__ == "__main__":

    event_handler = FileSystemEventHandler()

    # Calling Function
    event_handler.on_created = on_Created

    #
    path = ('/home/vert/Desktop/Images')
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # observer.stop()
        observer.join()
        time.sleep(1)