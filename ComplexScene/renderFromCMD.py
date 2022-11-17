import os
import subprocess
import sys

# fbx model file paths
target_folder = r'../data/FullBodyModels/'
# associated python script file paths
renderScript = r'\captureWithGaze.py'
importfbxScript = r'\importFbx.py'
sceneSetupScript = r'\sceneSetupComplex.py'
compositorScript = r'\compositorSetup.py'
importMissingFileScript = r'\importMisFileBlender.py'
# blender scene file path
blenderScenePath = r'../data/Environments/Barbershop/barbershop_interior_gpu.blend'
sceneName = '_barbershop'

blenderPath = '/mnt/fastssd/Shubhajit_Stuff/blender-2.81-linux-glibc217-x86_64/blender '

# ----------- Blender FBX setup ---------------- #

# for root, dirs, files in os.walk(target_folder):
#     for dir in dirs:
#         for file in os.listdir(str(root) + '/' + str(dir)):
#             if file.endswith(".fbx"):
#                 fbxFilePath = os.path.join(root, dir, file)
#                 blenderFile = os.path.basename(fbxFilePath).split('.')[0] + sceneName + '.blend'
#                 blenderFilePath = os.path.join(root, dir, blenderFile)
#                 if os.path.exists(blenderFilePath):
#                     os.remove(blenderFilePath)
#                 pwd = 'galwaydnn'
#                 cmd = blenderPath + blenderScenePath + " --background -P " \
#                       + importfbxScript + " " + fbxFilePath + " " + blenderFilePath
#                 print(cmd)
# p = subprocess.call('echo {} | sudo -S {}'.format(pwd, cmd), shell=True)

# ----------- Blender Import Missing File ---------------- #

# for root, dirs, files in os.walk(target_folder):
#     for dir in dirs:
#         for file in os.listdir(str(root) + '/' + str(dir)):
#             if file.endswith(".blend"):  # & file.startswith('female'):
#                 blenderFilePath = os.path.join(root, dir, file)
#                 pwd = 'galwaydnn'
#                 cmd = blenderPath + " --background " \
#                       + blenderFilePath + " -P " + importMissingFileScript
#                 # print(cmd)
#                 p = subprocess.call('echo {} | sudo -S {}'.format(pwd, cmd), shell=True)

# ----------- Blender Model setup ---------------- #

# for root, dirs, files in os.walk(target_folder):
#     for dir in dirs:
#         for file in os.listdir(str(root) + '/' + str(dir)):
#             if file.endswith(".blend"):  # & file.startswith('female'):
#                     blenderFilePath = os.path.join(root, dir, file)
#                     pwd = 'galwaydnn'
#                     cmd = blenderPath + " --background " \
#                           + blenderFilePath + " -P " + sceneSetupScript
#                     # print(cmd)
#                     p = subprocess.call('echo {} | sudo -S {}'.format(pwd, cmd), shell=True)

# ----------- Blender Compositor setup ---------------- #

# for root, dirs, files in os.walk(target_folder):
#     for dir in dirs:
#         for file in os.listdir(str(root) + '/' + str(dir)):
#             if file.endswith(".blend"):  # & file.startswith('female'):
#                 blenderFilePath = os.path.join(root, dir, file)
#                 pwd = 'galwaydnn'
#                 cmd = blenderPath + " --background " \
#                       + blenderFilePath + " -P " + compositorScript
#                 # print(cmd)
#                 p = subprocess.call('echo {} | sudo -S {}'.format(pwd, cmd), shell=True)

# -------- Blender Rendering -------#
for root, dirs, files in os.walk(target_folder):
    for dir in dirs:
        for file in os.listdir(str(root) + '/' + str(dir)):
            if file.endswith(".blend"):  # & file.startswith('female'):
                blenderFilePath = os.path.join(root, dir, file)
                pwd = 'galwaydnn'
                cmd = blenderPath + " --background " \
                        + blenderFilePath + " -P " + renderScript
                # print(cmd)
                p = subprocess.call('echo {} | sudo -S {}'.format(pwd, cmd), shell=True)
