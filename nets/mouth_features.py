from keras.layers import Dropout
from keras.layers import Conv2D,MaxPool2D,Dense,Flatten,Input,Concatenate
from keras.layers import LSTM,TimeDistributed,Add,Bidirectional
from keras.models import Model,Sequential
import keras
import numpy as np

class MouthFeatureOnlyNet(object):
    def __init__(self,dataset,input_shape,max_sequence_length):
        self.dataset = dataset
        self.input_shape = input_shape
        self.max_sequence_length = max_sequence_length
        self.model = self.build()
        self.model.summary()
    def build(self):
        mouth_image_model = Sequential()
        mouth_image_model.add(TimeDistributed(Conv2D(32,(3,3),padding='same',activation="relu",strides=(1, 1)),\
                    name="mouth_image_layer1",input_shape=(self.max_sequence_length, self.input_shape[0], self.input_shape[1], self.input_shape[2])))
        
        mouth_image_model.add(TimeDistributed(MaxPool2D(pool_size=(2, 2))))
        mouth_image_model.add(TimeDistributed(Conv2D(64,kernel_size=(3,3),strides=(1, 1),padding='same',\
                activation="relu",name="mouth_image_layer2")))
        mouth_image_model.add(TimeDistributed(MaxPool2D(pool_size=(2, 2))))
        mouth_image_model.add(TimeDistributed(Conv2D(128,kernel_size=(3,3),strides=(1, 1),padding='same',\
            activation="relu",name="mouth_image_layer3")))
        mouth_image_model.add(TimeDistributed(MaxPool2D(pool_size=(2, 2))))
        mouth_image_model.add(TimeDistributed(Flatten()))
        
        mouth_image_model.add(Bidirectional(LSTM(32,return_sequences=True)))
        mouth_image_model.add(Bidirectional(LSTM(128,return_sequences=False)))
        mouth_image_model.add(Dense(1024,activation="relu"))
        mouth_image_model.add(Dense(2,activation="softmax"))
        return mouth_image_model
        


        # key_points_model = Sequential()
        # key_points_model.add(TimeDistributed(Conv2D(32,(1,3),padding='valid',activation="relu",strides=(1, 1)),\
        #             name="key_points_layer1",input_shape=(self.max_sequence_length, 1,20,2)))
        
        # key_points_model.add(TimeDistributed(Conv2D(64,kernel_size=(1,3),strides=(1, 1),padding='valid',\
        #         activation="relu",name="key_points_layer2")))
        # key_points_model.add(TimeDistributed(Conv2D(128,kernel_size=(1,3),strides=(1, 1),padding='valid',\
        #     activation="relu",name="key_points_layer3")))
        # key_points_model.add(TimeDistributed(Flatten()))

        # distances_model = Sequential()
        # distances_model.add(TimeDistributed(Conv2D(32,(1,3),padding='valid',activation="relu",strides=(1, 1)),\
        #             name="distances_layer1",input_shape=(self.max_sequence_length, 1,20,1)))
        
        # distances_model.add(TimeDistributed(Conv2D(64,kernel_size=(1,3),strides=(1, 1),padding='valid',\
        #         activation="relu",name="distances_layer2")))
        # distances_model.add(TimeDistributed(Conv2D(128,kernel_size=(1,3),strides=(1, 1),padding='valid',\
        #     activation="relu",name="distances_layer3")))
        # distances_model.add(TimeDistributed(Flatten()))

        # angles_model = Sequential()
        # angles_model.add(TimeDistributed(Conv2D(32,(1,3),padding='valid',activation="relu",strides=(1, 1)),\
        #             name="angles_layer1",input_shape=(self.max_sequence_length, 1,20,1)))
        
        # angles_model.add(TimeDistributed(Conv2D(64,kernel_size=(1,3),strides=(1, 1),padding='valid',\
        #         activation="relu",name="angles_layer2")))
        # angles_model.add(TimeDistributed(Conv2D(128,kernel_size=(1,3),strides=(1, 1),padding='valid',\
        #     activation="relu",name="angles_layer3")))
        # angles_model.add(TimeDistributed(Flatten()))

        # merged_layer = Concatenate()([mouth_image_model.output,key_points_model.output,distances_model.output,angles_model.output])

        # dense1 = TimeDistributed(Dense(128,activation="relu"))(merged_layer)   
        # # dropout1 = TimeDistributed(Dropout(0.2))(dense1)
        # dense2 = TimeDistributed(Dense(256,activation="relu"))(dense1)
        # # dropout2 = TimeDistributed(Dropout(0.2))(dense2)
        # lstm1 = Bidirectional(LSTM(128,activation='sigmoid',return_sequences=False,stateful=False))(dense2)
        # # lstm2 = Bidirectional(LSTM(256,activation='sigmoid',return_sequences=True,stateful=False))(lstm1)
        # # lstm3 = Bidirectional(LSTM(1024,activation='sigmoid', return_sequences=False,stateful=False))(lstm2)
        
        # dense3 = Dense(256,activation="relu")(lstm1)
        # output = Dense(2,activation="softmax")(dense3)

        # # model = Model(inputs=[face_layer,left_eye_layer_input,right_eye_layer_input,nose_layer_input,mouth_layer_input],outputs=output)
        # model = Model(inputs=[mouth_image_model.input,key_points_model.input,distances_model.input,angles_model.input],\
        #                      outputs = output
        #                    )
        # return model


    def train(self):
        # X_test= [self.dataset.mouth_image_test_sequence, self.dataset.key_points_test_sequence, \
        #     self.dataset.distances_test_sequence, self.dataset.angles_test_sequence]
        X_test= self.dataset.mouth_image_test_sequence
        y_test = self.dataset.Y_test.astype(np.uint8)
        y_test = np.eye(2)[y_test]

        self.model.compile(loss=keras.losses.binary_crossentropy,optimizer=keras.optimizers.Adam(1e-4),metrics=["accuracy"])
        self.model.fit_generator(self.dataset.generator(1),steps_per_epoch=1000,epochs=50,verbose=1,validation_data=(X_test,y_test))
        self.model.save_weights("models/model-mouth-100.h5")
        model_json = self.model.to_json()
        with open("models/model-mouth-100.json","w+") as json_file:
            json_file.write(model_json)
        score = self.model.evaluate(X_test,y_test)
        with open("logs/log-mouth.txt","a+") as log_file:
            log_file.write("Score: "+str(score))
            log_file.write("\n")
