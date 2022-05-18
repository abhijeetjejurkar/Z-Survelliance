import cv2
from tensorflow.keras.models import load_model
from numpy import expand_dims
from numpy import load
from sklearn.preprocessing import Normalizer
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
from datetime import datetime, timedelta
import mysql.connector
import numpy as np # linear algebra


# get the face embedding for one face
def get_embedding(model, face_pixels):
    # scale pixel values
    face_pixels = face_pixels.astype('float32')
    # standardize pixel values across channels (global)
    mean, std = face_pixels.mean(), face_pixels.std()
    face_pixels = (face_pixels - mean) / std
    # transform face into one sample
    samples = expand_dims(face_pixels, axis=0)
    # make prediction to get embedding
    yhat = model.predict(samples)
    return yhat[0]

face_model = cv2.CascadeClassifier('Haar/haarcascade_frontalface_default.xml')

#loading haarcascade_frontalface_default.xml
modelm = load_model('models/masknet1.h5')
modelf = load_model('models/facenet_keras.h5')
img_height = 224
img_width = 224
required_size=(160, 160)

mask_label = {0:'MASK',1:'NO MASK'}
dist_label = {0:(0,255,0),1:(255,0,0)}

# load faces
data = load('models/Dataset.npz')
testX_faces = data['arr_2']

# load face embeddings
data = load('models/Dataset-embeddings.npz')
trainX, trainy, testX, testy = data['arr_0'], data['arr_1'], data['arr_2'], data['arr_3']

# normalize input vectors
in_encoder = Normalizer(norm='l2')
trainX = in_encoder.transform(trainX)
testX = in_encoder.transform(testX)

# label encode targets
out_encoder = LabelEncoder()
out_encoder.fit(trainy)
trainy = out_encoder.transform(trainy)
testy = out_encoder.transform(testy)

# fit model
model = SVC(kernel='linear', probability=True)
model.fit(trainX, trainy)

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  #database="mydatabase"
)

mycursor = mydb.cursor()
mycursor.execute("CREATE DATABASE IF NOT EXISTS z_intelligence")
mycursor.execute("USE z_intelligence")
mycursor.execute("CREATE TABLE IF NOT EXISTS Entry_Exit_Logs(EntryId INT NOT NULL AUTO_INCREMENT, EmployeeID VARCHAR(20) NOT NULL, EntryDate DATE NOT NULL, EntryTime TIME NOT NULL, ExitDate DATE NOT NULL, ExitTime TIME NOT NULL, PRIMARY KEY (EntryId))")

class VideoCamera(object):
    def __init__(self):
        self.dicta = {}
        self.dictl = {}
        self.checktime=20
        self.sendtime=5
        self.updatetime = datetime.now();
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        delete = []
        for id in self.dictl:
            check = datetime.now()-self.dictl.get(id)
            dayl = self.dictl.get(id).day
            daya = self.dicta.get(id).day
            monthl = self.dictl.get(id).month
            montha = self.dicta.get(id).month
            yearl = self.dictl.get(id).year
            yeara = self.dicta.get(id).year
            hourl = self.dictl.get(id).hour
            minutel = self.dictl.get(id).minute
            secondl = self.dictl.get(id).second
            houra = self.dicta.get(id).hour
            minutea = self.dicta.get(id).minute
            seconda = self.dicta.get(id).second

            EntryDate = str(yeara) +"-"+ str(montha) +"-"+ str(daya)
            ExitDate = str(yearl) +"-"+ str(monthl) +"-"+ str(dayl)

            EntryTime = str(houra) +":"+ str(minutea) +":"+ str(seconda)
            ExitTime = str(hourl) +":"+ str(minutel) +":"+ str(secondl)

            query = "INSERT INTO entry_exit_logs(EmployeeID,EntryDate,EntryTime,ExitDate,ExitTime) VALUES('"+ str(id) +"','"+ EntryDate +"','"+ EntryTime +"','"+ ExitDate +"','"+ ExitTime +"');"
            mycursor.execute(query)
            print("Added Entry of Person with last exit time(stored in dictl) and entry time(stored in dicta)")
            delete.append(id)
        for id in delete:
            self.dictl.pop(id)
            self.dicta.pop(id)
        mycursor.execute("COMMIT;")
        print("COMMITTED")
        self.video.release()

    def get_frame(self):
        
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        rval, im = self.video.read()
        img=cv2.flip(im,1,1) #Flip to act as a mirror
        faces = face_model.detectMultiScale(img,scaleFactor=1.1, minNeighbors=4) #returns a list of (x,y,w,h) tuples
        new_img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR) #colored output image

        for i in range(len(faces)):
            (x,y,w,h) = faces[i]
            
            crop = new_img[y:y+h,x:x+w]
            crop1 = cv2.resize(crop,(img_height,img_width))
            crop1 = np.reshape(crop1,[1,img_height,img_width,3])/255.0
            mask_result = modelm.predict(crop1)
            (mask, withoutMask) = mask_result[0]            
            crop2 = cv2.resize(crop,(160,160))
            random_face_pixels =crop2
            random_face_emb = get_embedding(modelf, random_face_pixels)
            samples = expand_dims(random_face_emb, axis=0)
            yhat_class = model.predict(samples)
            yhat_prob = model.predict_proba(samples)
            class_index = yhat_class[0]
            class_probability = yhat_prob[0,class_index] * 100
            predict_names = out_encoder.inverse_transform(yhat_class)
            if(mask_label[mask_result.argmax()]=="NO MASK" and (max(mask, withoutMask) * 100)>85):
                if((int(class_probability))>=99):
                    flabel = 'Predicted: %s (%.2f)' % (predict_names[0], class_probability)
                    if(predict_names[0] not in self.dicta):
                        print("Created")
                        self.dicta[predict_names[0]]=datetime.now();
                        self.dictl[predict_names[0]]=datetime.now();
                    elif(predict_names[0] in self.dicta):
                            print("Updated Left")
                            self.dictl[predict_names[0]]=datetime.now();
                else:
                    flabel = 'Predicted: UNKNOWN (%.3f)' % (class_probability)
                
            else:
                flabel = "{}: {:.2f}%".format(mask_label[mask_result.argmax()], max(mask, withoutMask) * 100)
            
            cv2.putText(new_img,flabel,(x, y-10),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)
            cv2.rectangle(new_img,(x,y),(x+w,y+h),(255,0,0),1)
        new_img = cv2.cvtColor(new_img, cv2.COLOR_RGB2BGR) #colored output image
        delete = []
        u_diff=datetime.now()-self.updatetime
        if(u_diff.seconds>self.sendtime):
            for id in self.dictl:
                check = datetime.now()-self.dictl.get(id)
                dayl = self.dictl.get(id).day
                daya = self.dicta.get(id).day
                monthl = self.dictl.get(id).month
                montha = self.dicta.get(id).month
                yearl = self.dictl.get(id).year
                yeara = self.dicta.get(id).year
                hourl = self.dictl.get(id).hour
                minutel = self.dictl.get(id).minute
                secondl = self.dictl.get(id).second
                houra = self.dicta.get(id).hour
                minutea = self.dicta.get(id).minute
                seconda = self.dicta.get(id).second
                
                EntryDate = str(yeara) +"-"+ str(montha) +"-"+ str(daya)
                ExitDate = str(yearl) +"-"+ str(monthl) +"-"+ str(dayl)
                
                EntryTime = str(houra) +":"+ str(minutea) +":"+ str(seconda)
                ExitTime = str(hourl) +":"+ str(minutel) +":"+ str(secondl)
                
                if(check.seconds>self.checktime):
                    query = "INSERT INTO entry_exit_logs(EmployeeID,EntryDate,EntryTime,ExitDate,ExitTime) VALUES('"+ str(id) +"','"+ EntryDate +"','"+ EntryTime +"','"+ ExitDate +"','"+ ExitTime +"');"
                    mycursor.execute(query)
                    print("Added Entry of Person with last exit time(stored in self.dictl) and entry time(stored in self.dicta)")
                    mycursor.execute("COMMIT;")
                    print("COMMITTED")
                    delete.append(id)
            for id in delete:
                self.dictl.pop(id)
                self.dicta.pop(id)
            self.updatetime = datetime.now();
            print(self.updatetime)

        ########################################################
        # img=cv2.flip(im,1,1) #Flip to act as a mirror
        # img = cv2.cvtColor(img, cv2.IMREAD_GRAYSCALE)
        # faces = face_model.detectMultiScale(img,scaleFactor=1.1, minNeighbors=4) #returns a list of (x,y,w,h) tuples
        # new_img=img
        
        # for i in range(len(faces)):
        #     (x,y,w,h) = faces[i]
        #     # cv2.putText(new_img,str(dists[i]),(x, y-10),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),2)
        #     cv2.rectangle(new_img,(x,y),(x+w,y+h),(0,255,0),1)
        ##########################################################

        # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        # for (x, y, w, h) in faces:
        #     gray_face = cv2.resize((gray[y:y + h, x:x + w]), (110, 110))
        #     eyes = eye_cascade.detectMultiScale(gray_face)
        #     for (ex, ey, ew, eh) in eyes:

        #         draw_box(gray, x, y, w, h)

        ###########################################################


        ret, jpeg = cv2.imencode('.jpg', new_img)

        return jpeg.tobytes()