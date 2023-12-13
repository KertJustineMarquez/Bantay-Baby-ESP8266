
#IMPORTED LIBRARIES
import cv2
import numpy as np
import face_recognition
import os
import urllib.request

#initialization of path of the folder to a variable
path = r'faceimages2'

#can be replaceable, it depends on IP address
url = 'http://192.168.137.18/cam-lo.jpg'

#initialization of image list 
images = []

#initialization of image names in the folder
className = []

#initialization of mylist variable to store list directory from path
myList = os.listdir(path)


#loop function to grab image from path which is the image folder 
for cls in myList:
    #variable for reading the path in the folder
    currentImage = cv2.imread(f'{path}/{cls}')
    #appending the images from the folder to the list 'images'
    images.append(currentImage)
    #appending the names of the images from the folder without grabbing the image format
    className.append(os.path.splitext(cls)[0])
   

# define function for finding the image that will be encoded in the program 
def findEncondings(images, names):
    # initialization of encodeList list
    encodeList = []

    # for loop function of image in image folder
    for img, name in zip(images, names):
        # conversion of image to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # initialization of encode variable for face recognition face encoding image
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

        # print the name associated with the current image
        print(f"Encoding {name} complete")

    return encodeList

# initialization of variable for encoded images
encodeListKnown = findEncondings(images, className)
print('Encoding Complete')

# initialization of video capture. PS change the number '0' to any number corresponding to what camera you want to use
cap = cv2.VideoCapture(url)

#function if real or fake person
def is_face_moving(prev_face_locations, current_face_locations):
    if not prev_face_locations or not current_face_locations:
        return False

    # Convert the locations to NumPy arrays
    prev_face_locations = np.array(prev_face_locations)
    current_face_locations = np.array(current_face_locations)

    # Calculate the distance between the current and previous face locations
    distance = np.mean(np.linalg.norm(prev_face_locations - current_face_locations, axis=1))
    return distance > 10  # You can adjust the threshold as needed

# Initialization of previous face locations
prev_face_locations = []

while True:
    img_resp = urllib.request.urlopen(url)
    imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
    img = cv2.imdecode(imgnp, -1)
    imgSmall = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
    imgSmall = cv2.cvtColor(imgSmall, cv2.COLOR_BGR2RGB)
    
    faceCurrentFrame = face_recognition.face_locations(imgSmall)
    encodeCurrentFrame = face_recognition.face_encodings(imgSmall, faceCurrentFrame)

    # Check liveness by comparing current and previous face locations
    if is_face_moving(prev_face_locations, faceCurrentFrame):
        print("Liveness Check: Real Person")
        liveness_color = (0, 255, 0)  # Green for real person
    else:
        print("Liveness Check: Potential Spoofing")
        liveness_color = (0, 0, 255)  # Red for potential spoofing

    prev_face_locations = faceCurrentFrame  

    for encodeFace, faceLoc in zip(encodeCurrentFrame, faceCurrentFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

        if any(face_distance < 0.6 for face_distance in faceDis):
            matchIndex = np.argmin(faceDis)
            confidence = (1 - faceDis[matchIndex]) * 100  # Confidence level in percentage

            if confidence < 50:
                name = "Unknown"
                confidence_text = f"Confidence: {confidence:.2f}% (Below Threshold)"
                blurriness_text = ""
            elif matches[matchIndex]:
                name = className[matchIndex].upper()
                confidence_text = f"Confidence: {confidence:.2f}%"
                
                # Calculate blurriness
                gray_face = cv2.cvtColor(imgSmall, cv2.COLOR_RGB2GRAY)
                laplacian_var = cv2.Laplacian(gray_face, cv2.CV_64F).var()
                blurriness_text = f"Blurriness: {laplacian_var:.2f}"
            else:
                name = "Unknown"
                confidence_text = f"Confidence: {confidence:.2f}% (Below Threshold)"
                blurriness_text = ""

            # Draw rectangle with different colors for potential spoofing
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), liveness_color, 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), liveness_color, cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(img, confidence_text, (x1 + 6, y2 + 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(img, blurriness_text, (x1 + 6, y2 + 60), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
        else:
            print("Unknown face detected - potential spoofing")
            # Draw rectangle with red color for potential spoofing
            for faceLoc in faceCurrentFrame:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 0, 255), cv2.FILLED)

    cv2.imshow('live Cam Testing', img)
    key = cv2.waitKey(5)
    if key == ord('q'):
        break
