# File name - importFbx.py
import bpy
import os
import sys

# argument to pass the fbx file path
fbxFilePath = sys.argv[-2]
# argument to pass the blend file path (e.g. - barbershop.blend)
blendFilePath = sys.argv[-1]

# Import FBX
bpy.ops.import_scene.fbx(filepath=fbxFilePath)
bpy.context.object.scale = (0.01, 0.01, 0.01)

# Export blend file
if os.path.exists(blendFilePath):
    os.remove(blendFilePath)
# save the blend file
bpy.ops.wm.save_mainfile(filepath=blendFilePath)
