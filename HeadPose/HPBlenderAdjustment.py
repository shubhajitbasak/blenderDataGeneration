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
basePath = r'D:\project1\dataCreation\Scripts\BlenderHeadPoseCreation\Data'

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

neckBoneInitRotation = tuple(map(degrees,bpy.context.object.pose.bones["NeckTwist01"].rotation_euler))

material = bpy.data.materials['MaterialPlane001']
material.use_nodes = True
_nodes = material.node_tree.nodes
_material_links = material.node_tree.links
node_principledBsdf = _nodes['Principled BSDF']
node_mat_texture = _nodes.new('ShaderNodeTexImage')
node_mat_texture.location = -50, 90
_material_links.new(node_mat_texture.outputs['Color'], node_principledBsdf.inputs['Base Color'])

light = bpy.data.objects["Light"]

# /mnt/fastssd/Shubhajit_Stuff/Code/HeadPose/BIWI_noTrack_pose.npy
# poseData = np.load(r'D:\project1\dataCreation\Scripts\BlenderHeadPoseCreation\BIWI_noTrack_pose.npy')
# data = poseData


neckBoneDataPath = bpy.data.filepath.replace('.blend', '_neckbone.txt')
neckBoneBkpDataPath = neckBoneDataPath.replace('_neckbone', '_neckboneBkp')

if os.path.exists(neckBoneDataPath):
    with open(neckBoneDataPath, 'r') as f1:
        data = f1.readlines()

    if os.path.exists(neckBoneBkpDataPath):
        os.remove(neckBoneBkpDataPath)

    os.rename(neckBoneDataPath, neckBoneBkpDataPath)

else:
    with open(r'D:\project1\dataCreation\BlenderData\biwiNeckBone.txt', 'r') as f1:
        data = f1.readlines()

with open(r'D:\project1\dataCreation\BlenderData\biwiNoTrack.txt', 'r') as f1:
    biwi = f1.readlines()

fid = int(bpy.data.filepath.split('\\')[-4])
print(fid)

# --------- Region Head Rotation ------------- #
if True:

    dataPath = basePath + '/'.join(bpy.data.filepath.split('/')[-5:-1]) + '/HeadRot'
    dataPath = dataPath.replace('Simple', 'HeadPose/Textured')

    # fid = int(bpy.data.filepath.split('\\')[-4])

    bpy.data.scenes["Scene"].node_tree.nodes["File Output"].base_path = dataPath

    i = 0

    f = open(neckBoneDataPath, "w+")

    # f1 = open('sampleOutput.txt', 'a')

    print(len(data))
    for k in range(1):

        for idx, hp in enumerate(data):
            # print(neckBoneInitRotation)
            # print(idx)
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

            matrix_empty = bpy.data.objects['empty'].matrix_world
            r_empty = tuple(map(round, np.degrees(np.array(matrix_empty.to_euler('XYZ')[0:3])), repeat(4)))
            l_empty = tuple(map(round, matrix_empty.translation, repeat(4)))

            matrix_camera = bpy.data.objects['Camera'].matrix_world
            r_camera = tuple(map(round, np.degrees(np.array(matrix_camera.to_euler('XYZ')[0:3])), repeat(4)))

            y, p, r = tuple(map(float, biwi[idx].strip().split()))

            y1, p1, r1 = -r_empty[2], -r_empty[0], r_empty[1]

            gt = np.array([y, p, r], dtype=np.int32)
            pred = np.array([y1, p1, r1], dtype=np.int32)

            error1 = np.mean(np.abs(pred - gt), axis=0)

            diff = (pred - gt)

            if error1 > 0.3:
                i += 1
                # print(fid)

                # print('%0.0f  %0.0f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f  %.2f' %
                #       (fid, idx, t1, t2, t3, y, p, r, y1, p1, r1, error1))
                #
                # print(diff)

                # f1.write('%0.0f  %0.0f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f  %.2f \n' %
                #       (fid, idx, t1, t2, t3, y, p, r, y1, p1, r1, error1))
                # f1.write(str(diff))
                # f1.write('\n')

                if np.array_equal(diff, np.array([0, 2, -1])):

                    print('%0.0f  %0.0f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f  %.2f' %
                          (fid, idx, t1, t2, t3, y, p, r, y1, p1, r1, error1))

                    print(diff)

                    if (t1 < 0) and (t2 < 0) and (t3 > 0):
                        _t1 = t1 + (1.0 * diff[1])
                        _t2 = t2 - (0.1 * diff[0])
                        _t3 = t3 + (0.8 * diff[2])

                    elif (t1 < 0) and (t2 < 0) and (t3 < 0):
                        _t1 = t1 + (1.5 * diff[1])
                        _t2 = t2 + (0.1 * diff[0])
                        _t3 = t3 + (0.9 * diff[2])

                    elif (t1 > 0) and (t2 < 0) and (t3 > 0):
                        _t1 = t1 + (1.0 * diff[1])
                        _t2 = t2 + (0.1 * diff[0])
                        _t3 = t3 + (0.7 * diff[2])

                    elif (t1 > 0) and (t2 < 0) and (t3 < 0):
                        _t1 = t1 + (1.0 * diff[1])
                        _t2 = t2 + (0.1 * diff[0])
                        _t3 = t3 + (1.0 * diff[2])

                    else:
                        _t1 = t1
                        _t2 = t2
                        _t3 = t3

                elif np.array_equal(diff, np.array([0, 1, -1])):

                    print('%0.0f  %0.0f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f  %.2f' %
                          (fid, idx, t1, t2, t3, y, p, r, y1, p1, r1, error1))

                    print(diff)

                    if (t1 < 0) and (t2 < 0) and (t3 > 0):
                        _t1 = t1 + (2.0 * diff[1])
                        _t2 = t2 + (0.1 * diff[0])
                        _t3 = t3 + (1.6 * diff[2])

                    elif (t1 < 0) and (t2 < 0) and (t3 < 0):
                        _t1 = t1 + (1.0 * diff[1])
                        _t2 = t2 + (0.1 * diff[1])
                        _t3 = t3 + (1.0 * diff[2])

                    elif (t1 < 0) and (t2 > 0) and (t3 > 0):
                        _t1 = t1 + (0.1 * diff[0])
                        _t2 = t2 + (0.1 * diff[0])
                        _t3 = t3 + (1.1 * diff[2])

                    elif (t1 < 0) and (t2 > 0) and (t3 < 0):
                        _t1 = t1 + (0.2 * diff[1])
                        _t2 = t2 - (0.1 * diff[0])
                        _t3 = t3 + (1.0 * diff[2])

                    elif (t1 > 0) and (t2 < 0) and (t3 > 0):
                        _t1 = t1 + (0.8 * diff[1])
                        _t2 = t2 + (1.0 * diff[2])
                        _t3 = t3 + (0.1 * diff[2])

                    elif (t1 > 0) and (t2 < 0) and (t3 < 0):
                        _t1 = t1 + (1.3 * diff[1])
                        _t2 = t2 + (0.4 * diff[0])
                        _t3 = t3 + (0.6 * diff[2])

                    elif (t1 > 0) and (t2 > 0) and (t3 < 0):
                        _t1 = t1 + (0.9 * diff[1])
                        _t2 = t2 - (0.9 * diff[1])
                        _t3 = t3 + (0.4 * diff[2])

                    else:
                        _t1 = t1
                        _t2 = t2
                        _t3 = t3

                elif np.array_equal(diff, np.array([-1, 1, 1])):

                    print('%0.0f  %0.0f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f  %.2f' %
                          (fid, idx, t1, t2, t3, y, p, r, y1, p1, r1, error1))

                    print(diff)

                    if (t1 < 0) and (t2 > 0) and (t3 > 0):
                        _t1 = t1 + (1.2 * diff[1])
                        _t2 = t2 + (0.9 * diff[0])
                        _t3 = t3 + (1.0 * diff[2])

                    elif (t1 < 0) and (t2 > 0) and (t3 < 0):
                        _t1 = t1 + (1.8 * diff[1])
                        _t2 = t2 + (0.8 * diff[0])
                        _t3 = t3 + (1.3 * diff[2])

                    elif (t1 < 0) and (t2 < 0) and (t3 < 0):
                        _t1 = t1 + (0.2 * diff[1])
                        _t2 = t2 + (1.0 * diff[0])
                        _t3 = t3 + (1.0 * diff[2])

                    elif (t1 > 0) and (t2 < 0) and (t3 < 0):
                        _t1 = t1 + (0.1 * diff[1])
                        _t2 = t2 + (1.0 * diff[0])
                        _t3 = t3 + (1.3 * diff[2])

                    else:
                        _t1 = t1
                        _t2 = t2
                        _t3 = t3

                elif np.array_equal(diff, np.array([-1, 1, -1])):

                    print('%0.0f  %0.0f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f  %.2f' %
                          (fid, idx, t1, t2, t3, y, p, r, y1, p1, r1, error1))

                    print(diff)

                    if (t1 > 0) and (t2 > 0) and (t3 < 0):
                        _t1 = t1 + (0.2 * diff[1])
                        _t2 = t2 + (0.9 * diff[0])
                        _t3 = t3 + (1.0 * diff[2])

                    elif (t1 < 0) and (t2 > 0) and (t3 < 0):
                        _t1 = t1 + (1.2 * diff[1])
                        _t2 = t2 + (1.6 * diff[0])
                        _t3 = t3 + (0.3 * diff[2])

                    elif (t1 > 0) and (t2 < 0) and (t3 > 0):
                        _t1 = t1 + (1.0 * diff[1])
                        _t2 = t2 + (1.0 * diff[0])
                        _t3 = t3 + (0.4 * diff[2])

                    elif (t1 < 0) and (t2 < 0) and (t3 > 0):
                        _t1 = t1 + (0.9 * diff[1])
                        _t2 = t2 + (1.0 * diff[0])
                        _t3 = t3 + (0.5 * diff[2])

                    else:
                        _t1 = t1
                        _t2 = t2
                        _t3 = t3

                elif np.array_equal(diff, np.array([-1, 0, 1])):

                    print('%0.0f  %0.0f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f  %.2f' %
                          (fid, idx, t1, t2, t3, y, p, r, y1, p1, r1, error1))

                    print(diff)

                    if (t1 > 0) and (t2 < 0) and (t3 < 0):
                        _t1 = t1 + (0.4 * diff[0])
                        _t2 = t2 + (0.9 * diff[0])
                        _t3 = t3 + (0.9 * diff[2])

                    elif (t1 > 0) and (t2 < 0) and (t3 > 0):
                        _t1 = t1 + (0.2 * diff[0])
                        _t2 = t2 + (1.0 * diff[0])
                        _t3 = t3 + (0.9 * diff[2])

                    elif (t1 < 0) and (t2 < 0) and (t3 < 0):
                        _t1 = t1 + (1.0 * diff[0])
                        _t2 = t2 + (1.0 * diff[0])
                        _t3 = t3 + (2.0 * diff[2])

                    elif (t1 < 0) and (t2 > 0) and (t3 > 0):
                        _t1 = t1 + (1.0 * diff[2])
                        _t2 = t2 + (1.0 * diff[0])
                        _t3 = t3 + (1.0 * diff[2])

                    else:
                        _t1 = t1
                        _t2 = t2
                        _t3 = t3

                elif np.array_equal(diff, np.array([2, -1, 0])):

                    print('%0.0f  %0.0f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f  %.2f' %
                          (fid, idx, t1, t2, t3, y, p, r, y1, p1, r1, error1))

                    print(diff)

                    if (t1 < 0) and (t2 > 0) and (t3 > 0):
                        _t1 = t1 - (1.7 * diff[1])
                        _t2 = t2 + (1.0 * diff[0])
                        _t3 = t3 + (0.1 * diff[2])

                    elif (t1 < 0) and (t2 > 0) and (t3 < 0):
                        _t1 = t1 + (1.8 * diff[1])
                        _t2 = t2 + (0.8 * diff[0])
                        _t3 = t3 + (1.3 * diff[2])

                    # elif (t1 < 0) and (t2 > 0) and (t3 < 0):
                    #     _t1 = t1 + (0.9 * diff[2])
                    #     _t2 = t2 + (0.1 * diff[0])
                    #     _t3 = t3 + (1.7 * diff[2])
                    #
                    # elif (t1 < 0) and (t2 < 0) and (t3 < 0):
                    #     _t1 = t1 - (0.5 * diff[2])
                    #     _t2 = t2 - (1.0 * diff[2])
                    #     _t3 = t3 + (1.0 * diff[2])

                    else:
                        _t1 = t1
                        _t2 = t2
                        _t3 = t3

                elif np.array_equal(diff, np.array([0, 1, 0])):

                    print('%0.0f  %0.0f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f  %.2f' %
                          (fid, idx, t1, t2, t3, y, p, r, y1, p1, r1, error1))

                    print(diff)

                    if (t1 < 0) and (t2 < 0) and (t3 > 0):
                        _t1 = t1 + (1.0 * diff[1])
                        _t2 = t2 + (0.1 * diff[0])
                        _t3 = t3 + (0.1 * diff[2])

                    elif (t1 < 0) and (t2 < 0) and (t3 < 0):
                        _t1 = t1 + (1.0 * diff[1])
                        _t2 = t2 + (0.1 * diff[0])
                        _t3 = t3 + (0.1 * diff[2])

                    elif (t1 < 0) and (t2 > 0) and (t3 < 0):
                        _t1 = t1 + (1.0 * diff[1])
                        _t2 = t2 + (0.1 * diff[0])
                        _t3 = t3 + (0.1 * diff[2])

                    elif (t1 < 0) and (t2 > 0) and (t3 > 0):
                        _t1 = t1 + (1.0 * diff[1])
                        _t2 = t2 + (0.1 * diff[0])
                        _t3 = t3 + (0.1 * diff[2])

                    elif (t1 > 0) and (t2 < 0) and (t3 > 0):
                        _t1 = t1 + (1.0 * diff[1])
                        _t2 = t2 - (0.1 * diff[0])
                        _t3 = t3 + (0.1 * diff[2])

                    elif (t1 > 0) and (t2 > 0) and (t3 > 0):
                        _t1 = t1 + (1.0 * diff[1])
                        _t2 = t2 - (0.1 * diff[0])
                        _t3 = t3 + (0.1 * diff[2])

                    elif (t1 > 0) and (t2 > 0) and (t3 < 0):
                        _t1 = t1 + (1.0 * diff[1])
                        _t2 = t2 - (0.1 * diff[0])
                        _t3 = t3 + (0.1 * diff[2])

                    elif (t1 > 0) and (t2 < 0) and (t3 < 0):
                        _t1 = t1 + (1.0 * diff[1])
                        _t2 = t2 - (0.1 * diff[0])
                        _t3 = t3 + (0.1 * diff[2])

                    else:
                        _t1 = t1
                        _t2 = t2
                        _t3 = t3

                elif np.array_equal(diff, np.array([0, 0, -2])):

                    print('%0.0f  %0.0f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f  %.2f' %
                          (fid, idx, t1, t2, t3, y, p, r, y1, p1, r1, error1))

                    print(diff)

                    if (t1 < 0) and (t2 > 0) and (t3 < 0):
                        _t1 = t1 + (1.5 * diff[2])
                        _t2 = t2 + (0.5 * diff[0])
                        _t3 = t3 + (1.5 * diff[2])

                    elif (t1 > 0) and (t2 > 0) and (t3 < 0):
                        _t1 = t1 + (1.0 * diff[2])
                        _t2 = t2 + (0.5 * diff[2])
                        _t3 = t3 + (1.5 * diff[2])

                    elif (t1 > 0) and (t2 > 0) and (t3 > 0):
                        _t1 = t1 + (0.9 * diff[2])
                        _t2 = t2 + (0.1 * diff[0])
                        _t3 = t3 + (1.45 * diff[2])

                    elif (t1 < 0) and (t2 < 0) and (t3 < 0):
                        _t1 = t1 - (1.5 * diff[2])
                        _t2 = t2 + (0.1 * diff[2])
                        _t3 = t3 + (1.5 * diff[2])

                    elif (t1 < 0) and (t2 > 0) and (t3 > 0):
                        _t1 = t1 + (0.5 * diff[2])
                        _t2 = t2 - (0.05 * diff[2])
                        _t3 = t3 + (1.0 * diff[2])

                    else:
                        _t1 = t1
                        _t2 = t2
                        _t3 = t3

                elif np.array_equal(diff, np.array([0, 0, 2])):

                    print('%0.0f  %0.0f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f  %.2f' %
                          (fid, idx, t1, t2, t3, y, p, r, y1, p1, r1, error1))

                    print(diff)

                    if (t1 > 0) and (t2 < 0) and (t3 > 0):
                        _t1 = t1 - (1.1 * diff[2])
                        _t2 = t2 + (0.5 * diff[2])
                        _t3 = t3 + (1.5 * diff[2])

                    elif (t1 > 0) and (t2 < 0) and (t3 < 0):
                        _t1 = t1 - (1.5 * diff[2])
                        _t2 = t2 - (0.2 * diff[2])
                        _t3 = t3 + (1.5 * diff[2])

                    elif (t1 > 0) and (t2 > 0) and (t3 > 0):
                        _t1 = t1 + (0.1 * diff[0])
                        _t2 = t2 + (0.2 * diff[0])
                        _t3 = t3 + (1.0 * diff[2])

                    elif (t1 > 0) and (t2 > 0) and (t3 < 0):
                        _t1 = t1 + (0.35 * diff[2])
                        _t2 = t2 + (0.5 * diff[2])
                        _t3 = t3 + (1.0 * diff[2])

                    elif (t1 < 0) and (t2 < 0) and (t3 > 0):
                        _t1 = t1 - (0.3 * diff[2])
                        _t2 = t2 + (0.3 * diff[2])
                        _t3 = t3 + (1.0 * diff[2])

                    elif (t1 < 0) and (t2 > 0) and (t3 < 0):
                        _t1 = t1 + (1.0 * diff[2])
                        _t2 = t2 + (0.5 * diff[2])
                        _t3 = t3 + (1.1 * diff[2])

                    elif (t1 < 0) and (t2 < 0) and (t3 < 0):
                        _t1 = t1 - (1.0 * diff[2])
                        _t2 = t2 + (0.1 * diff[2])
                        _t3 = t3 + (1.0 * diff[2])

                    elif (t1 < 0) and (t2 > 0) and (t3 > 0):
                        _t1 = t1 + (1.8 * diff[2])
                        _t2 = t2 - (0.1 * diff[2])
                        _t3 = t3 + (1.8 * diff[2])

                    elif (t1 < 0) and (t2 < 0) and (t3 > 0):
                        _t1 = t1 - (1.0 * diff[2])
                        _t2 = t2 + (0.5 * diff[0])
                        _t3 = t3 + (1.5 * diff[2])

                    else:
                        _t1 = t1
                        _t2 = t2
                        _t3 = t3

                elif np.array_equal(diff, np.array([0, 0, 1])):

                    print('%0.0f  %0.0f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f  %.2f' %
                          (fid, idx, t1, t2, t3, y, p, r, y1, p1, r1, error1))

                    print(diff)

                    if (t1 < 0) and (t2 < 0) and (t3 < 0):
                        _t1 = t1 - (0.5 * diff[2])
                        _t2 = t2 + (0.1 * diff[2])
                        _t3 = t3 + (1.0 * diff[2])

                    elif (t1 < 0) and (t2 < 0) and (t3 > 0):
                        _t1 = t1 - (4.0 * diff[2])
                        _t2 = t2 + (0.6 * diff[2])
                        _t3 = t3 + (1.8 * diff[2])

                    elif (t1 > 0) and (t2 < 0) and (t3 > 0):
                        _t1 = t1 - (1.0 * diff[2])
                        _t2 = t2 + (0.1 * diff[2])
                        _t3 = t3 + (2.0 * diff[2])

                    elif (t1 > 0) and (t2 < 0) and (t3 < 0):
                        _t1 = t1 - (1.9 * diff[2])
                        _t2 = t2 - (0.3 * diff[2])
                        _t3 = t3 + (2.0 * diff[2])

                    elif (t1 > 0) and (t2 > 0) and (t3 > 0):
                        _t1 = t1 - (0.1 * diff[0])
                        _t2 = t2 + (0.2 * diff[2])
                        _t3 = t3 + (2.0 * diff[2])

                    elif (t1 > 0) and (t2 > 0) and (t3 < 0):
                        _t1 = t1 + (0.5 * diff[2])
                        _t2 = t2 + (0.4 * diff[2])
                        _t3 = t3 + (1.0 * diff[2])

                    else:
                        _t1 = t1
                        _t2 = t2
                        _t3 = t3

                elif np.array_equal(diff, np.array([0, 0, -1])):

                    print('%0.0f  %0.0f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f  %.2f' %
                          (fid, idx, t1, t2, t3, y, p, r, y1, p1, r1, error1))

                    print(diff)

                    if (t1 < 0) and (t2 > 0) and (t3 < 0):
                        _t1 = t1 + (1.0 * diff[2])
                        _t2 = t2 + (1.0 * diff[2])
                        _t3 = t3 + (1.1 * diff[2])

                    elif (t1 < 0) and (t2 > 0) and (t3 > 0):
                        _t1 = t1 + (0.3 * diff[2])
                        _t2 = t2 - (0.1 * diff[2])
                        _t3 = t3 + (1.55 * diff[2])

                    elif (t1 > 0) and (t2 > 0) and (t3 < 0):
                        _t1 = t1 + (0.1 * diff[0])
                        _t2 = t2 + (1.0 * diff[2])
                        _t3 = t3 + (0.8 * diff[2])

                    elif (t1 < 0) and (t2 < 0) and (t3 > 0):
                        _t1 = t1 - (0.0 * diff[0])
                        _t2 = t2 - (0.1 * diff[0])
                        _t3 = t3 - (0.6 * diff[2])

                    elif (t1 < 0) and (t2 < 0) and (t3 < 0):
                        _t1 = t1 - (0.3 * diff[2])
                        _t2 = t2 - (0.1 * diff[2])
                        _t3 = t3 + (0.9 * diff[2])

                    else:
                        _t1 = t1
                        _t2 = t2
                        _t3 = t3

                elif np.array_equal(diff, np.array([1, 0, 2])):

                    print('%0.0f  %0.0f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f  %.2f' %
                          (fid, idx, t1, t2, t3, y, p, r, y1, p1, r1, error1))

                    print(diff)

                    if (t1 > 0) and (t2 < 0) and (t3 > 0):
                        _t1 = t1 - (0.1 * diff[1])
                        _t2 = t2 + (1.6 * diff[0])
                        _t3 = t3 + (1.5 * diff[2])

                    elif (t1 > 0) and (t2 > 0) and (t3 < 0):
                        _t1 = t1 + (0.1 * diff[1])
                        _t2 = t2 + (1.0 * diff[0])
                        _t3 = t3 + (1.0 * diff[2])

                    elif (t1 > 0) and (t2 < 0) and (t3 < 0):
                        _t1 = t1 - (0.1 * diff[0])
                        _t2 = t2 + (1.6 * diff[0])
                        _t3 = t3 + (1.0 * diff[2])

                    elif (t1 > 0) and (t2 > 0) and (t3 > 0):
                        _t1 = t1 - (0.2 * diff[0])
                        _t2 = t2 + (1.0 * diff[0])
                        _t3 = t3 + (1.0 * diff[2])

                    elif (t1 < 0) and (t2 < 0) and (t3 > 0):
                        _t1 = t1 - (1.8 * diff[0])
                        _t2 = t2 + (1.6 * diff[0])
                        _t3 = t3 + (2.0 * diff[0])

                    elif (t1 < 0) and (t2 > 0) and (t3 > 0):
                        _t1 = t1 + (1.0 * diff[0])
                        _t2 = t2 + (2.0 * diff[0])
                        _t3 = t3 + (3.0 * diff[0])

                    elif (t1 < 0) and (t2 < 0) and (t3 < 0):
                        _t1 = t1 - (1.0 * diff[0])
                        _t2 = t2 + (1.0 * diff[2])
                        _t3 = t3 + (1.25 * diff[2])

                    elif (t1 < 0) and (t2 > 0) and (t3 < 0):
                        _t1 = t1 + (2.0 * diff[0])
                        _t2 = t2 + (1.5 * diff[0])
                        _t3 = t3 + (1.0 * diff[2])

                    else:
                        _t1 = t1
                        _t2 = t2
                        _t3 = t3

                elif np.array_equal(diff, np.array([1, 0, 0])):

                    print('%0.0f  %0.0f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f  %.2f' %
                          (fid, idx, t1, t2, t3, y, p, r, y1, p1, r1, error1))

                    print(diff)

                    if (t1 < 0) and (t2 < 0) and (t3 > 0):
                        _t1 = t1 + (0.3 * diff[0])
                        _t2 = t2 + (0.9 * diff[0])
                        _t3 = t3 - (0.4 * diff[0])

                    elif (t1 < 0) and (t2 > 0) and (t3 > 0):
                        _t1 = t1 + (0.8 * diff[0])
                        _t2 = t2 + (0.9 * diff[0])
                        _t3 = t3 - (0.2 * diff[0])

                    elif (t1 > 0) and (t2 > 0) and (t3 > 0):
                        _t1 = t1 + (0.9 * diff[0])
                        _t2 = t2 + (0.8 * diff[0])
                        _t3 = t3 + (0.1 * diff[2])

                    elif (t1 > 0) and (t2 < 0) and (t3 > 0):
                        _t1 = t1 + (0.9 * diff[0])
                        _t2 = t2 + (0.9 * diff[0])
                        _t3 = t3 - (0.2 * diff[0])

                    # elif (t1 > 0) and (t2 < 0) and (t3 < 0):
                    #     _t1 = t1 - (2.0 * diff[2])
                    #     _t2 = t2 - (0.1 * diff[0])
                    #     _t3 = t3 + (2.5 * diff[2])

                    else:
                        _t1 = t1
                        _t2 = t2
                        _t3 = t3

                elif np.array_equal(diff, np.array([1, 1, 2])):

                    print('%0.0f  %0.0f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f  %.2f' %
                          (fid, idx, t1, t2, t3, y, p, r, y1, p1, r1, error1))

                    print(diff)

                    if (t1 > 0) and (t2 < 0) and (t3 > 0):
                        _t1 = t1 - (0.3 * diff[1])
                        _t2 = t2 + (2.0 * diff[0])
                        _t3 = t3 + (0.8 * diff[2])

                    elif (t1 > 0) and (t2 < 0) and (t3 < 0):
                        _t1 = t1 + (0.1 * diff[0])
                        _t2 = t2 + (1.0 * diff[2])
                        _t3 = t3 + (1.0 * diff[2])

                    elif (t1 > 0) and (t2 > 0) and (t3 < 0):
                        _t1 = t1 + (1.0 * diff[0])
                        _t2 = t2 + (1.0 * diff[0])
                        _t3 = t3 + (1.0 * diff[2])

                    elif (t1 < 0) and (t2 < 0) and (t3 > 0):
                        _t1 = t1 + (0.1 * diff[0])
                        _t2 = t2 + (2.0 * diff[0])
                        _t3 = t3 + (1.0 * diff[0])

                    elif (t1 < 0) and (t2 > 0) and (t3 < 0):
                        _t1 = t1 + (1.5 * diff[0])
                        _t2 = t2 + (2.0 * diff[0])
                        _t3 = t3 + (1.45 * diff[2])

                    else:
                        _t1 = t1
                        _t2 = t2
                        _t3 = t3

                elif np.array_equal(diff, np.array([1, 1, 1])):

                    print('%0.0f  %0.0f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f  %.2f' %
                          (fid, idx, t1, t2, t3, y, p, r, y1, p1, r1, error1))

                    print(diff)

                    if (t1 < 0) and (t2 > 0) and (t3 < 0):
                        _t1 = t1 + (0.8 * diff[1])
                        _t2 = t2 + (1.8 * diff[0])
                        _t3 = t3 + (0.4 * diff[2])

                    elif (t1 > 0) and (t2 > 0) and (t3 < 0):
                        _t1 = t1 + (0.0 * diff[1])
                        _t2 = t2 + (1.3 * diff[0])
                        _t3 = t3 + (0.0 * diff[2])

                    elif (t1 > 0) and (t2 < 0) and (t3 > 0):
                        _t1 = t1 + (0.4 * diff[1])
                        _t2 = t2 + (1.4 * diff[0])
                        _t3 = t3 + (0.8 * diff[2])

                    elif (t1 < 0) and (t2 < 0) and (t3 > 0):
                        _t1 = t1 + (0.1 * diff[1])
                        _t2 = t2 + (1.0 * diff[0])
                        _t3 = t3 + (0.9 * diff[2])




                    else:
                        _t1 = t1
                        _t2 = t2
                        _t3 = t3

                elif np.array_equal(diff, np.array([0, 1, 0])):

                    print('%0.0f  %0.0f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f  %.2f' %
                          (fid, idx, t1, t2, t3, y, p, r, y1, p1, r1, error1))

                    print(diff)

                    if (t1 < 0) and (t2 < 0) and (t3 > 0):
                        _t1 = t1 + (1.0 * diff[1])
                        _t2 = t2 + (0.1 * diff[0])
                        _t3 = t3 + (0.1 * diff[2])

                    elif (t1 < 0) and (t2 < 0) and (t3 < 0):
                        _t1 = t1 + (1.0 * diff[1])
                        _t2 = t2 + (0.1 * diff[0])
                        _t3 = t3 + (0.1 * diff[2])

                    elif (t1 < 0) and (t2 > 0) and (t3 > 0):
                        _t1 = t1 + (1.0 * diff[1])
                        _t2 = t2 + (0.1 * diff[0])
                        _t3 = t3 + (0.1 * diff[2])

                    # elif (t1 < 0) and (t2 > 0) and (t3 > 0):
                    #     _t1 = t1 + (0.7 * diff[2])
                    #     _t2 = t2 + (0.3 * diff[0])
                    #     _t3 = t3 + (0.7 * diff[2])

                    else:
                        _t1 = t1
                        _t2 = t2
                        _t3 = t3


                else:
                    _t1 = t1
                    _t2 = t2
                    _t3 = t3


                # *****************************************************************

                # if (t1 < 0) and (t2 < 0) and (t3 > 0):
                #     _t1 = t1 + (1.0 * diff[1])
                #     _t2 = t2 + (0.1 * diff[0])
                #     _t3 = t3 + (0.1 * diff[2])
                #
                # elif (t1 < 0) and (t2 < 0) and (t3 < 0):
                #     _t1 = t1 + (1.0 * diff[1])
                #     _t2 = t2 + (0.1 * diff[0])
                #     _t3 = t3 + (0.1 * diff[2])
                #
                # elif (t1 < 0) and (t2 > 0) and (t3 < 0):
                #     _t1 = t1 + (1.0 * diff[1])
                #     _t2 = t2 + (0.1 * diff[0])
                #     _t3 = t3 + (0.1 * diff[2])
                #
                # elif (t1 < 0) and (t2 > 0) and (t3 > 0):
                #     _t1 = t1 + (1.0 * diff[1])
                #     _t2 = t2 + (0.1 * diff[0])
                #     _t3 = t3 + (0.1 * diff[2])
                #
                # elif (t1 > 0) and (t2 < 0) and (t3 > 0):
                #     _t1 = t1 + (1.0 * diff[1])
                #     _t2 = t2 - (0.1 * diff[0])
                #     _t3 = t3 + (0.1 * diff[2])
                #
                # elif (t1 > 0) and (t2 < 0) and (t3 < 0):
                #     _t1 = t1 + (1.0 * diff[1])
                #     _t2 = t2 - (0.1 * diff[0])
                #     _t3 = t3 + (0.1 * diff[2])
                #
                # elif (t1 > 0) and (t2 > 0) and (t3 > 0):
                #     _t1 = t1 + (1.0 * diff[1])
                #     _t2 = t2 - (0.1 * diff[0])
                #     _t3 = t3 + (0.1 * diff[2])
                #
                # elif (t1 > 0) and (t2 > 0) and (t3 < 0):
                #     _t1 = t1 + (1.0 * diff[1])
                #     _t2 = t2 - (0.1 * diff[0])
                #     _t3 = t3 + (0.1 * diff[2])
                #
                # else:
                #     _t1 = t1
                #     _t2 = t2
                #     _t3 = t3


                # *****************************************************************



                applyHPtoNeckBone(_t1, _t2, _t3)
                bpy.context.view_layer.update()

                matrix_empty = bpy.data.objects['empty'].matrix_world
                r_empty = tuple(map(round, np.degrees(np.array(matrix_empty.to_euler('XYZ')[0:3])), repeat(4)))
                l_empty = tuple(map(round, matrix_empty.translation, repeat(4)))

                matrix_camera = bpy.data.objects['Camera'].matrix_world
                r_camera = tuple(map(round, np.degrees(np.array(matrix_camera.to_euler('XYZ')[0:3])), repeat(4)))

                y, p, r = tuple(map(float, biwi[idx].strip().split()))

                y1, p1, r1 = -r_empty[2], -r_empty[0], r_empty[1]

                gt = np.array([y, p, r], dtype=np.int32)
                pred = np.array([y1, p1, r1], dtype=np.int32)

                error2 = np.mean(np.abs(pred - gt), axis=0)

                if error2 < error1:
                    print('----------------------------------------------------------------')
                    print('%.5f,%.5f,%.5f   %.5f,%.5f,%.5f   %.5f,%.5f,%.5f  %.2f' %
                          (_t1, _t2, _t3, y, p, r, y1, p1, r1, error2))

                    f.write('%.5f,%.5f,%.5f\n' % (_t1, _t2, _t3))
                else:
                    f.write('%.5f,%.5f,%.5f\n' % (t1, t2, t3))
            else:
                f.write('%.5f,%.5f,%.5f\n' % (t1, t2, t3))
        # else:
        #     f.write('%.5f,%.5f,%.5f\n' % (t1, t2, t3))
    f.close()
    # f1.close()
