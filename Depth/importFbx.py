import bpy 
import os 
import sys

#fbxFilePath = 'C:\\Users\\sbasak\\Desktop\\test\\Angry\\male0020.fbx'
#blendFilePath = 'C:\\Users\\sbasak\\Desktop\\test\\Angry\\male0020.blend'

# print(sys.argv)
# print(sys.argv[-2])
# print(sys.argv[-1])


fbxFilePath = sys.argv[-2]
blendFilePath = sys.argv[-1]


#bpy.ops.object.select_all()
#bpy.ops.object.delete() 



# Import FBX
bpy.ops.import_scene.fbx( filepath = fbxFilePath )
bpy.context.object.scale = (0.01, 0.01, 0.01)

# Export blend file

if os.path.exists(blendFilePath):
  os.remove(blendFilePath)

bpy.ops.wm.save_mainfile( filepath = blendFilePath )