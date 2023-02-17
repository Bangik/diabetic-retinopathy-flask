import numpy as np
from PIL import Image
import math
from tensorflow.keras.models import Sequential
from tensorflow.keras import layers
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.applications import DenseNet121

densenet = DenseNet121(
  weights='static/model_keras/DenseNet-BC-121-32-no-top.h5',
  include_top=False,
  input_shape=(224,224,3)
)

def build_model():
  model = Sequential()
  model.add(densenet)
  model.add(layers.GlobalAveragePooling2D())
  model.add(layers.Dropout(0.5))
  model.add(layers.Dense(5, activation='sigmoid'))
  
  model.compile(
      loss='binary_crossentropy',
      optimizer=Adam(lr=0.00005),
      metrics=['accuracy']
  )
  
  return model

model = build_model()
model.load_weights('static/model_ml/model.h5')

def get_pad_width(im, new_shape, is_rgb=True):
  pad_diff = new_shape - im.shape[0], new_shape - im.shape[1]
  t, b = math.floor(pad_diff[0]/2), math.ceil(pad_diff[0]/2)
  l, r = math.floor(pad_diff[1]/2), math.ceil(pad_diff[1]/2)
  if is_rgb:
      pad_width = ((t,b), (l,r), (0, 0))
  else:
      pad_width = ((t,b), (l,r))
  return pad_width

def preprocess_image(image_path, desired_size=224):
  im = Image.open(image_path)
  im = im.resize((desired_size, )*2, resample=Image.LANCZOS)
  
  return im

def prediction(image_path):
  tes_image = np.empty((1, 224, 224, 3), dtype=np.uint8)
  tes_image[0, :, :, :] = preprocess_image(image_path)
  predicted = model.predict(tes_image)
  probability = predicted.max()
  predicted = predicted > 0.5
  predicted = predicted.astype(int).sum(axis=1) - 1
  return predicted[0], probability