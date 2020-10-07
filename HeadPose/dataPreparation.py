import os
import shutil
import numpy as np
from distutils import util
import glob
import cv2
import re
from os import listdir
from os.path import isfile, join
import face_recognition


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    """
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    """
    return [atoi(c) for c in re.split(r'(\d+)', text)]


def getRGBPoseDatawithMTCNN(rgbFilePath, ad, fileName):
    img = cv2.imread(rgbFilePath)
    img_h = img.shape[0]
    img_w = img.shape[1]

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    detected = detector.detect_faces(imgRGB)

    # print(fileName, detected)

    if len(detected) > 0:
        print(fileName, str(detected))  # detected[0]['box']
        x1, y1, w, h = detected[0]['box']
        if float(detected[0]['confidence']) > 0.78:
            if (w > 105) or (h > 105):
                y1 = y1 - 20
                size = max(w, h)
                looseSize = int((size + (ad * size)) / 2)
                xc = int(x1 + w / 2)
                yc = int(y1 + h / 2)

                xw1 = max(xc - looseSize, 0)
                yw1 = max(yc - looseSize, 0)
                xw2 = min(xc + looseSize, img_w)
                yw2 = min(yc + looseSize, img_h)

                if xw1 == 0:
                    xw2 = looseSize * 2

                if xw2 == img_w:
                    xw1 = img_w - (looseSize * 2)

                if yw1 == 0:
                    yw2 = looseSize * 2

                if yw2 == img_h:
                    yw1 = img_h - (looseSize * 2)

                img = img[yw1:yw2, xw1:xw2, :]

                return img, (xw1, xw2, yw1, yw2)
            else:
                return False, (None, None, None, None)
        else:
            return False, (None, None, None, None)
    else:
        print(fileName, '[]')
        return False, (None, None, None, None)


# ---- Male List ---- #  2
maleidList = [1, 4, 7, 9, 10, 11, 13, 15, 18, 20, 24, 25, 28, 31, 35,
              37, 38, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 54, 56, 58, 60,
              61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74,
              75, 76, 77, 78, 79, 80, 81, 82, 83, 84]

# ---- Female List ---- #
femaleidList = [1, 3, 7, 8, 13, 15, 17, 20, 24, 25, 28, 29, 33, 34, 38,
                41, 45, 48, 49, 53, 56, 59, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72,
                73, 74, 75, 76, 77, 78, 79, 80, 84, 86, 89, 92, 94, 100]

# ''' Create the backup of the neck bone data files if exist '''
if False:

    basePath = r'D:\project1\dataCreation\BlenderData'
    genders = ['male', 'female']
    for gender in genders:
        genderPath = os.path.join(basePath, gender)
        if gender == 'male':
            for idx in maleidList:
                blenderPath = os.path.join(genderPath, str(idx).zfill(4), 'Simple', 'Neutral')
                fileName = gender + '_' + 'simple' + str(idx).zfill(4) + '_neckboneBkp.txt'
                filePath = os.path.join(blenderPath, fileName)
                if os.path.exists(filePath):
                    os.rename(filePath, filePath.replace('Bkp', ''))
        else:
            for idx in femaleidList:
                blenderPath = os.path.join(genderPath, str(idx).zfill(4), 'Simple', 'Neutral')
                fileName = gender + '_' + 'simple' + str(idx).zfill(4) + '_neckboneBkp.txt'
                filePath = os.path.join(blenderPath, fileName)
                if os.path.exists(filePath):
                    os.rename(filePath, filePath.replace('Bkp', ''))

# Append the Flag (camera distance variation) on the neckBone data files
if False:

    with open(r'D:\project1\dataCreation\BlenderData\flag.txt', 'r') as f2:
        d = f2.readlines()

    flag = np.asarray(list(map(util.strtobool, map(str.strip, d))))
    flag = flag.reshape(flag.shape[0], 1)

    basePath = r'D:\project1\dataCreation\BlenderData'
    genders = ['male', 'female']
    for gender in genders:
        genderPath = os.path.join(basePath, gender)
        if gender == 'female':
            for idx in femaleidList:
                blenderPath = os.path.join(genderPath, str(idx).zfill(4), 'Simple', 'Neutral')
                fileName = gender + '_' + 'simple' + str(idx).zfill(4) + '_neckbone.txt'
                filePath = os.path.join(blenderPath, fileName)
                neckBoneData = []
                if os.path.exists(filePath):
                    with open(filePath, 'r') as f1:
                        data = f1.readlines()
                        for i, hp in enumerate(data):
                            neckBoneData.append(list(map(float, hp.strip().split(','))))

                    neckBoneDataNP = np.asarray(neckBoneData)
                    appendedArray = np.append(flag, neckBoneDataNP, axis=1)

                    newDataPath = os.path.join(r'D:\project1\dataCreation\BlenderData\neckBoneData', fileName)

                    np.savetxt(newDataPath, appendedArray, fmt='%.5f')

# Create short version of neckbone data file with 3000 data point each
if False:

    newDataPath = r'D:\project1\dataCreation\BlenderData\neckBoneDataShort'
    DataPath = r'D:\project1\dataCreation\BlenderData\neckBoneData'
    n1 = -3000
    n2 = 0
    for file in os.listdir(DataPath):
        if n2 < 15000:
            n1 = n1 + 3000
            n2 = n1 + 3000
            if n2 == 15000:
                t1 = 10219
                t2 = 13219
            else:
                t1 = n1
                t2 = n2
        else:
            n1 = 0
            n2 = 3000
            t1 = n1
            t2 = n2

        print(file, t1, t2)

        neckBoneData = []
        with open(os.path.join(DataPath, file), 'r') as f1:
            data = f1.readlines()
            for i, hp in enumerate(data):
                neckBoneData.append(list(map(float, hp.strip().split(' '))))

        neckBoneDataNP = np.asarray(neckBoneData)
        neckBoneDataNP = neckBoneDataNP[t1:t2]
        np.savetxt(os.path.join(newDataPath, file), neckBoneDataNP, fmt='%.5f')

# Apply FR to a headpose image file
# Check MTCNN and face recognition library
if False:

    from mtcnn.mtcnn import MTCNN

    detector = MTCNN()

    dataPath = r'D:\project1\dataCreation\Others\FRTesting\HeadRot'
    dataPathNew = r'D:\project1\dataCreation\Others\FRTesting\HeadRotFR'

    for gender in ['male', 'female']:  # 'female'
        for id in next(os.walk(os.path.join(dataPath, gender)))[1]:
            if True:  # id == '0040':
                idPath = os.path.join(dataPath, gender, id, 'HeadPose', 'Textured', 'Neutral')
                idPathNew = os.path.join(dataPathNew, gender, id, 'HeadPose', 'Textured', 'Neutral')

                if not os.path.exists(idPathNew):
                    os.makedirs(idPathNew, exist_ok=True)

                onlyfiles_txt_temp = [f for f in listdir(idPath) if
                                      isfile(join(idPath, f)) and join(idPath, f).endswith('.txt')]
                onlyfiles_jpg_temp = [f for f in listdir(idPath) if
                                      isfile(join(idPath, f)) and join(idPath, f).endswith('.jpg')]

                onlyfiles_txt_temp.sort(key=natural_keys)
                onlyfiles_jpg_temp.sort(key=natural_keys)

                if len(onlyfiles_txt_temp) == len(onlyfiles_jpg_temp):

                    # onlyfiles_txt_temp = onlyfiles_txt_temp[410:415]
                    # onlyfiles_jpg_temp = onlyfiles_jpg_temp[410:415]

                    (xw1p, xw2p, yw1p, yw2p) = (120, 520, 80, 480)
                    yP, pP, rP = 0, 0, 0

                    for f1, f2 in zip(onlyfiles_txt_temp, onlyfiles_jpg_temp):

                        rgbPath = os.path.join(idPath, f2)
                        if len(f2) > 11:
                            _f2 = f2[:-8] + '.jpg'
                        else:
                            _f2 = f2
                        rgbPathNew = os.path.join(idPathNew, _f2)

                        txtPath = os.path.join(idPath, f1)
                        if 'data' in f1:
                            _f1 = f1.replace('data_', 'pose')
                        else:
                            _f1 = f1
                        txtPathNew = os.path.join(idPathNew, _f1)

                        with open(txtPath, 'r') as f1:
                            data = f1.readlines()
                        y, p, r = tuple(map(float, data[0].strip().split(',')))

                        deltaY, deltaP, deltaR = y - yP, p - pP, r - rP
                        print(f'{deltaY:.2f},{deltaP:.2f},{deltaR:.2f}')

                        img, (xw1, xw2, yw1, yw2) = getRGBPoseDatawithMTCNN(rgbPath, 0.5, f2)

                        if img is not False:
                            if img.shape[0] != img.shape[1]:
                                # print('Shape Issue : ', rgb)
                                img = cv2.imread(rgbPath)
                                img = img[yw1p:yw2p, xw1p:xw2p, :]
                                img = cv2.resize(img, (400, 400), interpolation=cv2.INTER_AREA)
                                cv2.imwrite(rgbPathNew, img)


                            else:
                                img = cv2.resize(img, (400, 400), interpolation=cv2.INTER_AREA)
                                cv2.imwrite(rgbPathNew, img)
                                (xw1p, xw2p, yw1p, yw2p) = (xw1, xw2, yw1, yw2)
                        else:
                            # print('Face not detected : ', rgb)
                            img = cv2.imread(rgbPath)
                            if abs(deltaY) > 9:
                                img = img[80:480, 120:520, :]
                                (xw1p, xw2p, yw1p, yw2p) = (120, 520, 80, 480)
                            else:
                                img = img[yw1p:yw2p, xw1p:xw2p, :]
                            img = cv2.resize(img, (400, 400), interpolation=cv2.INTER_AREA)
                            cv2.imwrite(rgbPathNew, img)

                        shutil.copy2(txtPath, txtPathNew)

                        yP, pP, rP = y, p, r

                else:
                    print('issue in : ', idPath)

# Manually modify the bad data where the face is not visible..
if False:
    import matplotlib.pyplot as plt

    with open(r'C:\Users\sbasak\Desktop\modify.txt', 'r') as f:
        test = f.readlines()

    for l in test:
        print(l.strip())
        name = l.strip().split('\\')[-1]
        name = name[:-8] + '.jpg'
        img = cv2.imread(l.strip())
        # img = img[100:480, 260:640, :]
        img = img[80:480, 120:520, :]
        img = cv2.resize(img, (400, 400), interpolation=cv2.INTER_AREA)
        # plt.imshow(img)
        # plt.show()
        cv2.imwrite(os.path.join(r'C:\Users\sbasak\Desktop\test', name), img)

# Create the text file with RGB and pose txt
if True:
    dataPath = r'D:\project1\dataCreation\Others\FRTesting\HeadRotFR'
    with open(os.path.join(dataPath, 'data.txt'), 'a') as f1:
        for gender in ['male', 'female']:  # 'female'
            for id in next(os.walk(os.path.join(dataPath, gender)))[1]:
                if True:  # id == '0040':
                    idPath = os.path.join(dataPath, gender, id, 'HeadPose', 'Textured', 'Neutral')
                    printPath = os.path.join(gender, id, 'HeadPose', 'Textured', 'Neutral')

                    onlyfiles_txt_temp = [f for f in listdir(idPath) if
                                          isfile(join(idPath, f)) and join(idPath, f).endswith('.txt')]
                    onlyfiles_jpg_temp = [f for f in listdir(idPath) if
                                          isfile(join(idPath, f)) and join(idPath, f).endswith('.jpg')]

                    onlyfiles_txt_temp.sort(key=natural_keys)
                    onlyfiles_jpg_temp.sort(key=natural_keys)

                    if len(onlyfiles_txt_temp) == len(onlyfiles_jpg_temp):

                        for img, pose in zip(onlyfiles_jpg_temp, onlyfiles_txt_temp):
                            # print(img, pose)
                            if int(img.split('.')[0][-4:]) == int(pose.split('.')[0][-4:]):
                                # print(os.path.join(idPath, img), os.path.join(idPath, pose))
                                f1.write(os.path.join(printPath, img) + ',' + os.path.join(printPath, pose) + '\n')

                    else:
                        print('issue in : ', idPath)
