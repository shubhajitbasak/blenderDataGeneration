import os
import subprocess
import sys
from datetime import datetime

# '/mnt/fastssd/Shubhajit_Stuff/blender-2.81-linux-glibc217-x86_64/blender '
blenderPath = r'"C:\Program Files\Blender Foundation\Blender 2.81\blender.exe" '

# r'/mnt/fastssd/Shubhajit_Stuff/dataCreation/male/'
target_folder = r'D:\project1\dataCreation\BlenderData\female'

renderScript = r'\captureWithGaze.py'
importfbxScript = r'\importFBX.py'
simpleScnScript = r'\sceneSetup.py'
compositorScript = r'\compositorSetup.py'
importMissingFileScript = r'\importMissingFile.py'
adjustScript = r'\HPBlenderAdjustment.py'

renderReal = False
# simpleScene.blend    |     headPoseScene.blend
if renderReal:
    # r'/mnt/fastssd/Shubhajit_Stuff/Environments/SimpleScene/headPoseScene.blend'
    blenderScenePath = r'D:\project1\dataCreation\Scripts\BlenderHeadPoseCreation\Environments\SimpleScene\headPoseScene.blend'
else:
    # r'/mnt/fastssd/Shubhajit_Stuff/Environments/SimpleScene/simpleScene.blend'
    blenderScenePath = r'D:\project1\dataCreation\Scripts\BlenderHeadPoseCreation\Environments\SimpleScene\simpleScene.blend'

sceneName = '_simple'

# ---- Male List ---- #  2
# idList = [1, 4,  7,  9, 10, 11, 13, 15, 18, 20, 24, 25, 28, 31, 35,
# 37, 38, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 54, 56, 58, 60,
# 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74,
# 75, 76, 77, 78, 79, 80, 81, 82, 83, 84]


# ---- Female List ---- #
idList = [
    1, 3, 7, 8, 13, 15, 17, 20, 24, 25, 28, 29, 33, 34, 38,
    41, 45, 48, 49, 53, 56, 59, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72,
    73, 74, 75, 76, 77, 78, 79, 80, 84, 86, 89, 92, 94, 100,
    ]

flag = False
renderFlag = False

adjustFlag = True

# ----------- Blender FBX setup ---------------- #

if flag:
    for root, dirs, files in os.walk(target_folder):
        for dir in dirs:
            for file in os.listdir(str(root) + '/' + str(dir)):
                if file.endswith(".fbx") & ('Simple' in os.path.join(root, dir, file)):  # & file.startswith('male')
                    # print(os.path.join(root, dir, file).split('/')[-4])
                    id = int(float(os.path.join(root, dir, file).split('\\')[-4]))  # replace / \\ ubuntu
                    if id in idList:
                        # if (id > 0) & (id < 101):
                        fbxFilePath = os.path.join(root, dir, file)
                        if 'Neutral' in fbxFilePath:
                            # if True:
                            blenderFile = sceneName.join(fbxFilePath.split('\\')[4:6]) + '.blend'  # replace / \\ ubuntu
                            blenderFilePath = os.path.join(root, dir, blenderFile)
                            cmd = blenderPath + blenderScenePath \
                                  + " --background -P " \
                                  + importfbxScript + " " + fbxFilePath + " " + blenderFilePath
                            # print(cmd)
                            # p = subprocess.call('echo {} | sudo -S {}'.format(pwd, cmd), shell=True)
                            p = subprocess.call(cmd, shell=True)

# ----------- Blender Import Missing File ---------------- #

if flag:
    for root, dirs, files in os.walk(target_folder):
        for dir in dirs:
            for file in os.listdir(str(root) + '/' + str(dir)):
                if file.endswith(".blend") & file.startswith('female_simple'):
                    # print(os.path.join(root, dir, file))
                    if int(file.split('.')[0][-3:]) in idList:
                        # if (int(file.split('.')[0][-3:]) > 0) & (int(file.split('.')[0][-3:]) < 101):
                        blenderFilePath = os.path.join(root, dir, file)
                        if 'Neutral' in blenderFilePath:
                            pwd = 'galwaydnn'
                            # print(blenderFilePath)
                            cmd = blenderPath + " --background " \
                                  + blenderFilePath + " -P " + importMissingFileScript
                            # print(cmd)
                            # p = subprocess.call('echo {} | sudo -S {}'.format(pwd, cmd), shell=True)
                            p = subprocess.call(cmd, shell=True)

# ----------- Blender Model setup ---------------- #

if flag:
    for root, dirs, files in os.walk(target_folder):
        for dir in dirs:
            for file in os.listdir(str(root) + '/' + str(dir)):
                if file.endswith(".blend") & file.startswith('female_simple'):
                    # print(os.path.join(root, dir, file))
                    if int(file.split('.')[0][-3:]) in idList:
                        # if (int(file.split('.')[0][-3:]) > 0) & (int(file.split('.')[0][-3:]) < 101):
                        blenderFilePath = os.path.join(root, dir, file)
                        if 'Neutral' in blenderFilePath:
                            pwd = 'galwaydnn'
                            cmd = blenderPath + " --background " \
                                  + blenderFilePath + " -P " + simpleScnScript
                            # print(cmd)
                            # p = subprocess.call('echo {} | sudo -S {}'.format(pwd, cmd), shell=True)
                            p = subprocess.call(cmd, shell=True)

# ----------- Blender Compositor setup ---------------- #

if flag:
    if not renderReal:
        print('compositor called')
        for root, dirs, files in os.walk(target_folder):
            for dir in dirs:
                for file in os.listdir(str(root) + '/' + str(dir)):
                    if file.endswith(".blend") & file.startswith('female_simple'):
                        # print(os.path.join(root, dir, file))
                        if int(file.split('.')[0][-3:]) in idList:
                            # if (int(file.split('.')[0][-3:]) > 0) & (int(file.split('.')[0][-3:]) < 101):
                            blenderFilePath = os.path.join(root, dir, file)
                            if 'Neutral' in blenderFilePath:
                                pwd = 'galwaydnn'
                                # print(blenderFilePath)
                                cmd = blenderPath + " --background " \
                                      + blenderFilePath + " -P " + compositorScript  # importMissingFileScript
                                print(cmd)
                                # p = subprocess.call('echo {} | sudo -S {}'.format(pwd, cmd), shell=True)
                                p = subprocess.call(cmd, shell=True)

# -------- Blender Rendering -------#

if renderFlag:

    biwiTrainLabels = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 1, 2, 3, 4]

    # for l in range(0,len(biwiTrainLabels)-1): #
    #     print(biwiTrainLabels[l], biwiTrainLabels[l+1])

    c = 0
    for root, dirs, files in os.walk(target_folder):
        for dir in dirs:
            for file in os.listdir(str(root) + '/' + str(dir)):
                if file.endswith(".blend") & file.startswith('male_simple'):
                    if int(file.split('.')[0][-3:]) in idList:
                        # if (int(file.split('.')[0][-3:]) > 0) & (int(file.split('.')[0][-3:]) < 21):
                        blenderFilePath = os.path.join(root, dir, file)
                        if 'Neutral' in blenderFilePath:
                            # if True:
                            pwd = 'galwaydnn'
                            cmd = blenderPath + " --background " \
                                  + blenderFilePath + " -P " + renderScript + " -- " + str(biwiTrainLabels[0]) \
                                  + " " + str(renderReal)

                            print(cmd)
                            # p = subprocess.call('echo {} | sudo -S {}'.format(pwd, cmd), shell=True)
                            p = subprocess.call(cmd, shell=True)

                            # print(biwiTrainLabels[c], biwiTrainLabels[c + 1])

                            # print(c, c+1)
                            c += 1

# -------- Blender Head Pose Adjustment -------#

if adjustFlag:

    for root, dirs, files in os.walk(target_folder):
        for dir in dirs:
            for file in os.listdir(str(root) + '/' + str(dir)):
                if file.endswith(".blend") & file.startswith('female_simple'):
                    if int(file.split('.')[0][-3:]) in idList:
                        # if (int(file.split('.')[0][-3:]) > 0) & (int(file.split('.')[0][-3:]) < 21):
                        blenderFilePath = os.path.join(root, dir, file)
                        if 'Neutral' in blenderFilePath:
                            # if True:
                            pwd = 'galwaydnn'
                            cmd = blenderPath + " --background " \
                                  + blenderFilePath + " -P " + adjustScript

                            # print(cmd)
                            # p = subprocess.call('echo {} | sudo -S {}'.format(pwd, cmd), shell=True)
                            p = subprocess.call(cmd, shell=True)

