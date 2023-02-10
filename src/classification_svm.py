import os
import cv2
import numpy as np
import skimage.morphology as morph
import skimage.filters as filters
import skimage.exposure as exposure
from skimage.feature import greycomatrix, greycoprops

glcm_feature = ['contrast', 'dissimilarity', 'homogeneity', 'ASM', 'energy', 'correlation']
angle = [0]

def preprocessing(img, filename):
    image = cv2.imread(img)
    img = cv2.resize(image, (500, 500)) # Resize image
    green = img[:, :, 1] # Get green channel
    incomplement = cv2.bitwise_not(green) # negative image
    clache = cv2.createCLAHE(clipLimit=5) # Contrast Limited Adaptive Histogram Equalization
    cl1 = clache.apply(incomplement) # Apply CLAHE
    mopopen = morph.opening(cl1, morph.disk(8, dtype=np.uint8)) # Morphological opening with disk kernel of radius 8
    godisk = cl1 - mopopen #remove optical disk
    medfilt = filters.median(godisk) # Median filter
    background = morph.opening(medfilt, morph.disk(15, dtype=np.uint8)) #get background
    rmBack = medfilt - background #remove background
    v_min, v_max = np.percentile(rmBack, (0.2, 99.8)) #get 0.2% and 99.8% percentile
    better_contrast = exposure.rescale_intensity(rmBack, in_range=(v_min, v_max)) #rescale intensity
    ret, thresh = cv2.threshold(better_contrast, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU) #Otsu thresholding
    rmSmall = morph.remove_small_objects(thresh, min_size=50, connectivity=1, in_place=False) #remove small objects
    filename = 'static/uploads/processed-' + filename
    cv2.imwrite(os.path.join(os.getcwd(), filename), rmSmall) #save preprocessed image

    return rmSmall

def glcm(img):
    glcm_feature_prop = []
    distance = [5]
    angles = [0]
    level = 256
    symetric = True
    normed = True

    glcm = greycomatrix(img, distance, angles, level, symmetric=symetric, normed=normed)
    glcm_props = [property for name in glcm_feature for property in greycoprops(glcm, name)[0]]
    for prop in glcm_props:
        glcm_feature_prop.append(prop)
    return glcm_feature_prop