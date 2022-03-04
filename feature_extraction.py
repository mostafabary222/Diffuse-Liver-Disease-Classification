# import cv2 as cv
import SimpleITK as sitk
import numpy as np
import os
from skimage.feature.texture import greycomatrix
from skimage.feature.texture import greycoprops
from skimage.measure import shannon_entropy
from radiomics import glrlm, glcm, firstorder
# import pyfeats
import pandas as pd
import math


def read_images(folder = "dataset/train",
                classes = [
                            "normal",
                            "fatty",
                            "cirrhosis"
                        ]):
    image_names = {}
    images = []
    # Get all image names in folders
    for cls in classes:
        image_names[cls] = os.listdir(f'{folder}/{cls}')

    # read all images to list
    for cls in classes:
        for name in image_names[cls]:
            mask = []
            with open(f'dataset/masks/{name[0:-4]}.txt', 'r') as file:
                data = file.read()
                data = data.strip().split('\n')
                for line in data:
                    x, y = line.split(',')
                    mask.append((int(y),int(x)))
            img = sitk.ReadImage(f'{folder}/{cls}/{name}', sitk.sitkUInt8)
            images.append((img,cls,mask))
    return images


def extract_roi(img, start , size = (32,32)):
    img = sitk.GetArrayFromImage(img)
    roi = img[start[0]:start[0]+size[0],start[1]:start[1]+size[1]]
    mask = np.zeros(img.shape)
    mask[start[0]:start[0]+size[0],start[1]:start[1]+size[1]] = 1
    return roi, mask


def feature_extraction(img, roi_pos):
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
        features = {}

        glcm_mtx = greycomatrix(roi, distances = [1,2,3], angles = angles, levels = 256)
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

        # features[f'mean'] = np.mean(roi)
        # features[f'variance'] = np.var(roi)

        # pyradiomics
        mask = sitk.GetImageFromArray(mask)
        # First Order features
        firstOrderFeatures = firstorder.RadiomicsFirstOrder(img, mask)
        # firstOrderFeatures.enableFeatureByName('Mean', True)
        firstOrderFeatures.enableAllFeatures()
        results = firstOrderFeatures.execute()
        for col in results.keys():
            features[col] = results[col].item()

        # GLCM features
        glcmFeatures = glcm.RadiomicsGLCM(img, mask)
        glcmFeatures.enableAllFeatures()
        results = glcmFeatures.execute()
        for col in results.keys():
            features[col] = results[col].item()
        #
        # GLRLM features
        glrlmFeatures = glrlm.RadiomicsGLRLM(img, mask)
        glrlmFeatures.enableAllFeatures()
        results = glrlmFeatures.execute()
        features['LongRunEmphasis'] = results['LongRunEmphasis'].item()
        features['RunPercentage'] = results['RunPercentage'].item()
        for col in results.keys():
            features[col] = results[col].item()

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

    for name, img, cls, mask in images:
        feat_arr = feature_extraction(img, mask)
        count = 1
        for row in feat_arr:
            row['name'] = name
            count += 1
            row['target'] = cls
            data = data.append(row,ignore_index=True)
    return data
