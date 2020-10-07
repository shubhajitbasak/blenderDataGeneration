import bpy
import numpy as np
from itertools import repeat
import random
import bmesh

from math import radians, degrees
from mathutils import Matrix, Euler
from sympy.geometry import Point


class Camera:
    def __init__(self):
        self.camera = bpy.data.cameras.new('Camera')
        self.camera.name = 'Camera'
        # Import camera object
        self.scene_camera = bpy.data.objects.new('Camera', self.camera)
        self.location = self.scene_camera.location
        bpy.context.collection.objects.link(self.scene_camera)
        bpy.context.scene.camera = self.scene_camera

    def set_perspective(self, focal_length=35, sensor=32):
        self.scene_camera.data.type = "PERSP"
        self.scene_camera.data.lens = focal_length
        self.scene_camera.data.sensor_width = sensor

    def set_orthographic(self, ortho_scale):
        self.scene_camera.data.type = "ORTHO"
        self.scene_camera.data.ortho_scale = ortho_scale

    def set_far_clipping_plane(self, clip):
        self.scene_camera.data.clip_end = clip

    def rotate_around_3D_point(self, point, context_override, angle_degrees, axis):
        # Place the 3D cursor at the point
        bpy.context.scene.cursor_location = point

        # Set the pivot point to the 3D cursor
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].pivot_point = 'CURSOR'
                break

        bpy.ops.object.select_all(action='DESELECT')  # Deselect all
        blender_scene = bpy.context.scene
        blender_scene.objects.active = self.scene_camera

        print("CAMERA: {}. Rotation {}".format(self.scene_camera, angle_degrees))

        self.scene_camera.select = True  # Ensure only the camera is rotated

        #  Override the context of the operator or else it will only rotate around the object's median point
        bpy.ops.transform.rotate(context_override, value=Util.degrees_to_Radians(angle_degrees), axis=axis)

    def set_rotation(self,
                     rotation):  # TODO modify set_rotation so that it takes angles in degrees and converts them to radians
        self.scene_camera.rotation_euler = rotation

    def set_location(self, location):
        self.scene_camera.location = location

    def get_location(self):
        return self.scene_camera.location

    def get_roatation(self):
        return self.scene_camera.rotation_euler.copy()

    def get_roatation_degrees(self):
        rotation_radians = self.get_roatation()
        rotation_degrees = []
        for i in range(0, 3):
            rotation_degrees.append(Util.radians_to_degrees(rotation_radians[i]))
        return rotation_degrees


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


# Align initial head with respect to head bone

arma = bpy.data.objects['Armature']
bpy.context.view_layer.objects.active = arma
bpy.ops.object.mode_set(mode='POSE')

boneHead = arma.pose.bones['Head']  # Head  G6Beta_Head
boneNeck = arma.pose.bones['NeckTwist01']  # NeckTwist01  G6Beta_Neck
boneHead.rotation_mode = 'XYZ'
boneNeck.rotation_mode = 'XYZ'

bpy.context.view_layer.update()
boneHeadPose = tuple(map(round, np.degrees(np.array(boneHead.matrix.to_euler('XYZ')[0:3])), repeat(4)))
boneNeck.rotation_euler.rotate_axis('X', radians(90 - boneHeadPose[0]))  # pitch

bpy.context.view_layer.update()
boneHeadPose = tuple(map(round, np.degrees(np.array(boneHead.matrix.to_euler('XYZ')[0:3])), repeat(4)))
boneNeck.rotation_euler.rotate_axis('Z', radians(boneHeadPose[1]))  # roll

bpy.context.view_layer.update()
boneHeadPose = tuple(map(round, np.degrees(np.array(boneHead.matrix.to_euler('XYZ')[0:3])), repeat(4)))
boneNeck.rotation_euler.rotate_axis('Y', radians(-boneHeadPose[2]))  # yaw

#############################################################


# region Render
# The render resolution of the final texture and depth images:
final_image_resolution_x = 640
final_image_resolution_y = 480

render_resolution_percent = 100

render_focal_length = 20  # 35 is the default Blender uses - using 20 to match Synaptics data when camera is 500mm away
render_sensor_size = 32
default_camera_position = 0.3  # Default distance from the origin on the z-axis (assume millimetres)

bpy.context.scene.unit_settings.system = 'METRIC'

bpy.context.scene.unit_settings.length_unit = 'METERS'

# -------  setup scene render parameters -------- #
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'GPU'

# ------- setup screen resolution ------- #
bpy.context.scene.render.resolution_x = final_image_resolution_x
bpy.context.scene.render.resolution_y = final_image_resolution_y
bpy.context.view_layer.update()

_objects = bpy.context.scene.objects
bpy.ops.object.mode_set(mode='EDIT')

# --- Get the Mid Point of wye ball ---- #
emptyList = []

for _obj in _objects:
    # print(_obj.type)
    if _obj.type == 'MESH':
        # print(_obj_name)
        if 'Eye' in _obj.name:
            # print(_obj.name)
            for name in _obj.vertex_groups.keys():
                # print(name)
                # bpy.ops.object.empty_add(location=(0, 0, 0))
                mt = bpy.data.objects.new("empty", None)
                bpy.context.scene.collection.objects.link(mt)
                # mt = context.object
                mt.name = f"{_obj.name}_{name}"

                emptyList.append(mt.name)

                cl = mt.constraints.new('COPY_LOCATION')
                cl.target = _obj
                cl.subtarget = name

                cr = mt.constraints.new('COPY_ROTATION')
                cr.target = _obj
                cr.subtarget = name
                # print(mt.matrix_world)

bpy.ops.object.mode_set(mode='OBJECT')

l_eye = bpy.data.objects[emptyList[1]]
r_eye = bpy.data.objects[emptyList[0]]

l_eye_pos = Point(l_eye.matrix_world.translation)
r_eye_pos = Point(r_eye.matrix_world.translation)

global_location = map_tuple_gen(float, l_eye_pos.midpoint(r_eye_pos))

scn = bpy.context.scene

# --- Set Scene camera ---- #

camera = Camera()
camera.set_perspective(focal_length=render_focal_length, sensor=render_sensor_size)

bpy.data.scenes["Scene"].render.resolution_x = final_image_resolution_x
bpy.data.scenes["Scene"].render.resolution_y = final_image_resolution_y
bpy.data.scenes["Scene"].render.resolution_percentage = render_resolution_percent

# Offset the camera by the default camera position along the z-axis
camera_location = [global_location[0], -(-global_location[1] + default_camera_position), global_location[2]]
camera.set_location(camera_location)
camera.set_rotation((radians(90), 0, 0))

# Set the far clipping plane of the camera
camera.set_far_clipping_plane(default_camera_position * 10)

# Deselect all and delete the eye empty
bpy.ops.object.select_all(action='DESELECT')
l_eye.select_set(True)
bpy.ops.object.delete()
bpy.ops.object.select_all(action='DESELECT')
r_eye.select_set(True)
bpy.ops.object.delete()

# -----------------------------------

empty1 = bpy.data.objects.new("empty", None)
empty1.location = global_location
scn.collection.objects.link(empty1)

bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.object.select_all(action='DESELECT')

ob = bpy.data.objects['empty']
arma = bpy.data.objects['Armature']

bpy.ops.object.select_all(action='DESELECT')
arma.select_set(True)
bpy.context.view_layer.objects.active = arma

bpy.ops.object.mode_set(mode='EDIT')

parent_bone = 'Head'  # choose the bone name which you want to be the parent # G6Beta_Head  Head

arma.data.edit_bones.active = arma.data.edit_bones[parent_bone]

bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.object.select_all(action='DESELECT')  # deselect all objects
ob.select_set(True)
arma.select_set(True)
bpy.context.view_layer.objects.active = arma  # the active object will be the parent of all selected object

bpy.ops.object.parent_set(type='BONE', keep_transform=True)

context = bpy.context
for ob in context.selected_objects:
    ob.animation_data_clear()

arma = bpy.data.objects['Armature']
# bpy.context.scene.objects.active = ob
bpy.context.view_layer.objects.active = arma
bpy.ops.object.mode_set(mode='POSE')

pbone = arma.pose.bones['NeckTwist01']  # G6Beta_Neck  NeckTwist01
# Set rotation mode to Euler XYZ, easier to understand
# than default quaternions
pbone.rotation_mode = 'XYZ'
init_headpose = tuple(pbone.rotation_euler)

# Head Pose Frame Setup
if False:

    pbone.keyframe_insert(data_path="rotation_euler", frame=0)

    print("-------------------------------------------")
    print(map_tuple_gen(degrees, pbone.rotation_euler))

    # ------ Yaw (-80, +80) Pitch 0, Roll (-8.0, 8.0) ------ #

    for i in range(1, 21):
        pbone.rotation_euler = init_headpose  # Pitch 0
        pbone.rotation_euler.rotate_axis('Z', radians(random.uniform(-8.0, 8.0)))  # Roll
        pbone.rotation_euler.rotate_axis('Y', radians(-4 * (i - 0 + 1)))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    for i in range(21, 41):
        pbone.rotation_euler = init_headpose  # Pitch 0
        pbone.rotation_euler.rotate_axis('Z', radians(random.uniform(-8.0, 8.0)))  # Roll
        pbone.rotation_euler.rotate_axis('Y', radians(4 * (i - 20 + 1)))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # ------ Yaw (-60, +60) Pitch 10, Roll (-10.0, 10.0) ------ #

    for i in range(41, 61):
        pbone.rotation_euler = init_headpose
        pbone.rotation_euler.rotate_axis('X', radians(-10))  # Pitch 10
        pbone.rotation_euler.rotate_axis('Z', radians(random.uniform(-10.0, 10.0)))  # Roll
        pbone.rotation_euler.rotate_axis('Y', radians(-3 * (i - 40 + 1)))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    for i in range(61, 81):
        pbone.rotation_euler = init_headpose
        pbone.rotation_euler.rotate_axis('X', radians(-10))  # Pitch 10
        pbone.rotation_euler.rotate_axis('Z', radians(random.uniform(-10.0, 10.0)))  # Roll
        pbone.rotation_euler.rotate_axis('Y', radians(3 * (i - 60 + 1)))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    for i in range(81, 101):
        pbone.rotation_euler = init_headpose
        pbone.rotation_euler.rotate_axis('X', radians(10))  # Pitch -10
        pbone.rotation_euler.rotate_axis('Z', radians(random.uniform(-10.0, 10.0)))  # Roll
        pbone.rotation_euler.rotate_axis('Y', radians(-3 * (i - 80 + 1)))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    for i in range(101, 121):
        pbone.rotation_euler = init_headpose
        pbone.rotation_euler.rotate_axis('X', radians(10))  # Pitch -10
        pbone.rotation_euler.rotate_axis('Z', radians(random.uniform(-10.0, 10.0)))  # Roll
        pbone.rotation_euler.rotate_axis('Y', radians(3 * (i - 100 + 1)))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # ------ Yaw (-75, +75) Pitch 20, Roll (-20.0, 20.0) ------ #

    for i in range(121, 151):
        pbone.rotation_euler = init_headpose
        pbone.rotation_euler.rotate_axis('X', radians(20))  # Pitch -20
        pbone.rotation_euler.rotate_axis('Z', radians(random.uniform(-20.0, 20.0)))  # Roll
        pbone.rotation_euler.rotate_axis('Y', radians(-2.5 * (i - 120 + 1)))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    for i in range(151, 181):
        pbone.rotation_euler = init_headpose
        pbone.rotation_euler.rotate_axis('X', radians(20))  # Pitch -20
        pbone.rotation_euler.rotate_axis('Z', radians(random.uniform(-20.0, 20.0)))  # Roll
        pbone.rotation_euler.rotate_axis('Y', radians(2.5 * (i - 150 + 1)))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    for i in range(181, 211):
        pbone.rotation_euler = init_headpose
        pbone.rotation_euler.rotate_axis('X', radians(-20))  # Pitch 20
        pbone.rotation_euler.rotate_axis('Z', radians(random.uniform(-20.0, 20.0)))  # Roll
        pbone.rotation_euler.rotate_axis('Y', radians(-2.5 * (i - 180 + 1)))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    for i in range(211, 241):
        pbone.rotation_euler = init_headpose
        pbone.rotation_euler.rotate_axis('X', radians(-20))  # Pitch 20
        pbone.rotation_euler.rotate_axis('Z', radians(random.uniform(-20.0, 20.0)))  # Roll
        pbone.rotation_euler.rotate_axis('Y', radians(2.5 * (i - 210 + 1)))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # ------ Yaw (-75, +75) Pitch 35, Roll (-30.0, 30.0) ------ #


    for i in range(241, 261):
        pbone.rotation_euler = init_headpose
        pbone.rotation_euler.rotate_axis('X', radians(35))  # Pitch -35
        pbone.rotation_euler.rotate_axis('Z', radians(random.uniform(-30.0, 30.0)))  # Roll
        pbone.rotation_euler.rotate_axis('Y', radians(3 * (i - 240 + 1)))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    for i in range(261, 281):
        pbone.rotation_euler = init_headpose
        pbone.rotation_euler.rotate_axis('X', radians(35))  # Pitch -35
        pbone.rotation_euler.rotate_axis('Z', radians(random.uniform(-30.0, 30.0)))  # Roll
        pbone.rotation_euler.rotate_axis('Y', radians(-3 * (i - 260 + 1)))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    for i in range(281, 301):
        pbone.rotation_euler = init_headpose
        pbone.rotation_euler.rotate_axis('X', radians(-35))  # Pitch 35
        pbone.rotation_euler.rotate_axis('Z', radians(random.uniform(-30.0, 30.0)))  # Roll
        pbone.rotation_euler.rotate_axis('Y', radians(3 * (i - 280 + 1)))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    for i in range(301, 321):
        pbone.rotation_euler = init_headpose
        pbone.rotation_euler.rotate_axis('X', radians(-35))  # Pitch 35
        pbone.rotation_euler.rotate_axis('Z', radians(random.uniform(-30.0, 30.0)))  # Roll
        pbone.rotation_euler.rotate_axis('Y', radians(-3 * (i - 300 + 1)))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # ------ Yaw (-80, +80) Pitch 0 ------ #

    pbone.rotation_euler = init_headpose  # Pitch 0
    for i in range(321, 361):
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw

    pbone.rotation_euler = init_headpose  # Pitch 0
    for i in range(361, 421):
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw

    # ------ Yaw (-70, +70) Pitch Up to 62.5 ------ #

    # Pitch 2.5
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-2.5))  # Pitch 2.5
    for i in range(421, 456):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-2.5))  # Pitch 2.5
    for i in range(456, 491):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch 5
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-5))  # Pitch 5
    for i in range(491, 526):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-5))  # Pitch 5
    for i in range(526, 561):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch 7.5
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-7.5))  # Pitch 7.5
    for i in range(561, 596):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-7.5))  # Pitch 7.5
    for i in range(596, 631):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch 10
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-10))  # Pitch 10
    for i in range(631, 666):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-10))  # Pitch 10
    for i in range(666, 701):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch 12.5
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-12.5))  # Pitch 12.5
    for i in range(701, 736):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-12.5))  # Pitch 12.5
    for i in range(736, 771):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch 15
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-15))  # Pitch 15
    for i in range(771, 806):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-15))  # Pitch 15
    for i in range(806, 841):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch 17.5
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-17.5))  # Pitch 17.5
    for i in range(841, 876):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-17.5))  # Pitch 17.5
    for i in range(876, 911):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch 20
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-20))  # Pitch 20
    for i in range(911, 946):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-20))  # Pitch 20
    for i in range(946, 981):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch 22.5
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-22.5))  # Pitch 22.5
    for i in range(981, 1016):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-22.5))  # Pitch 22.5
    for i in range(1016, 1051):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch 25
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-25))  # Pitch 25
    for i in range(1051, 1086):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-25))  # Pitch 25
    for i in range(1086, 1121):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch 27.5
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-27.5))  # Pitch 27.5
    for i in range(1121, 1156):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-27.5))  # Pitch 27.5
    for i in range(1156, 1191):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch 30
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-30))  # Pitch 30
    for i in range(1191, 1226):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-30))  # Pitch 30
    for i in range(1226, 1261):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch 32.5
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-32.5))  # Pitch 32.5
    for i in range(1261, 1296):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-32.5))  # Pitch 32.5
    for i in range(1296, 1331):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch 35
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-35))  # Pitch 35
    for i in range(1331, 1366):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-35))  # Pitch 35
    for i in range(1366, 1401):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch 37.5
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-37.5))  # Pitch 37.5
    for i in range(1401, 1436):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-37.5))  # Pitch 37.5
    for i in range(1436, 1471):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch 40
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-40))  # Pitch 40
    for i in range(1471, 1506):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-40))  # Pitch 40
    for i in range(1506, 1541):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch 42.5
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-42.5))  # Pitch 42.5
    for i in range(1541, 1576):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-42.5))  # Pitch 42.5
    for i in range(1576, 1611):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch 45
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-45))  # Pitch 45
    for i in range(1611, 1646):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-45))  # Pitch 45
    for i in range(1646, 1681):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch 47.5
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-47.5))  # Pitch 47.5
    for i in range(1681, 1716):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-47.5))  # Pitch 47.5
    for i in range(1716, 1751):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch 50
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-50))  # Pitch 50
    for i in range(1751, 1786):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-50))  # Pitch 50
    for i in range(1786, 1821):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch 52.5
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-52.5))  # Pitch 52.5
    for i in range(1821, 1856):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-52.5))  # Pitch 52.5
    for i in range(1856, 1891):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch 55
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-55))  # Pitch 55
    for i in range(1891, 1926):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-55))  # Pitch 55
    for i in range(1926, 1961):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch 57.5
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-57.5))  # Pitch 57.5
    for i in range(1961, 1996):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-57.5))  # Pitch 57.5
    for i in range(1996, 2031):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch 60
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-60))  # Pitch 60
    for i in range(2031, 2066):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-60))  # Pitch 60
    for i in range(2066, 2101):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch 62.5
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-62.5))  # Pitch 62.5
    for i in range(2101, 2136):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(-62.5))  # Pitch 62.5
    for i in range(2136, 2171):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # ------ Yaw (-70, +70) Pitch Down to 47.5 ------ #

    # Pitch -2.5
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(2.5))  # Pitch -2.5
    for i in range(2171, 2206):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(2.5))  # Pitch -2.5
    for i in range(2206, 2241):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch -5
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(5))  # Pitch -5
    for i in range(2241, 2276):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(5))  # Pitch -5
    for i in range(2276, 2311):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch -7.5
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(7.5))  # Pitch -7.5
    for i in range(2311, 2346):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(7.5))  # Pitch 7.5
    for i in range(2346, 2381):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch -10
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(10))  # Pitch -10
    for i in range(2381, 2416):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(10))  # Pitch -10
    for i in range(2416, 2451):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch -12.5
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(12.5))  # Pitch -12.5
    for i in range(2451, 2486):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(12.5))  # Pitch -12.5
    for i in range(2486, 2521):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch -15
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(15))  # Pitch -15
    for i in range(2521, 2556):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(15))  # Pitch -15
    for i in range(2556, 2591):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch -17.5
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(17.5))  # Pitch -17.5
    for i in range(2591, 2626):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(17.5))  # Pitch -17.5
    for i in range(2626, 2661):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch -20
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(20))  # Pitch -20
    for i in range(2661, 2696):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(20))  # Pitch -20
    for i in range(2696, 2731):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch -22.5
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(22.5))  # Pitch -22.5
    for i in range(2731, 2766):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(22.5))  # Pitch -22.5
    for i in range(2766, 2801):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch -25
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(25))  # Pitch -25
    for i in range(2801, 2836):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(25))  # Pitch -25
    for i in range(2836, 2871):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch -27.5
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(27.5))  # Pitch -27.5
    for i in range(2871, 2906):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(27.5))  # Pitch -27.5
    for i in range(2906, 2941):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch -30
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(30))  # Pitch -30
    for i in range(2941, 2976):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(30))  # Pitch -30
    for i in range(2976, 3011):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch -32.5
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(32.5))  # Pitch -32.5
    for i in range(3011, 3046):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(32.5))  # Pitch -32.5
    for i in range(3046, 3081):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch -35
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(35))  # Pitch -35
    for i in range(3081, 3116):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(35))  # Pitch -35
    for i in range(3116, 3151):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch -37.5
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(37.5))  # Pitch -37.5
    for i in range(3151, 3186):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(37.5))  # Pitch -37.5
    for i in range(3186, 3221):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch 40
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(40))  # Pitch -40
    for i in range(3221, 3246):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(40))  # Pitch -40
    for i in range(3246, 3271):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch 42.5
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(42.5))  # Pitch -42.5
    for i in range(3271, 3296):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(42.5))  # Pitch -42.5
    for i in range(3296, 3321):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch 45
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(45))  # Pitch -45
    for i in range(3321, 3346):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(45))  # Pitch -45
    for i in range(3346, 3371):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # Pitch -47.5
    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(47.5))  # Pitch -47.5
    for i in range(3371, 3396):
        pbone.rotation_euler.rotate_axis('Y', radians(-2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    pbone.rotation_euler = init_headpose
    pbone.rotation_euler.rotate_axis('X', radians(47.5))  # Pitch -47.5
    for i in range(3396, 3421):
        pbone.rotation_euler.rotate_axis('Y', radians(2))  # Yaw
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    # ------ Roll (-45, +45) ------ #

    for i in range(3421, 3445):
        pbone.rotation_euler = init_headpose
        pbone.rotation_euler.rotate_axis('Z', radians(-2 * (i - 3421 + 1)))  # roll
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

    for i in range(3445, 3469):
        pbone.rotation_euler = init_headpose
        pbone.rotation_euler.rotate_axis('Z', radians(2 * (i - 3445 + 1)))  # roll
        pbone.keyframe_insert(data_path="rotation_euler", frame=i)

# -----------------------------------

bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.object.select_all(action='DESELECT')

bpy.ops.wm.save_mainfile()