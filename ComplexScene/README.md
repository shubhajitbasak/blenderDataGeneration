
Before generating the data delete any '*.blend' and '*.blend1' files.

Update RenderFromCMD.py -
 * target_folder - folder with the fbx models
 * blenderScenePath - complex scene blend file path
 * sceneName - sceneName (e.g. - classroom, barbershop)
 * blenderPath - blender executable path

Update compositorSetup.py -
 * basePath - base data generation path
 * filepath - update file path with the complex scene (e.g. - classroom / barbershop)
 * bpy.context.scene.cycles.aa_samples  - rendering samples in blender cycle rendering engine (e.g. - 64/128) 
 * bpy.context.scene.render.resolution_x / resolution_y - output image resolution