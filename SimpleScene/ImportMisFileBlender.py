import bpy

currentDir = '/'.join(bpy.data.filepath.split('/')[0:-1])

bpy.ops.file.find_missing_files(find_all=True, directory = currentDir)

bpy.ops.wm.save_mainfile()