import os
import numpy as np

# ---- Male List ---- #  2,
idList = [1, 4, 7, 9, 10, 11, 13, 15, 18, 20, 24, 25, 28, 31, 35,
          37, 38, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 54, 56, 58, 60,
          61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74,
          75, 76, 77, 78, 79, 80, 81, 82, 83, 84]

# ---- Female List ---- #
# idList = [1,  3,  7,  8, 13, 15, 17, 20, 24, 25, 28, 29, 33, 34, 38,
# 41, 45, 48, 49, 53, 56, 59, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72,
# 73, 74, 75, 76, 77, 78, 79, 80, 84, 86, 89, 92, 94, 100]

target_folder = r'D:\project1\dataCreation\BlenderData\male'

if True:

    biwiOrig = []

    with open(r'biwiNoTrack.txt', 'r') as f1:
        data = f1.readlines()
        for i, hp in enumerate(data):
            t1, t2, t3 = tuple(map(float, hp.strip().split()))
            biwiOrig.append([t1, t2, t3])
    biwiOrigNP = np.asarray(biwiOrig)

    for root, dirs, files in os.walk(target_folder):
        for dir in dirs:
            for file in os.listdir(str(root) + '/' + str(dir)):
                if file.endswith(".blend") & file.startswith('male_simple'):
                    if int(file.split('.')[0][-3:]) in idList:
                        # if (int(file.split('.')[0][-3:]) > 0) & (int(file.split('.')[0][-3:]) < 21):
                        blenderFilePath = os.path.join(root, dir, file)
                        if 'Neutral' in blenderFilePath:
                            # print(blenderFilePath)
                            hpDataPath = blenderFilePath.replace('.blend', '.txt')
                            print(hpDataPath)
                            biwiGen = []
                            with open(hpDataPath, 'r') as f1:
                                data = f1.readlines()
                                for i, hp in enumerate(data):
                                    t1, t2, t3 = tuple(map(float, hp.strip().split(',')))
                                    biwiGen.append([t1, t2, t3])
                            biwiGenNP = np.asarray(biwiGen)

                            pose_matrix = np.mean(np.abs(biwiGen - biwiOrigNP), axis=0)
                            MAE = np.mean(pose_matrix)
                            yaw = pose_matrix[0]
                            pitch = pose_matrix[1]
                            roll = pose_matrix[2]
                            print(file.split('.')[0][-3:], '   :   MAE = %3.3f, [yaw,pitch,roll] = [%3.3f, %3.3f, %3.3f]\n' % (MAE, yaw, pitch, roll))

