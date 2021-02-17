# Importing necessary library
import sys
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# Create a function to monitor the folder & what ever you want to perform when any change happen write here.
def on_Created(event):
    import cv2
    import os
    import easyocr
    reader = easyocr.Reader(['en'])
    # Create empty class to store the result
    images = []

    # Need to give Image file path
    for root, dirs, files in os.walk('/home/vert/Desktop/Images'):
        for files in files:
            if files.endswith('.jpg'):
                Image_path = os.path.join(root, files)
                # print(Image_path)
                # image_name =(os.path.split(Image_path)[-1])

               # Read the image frm the folder
                img = cv2.imread(Image_path)
                if img is not None:
                    result = reader.readtext(img)

                    # Running for loop inside the result to take index
                    for j in result:

                        # Take the proper number from the list
                        i=str(j[1])
                        # Replace the special char to 1
                        a = i.replace('|', '1')
                        b = a.replace('/','1')
                        c = b.replace('!','1')
                        d = c.replace('(','1')
                        e = d.replace(')', '1')
                        result = e.replace('?','1')

                    # Create a txt file in specific folder give the path
                        with open("/home/vert/Desktop/Images/Ref.txt", "a") as f:
                            # Writing the result
                            f.write(result)
                            f.write("\n")
                            f.write("*" * 11)
                            f.write("\n")

                            # Removing the duplicate line in txt
                            lines_seen = set()  # holds lines already seen
                            with open("/home/vert/Desktop/Images/Ref.txt", "w") as output_file:
                                for each_line in open("/home/vert/Desktop/Images/Ref.txt", "r"):
                                    if each_line not in lines_seen:  # check if line is not duplicate
                                        output_file.write(each_line)
                                        lines_seen.add(each_line)

                    # Taking txt file name as x
                    import os
                    for root, dirs, files in os.walk('/home/vert/Desktop/Images/'):
                        for files in files:
                            if files.endswith('.txt'):
                                imagepath = os.path.join(root, files)
                                # image_name = (os.path.split(imagepath)[-1])
                                x = imagepath
                                # print(x)
                    # Taking image file name as y
                    for root, dirs, files in os.walk('/home/vert/Desktop/Images/'):
                        a = 0
                        b = 0
                        for files in files:
                            if files.endswith('.jpg'):
                                imagepath = os.path.join(root, files)
                                y = imagepath
                                y = y.replace('jpg', 'txt')
                                # print(y)

                                #     os.rename(x, y)
                                # except Exception as e:
                                #     continue

                                # Change txt file as per image name
                                b = 0
                                if os.path.isfile(y):
                                    a = 2
                                    # print(x)
                                else:
                                    b = 1
                                    # print(y)
                                if os.path.isfile(x) and b == 1:
                                    os.rename(x, y)
                                    # print("file name change")
                                    b = 0

    # else:
    #     continue
if __name__ == "__main__":

    event_handler = FileSystemEventHandler()
    # Calling Function
    event_handler.on_created = on_Created
    path = ('/home/vert/Desktop/Images')
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
