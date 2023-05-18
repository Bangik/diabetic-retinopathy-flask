import numpy as np
from PIL import Image
import cv2
from keras.models import Sequential
from keras import layers
from keras.optimizers import Adam
from keras.applications import DenseNet121

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
      optimizer=Adam(learning_rate=0.00005),
      metrics=['accuracy']
  )
  
  return model

model = build_model()
model.load_weights('static/model_ml/model-cnn-17-5-23.h5')

def crop_image_from_gray(img,tol=7):
  if img.ndim ==2:
    mask = img>tol
    return img[np.ix_(mask.any(1),mask.any(0))]
  elif img.ndim==3:
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mask = gray_img>tol        
    check_shape = img[:,:,0][np.ix_(mask.any(1),mask.any(0))].shape[0]
    if (check_shape == 0):
      return img
    else:
      img1=img[:,:,0][np.ix_(mask.any(1),mask.any(0))]
      img2=img[:,:,1][np.ix_(mask.any(1),mask.any(0))]
      img3=img[:,:,2][np.ix_(mask.any(1),mask.any(0))]
      img = np.stack([img1,img2,img3],axis=-1)
      return img

def circle_crop_v2(img):
  img = crop_image_from_gray(img)

  height, width, depth = img.shape
  largest_side = np.max((height, width))
  img = cv2.resize(img, (largest_side, largest_side))

  height, width, depth = img.shape

  x = int(width / 2)
  y = int(height / 2)
  r = np.amin((x, y))

  circle_img = np.zeros((height, width), np.uint8)
  cv2.circle(circle_img, (x, y), int(r), 1, thickness=-1)
  img = cv2.bitwise_and(img, img, mask=circle_img)
  img = crop_image_from_gray(img)

  return img

def preprocess_image(image_path, desired_size=224):
  img = cv2.imread(image_path)
  circle_crop = circle_crop_v2(img)
  bgr2rgb = cv2.cvtColor(circle_crop, cv2.COLOR_BGR2RGB)
  img_pil = Image.fromarray(bgr2rgb)
  im = img_pil.resize((desired_size, )*2, resample=Image.LANCZOS)

  return im

def prediction(image_path):
  tes_image = np.empty((1, 224, 224, 3), dtype=np.uint8)
  tes_image[0, :, :, :] = preprocess_image(image_path)
  predicted = model.predict(tes_image)
  probability = predicted.max()
  predicted = predicted > 0.5
  predicted = predicted.astype(int).sum(axis=1) - 1
  return predicted[0], probability