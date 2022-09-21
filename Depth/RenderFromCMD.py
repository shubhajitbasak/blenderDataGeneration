import os
import subprocess
import sys
import importlib
import config


renderScript = r'\captureWithGaze.py'  #
importfbxScript = r'\importFbx.py'
simpleScnScript = r'\sceneSetup_V1.py'
compositorScript = r'\compositorSetup.py'
importMissingFileScript = r'\ImportMisFileBlender.py'


cfg = config.config
target_folder = cfg.modelRoot
blenderPath = cfg.blenderPath
blendFileSimple = cfg.blendFileSimple

# ----------- Blender FBX setup ---------------- #

for root, dirs, files in os.walk(target_folder):
    for dir in dirs:
        for file in os.listdir(str(root) + '/' + str(dir)):
            if file.endswith(".fbx") & file.startswith('male'): # & ('male/0001' in root)
                if 'male/0001/Simple/Neutral' in os.path.join(root, dir):
                    fbxFilePath = os.path.join(root, dir, file)

                    blenderFile = os.path.basename(fbxFilePath).split('.')[0] + '.blend'
                    blenderFilePath = os.path.join(root, dir, blenderFile)
                    if os.path.exists(blenderFilePath):
                        os.remove(blenderFilePath)
                    # print(fbxFilepath)
                    cmd = blenderPath + blendFileSimple + " --background -P " \
                          + importfbxScript + " " + fbxFilePath + " " + blenderFilePath
                    # print(cmd)
                    p = subprocess.call(cmd, shell=True)

# ----------- Blender Import Missing File ---------------- #

for root, dirs, files in os.walk(target_folder):
    for dir in dirs:
        for file in os.listdir(str(root) + '/' + str(dir)):
            if file.endswith(".blend") & file.startswith('male'):
                # print(os.path.join(root, dir, file))
                # if int(file.split('.')[0][-3:]) == 2:
                if 'male/0001/Simple/Neutral' in os.path.join(root, dir):
                    blenderFilePath = os.path.join(root, dir, file)
                    # print(blenderFilePath)
                    cmd = blenderPath + " --background " \
                          + blenderFilePath + " -P " + importMissingFileScript
                    # print(cmd)
                    p = subprocess.call(cmd, shell=True)


# ----------- Blender Model setup ---------------- #

for root, dirs, files in os.walk(target_folder):
    for dir in dirs:
        for file in os.listdir(str(root) + '/' + str(dir)):
            if file.endswith(".blend") & file.startswith('male'):
                # print(os.path.join(root, dir, file))
                # if int(file.split('.')[0][-3:]) == 51:
                if 'male/0001/Simple/Neutral' in os.path.join(root, dir):
                    blenderFilePath = os.path.join(root, dir, file)
                    # print(blenderFilePath)
                    cmd = blenderPath + " --background " \
                          + blenderFilePath + " -P " + simpleScnScript
                    # print(cmd)
                    p = subprocess.call(cmd, shell=True)

# ----------- Blender Compositor setup ---------------- #

for root, dirs, files in os.walk(target_folder):
    for dir in dirs:
        for file in os.listdir(str(root) + '/' + str(dir)):
            if file.endswith(".blend") & file.startswith('male'):
                if 'male/0001/Simple/Neutral' in os.path.join(root, dir):
                    blenderFilePath = os.path.join(root, dir, file)
                    cmd = blenderPath+ " --background " \
                            + blenderFilePath + " -P " + compositorScript
                    # print(cmd)
                    p = subprocess.call(cmd, shell=True)


# -------- Blender Rendering -------#
for root, dirs, files in os.walk(target_folder):
    for dir in dirs:
        for file in os.listdir(str(root) + '/' + str(dir)):
            if file.endswith(".blend"):
                if 'male/0001/Simple/Neutral' in os.path.join(root, dir):
                    blenderFilePath = os.path.join(root, dir, file)
                    cmd = blenderPath + " --background " \
                            + blenderFilePath + " -P " + renderScript
                    # print(cmd)
                    p = subprocess.call(cmd, shell=True)
