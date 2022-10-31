import bpy
import os
import sys

# print(sys.argv)
# print(sys.argv[-2])
# print(sys.argv[-1])


fbxFilePath = sys.argv[-2]
blendFilePath = sys.argv[-1]

# Import FBX
bpy.ops.import_scene.fbx(filepath=fbxFilePath)  # find_all=True,
bpy.context.object.scale = (0.01, 0.01, 0.01)

# Export blend file

if os.path.exists(blendFilePath):
    os.remove(blendFilePath)

bpy.ops.wm.save_mainfile(filepath=blendFilePath)
