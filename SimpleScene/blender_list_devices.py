import bpy

def main():
    # # Get the scene
    # scene = bpy.context.scene
    #
    # # Set render resolution
    # scene.render.resolution_x = 1024
    # scene.render.resolution_y = 1024
    # scene.render.resolution_percentage = 100
    #
    # # 16 for CPU, 256 for GPU
    # scene.render.tile_x = 64
    # scene.render.tile_y = 64
    #
    # # [8] Enable CUDA and activate GPU
    # # adapted from https://developer.blender.org/T54099
    #
    # scene = bpy.context.scene
    # scene.cycles.device = 'GPU'

    prefs = bpy.context.preferences
    cprefs = prefs.addons['cycles'].preferences   

    # # Attempt to set GPU device types if available
    # for compute_device_type in ('CUDA', 'OPENCL', 'NONE'):
    #     try:
    #         cprefs.compute_device_type = compute_device_type
    #         break
    #     except TypeError:
    #         pass
    #
    # # Enable all CPU and GPU devices
    # for device in cprefs.devices:
    #     print(device.name)
    #     device.use = True
    #     if device.type == 'GPU':
    #         scene.render.tile_x = 256
    #         scene.render.tile_y = 256
    
    print(prefs.addons['cycles'].preferences.get_devices())
    print(prefs.addons['cycles'].preferences.devices[0].use)
    print(prefs.addons['cycles'].preferences.devices[1].use)
    print(prefs.addons['cycles'].preferences.devices[2].use)
    # prefs.addons['cycles'].preferences.devices[2].use = True
    # bpy.ops.wm.save_userpref()

main()