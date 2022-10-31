import bpy
from math import radians, degrees
import bmesh
import numpy as np
import os

from math import radians, degrees
from mathutils import Matrix, Euler
from sympy.geometry import Point
import random


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
                     rotation):  # TO DO modify set_rotation so that it takes angles in degrees and converts them to radians
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


# region Render
# The render resolution of the final texture and depth images:
final_image_resolution_x = 640
final_image_resolution_y = 480

render_resolution_percent = 100

render_focal_length = 20  # 35 is the default Blender uses - using 20 to match Synaptics data when camera is 500mm away
render_sensor_size = 32
default_camera_position = 0.3  # Default distance from the origin on the z-axis (assume millimetres)

min_camera_position = 0.2
max_camera_position = 0.5

min_rotations = [-30, -45, -50]
max_rotations = [30, 45, 50]  # Max rotations for renders in pitch, yaw and roll
# rotation_step_degrees = [10,10,10] # Amount to rotate the face in each render on pitch, yaw and roll

bpy.context.scene.unit_settings.system = 'METRIC'

bpy.context.scene.unit_settings.length_unit = 'METERS'

# -------  setup scene render parameters -------- #
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'GPU'
# bpy.context.scene.cycles.samples = 64
bpy.context.scene.cycles.progressive = 'BRANCHED_PATH'
bpy.context.scene.cycles.aa_samples = 64
bpy.context.scene.cycles.min_transparent_bounces = 32
bpy.context.scene.cycles.light_sampling_threshold = 0

bpy.context.scene.cycles.sample_clamp_indirect = 0

bpy.context.scene.cycles.transparent_max_bounces = 32
bpy.context.scene.cycles.transmission_bounces = 32
bpy.context.scene.cycles.sample_clamp_indirect = 0

bpy.context.scene.cycles.max_bounces = 32
bpy.context.scene.cycles.diffuse_bounces = 0
bpy.context.scene.cycles.glossy_bounces = 0
bpy.context.scene.cycles.transparent_max_bounces = 16
bpy.context.scene.cycles.transmission_bounces = 16

# ------- setup screen resolution ------- #
bpy.context.scene.render.resolution_x = final_image_resolution_x
bpy.context.scene.render.resolution_y = final_image_resolution_y


_objects = bpy.context.scene.objects

bpy.ops.object.mode_set(mode='EDIT')

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
                # print(mt.matrix_world)

bpy.ops.object.mode_set(mode='OBJECT')

l_eye = bpy.data.objects[emptyList[1]]
r_eye = bpy.data.objects[emptyList[0]]

l_eye_pos = Point(l_eye.matrix_world.translation)
r_eye_pos = Point(r_eye.matrix_world.translation)

global_location = map_tuple_gen(float,l_eye_pos.midpoint(r_eye_pos))

scn = bpy.context.scene

camera = Camera()
camera.set_perspective(focal_length=render_focal_length, sensor=render_sensor_size)

bpy.data.scenes["Scene"].render.resolution_x = final_image_resolution_x
bpy.data.scenes["Scene"].render.resolution_y = final_image_resolution_y
bpy.data.scenes["Scene"].render.resolution_percentage = render_resolution_percent

# Offset the camera by the default camera position along the z-axis
camera_location = [global_location[0], -(-global_location[1] + default_camera_position), global_location[2]]
camera.set_location(camera_location)
camera.set_rotation((radians(90), 0, 0))

# Set the far clipping plane of the camera to a multiple of its distance from the origin
# far clip around 7 meter
camera.set_far_clipping_plane(default_camera_position * 50)

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

parent_bone = 'Head'  # choose the bone name which you want to be the parent # G6Beta_Head # Head

arma.data.edit_bones.active = arma.data.edit_bones[parent_bone]

bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.object.select_all(action='DESELECT')  # deselect all objects
ob.select_set(True)
arma.select_set(True)
bpy.context.view_layer.objects.active = arma  # the active object will be the parent of all selected object

bpy.ops.object.parent_set(type='BONE', keep_transform=True)

# ------------------------------------------------------------------------


matrix = bpy.data.objects['empty'].matrix_world

e = np.degrees(np.array(matrix.to_euler('XYZ')[0:3]))
print('Yaw %.2f Pitch %.2f Roll %.2f' % (e[2], e[1], e[0]))


# ------------------------------------------------------------------------------------------------


# with Gaze ------------------



context = bpy.context
for ob in context.selected_objects:
    ob.animation_data_clear()

arma = bpy.data.objects['Armature']
# bpy.context.scene.objects.active = ob
bpy.context.view_layer.objects.active = arma
bpy.ops.object.mode_set(mode='POSE')

pbone = arma.pose.bones['NeckTwist01']   # G6Beta_Neck  NeckTwist01
# Set rotation mode to Euler XYZ, easier to understand
# than default quaternions
pbone.rotation_mode = 'XYZ'
# select axis in ['X','Y','Z']  <--bone local
# axis = 'Z'
# angle = 2
# pbone.rotation_euler.rotate_axis(axis, math.radians(angle))


print("-------------------------------------------")
print(map_tuple_gen(degrees, pbone.rotation_euler))

# base_rot_deg = map_tuple_gen(degrees,pbone.rotation_euler)
# deg_X = base_rot_deg[0]
# deg_Y = base_rot_deg[1]
# deg_Z = base_rot_deg[2]


for i in range(0, 10):
    print(i)

    pbone.keyframe_insert(data_path="rotation_euler", frame=i + 1)
    pbone.rotation_euler.rotate_axis('Y', radians(-3))

    print(map_tuple_gen(degrees, pbone.rotation_euler))

for i in range(10, 30):
    print(i)

    pbone.keyframe_insert(data_path="rotation_euler", frame=i + 1)
    pbone.rotation_euler.rotate_axis('Y', radians(3))

for i in range(30, 50):
    print(i)

    pbone.rotation_euler.rotate_axis('Y', radians(-3))
    pbone.rotation_euler.rotate_axis('X', radians(20))
    pbone.keyframe_insert(data_path="rotation_euler", frame=i + 1)
    pbone.rotation_euler.rotate_axis('X', radians(-20))

    print(map_tuple_gen(degrees, pbone.rotation_euler))

for i in range(50, 70):
    print(i)

    pbone.rotation_euler.rotate_axis('Y', radians(3))
    pbone.rotation_euler.rotate_axis('X', radians(-20))
    pbone.keyframe_insert(data_path="rotation_euler", frame=i + 1)
    pbone.rotation_euler.rotate_axis('X', radians(20))

    print(map_tuple_gen(degrees, pbone.rotation_euler))

# -----------------------------------

bpy.ops.object.mode_set(mode='OBJECT')

# shiftDis = round(random.uniform(1, 1.6), 2)
#
# arma.location[1] = arma.location[1] - shiftDis
#
# cam = bpy.data.objects['Camera']
# cam.location[1] = cam.location[1] - shiftDis

bpy.ops.object.select_all(action='DESELECT')

bpy.ops.wm.save_mainfile()

