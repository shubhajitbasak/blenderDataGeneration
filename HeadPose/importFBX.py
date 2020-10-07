import bpy
import os
import sys

fbxFilePath = sys.argv[-2]
blendFilePath = sys.argv[-1]


if os.path.exists(blendFilePath):
    os.remove(blendFilePath)

# bpy.ops.object.select_all(action= 'DESELECT')
# bpy.ops.object.select_all()
# bpy.ops.object.delete()

# Import FBX
bpy.ops.import_scene.fbx( filepath = fbxFilePath )
bpy.context.object.scale = (0.01, 0.01, 0.01)

# Export blend file
if os.path.exists(blendFilePath):
    os.remove(blendFilePath)

# Save blend file
bpy.ops.wm.save_mainfile(filepath=blendFilePath)