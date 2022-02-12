import cv2 as cv
import numpy as np
import os
from skimage.feature.texture import greycomatrix
from skimage.feature.texture import greycoprops
from skimage.measure import shannon_entropy
import pyfeats
import pandas as pd
import math


def read_images(folder = "dataset/train", classes = ["normal", "fatty"]):
    image_names = {}
    images = []
    # Get all image names in folders
    for cls in classes:
        image_names[cls] = os.listdir(f'{folder}/{cls}')

    # read all images to list
    for cls in classes:
        for name in image_names[cls]:
            img = cv.imread(f'{folder}/{cls}/{name}', cv.IMREAD_GRAYSCALE)
            images.append((img,cls))
    return images


def extract_roi(img, start , size = (32,32)):
    roi = img[start[0]:start[0]+size[0],start[1]:start[1]+size[1]]
    mask = np.zeros(img.shape)
    mask[start[0]:start[0]+size[0],start[1]:start[1]+size[1]] = 1
    return roi, mask


def feature_extraction(img, roi_pos=[
    (160, 230),
    (118, 224),
    (241, 151),
    (120, 420),
    (170, 300),
    (400, 200),
    (300, 120),
    (240, 240),
    (360, 160)
]):
    roi_mask_arr = []
    for pos in roi_pos:
        roi_mask_arr.append(extract_roi(img, pos))

    # 0 45 90 135 degrees
    angles = [0, np.pi / 4, np.pi / 2, 3 * np.pi / 4]

    da_dict = {
        0: "d1_0",
        1: "d1_45",
        2: "d1_90",
        3: "d1_135",

        4: "d2_0",
        5: "d2_45",
        6: "d2_90",
        7: "d2_135",

        8: "d3_0",
        9: "d3_45",
        10: "d3_90",
        11: "d3_135",

    }

    feat_arr = []
    for roi, mask in roi_mask_arr:
        if roi.shape != (32, 32):
            continue
        features = {}

        glcm_mtx = greycomatrix(roi, distances=[1, 2, 3], angles=angles, levels=256)
        con = greycoprops(glcm_mtx, 'contrast').flatten()
        hom = greycoprops(glcm_mtx, 'homogeneity').flatten()
        en = greycoprops(glcm_mtx, 'energy').flatten()
        corr = greycoprops(glcm_mtx, 'correlation').flatten()

        for j in range(len(da_dict)):
            features[f'contrast_{da_dict[j]}'] = con[j]
            features[f'homogeneity_{da_dict[j]}'] = hom[j]
            features[f'energy_{da_dict[j]}'] = en[j]
            features[f'correlation_{da_dict[j]}'] = corr[j]

        features[f'entropy'] = shannon_entropy(roi)
        # features[f'var'] = np.var(roi)
        # features[f'mean'] = np.mean(roi)
        # GLRLM Features
        #         feat, labels = pyfeats.glrlm_features(img, mask, 256)
        #         for i in range(len(labels)):
        #             features[labels[i]] = feat[i]
        #         glrlm = {l : f for l,f in zip(labels,feat)}
        #         features[f'longRunEmphasis'] = glrlm['GLRLM_LongRunEmphasis']
        #         features[f'runPercentage'] = glrlm['GLRLM_RunPercentage']

        feat_arr.append(features)

    return feat_arr


def chunks(arr, number_of_chunks):
    # n elements in chunk for splitting into n chunks
    chunk_arr = []
    n = math.ceil(len(arr)/number_of_chunks)
    for i in range(0, len(arr), n):
        chunk_arr.append(arr[i:i + n])
    return chunk_arr


def build_dataframe(images):
    # dataframe consists of features of 1 ROI per image
    # column name roiNum_feature
    data = pd.DataFrame()

    for img, cls, mask in images:
        feat_arr = feature_extraction(img, mask)
        for row in feat_arr:
            row['target'] = cls
            data = data.append(row,ignore_index=True)
    return data
