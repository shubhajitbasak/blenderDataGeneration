# file name - importMisFileBlender.py
import bpy

# point the directory containing all the associated files
currentDir = '/'.join(bpy.data.filepath.split('/')[0:-1])

bpy.ops.file.find_missing_files(directory=currentDir)
bpy.ops.wm.save_mainfile()
