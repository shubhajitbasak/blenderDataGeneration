import bpy
from math import radians, degrees
import bmesh
import numpy as np
import os

from math import radians, degrees
from mathutils import Matrix, Euler


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
                     rotation):  # future modify set_rotation so that it takes angles in degrees and converts them to radians
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

    """"def rotateToPosition(self, override, finalPosition):
        rotates Camera from current position to final position
        current = self.get_roatation_degrees()
        print("current", current)
        current_degree = []
        for i in range(0,3):
            current_degree.append(finalPosition[i])
        self.rotateAroundAxis(override, current_degree[1], [0,1,0])
        self.rotateAroundAxis(override, -current_degree[0], [1,0,0])    
        self.rotateAroundAxis(override, current_degree[2], [0,0,1])
     """
    # future Add location function


# -------- To get the head bone and the neck bone ----------- #
#import bpy
#bpy.ops.object.mode_set(mode="OBJECT")
#for ob in bpy.data.objects:
#    if ob.type == "ARMATURE" and ob.users !=0:
#        for bone in ob.data.bones:
#            if('Head' in bone.name):
#                print('%s, %s' %(bone.name, bone.parent))


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

ob = bpy.context.object
me = ob.data
bm = bmesh.from_edit_mesh(me)

# --------- select the vertex midpoint of eyes ----- #
# --- need to manually select the vertex before running --- #

for elem in reversed(bm.select_history):
    if isinstance(elem, bmesh.types.BMVert):
        print("Active vertex:", elem)
        global_location = ob.matrix_world @ elem.co
        print(global_location)
        break

scn = bpy.context.scene

camera = Camera()
camera.set_perspective(focal_length=render_focal_length, sensor=render_sensor_size)

bpy.data.scenes["Scene"].render.resolution_x = final_image_resolution_x
bpy.data.scenes["Scene"].render.resolution_y = final_image_resolution_y
bpy.data.scenes["Scene"].render.resolution_percentage = render_resolution_percent

# Offset the camera by the default camera position along the z-axis
camera_location = [global_location.x, -(-global_location.y + default_camera_position), global_location.z]
camera.set_location(camera_location)
camera.set_rotation((radians(90), 0, 0))

# Set the far clipping plane of the camera to a multiple of its distance from the origin
# far clip around 7 meter
camera.set_far_clipping_plane(default_camera_position * 10)

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

parent_bone = 'Head'  # choose the bone name which you want to be the parent # G6Beta_Head

arma.data.edit_bones.active = arma.data.edit_bones[parent_bone]

bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.object.select_all(action='DESELECT')  # deselect all objects
ob.select_set(True)
arma.select_set(True)
bpy.context.view_layer.objects.active = arma  # the active object will be the parent of all selected object

bpy.ops.object.parent_set(type='BONE', keep_transform=True)

# ------------------------------------------------------------------------


# create light datablock, set attributes
light_data_1 = bpy.data.lights.new(name="Light_001", type='POINT')
light_data_1.energy = 200

# create new object with our light datablock
light_object_1 = bpy.data.objects.new(name="Light_001", object_data=light_data_1)

# link light object
scn.collection.objects.link(light_object_1)

# make it active 
bpy.context.view_layer.objects.active = light_object_1

# change location
light_object_1.location = (1, -(-camera.location.y + 2), camera.location.z)

bpy.ops.mesh.primitive_plane_add(location=(0, 0.5, 2.5), rotation=(radians(90), 0, 0))
objPlane_001 = bpy.data.objects['Plane']
objPlane_001.name = 'Plane.001'
objPlane_001.scale = (3, 3, 3)

bpy.ops.mesh.primitive_plane_add(location=(2, 0, 2.5), rotation=(0, radians(90), 0))
objPlane_002 = bpy.data.objects['Plane']
objPlane_002.name = 'Plane.002'
objPlane_002.scale = (3, 3, 3)

bpy.ops.mesh.primitive_plane_add(location=(-2, 0, 2.5), rotation=(0, radians(90), 0))
objPlane_003 = bpy.data.objects['Plane']
objPlane_003.name = 'Plane.003'
objPlane_003.scale = (3, 3, 3)

bpy.ops.mesh.primitive_plane_add(location=(0, 0, 3), rotation=(0, 0, 0))
objPlane_004 = bpy.data.objects['Plane']
objPlane_004.name = 'Plane.004'
objPlane_004.scale = (3, 3, 3)

bpy.ops.mesh.primitive_plane_add(location=(0, 0, 0), rotation=(0, 0, 0))
objPlane_005 = bpy.data.objects['Plane']
objPlane_005.name = 'Plane.005'
objPlane_005.scale = (3, 3, 3)

mat = bpy.data.materials.new(name="MaterialPlane001")
objPlane_001.data.materials.append(mat)
objPlane_002.data.materials.append(mat)
objPlane_003.data.materials.append(mat)
objPlane_004.data.materials.append(mat)
# objPlane_005.data.materials.append(mat)

matrix = bpy.data.objects['empty'].matrix_world

e = np.degrees(np.array(matrix.to_euler('XYZ')[0:3]))
print('Yaw %.2f Pitch %.2f Roll %.2f' % (e[2], e[1], e[0]))


# ------------------------------------------------------------------------------------------------


# with Gaze ------------------


def map_tuple_gen(func, tup):
    """
    Applies func to each element of tup and returns a new tuple.

    >>> a = (1, 2, 3, 4)
    >>> func = lambda x: x * x
    >>> map_tuple(func, a)
    (1, 4, 9, 16)
    """
    return tuple(func(itup) for itup in tup)


context = bpy.context
for ob in context.selected_objects:
    ob.animation_data_clear()

arma = bpy.data.objects['Armature']
# bpy.context.scene.objects.active = ob
bpy.context.view_layer.objects.active = arma
bpy.ops.object.mode_set(mode='POSE')

pbone = arma.pose.bones['NeckTwist01']   # G6Beta_Neck
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

bpy.ops.object.select_all(action='DESELECT')
