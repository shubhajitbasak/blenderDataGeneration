import os
import subprocess
import sys

target_folder = r'/mnt/sata/code/blenderDataGenerationFinal/data/FullBodyModels'
renderScript = r'\captureWithGaze.py'  #
importfbxScript = r'\importFbx.py'
simpleScnScript = r'\sceneSetup_Complex.py'
compositorScript = r'\compositorSetup.py'
importMissingFileScript = r'\ImportMisFileBlender.py'
blenderScenePath = r'/mnt/sata/code/blenderDataGenerationFinal/data/Environments/Barbershop/barbershop_interior_gpu.blend'
sceneName = '_barbershop'

blenderPath = '/mnt/fastssd/Shubhajit_Stuff/blender-2.81-linux-glibc217-x86_64/blender '

# ----------- Blender FBX setup ---------------- #

for root, dirs, files in os.walk(target_folder):
    for dir in dirs:
        for file in os.listdir(str(root) + '/' + str(dir)):
            if file.endswith(".fbx") & file.startswith('female'):  # & ('male/0001' in root)
                if True:  # 'male/0001/Simple/Neutral' in os.path.join(root, dir):
                    fbxFilePath = os.path.join(root, dir, file)

                    blenderFile = os.path.basename(fbxFilePath).split('.')[0] + sceneName + '.blend'
                    blenderFilePath = os.path.join(root, dir, blenderFile)
                    if os.path.exists(blenderFilePath):
                        os.remove(blenderFilePath)
                    # print(fbxFilepath)
                    pwd = 'galwaydnn'
                    cmd = blenderPath + blenderScenePath + " --background -P " \
                          + importfbxScript + " " + fbxFilePath + " " + blenderFilePath
                    print(cmd)
                    # p = subprocess.call('echo {} | sudo -S {}'.format(pwd, cmd), shell=True)

# ----------- Blender Import Missing File ---------------- #

for root, dirs, files in os.walk(target_folder):
    for dir in dirs:
        for file in os.listdir(str(root) + '/' + str(dir)):
            if file.endswith(".blend") & file.startswith('female'):
                # print(os.path.join(root, dir, file))
                # if int(file.split('.')[0][-3:]) == 2:
                if True:  # 'male/0001/Simple/Neutral' in os.path.join(root, dir):
                    blenderFilePath = os.path.join(root, dir, file)
                    # print(blenderFilePath)
                    pwd = 'galwaydnn'
                    cmd = blenderPath + " --background " \
                          + blenderFilePath + " -P " + importMissingFileScript
                    print(cmd)
                    # p = subprocess.call('echo {} | sudo -S {}'.format(pwd, cmd), shell=True)

# ----------- Blender Model setup ---------------- #

for root, dirs, files in os.walk(target_folder):
    for dir in dirs:
        for file in os.listdir(str(root) + '/' + str(dir)):
            if file.endswith(".blend") & file.startswith('female'):
                # print(os.path.join(root, dir, file))
                # if int(file.split('.')[0][-3:]) == 51:
                if True:  # 'male/0001/Simple/Neutral' in os.path.join(root, dir):
                    blenderFilePath = os.path.join(root, dir, file)
                    # print(blenderFilePath)
                    pwd = 'galwaydnn'
                    cmd = blenderPath + " --background " \
                          + blenderFilePath + " -P " + simpleScnScript
                    # print(cmd)
                    p = subprocess.call('echo {} | sudo -S {}'.format(pwd, cmd), shell=True)

# ----------- Blender Compositor setup ---------------- #

for root, dirs, files in os.walk(target_folder):
    for dir in dirs:
        for file in os.listdir(str(root) + '/' + str(dir)):
            if file.endswith(".blend") & file.startswith('female'):
                if True:  # 'male/0001/Simple/Neutral' in os.path.join(root, dir):
                    blenderFilePath = os.path.join(root, dir, file)
                    pwd = 'galwaydnn'
                    cmd = blenderPath + " --background " \
                          + blenderFilePath + " -P " + compositorScript
                    # print(cmd)
                    p = subprocess.call('echo {} | sudo -S {}'.format(pwd, cmd), shell=True)

# -------- Blender Rendering -------#
for root, dirs, files in os.walk(target_folder):
    for dir in dirs:
        for file in os.listdir(str(root) + '/' + str(dir)):
            if file.endswith(".blend") & file.startswith('female'):
                if True:  # 'male/0001/Simple/Neutral' in os.path.join(root, dir):
                    blenderFilePath = os.path.join(root, dir, file)
                    pwd = 'galwaydnn'
                    cmd = blenderPath + " --background " \
                          + blenderFilePath + " -P " + renderScript
                    # print(cmd)
                    p = subprocess.call('echo {} | sudo -S {}'.format(pwd, cmd), shell=True)
