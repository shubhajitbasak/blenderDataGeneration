# with Gaze ------------------

import bpy
import numpy as np
from itertools import repeat
import random
import os
import sys

# from sympy.geometry import Point

from numpy import cos, sin
from math import radians, degrees
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


def map_tuple_gen(func, tup):
    return tuple(func(itup) for itup in tup)


def getHP():
    matrix_empty = bpy.data.objects['empty'].matrix_world
    r_empty = tuple(map(round, np.degrees(np.array(matrix_empty.to_euler('XYZ')[0:3])), repeat(4)))
    # l_empty = tuple(map(round, matrix_empty.translation, repeat(4)))
    return (-r_empty[2], -r_empty[0], r_empty[1])


def getDeltaHP(yaw, pitch, roll):
    yawU, pitchU, rollU = getHP()

    deltaYaw = yaw - yawU
    deltaPitch = pitch - pitchU
    deltaRoll = roll - rollU

    return deltaYaw, deltaPitch, deltaRoll


def applyHP(yaw, pitch, roll):
    # print('\n', round(yaw, 4), round(pitch, 4), round(roll, 4))

    arma = bpy.data.objects['Armature']
    bpy.context.view_layer.objects.active = arma
    bpy.ops.object.mode_set(mode='POSE')

    boneHead = arma.pose.bones['Head']  # Head  G6Beta_Head
    boneNeck = arma.pose.bones['NeckTwist01']  # NeckTwist01  G6Beta_Neck
    boneHead.rotation_mode = 'XYZ'
    boneNeck.rotation_mode = 'XYZ'

    boneNeck.rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()

    bpy.context.scene.transform_orientation_slots[0].type = 'LOCAL'

    if (yaw > 0) & (pitch < 0) & (roll < 0):

        # print(1)

        boneNeck.rotation_euler.rotate_axis('Y', -radians(yaw))  # yaw
        bpy.context.view_layer.update()

        boneNeck.rotation_euler.rotate_axis('Z', -radians(roll))  # roll
        bpy.context.view_layer.update()

        boneNeck.rotation_euler.rotate_axis('X', -radians(pitch))  # pitch
        bpy.context.view_layer.update()

    elif (yaw < 0) & (pitch > 0) & (roll < 0):

        # print(2)

        boneNeck.rotation_euler.rotate_axis('Y', -radians(yaw))  # yaw
        bpy.context.view_layer.update()

        boneNeck.rotation_euler.rotate_axis('Z', -radians(roll))  # roll
        bpy.context.view_layer.update()

        boneNeck.rotation_euler.rotate_axis('X', -radians(pitch))  # pitch
        bpy.context.view_layer.update()

    else:

        # print(3)

        boneNeck.rotation_euler.rotate_axis('X', -radians(pitch))  # pitch
        bpy.context.view_layer.update()

        boneNeck.rotation_euler.rotate_axis('Z', -radians(roll))  # roll
        bpy.context.view_layer.update()

        boneNeck.rotation_euler.rotate_axis('Y', -radians(yaw))  # yaw
        bpy.context.view_layer.update()

    if (yaw > 0) & (pitch < 0) & (roll < 0):

        _, _, deltaRoll = getDeltaHP(yaw, pitch, roll)

        boneNeck.rotation_euler.rotate_axis('Z', -radians(deltaRoll))  # roll
        bpy.context.view_layer.update()

        _, deltaPitch, _ = getDeltaHP(yaw, pitch, roll)

        boneNeck.rotation_euler.rotate_axis('X', -radians(deltaPitch))  # pitch
        bpy.context.view_layer.update()

        deltaYaw, _, _ = getDeltaHP(yaw, pitch, roll)

        boneNeck.rotation_euler.rotate_axis('Y', -radians(deltaYaw))  # yaw
        bpy.context.view_layer.update()

    elif (yaw < 0) & (pitch > 0) & (roll < 0):

        deltaYaw, _, _ = getDeltaHP(yaw, pitch, roll)

        boneNeck.rotation_euler.rotate_axis('Y', -radians(deltaYaw))  # yaw
        bpy.context.view_layer.update()

        _, deltaPitch, _ = getDeltaHP(yaw, pitch, roll)

        boneNeck.rotation_euler.rotate_axis('X', -radians(deltaPitch))  # pitch
        bpy.context.view_layer.update()

        _, _, deltaRoll = getDeltaHP(yaw, pitch, roll)

        boneNeck.rotation_euler.rotate_axis('Z', -radians(deltaRoll))  # roll
        bpy.context.view_layer.update()

    else:

        _, deltaPitch, _ = getDeltaHP(yaw, pitch, roll)

        boneNeck.rotation_euler.rotate_axis('X', -radians(deltaPitch))  # pitch
        bpy.context.view_layer.update()

        _, _, deltaRoll = getDeltaHP(yaw, pitch, roll)

        boneNeck.rotation_euler.rotate_axis('Z', -radians(deltaRoll))  # roll
        bpy.context.view_layer.update()

        deltaYaw, _, _ = getDeltaHP(yaw, pitch, roll)

        boneNeck.rotation_euler.rotate_axis('Y', -radians(deltaYaw))  # yaw
        bpy.context.view_layer.update()

        bpy.context.scene.transform_orientation_slots[0].type = 'GLOBAL'

    return getHP()


def applyHPtoNeckBone(t1, t2, t3):
    bpy.context.object.pose.bones["NeckTwist01"].rotation_euler = tuple(map(radians, (t1, t2, t3)))
    bpy.context.view_layer.update()


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

# '/mnt/fastssd/Shubhajit_Stuff/dataCreation/Data/'
basePath = r'D:\project1\dataCreation\Scripts\BlenderHeadPoseCreation\Data\\'

# r"/mnt/fastssd/Shubhajit_Stuff/Code/Background/Colored Brodatz/"
baseTexturePath = r"D:\project1\dataCreation\Scripts\BlenderHeadPoseCreation\Background\Colored Brodatz"

bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT')

bpy.context.scene.cycles.progressive = 'PATH'
bpy.context.scene.cycles.samples = 256  # sbasak01
bpy.context.scene.frame_set(0)
bpy.context.view_layer.update()

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

light = bpy.data.objects["Light"]

argv = sys.argv
argv = argv[argv.index("--") + 1:]
print(argv)
biwiId = int(argv[0])

# set real background render
if argv[1] == 'True':
    renderReal = True
elif argv[1] == 'False':
    renderReal = False

# /mnt/fastssd/Shubhajit_Stuff/Code/HeadPose/BIWIPoseLabel/
# with open(fr'D:\project1\dataCreation\Scripts\BlenderHeadPoseCreation\BIWIPoseLabel\\{biwiId:02d}.txt', 'r') as f1:
#     data = f1.readlines()


if renderReal:
    bpy.data.objects['Plane.005'].hide_render = True

# /mnt/fastssd/Shubhajit_Stuff/Code/HeadPose/BIWI_noTrack_pose.npy
# poseData = np.load(r'D:\project1\dataCreation\Scripts\BlenderHeadPoseCreation\BIWI_noTrack_pose.npy')
# data = poseData

neckBoneDataPath = bpy.data.filepath.replace('.blend', '_neckbone.txt')
with open(neckBoneDataPath, 'r') as f1:
    data = f1.readlines()

# --------- Region Head Rotation ------------- #

if True:

    dataPath = basePath + '\\'.join(bpy.data.filepath.split('\\')[-5:-1]) + '/HeadRot'
    dataPath = dataPath.replace('Simple', 'HeadPose/Textured')

    hpDataPath = bpy.data.filepath.replace('.blend', '.txt')
    # print(basePath)
    print(hpDataPath)
    if os.path.exists(hpDataPath):
        os.remove(hpDataPath)

    bpy.data.scenes["Scene"].node_tree.nodes["File Output"].base_path = dataPath

    i = 0

    print(len(data))
    for k in range(1):

        for idx, hp in enumerate(data):

            textureFileName = "D" + str(random.randint(1, 112)) + "_COLORED.tif"
            texture_path = os.path.join(baseTexturePath, textureFileName)
            node_mat_texture.image = bpy.data.images.load(texture_path)

            bpy.data.materials["MaterialLight"].node_tree.nodes["Emission"].inputs[1].default_value = \
                random.uniform(20.0, 25.0)  # light intensity
            light.location.x = random.uniform(-2.0, 2.0)
            light.location.z = random.uniform(0.8, 2.8)

            camera.location = camera_init_loc

            t1, t2, t3 = tuple(map(float, hp.strip().split(',')))
            applyHPtoNeckBone(t1, t2, t3)

            bpy.context.view_layer.update()

            if renderReal:
                # /mnt/fastssd/Shubhajit_Stuff/Code/Background/RealBackGround/
                backGroundFilePath = os.path.join(
                    r'D:\project1\dataCreation\Scripts\BlenderHeadPoseCreation\Background\RealBackGround',
                    f'a{random.randint(1, 20):02d}new.jpg')
                bpy.data.scenes["Scene"].node_tree.nodes["Image"].image.filepath = backGroundFilePath

            bpy.data.scenes["Scene"].node_tree.nodes["File Output"].file_slots[0].path = f'rgb{i:04d}'
            textFilePath = dataPath + f'/data_{i:04d}.txt'

            matrix_empty = bpy.data.objects['empty'].matrix_world
            r_empty = tuple(map(round, np.degrees(np.array(matrix_empty.to_euler('XYZ')[0:3])), repeat(4)))
            l_empty = tuple(map(round, matrix_empty.translation, repeat(4)))

            # if r_empty[0] > 25:
            #     camera.location.y = camera.location.y - 0.15
            #
            # if r_empty[1] > 25 and r_empty[2] > 25:
            #     camera.location.y = camera.location.y - 0.15

            matrix_camera = bpy.data.objects['Camera'].matrix_world
            r_camera = tuple(map(round, np.degrees(np.array(matrix_camera.to_euler('XYZ')[0:3])), repeat(4)))

            # bpy.ops.render.render(write_still=True)

            # f = open(textFilePath, "w+")
            # f.write('Camera Location: ' + str(tuple(map(round, matrix_camera.translation, repeat(4)))) + '\n')
            # f.write('Head Point Location: ' + str(empty_init_loc) + '\n')
            # f.write('Head Point Current Location: ' + str(l_empty) + '\n')
            # f.write('Camera Rotation: ' + 'Yaw %.2f Pitch %.2f Roll %.2f' % (r_camera[2], r_camera[0], r_camera[1]) + '\n')
            # f.write('Head Rotation: ' + 'Yaw %.2f Pitch %.2f Roll %.2f' % (-r_empty[2], -r_empty[0], r_empty[1]) + '\n')
            # f.write('%.2f, %.2f, %.2f' % (-r_empty[2], -r_empty[0], r_empty[1]))
            # f.close()

            # n1, n2, n3 = tuple(map(degrees, bpy.context.object.pose.bones["NeckTwist01"].rotation_euler))

            # print(-r_empty[2], -r_empty[0], r_empty[1], n1, n2, n3)

            with open(hpDataPath,'a') as f:
                f.write('%.5f,%.5f,%.5f\n' % (-r_empty[2], -r_empty[0], r_empty[1]))

            # with open(r'D:\project1\dataCreation\Scripts\BlenderHeadPoseCreation\Data\target.txt', 'a') as f:
            #     f.write('%.5f,%.5f,%.5f\n' % (n2, n1, n3))

            # print('%.5f,%.5f,%.5f' % (-r_empty[2], -r_empty[0], r_empty[1]))

            i += 1
