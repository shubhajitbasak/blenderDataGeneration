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


print('################################### \n ################################# \n\n TEST TEST TEST \n\n')


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

bpy.context.scene.view_layers[0].cycles.use_denoising = True

basePath = '/mnt/sata/code/blenderDataGenerationFinal/data/Data/'

dataPath = basePath + '/'.join(bpy.data.filepath.split('/')[-5:-1])
dataPath = dataPath.replace('Simple', 'Complex/Barbershop')

bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT')

# bpy.data.objects["Point"].hide_render = False
bpy.context.scene.render.tile_x = 64
bpy.context.scene.render.tile_y = 64
bpy.context.scene.cycles.aa_samples = 1

bpy.context.scene.cycles.seed = 0

camera = bpy.data.objects['Camera']
camera.data.clip_end = 15
scene.camera = camera

empty = bpy.data.objects['empty']

empty_init_loc = tuple(map(round, empty.matrix_world.translation, repeat(4)))
camera_init_loc = tuple(camera.location)
camera_init_rotation = tuple(camera.rotation_euler)

print("****************** Starting *********************** \n ")
print("\n Path : " + dataPath)

# --------- Region Head Rotation ------------- #

if True:

    dataPathHeadRot = dataPath + '/HeadRot'

    bpy.data.scenes["Scene"].node_tree.nodes["File Output"].base_path = dataPathHeadRot

    if not os.path.exists(dataPathHeadRot):
        os.makedirs(dataPathHeadRot)

    print("\n\n Head Rotation Path : " + dataPathHeadRot)

    for i in range(0, 1):
        bpy.context.scene.frame_set(i)

        bpy.data.scenes["Scene"].render.filepath = dataPathHeadRot + f'/depth_{i:04d}.png'
        textFilePath = dataPathHeadRot + f'/data_{i:04d}.txt'

        bpy.ops.render.render(write_still=True)

        matrix_empty = bpy.data.objects['empty'].matrix_world
        matrix_camera = bpy.data.objects['Camera'].matrix_world

        r_empty = tuple(map(round, np.degrees(np.array(matrix_empty.to_euler('XYZ')[0:3])), repeat(4)))

        r_camera = tuple(map(round, np.degrees(np.array(matrix_camera.to_euler('XYZ')[0:3])), repeat(4)))

        with open(textFilePath, "w") as f:
            f.write('Camera Location: ' + str(tuple(map(round, matrix_camera.translation, repeat(4)))) + '\n')
            f.write('Head Point Location: ' + str(empty_init_loc) + '\n')
            f.write('Camera Rotation: ' + 'Yaw %.2f Pitch %.2f Roll %.2f' % (r_camera[2], r_camera[0], r_camera[1]) + '\n')
            f.write('Head Rotation: ' + 'Yaw %.2f Pitch %.2f Roll %.2f' % (r_empty[2], r_empty[0], r_empty[1]) + '\n')

# --------- Region Camera Translation ------------- #

if True:

    dataPathCameraTran = dataPath + '/CameraTran'

    if not os.path.exists(dataPathCameraTran):
        os.makedirs(dataPathCameraTran)

    print("\n\n Camera Trans Path : " + dataPathCameraTran)

    bpy.data.scenes["Scene"].node_tree.nodes["File Output"].base_path = dataPathCameraTran

    bpy.context.scene.frame_set(0)

    bpy.context.view_layer.update()

    for i in range(0, 1):

        bpy.data.scenes["Scene"].node_tree.nodes["File Output"].file_slots[0].path = f'image{i:04d}'
        bpy.data.scenes["Scene"].node_tree.nodes["File Output"].file_slots[1].path = f'depthExr{i:04d}'
        bpy.data.scenes["Scene"].render.filepath = dataPathCameraTran + f'/depth_{i:04d}.png'
        textFilePath = dataPathCameraTran + f'/data_{i:04d}.txt'

        bpy.ops.render.render(write_still=True)

        matrix_empty = bpy.data.objects['empty'].matrix_world
        matrix_camera = bpy.data.objects['Camera'].matrix_world

        r_empty = tuple(map(round, np.degrees(np.array(matrix_empty.to_euler('XYZ')[0:3])), repeat(4)))

        r_camera = tuple(map(round, np.degrees(np.array(matrix_camera.to_euler('XYZ')[0:3])), repeat(4)))

        with open(textFilePath, "w") as f:
            f.write('Camera Location: ' + str(tuple(map(round, matrix_camera.translation, repeat(4)))) + '\n')
            f.write('Head Point Location: ' + str(empty_init_loc) + '\n')
            f.write('Camera Rotation: ' + 'Yaw %.2f Pitch %.2f Roll %.2f' % (r_camera[2], r_camera[0], r_camera[1]) + '\n')
            f.write('Head Rotation: ' + 'Yaw %.2f Pitch %.2f Roll %.2f' % (r_empty[2], r_empty[0], r_empty[1]) + '\n')


        camera.location = camera_init_loc
        camera.rotation_euler = camera_init_rotation

        camera.location.x = camera.location.x + random.uniform(0.001, 0.140)
        camera.location.z = camera.location.z + random.uniform(0.001, 0.04)


    bpy.context.scene.frame_set(0)
    bpy.context.view_layer.update()

    camera.location = camera_init_loc
    camera.rotation_euler = camera_init_rotation

    for i in range(1, 2):

        bpy.data.scenes["Scene"].node_tree.nodes["File Output"].file_slots[0].path = f'image{i:04d}'
        bpy.data.scenes["Scene"].node_tree.nodes["File Output"].file_slots[1].path = f'depthExr{i:04d}'
        bpy.data.scenes["Scene"].render.filepath = dataPathCameraTran + f'/depth_{i:04d}.png'
        textFilePath = dataPathCameraTran + f'/data_{i:04d}.txt'

        bpy.ops.render.render(write_still=True)

        matrix_empty = bpy.data.objects['empty'].matrix_world
        matrix_camera = bpy.data.objects['Camera'].matrix_world

        r_empty = tuple(map(round, np.degrees(np.array(matrix_empty.to_euler('XYZ')[0:3])), repeat(4)))

        r_camera = tuple(map(round, np.degrees(np.array(matrix_camera.to_euler('XYZ')[0:3])), repeat(4)))

        with open(textFilePath, "w") as f:
            f.write('Camera Location: ' + str(tuple(map(round, matrix_camera.translation, repeat(4)))) + '\n')
            f.write('Head Point Location: ' + str(empty_init_loc) + '\n')
            f.write('Camera Rotation: ' + 'Yaw %.2f Pitch %.2f Roll %.2f' % (r_camera[2], r_camera[0], r_camera[1]) + '\n')
            f.write('Head Rotation: ' + 'Yaw %.2f Pitch %.2f Roll %.2f' % (r_empty[2], r_empty[0], r_empty[1]) + '\n')


        camera.location = camera_init_loc
        camera.rotation_euler = camera_init_rotation

        camera.location.x = camera.location.x - random.uniform(0.001, 0.140)
        camera.location.z = camera.location.z - random.uniform(0.001, 0.04)


# --------- Region Camera Rotation & Translation Head Rotation ------------- #

if True:

    camera.location = camera_init_loc
    camera.rotation_euler = camera_init_rotation

    bpy.context.scene.frame_set(0)
    bpy.context.view_layer.update()

    # empty_loc = tuple(empty.location)

    dataPathHeadCamRotTran = dataPath + '/HeadCameraRotTran'

    if not os.path.exists(dataPathHeadCamRotTran):
        os.makedirs(dataPathHeadCamRotTran)

    print("\n\n Head Rotation Camera Rotation Path : " + dataPathHeadCamRotTran)

    bpy.data.scenes["Scene"].node_tree.nodes["File Output"].base_path = dataPathHeadCamRotTran

    center = Point(tuple(empty_init_loc))
    start = 0
    r = 0.3
    # num = 70 - start
    num = 2
    pts = generatePoints(r, center, num)

    for i, pt in enumerate(pts, start):
        print(i, pt)

        frame = i
        if frame > 70:
            frame = frame - 70

        bpy.context.scene.frame_set(frame)
        # material.diffuse_color = get_random_color()
        bpy.context.view_layer.update()

        bpy.data.scenes["Scene"].node_tree.nodes["File Output"].file_slots[0].path = f'image{i:04d}'
        bpy.data.scenes["Scene"].node_tree.nodes["File Output"].file_slots[1].path = f'depthExr{i:04d}'

        bpy.data.scenes["Scene"].render.filepath = dataPathHeadCamRotTran + f'/depth_{i:04d}.png'
        textFilePath = dataPathHeadCamRotTran + f'/data_{i:04d}.txt'

        bpy.ops.render.render(write_still=True)

        matrix_empty = bpy.data.objects['empty'].matrix_world
        matrix_camera = bpy.data.objects['Camera'].matrix_world

        r_empty = tuple(map(round, np.degrees(np.array(matrix_empty.to_euler('XYZ')[0:3])), repeat(4)))

        r_camera = tuple(map(round, np.degrees(np.array(matrix_camera.to_euler('XYZ')[0:3])), repeat(4)))

        with open(textFilePath, "w") as f:
            f.write('Camera Location: ' + str(tuple(map(round, matrix_camera.translation, repeat(4)))) + '\n')
            f.write('Head Point Location: ' + str(empty_init_loc) + '\n')
            f.write('Camera Rotation: ' + 'Yaw %.2f Pitch %.2f Roll %.2f' % (r_camera[2], r_camera[0], r_camera[1]) + '\n')
            f.write('Head Rotation: ' + 'Yaw %.2f Pitch %.2f Roll %.2f' % (r_empty[2], r_empty[0], r_empty[1]) + '\n')

        camera.location = tuple(map(float, tuple(pt)))

        point_at(camera, empty_init_loc, roll=radians(0))

print("\n\n Completed \n\n ############################################# ******************************************* "
      "######################################## \n\n")