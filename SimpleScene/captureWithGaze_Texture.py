# with Gaze ------------------

import bpy
import numpy as np
from itertools import repeat
import random
import os

from sympy.geometry import Point

from numpy import cos, sin
from math import radians
import mathutils
from bpy import context

"""
    Render the images, Depth and capture the metadata
    Scenario 1 - Only rotate the head with respect to the head bone
                Stored in "HeadRot" folder
    Scenario 2 - Translate the camera without any head or camera rotation
                Stored in "CameraTran" folder
    Scenario 3 - Apply Head Rotation and Rotate the camera Centering the Head 
                with a Yaw within +-45 Degree and Pitch +-30 Degree
                Stored in "HeadCameraRotTran" folder
"""


def point_at(obj, target, roll=0):
    """
    Rotate obj to look at target

    :arg obj: the object to be rotated. Usually the camera
    :arg target: the location (3-tuple or Vector) to be looked at
    :arg roll: The angle of rotation about the axis from obj to target in radians. 

    Based on: https://blender.stackexchange.com/a/5220/12947 (ideasman42)      
    """
    if not isinstance(target, mathutils.Vector):
        target = mathutils.Vector(target)
    loc = obj.location
    # direction points from the object to the target
    direction = target - loc

    quat = direction.to_track_quat('-Z', 'Y')

    # /usr/share/blender/scripts/addons/add_advanced_objects_menu/arrange_on_curve.py
    quat = quat.to_matrix().to_4x4()
    rollMatrix = mathutils.Matrix.Rotation(roll, 4, 'Z')

    # remember the current location, since assigning to obj.matrix_world changes it
    loc = loc.to_tuple()
    obj.matrix_world = quat @ rollMatrix
    obj.location = loc


def map_tuple_gen(func, tup):
    """
    Applies func to each element of tup and returns a new tuple.

    >>> a = (1, 2, 3, 4)
    >>> func = lambda x: x * x
    >>> map_tuple(func, a)
    (1, 4, 9, 16)

    Based on : https://codereview.stackexchange.com/questions/86753/map-a-function-to-all-elements-of-a-tuple/86756
    """
    return tuple(func(itup) for itup in tup)


def generatePoints(r, center, num):
    """
        Generate the cartesian co-ordinates of random points on a surface of sphere
        Constraints : phi - with (60,120) degree
                      theta - with (-45,45) degree

        :arg r: radius of the sphere
        :arg center: center of the sphere
        :arg num: number of random locations to be generated

        Based on: https://stackoverflow.com/questions/33976911/generate-a-random-sample-of-points-distributed-on-the-surface-of-a-unit-sphere
        """
    pts = []
    for i in range(0, num):
        phi = radians(random.uniform(60, 120))
        theta = radians(random.uniform(-45, 45))
        x, y, z = (center.x - sin(theta) * sin(phi) * r), (center.y - (cos(theta) * sin(phi) * r)), (
                center.z + cos(phi) * r)
        pts.append((x, y, z))
    return pts


def get_random_color():
    ''' generate rgb using a list comprehension '''
    r, g, b = [random.uniform(0.4, 0.8) for i in range(3)]
    return r, g, b, 1


scene = context.scene

scene.cycles.device = 'GPU'

prefs = bpy.context.preferences
cprefs = prefs.addons['cycles'].preferences

# Attempt to set GPU device types if available
for compute_device_type in ('CUDA', 'OPENCL', 'NONE'):
    try:
        cprefs.compute_device_type = compute_device_type
        break
    except TypeError:
        pass

# Enable all CPU and GPU devices
for device in cprefs.devices:
    device.use = True

bpy.context.scene.unit_settings.length_unit = 'METERS'

basePath = '/mnt/fastssd/synData/Data'

baseTexturePath = r"/mnt/fastssd/Shubhajit_stuff/dataCreation/Script/Colored Brodatz"

bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT')

camera = bpy.data.objects['Camera']
scene.camera = camera

empty = bpy.data.objects['empty']

empty_init_loc = tuple(map(round, empty.matrix_world.translation, repeat(4)))
camera_init_loc = tuple(camera.location)
camera_init_rotation = tuple(camera.rotation_euler)

material = bpy.data.materials['MaterialPlane001']
material.use_nodes = True
_nodes = material.node_tree.nodes
_material_links = material.node_tree.links
node_principledBsdf = _nodes['Principled BSDF']
node_mat_texture = _nodes.new('ShaderNodeTexImage')
node_mat_texture.location = -50, 90
_material_links.new(node_mat_texture.outputs['Color'], node_principledBsdf.inputs['Base Color'])

light001 = bpy.data.objects["Light_001"]

# --------- Region Head Rotation ------------- #

dataPath = basePath + '/'.join(bpy.data.filepath.split('/')[-5:-1]) + '/HeadRot'
dataPath = dataPath.replace('Simple','Textured')

bpy.data.scenes["Scene"].node_tree.nodes["File Output"].base_path = dataPath

for i in range(0, 71):
    bpy.context.scene.frame_set(i)

    textureFileName = "D" + str(random.randint(1, 112)) + "_COLORED.tif"
    texture_path = os.path.join(baseTexturePath, textureFileName)
    node_mat_texture.image = bpy.data.images.load(texture_path)

    light001.location.x = random.uniform(-1, 1)

    bpy.context.view_layer.update()

    bpy.data.scenes["Scene"].node_tree.nodes["File Output"].file_slots[0].path = f'rgb'
    bpy.data.scenes["Scene"].render.filepath = dataPath + f'/depth_{i:04d}.png'
    textFilePath = dataPath + f'/data_{i:04d}.txt'

    bpy.ops.render.render(write_still=True)

    matrix_empty = bpy.data.objects['empty'].matrix_world
    matrix_camera = bpy.data.objects['Camera'].matrix_world

    r_empty = tuple(map(round, np.degrees(np.array(matrix_empty.to_euler('XYZ')[0:3])), repeat(4)))
    print('Yaw %.2f Pitch %.2f Roll %.2f' % (r_empty[2], r_empty[0], r_empty[1]))

    r_camera = tuple(map(round, np.degrees(np.array(matrix_camera.to_euler('XYZ')[0:3])), repeat(4)))
    print('Yaw %.2f Pitch %.2f Roll %.2f' % (r_camera[2], r_camera[0], r_camera[1]))

    f = open(textFilePath, "w+")
    f.write('Camera Location: ' + str(tuple(map(round, matrix_camera.translation, repeat(4)))) + '\n')
    f.write('Head Point Location: ' + str(empty_init_loc) + '\n')
    f.write('Camera Rotation: ' + 'Yaw %.2f Pitch %.2f Roll %.2f' % (r_camera[2], r_camera[0], r_camera[1]) + '\n')
    f.write('Head Rotation: ' + 'Yaw %.2f Pitch %.2f Roll %.2f' % (r_empty[2], r_empty[0], r_empty[1]) + '\n')

    f.close()

# --------- Region Camera Translation ------------- #

dataPath = basePath + '/'.join(bpy.data.filepath.split('/')[-5:-1]) + '/CameraTran'
dataPath = dataPath.replace('Simple','Textured')

bpy.data.scenes["Scene"].node_tree.nodes["File Output"].base_path = dataPath

bpy.context.scene.frame_set(0)

bpy.context.view_layer.update()

for i in range(0, 10):
    textureFileName = "D" + str(random.randint(1, 112)) + "_COLORED.tif"
    texture_path = os.path.join(baseTexturePath, textureFileName)
    node_mat_texture.image = bpy.data.images.load(texture_path)
    light001.location.x = random.uniform(-1, 1)
    bpy.context.view_layer.update()

    bpy.data.scenes["Scene"].node_tree.nodes["File Output"].file_slots[0].path = f'rgb{i:04d}'
    bpy.data.scenes["Scene"].node_tree.nodes["File Output"].file_slots[1].path = f'depthExr{i:04d}'
    bpy.data.scenes["Scene"].render.filepath = dataPath + f'/depth_{i:04d}.png'
    textFilePath = dataPath + f'/data_{i:04d}.txt'

    bpy.ops.render.render(write_still=True)

    matrix_empty = bpy.data.objects['empty'].matrix_world
    matrix_camera = bpy.data.objects['Camera'].matrix_world

    r_empty = tuple(map(round, np.degrees(np.array(matrix_empty.to_euler('XYZ')[0:3])), repeat(4)))
    print('Yaw %.2f Pitch %.2f Roll %.2f' % (r_empty[2], r_empty[0], r_empty[1]))

    r_camera = tuple(map(round, np.degrees(np.array(matrix_camera.to_euler('XYZ')[0:3])), repeat(4)))
    print('Yaw %.2f Pitch %.2f Roll %.2f' % (r_camera[2], r_camera[0], r_camera[1]))

    f = open(textFilePath, "w+")
    f.write('Camera Location: ' + str(tuple(map(round, matrix_camera.translation, repeat(4)))) + '\n')
    f.write('Head Point Location: ' + str(empty_init_loc) + '\n')
    f.write('Camera Rotation: ' + 'Yaw %.2f Pitch %.2f Roll %.2f' % (r_camera[2], r_camera[0], r_camera[1]) + '\n')
    f.write('Head Rotation: ' + 'Yaw %.2f Pitch %.2f Roll %.2f' % (r_empty[2], r_empty[0], r_empty[1]) + '\n')

    f.close()

    camera.location = camera_init_loc
    camera.rotation_euler = camera_init_rotation

    camera.location.x = camera.location.x + random.uniform(0.001, 0.140)
    camera.location.z = camera.location.z + random.uniform(0.001, 0.04)

    # point_at(camera, empty_loc, roll=radians(0))

    # print(camera.location.x)
    # print(camera.location.z)
    # print('#########################################\n')

bpy.context.scene.frame_set(0)
bpy.context.view_layer.update()

camera.location = camera_init_loc
camera.rotation_euler = camera_init_rotation

for i in range(10, 20):
    textureFileName = "D" + str(random.randint(1, 112)) + "_COLORED.tif"
    texture_path = os.path.join(baseTexturePath, textureFileName)
    node_mat_texture.image = bpy.data.images.load(texture_path)
    light001.location.x = random.uniform(-1, 1)
    bpy.context.view_layer.update()

    bpy.data.scenes["Scene"].node_tree.nodes["File Output"].file_slots[0].path = f'rgb{i:04d}'
    bpy.data.scenes["Scene"].node_tree.nodes["File Output"].file_slots[1].path = f'depthExr{i:04d}'
    bpy.data.scenes["Scene"].render.filepath = dataPath + f'/depth_{i:04d}.png'
    textFilePath = dataPath + f'/data_{i:04d}.txt'

    bpy.ops.render.render(write_still=True)

    matrix_empty = bpy.data.objects['empty'].matrix_world
    matrix_camera = bpy.data.objects['Camera'].matrix_world

    r_empty = tuple(map(round, np.degrees(np.array(matrix_empty.to_euler('XYZ')[0:3])), repeat(4)))
    print('Yaw %.2f Pitch %.2f Roll %.2f' % (r_empty[2], r_empty[0], r_empty[1]))

    r_camera = tuple(map(round, np.degrees(np.array(matrix_camera.to_euler('XYZ')[0:3])), repeat(4)))
    print('Yaw %.2f Pitch %.2f Roll %.2f' % (r_camera[2], r_camera[0], r_camera[1]))

    f = open(textFilePath, "w+")
    f.write('Camera Location: ' + str(tuple(map(round, matrix_camera.translation, repeat(4)))) + '\n')
    f.write('Head Point Location: ' + str(empty_init_loc) + '\n')
    f.write('Camera Rotation: ' + 'Yaw %.2f Pitch %.2f Roll %.2f' % (r_camera[2], r_camera[0], r_camera[1]) + '\n')
    f.write('Head Rotation: ' + 'Yaw %.2f Pitch %.2f Roll %.2f' % (r_empty[2], r_empty[0], r_empty[1]) + '\n')

    f.close()

    camera.location = camera_init_loc
    camera.rotation_euler = camera_init_rotation

    camera.location.x = camera.location.x - random.uniform(0.001, 0.140)
    camera.location.z = camera.location.z - random.uniform(0.001, 0.04)

    # point_at(camera, empty_loc, roll=radians(0))

    print(camera.location.x)
    print(camera.location.z)
    print('#########################################\n')

# --------- Region Camera Rotation & Translation Head Rotation ------------- #

camera.location = camera_init_loc
camera.rotation_euler = camera_init_rotation

bpy.context.scene.frame_set(0)
bpy.context.view_layer.update()

empty_loc = tuple(empty.location)

dataPath = basePath + '/'.join(bpy.data.filepath.split('/')[-5:-1]) + '/HeadCameraRotTran'
dataPath = dataPath.replace('Simple','Textured')

bpy.data.scenes["Scene"].node_tree.nodes["File Output"].base_path = dataPath

center = Point(tuple(empty.location))
r = 0.3
num = 70
pts = generatePoints(r, center, num)

print('Length pf pts :' + str(len(pts)))

for i, pt in enumerate(pts):

    frame = i
    if frame > 70:
        frame = frame - 70

    bpy.context.scene.frame_set(frame)
    textureFileName = "D" + str(random.randint(1, 112)) + "_COLORED.tif"
    texture_path = os.path.join(baseTexturePath, textureFileName)
    node_mat_texture.image = bpy.data.images.load(texture_path)
    light001.location.x = random.uniform(-1, 1)
    bpy.context.view_layer.update()

    bpy.data.scenes["Scene"].node_tree.nodes["File Output"].file_slots[0].path = f'rgb{i:04d}'
    bpy.data.scenes["Scene"].node_tree.nodes["File Output"].file_slots[1].path = f'depthExr{i:04d}'

    bpy.data.scenes["Scene"].render.filepath = dataPath + f'/depth_{i:04d}.png'
    textFilePath = dataPath + f'/data_{i:04d}.txt'

    bpy.ops.render.render(write_still=True)

    matrix_empty = bpy.data.objects['empty'].matrix_world
    matrix_camera = bpy.data.objects['Camera'].matrix_world

    r_empty = tuple(map(round, np.degrees(np.array(matrix_empty.to_euler('XYZ')[0:3])), repeat(4)))
    print('Yaw %.2f Pitch %.2f Roll %.2f' % (r_empty[2], r_empty[0], r_empty[1]))

    r_camera = tuple(map(round, np.degrees(np.array(matrix_camera.to_euler('XYZ')[0:3])), repeat(4)))
    print('Yaw %.2f Pitch %.2f Roll %.2f' % (r_camera[2], r_camera[0], r_camera[1]))

    f = open(textFilePath, "w+")
    f.write('Camera Location: ' + str(tuple(map(round, matrix_camera.translation, repeat(4)))) + '\n')
    f.write('Head Point Location: ' + str(empty_init_loc) + '\n')
    f.write('Camera Rotation: ' + 'Yaw %.2f Pitch %.2f Roll %.2f' % (r_camera[2], r_camera[0], r_camera[1]) + '\n')
    f.write('Head Rotation: ' + 'Yaw %.2f Pitch %.2f Roll %.2f' % (r_empty[2], r_empty[0], r_empty[1]) + '\n')

    f.close()

    camera.location = tuple(map(float, tuple(pt)))
    # camera.rotation_euler = camera_init_rotation

    # camera.location.x = camera.location.x + random.uniform(0.001,0.140)
    # camera.location.z = camera.location.z + random.uniform(0.001,0.04)

    point_at(camera, empty_loc, roll=radians(0))
