import bpy

# prefs = bpy.context.preferences
# cprefs = prefs.addons['cycles'].preferences
#
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
#     device.use = True
#
# bpy.ops.wm.save_userpref()

# bpy.context.scene.cycles.device = 'GPU'
# bpy.ops.render.render(True)

# prefs = bpy.context.preferences.addons['cycles'].preferences
# prefs.compute_device_type = 'CUDA'
# prefs.compute_device = 'CUDA_1'
#
# bpy.ops.wm.save_userpref()

print(bpy.context.preferences.addons['cycles'].preferences.devices[0])

prefs = bpy.context.preferences
# print(prefs.addons['cycles'].preferences.get_devices())
print(prefs.addons['cycles'].preferences.devices[0].use)
print(prefs.addons['cycles'].preferences.devices[1].use)
print(prefs.addons['cycles'].preferences.devices[2].use)