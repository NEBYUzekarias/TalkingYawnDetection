import cv2
import dlib
import os
import numpy as np
import pandas as pd
import json
from threading import Thread


class DriverActionDataset(object):
    def __init__(self,dataset_dir,image_shape,max_sequence_length=1519):
        self.dataset_dir = dataset_dir
        self.image_shape = image_shape
    def get_attribute(self,folder_name):
        subj,gender_glasses,action_str = folder_name.split("-")
        gender = -1
        glasses_str = None
        if gender_glasses[:4].lower() == "male":
            gender = 1
            glasses_str = gender_glasses[4:]
        elif gender_glasses[:6].lower() == "female":
            gender = 0
            glasses_str = gender_glasses[6:]
        else:
            raise Exception("Unable to parse gender from "+str(folder_name))
        glasses = -1
        
        if glasses_str[:9].lower() =="noglasses":
            glasses = 0
        elif glasses_str[:7].lower()  == "glasses" or glasses_str[:10].lower() == "sunglasses":
            glasses = 1
        else:
            raise Exception("Unable to parse glasses information from "+str(folder_name))
        
        actions_str = action_str.split("&")
        for i in range(len(actions_str)):
            if actions_str[i].lower()=="normal":
                action = 0
            elif actions_str[i].lower() == "yawning":
                action = 0
            elif actions_str[i].lower() == "talking":
                action = 1
                break
            else:
                raise Exception("Unable to parse action information from " + str(folder_name))

        
        output = {"Subject":subj,"Gender":gender,"Glasses":glasses,"Action":action}
        
        return output
    def get_dlib_points(self,image,face,predictor):
        shape = predictor(image,face)
        dlib_points = np.zeros((68,2))
        for i,part in enumerate(shape.parts()):
            dlib_points[i] = [part.x,part.y]
        return dlib_points
    def get_right_eye_attributes(self,image,dlib_points):
        right_eye_top = int(max(dlib_points[19][1]-5,0))
        right_eye_left = int(max(dlib_points[17][0]-5,0))
        right_eye_right  = int(min(dlib_points[21][0]+5,image.shape[1]))
        right_eye_bottom = int(min(dlib_points[41][1]+5,image.shape[0]))

        right_eye = image[right_eye_top:right_eye_bottom,right_eye_left:right_eye_right]

        r_left_corner_top   = int(max(dlib_points[19][1],0))
        r_left_corner_left  = int(max(dlib_points[19][0],0))
        r_left_corner_right = int(min(dlib_points[27][0],image.shape[1]))
        r_left_corner_bottom = int(min(dlib_points[41][1],image.shape[0]))

        right_eye_left_corner = image[r_left_corner_top:r_left_corner_bottom,r_left_corner_left:r_left_corner_right]

        r_right_corner_top   = int(max(dlib_points[19][1],0))
        r_right_corner_left  = int(max(dlib_points[17][0]-5,0))
        r_right_corner_right = int(min(dlib_points[19][0],image.shape[1]))
        r_right_corner_bottom = int(min(dlib_points[41][1]+5,image.shape[0]))

        right_eye_right_corner = image[r_right_corner_top:r_right_corner_bottom, r_right_corner_left:r_right_corner_right]
        
        right_eye = self.resize_to_output_shape(right_eye)
        right_eye_left_corner = self.resize_to_output_shape(right_eye_left_corner)
        right_eye_right_corner = self.resize_to_output_shape(right_eye_right_corner)

        return right_eye,right_eye_left_corner,right_eye_right_corner

    def get_left_eye_attributes(self,image,dlib_points):
        left_eye_top = int(max(dlib_points[24][1]-5,0))
        left_eye_left = int(max(dlib_points[22][0]-5,0))
        left_eye_right  = int(min(dlib_points[26][0]+5,image.shape[1]))
        left_eye_bottom = int(min(dlib_points[46][1]+5,image.shape[0]))

        left_eye = image[left_eye_top:left_eye_bottom,left_eye_left:left_eye_right]

        l_left_corner_top   = int(max(dlib_points[24][1],0))
        l_left_corner_left  = int(max(dlib_points[24][0],0))
        l_left_corner_right = int(min(dlib_points[26][0],image.shape[1]))
        l_left_corner_bottom = int(min(dlib_points[46][1],image.shape[0]))

        left_eye_left_corner = image[l_left_corner_top:l_left_corner_bottom,l_left_corner_left:l_left_corner_right]

        l_right_corner_top   = int(max(dlib_points[24][1],0))
        l_right_corner_left  = int(max(dlib_points[27][0],0))
        l_right_corner_right = int(min(dlib_points[24][0],image.shape[1]))
        l_right_corner_bottom = int(min(dlib_points[46][1],image.shape[0]))
        
        left_eye_right_corner = image[l_right_corner_top:l_right_corner_bottom, l_right_corner_left:l_right_corner_right]
        
        left_eye = self.resize_to_output_shape(left_eye)
        left_eye_left_corner = self.resize_to_output_shape(left_eye_left_corner)
        left_eye_right_corner = self.resize_to_output_shape(left_eye_right_corner)
        
        return left_eye,left_eye_left_corner,left_eye_right_corner 
    def resize_to_output_shape(self,image):
        img = cv2.resize(image,(self.image_shape[0],self.image_shape[1]))
        return img
    def get_nose_attributes(self,image,dlib_points):
        nose_top = int(max(dlib_points[27][1]-5,0))
        nose_left = int(max(dlib_points[31][0]-5,0))
        nose_right  = int(min(dlib_points[35][0]+5,image.shape[1]))
        nose_bottom = int(min(dlib_points[33][1]+5,image.shape[0]))

        nose = image[nose_top:nose_bottom,nose_left:nose_right]

        nose_left_corner_top   = int(max(dlib_points[27][1],0))
        nose_left_corner_left  = int(max(dlib_points[27][0],0))
        nose_left_corner_right = int(min(dlib_points[42][0],image.shape[1]))
        nose_left_corner_bottom = int(min(dlib_points[33][1],image.shape[0]))

        nose_left_corner = image[nose_left_corner_top:nose_left_corner_bottom,nose_left_corner_left:nose_left_corner_right]

        nose_right_corner_top   = int(max(dlib_points[27][1],0))
        nose_right_corner_left  = int(max(dlib_points[39][0],0))
        nose_right_corner_right = int(min(dlib_points[27][0],image.shape[1]))
        nose_right_corner_bottom = int(min(dlib_points[33][1],image.shape[0]))
        
        nose_right_corner = image[nose_right_corner_top:nose_right_corner_bottom, nose_right_corner_left:nose_right_corner_right]
        
     

        nose = self.resize_to_output_shape(nose)
        nose_left_corner = self.resize_to_output_shape(nose_left_corner)

        nose_right_corner = self.resize_to_output_shape(nose_right_corner)


        return nose,nose_left_corner,nose_right_corner
    def get_mouth_attributes(self,image,dlib_points):
        mouth_top = int(max(dlib_points[50][1]-5,0))
        mouth_left = int(max(dlib_points[48][0]-5,0))
        mouth_right  = int(min(dlib_points[54][0]+5,image.shape[1]))
        mouth_bottom = int(min(dlib_points[57][1]+5,image.shape[0]))

        mouth = image[mouth_top:mouth_bottom,mouth_left:mouth_right]

        mouth_left_corner_top   = int(max(dlib_points[52][1],0))
        mouth_left_corner_left  = int(max(dlib_points[51][0],0))
        mouth_left_corner_right = int(min(dlib_points[54][0]+5,image.shape[1]))
        mouth_left_corner_bottom = int(min(dlib_points[57][1],image.shape[0]))

        mouth_left_corner = image[mouth_left_corner_top:mouth_left_corner_bottom,mouth_left_corner_left:mouth_left_corner_right]

        mouth_right_corner_top   = int(max(dlib_points[52][1],0))
        mouth_right_corner_left  = int(max(dlib_points[48][0],0))
        mouth_right_corner_right = int(min(dlib_points[57][0],image.shape[1]))
        mouth_right_corner_bottom = int(min(dlib_points[57][1],image.shape[0]))
        
        mouth_right_corner = image[mouth_right_corner_top:mouth_right_corner_bottom, mouth_right_corner_left:mouth_right_corner_right]
        
        mouth_top_corner_top   = int(max(dlib_points[50][1],0))
        mouth_top_corner_left  = int(max(dlib_points[48][0],0))
        mouth_top_corner_right = int(min(dlib_points[54][0],image.shape[1]))
        mouth_top_corner_bottom = int(min(dlib_points[48][1],image.shape[0]))
        
        mouth_top_corner = image[mouth_top_corner_top:mouth_top_corner_bottom, mouth_top_corner_left:mouth_top_corner_right]
        
        mouth_bottom_corner_top   = int(max(dlib_points[48][1],0))
        mouth_bottom_corner_left  = int(max(dlib_points[48][0],0))
        mouth_bottom_corner_right = int(min(dlib_points[54][0],image.shape[1]))
        mouth_bottom_corner_bottom = int(min(dlib_points[57][1],image.shape[0]))
        
        mouth_bottom_corner = image[mouth_bottom_corner_top:mouth_bottom_corner_bottom, mouth_bottom_corner_left:mouth_bottom_corner_right]
        
        cv2.imshow("Mouth",mouth)
        cv2.imshow("Mouth left corner",mouth_left_corner)
        cv2.imshow("Mouth right corner",mouth_right_corner)
        cv2.imshow("Mouth top corner",mouth_top_corner)
        cv2.imshow("Mouth bottom corner",mouth_bottom_corner)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        mouth = self.resize_to_output_shape(mouth)
        mouth_left_corner = self.resize_to_output_shape(mouth_left_corner)
        mouth_right_corner = self.resize_to_output_shape(mouth_right_corner)
        mouth_top_corner = self.resize_to_output_shape(mouth_top_corner)
        mouth_bottom_corner = self.resize_to_output_shape(mouth_bottom_corner)

        

        return mouth,mouth_left_corner,mouth_right_corner,mouth_top_corner,mouth_bottom_corner
   
    def get_face_attributes(self,image,face,predictor):
        face_image =image[ int(max(0,face.top())):int(min(image.shape[0],face.bottom())),
                     int(max(0,face.left())):int(min(image.shape[1],face.right()))   
                    ]
        face_image = cv2.resize(face_image,(self.image_shape[0],self.image_shape[1]))

        dlib_points = self.get_dlib_points(image,face,predictor)
        cv2.circle(image,(int(dlib_points[46][0]),int(dlib_points[46][1])),1,(255,0,0))
        cv2.circle(image,(int(dlib_points[41][0]),int(dlib_points[41][1])),1,(0,255,0))
        right_eye,right_eye_left_corner,right_eye_right_corner  = self.get_right_eye_attributes(image,dlib_points)
        left_eye,left_eye_left_corner,left_eye_right_corner  = self.get_left_eye_attributes(image,dlib_points)
        nose,nose_right_corner,nose_left_corner = self.get_nose_attributes(image,dlib_points)
        mouth,mouth_left_corner,mouth_right_corner,mouth_top_corner,mouth_bottom_corner = self.get_mouth_attributes(image,dlib_points)
        output = {"face_image":face_image,"right_eye":right_eye,"left_eye":left_eye,
                    "mouth":mouth,"nose":nose,"left_eye_right_corner":left_eye_right_corner,
                    "left_eye_left_corner":left_eye_left_corner,"right_eye_right_corner":right_eye_right_corner,
                    "right_eye_left_corner":right_eye_left_corner,"nose_right_corner":nose_right_corner,
                    "nose_left_corner":nose_left_corner,"mouth_left_corner":mouth_left_corner,
                    "mouth_right_corner":mouth_right_corner,"mouth_top_corner":mouth_top_corner,
                    "mouth_bottom_corner":mouth_bottom_corner
                    }
        return output
    def load_image_sequence(self,path,detector,predictor):
        imgs_files = os.listdir(path)
        output_faces = np.zeros((len(imgs_files),self.image_shape[0],self.image_shape[1],self.image_shape[2]))
        output_right_eyes = np.zeros((len(imgs_files),self.image_shape[0],self.image_shape[1],self.image_shape[2]))
        output_left_eyes = np.zeros((len(imgs_files),self.image_shape[0],self.image_shape[1],self.image_shape[2]))
        output_mouths = np.zeros((len(imgs_files),self.image_shape[0],self.image_shape[1],self.image_shape[2]))
        output_noses = np.zeros((len(imgs_files),self.image_shape[0],self.image_shape[1],self.image_shape[2]))
        output_left_eye_right_corners = np.zeros((len(imgs_files),self.image_shape[0],self.image_shape[1],self.image_shape[2]))
        output_left_eye_left_corners = np.zeros((len(imgs_files),self.image_shape[0],self.image_shape[1],self.image_shape[2]))
        output_right_eye_right_corners = np.zeros((len(imgs_files),self.image_shape[0],self.image_shape[1],self.image_shape[2]))
        output_right_eye_left_corners = np.zeros((len(imgs_files),self.image_shape[0],self.image_shape[1],self.image_shape[2]))
        output_nose_right_corners = np.zeros((len(imgs_files),self.image_shape[0],self.image_shape[1],self.image_shape[2]))
        output_nose_left_corners = np.zeros((len(imgs_files),self.image_shape[0],self.image_shape[1],self.image_shape[2]))
        output_mouth_left_corners = np.zeros((len(imgs_files),self.image_shape[0],self.image_shape[1],self.image_shape[2]))
        output_mouth_right_corners = np.zeros((len(imgs_files),self.image_shape[0],self.image_shape[1],self.image_shape[2]))
        output_mouth_top_corners = np.zeros((len(imgs_files),self.image_shape[0],self.image_shape[1],self.image_shape[2]))
        output_mouth_bottom_corners = np.zeros((len(imgs_files),self.image_shape[0],self.image_shape[1],self.image_shape[2]))
        
    


        for i in range(len(imgs_files)):
            img = cv2.imread(os.path.join(path,imgs_files[i]))
            if not (img is None):
                faces = detector(img)
                if len(faces)>0:
                    face = faces[0]
                    # face_image =img[ max(0,face.top()):min(img.shape[0],face.bottom()),
                    #                  max(0,face.left()):min(img.shape[1],face.right())   
                    #                 ]
                    # [right_eye,left_eye,mouth,nose,left_eye_corners,right_eye_corners,nose_corners,mouth_corners]
                    cv2.imshow("Image",img)
                    attrs = self.get_face_attributes(img, face,predictor)
                    output_faces[i] = attrs["face_image"]
                    output_right_eyes[i] = attrs["right_eye"]
                    output_left_eyes[i] = attrs["left_eye"]
                    output_noses[i] = attrs["nose"]
                    output_mouths[i] = attrs["mouth"]
                    output_left_eye_right_corners[i] = attrs["left_eye_right_corner"]
                    output_left_eye_left_corners[i] = attrs["left_eye_left_corner"]
                    output_right_eye_right_corners[i] = attrs["right_eye_right_corner"]
                    output_right_eye_left_corners[i] = attrs["right_eye_left_corner"]
                    output_nose_right_corners[i] = attrs["nose_right_corner"]
                    output_nose_left_corners[i] = attrs["nose_left_corner"]
                    output_mouth_right_corners[i] = attrs["mouth_right_corner"]
                    output_mouth_left_corners[i] = attrs["mouth_left_corner"]
                    output_mouth_top_corners[i] = attrs["mouth_top_corner"]
                    output_mouth_bottom_corners[i] = attrs["mouth_bottom_corner"]
                    

                else:
                    print("No faces found for ",os.path.join(path,imgs_files[i]))
            else:
                print ("Unable to read image from ",os.path.join(path,imgs_files[i]))
        return output_faces,output_left_eyes,output_right_eyes,output_noses,output_mouths,\
            output_left_eye_right_corners,output_left_eye_right_corners,output_right_eye_left_corners,\
            output_right_eye_right_corners,output_nose_left_corners,output_nose_right_corners,\
            output_mouth_left_corners,output_mouth_right_corners,output_mouth_top_corners,output_mouth_bottom_corners
                
    def load_dataset(self):
        pass